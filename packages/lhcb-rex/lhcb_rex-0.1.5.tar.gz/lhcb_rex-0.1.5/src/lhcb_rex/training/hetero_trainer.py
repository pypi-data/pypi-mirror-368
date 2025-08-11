import lhcb_rex.settings.globals as myGlobals
import pytorch_lightning as pl
import torch
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
from tensorboard.backend.event_processing import event_accumulator
import numpy as np
from torchmetrics.regression import MeanAbsolutePercentageError
import torch.nn as nn
from torch_geometric.loader import DataLoader
from torch.utils.data import WeightedRandomSampler
import os
import shutil
import pickle
import importlib.resources
import lhcb_rex.processing.transformers as tfs
import re
from diffusers import DDPMScheduler

import torch.nn.functional as F
from torch.nn.utils import clip_grad_norm_

mean_abs_percentage_error = MeanAbsolutePercentageError()


class AdaptiveAdvLoss:
    def __init__(
        self, base_lambda_adv=0.1, alpha=0.5, min_lambda=0.01, max_lambda=10.0
    ):
        self.base_lambda_adv = base_lambda_adv
        self.alpha = alpha  # Scaling factor
        self.min_lambda = min_lambda
        self.max_lambda = max_lambda
        self.current_lambda_adv = base_lambda_adv  # Initialize λ_adv

    def update_lambda(self, discriminator_accuracy):
        """Adjust lambda_adv based on discriminator performance."""
        scaling_factor = 1 + self.alpha * (2 * discriminator_accuracy - 1)
        self.current_lambda_adv = self.base_lambda_adv * scaling_factor

        # Clip values to avoid extreme weights
        self.current_lambda_adv = max(
            self.min_lambda, min(self.current_lambda_adv, self.max_lambda)
        )

        return self.current_lambda_adv


class TrainerModule(pl.LightningModule):
    def __init__(
        self,
        model,
        dataloaders,
        val_dataloaders,
        training_batch_size=512,
        save_models=True,
        use_weights=False,
        network_option=False,
        enhance_fully_reco=1.0,
    ):
        super(TrainerModule, self).__init__()

        self.automatic_optimization = False
        self.network_option = network_option

        self.smearingnet = False
        if self.network_option in [
            "mom_smear",
            "PID_trig",
            "mom_smear_diffusion",
            "mom_smear_VAE",
            "mom_smear_flowmatching",
            "PID_trig_diffusion",
            "PID_trig_flowmatching",
        ]:  # need to be able to untransform PID?
            self.smearingnet = True
            transformer_quantiles = pickle.load(
                importlib.resources.files("lhcb_rex")
                .joinpath("processing/transfomer_quantiles.pkl")
                .open("rb")
            )
            min_maxes = pickle.load(
                importlib.resources.files("lhcb_rex")
                .joinpath("processing/min_maxes.pkl")
                .open("rb")
            )
            self.Transformers = {}
            for i, (key, quantiles) in enumerate(transformer_quantiles.items()):
                transformer_i = tfs.UpdatedTransformer(min_maxes=min_maxes)
                transformer_i.fit(quantiles, key)
                self.Transformers[key] = transformer_i

        self.saved_code = False
        self.save_models = save_models
        self.training_batch_size = training_batch_size

        self.dataloaders = dataloaders

        self.val_dataloaders = val_dataloaders
        self.models = model

        self.mother_targets = model.branch_options["mother_targets"]
        self.track_targets = model.branch_options["track_targets"]
        self.intermediate_targets = model.branch_options["intermediate_targets"]

        self.N_mother_targets = len(self.mother_targets)
        self.N_track_targets = len(self.track_targets)
        self.N_intermediate_targets = len(self.intermediate_targets)
        self.N_targets = (
            self.N_mother_targets + self.N_track_targets + self.N_intermediate_targets
        )

        self.using_node_targets = True
        if len(self.track_targets) == 0:
            self.using_node_targets = False

        self.gan = self.models.gan

        if val_dataloaders:
            self.val_labels = list(val_dataloaders.keys())

        self.gen_data = {}
        self.gen_data_physical = {}
        self.true_data = {}
        self.true_data_physical = {}
        self.reco_data = {}
        self.val_losses = {}

        self.ROC_scores = {}

        self.initialisation = True

        self.plot_counter = -1
        self.previous_epoch = -1

        self.step_counter = 0

        self.use_weights = use_weights
        self.enhance_fully_reco = enhance_fully_reco

        if "reco_vertex" in self.network_option:
            transformer_quantiles = pickle.load(
                importlib.resources.files("lhcb_rex")
                .joinpath("processing/transfomer_quantiles.pkl")
                .open("rb")
            )
            min_maxes = pickle.load(
                importlib.resources.files("lhcb_rex")
                .joinpath("processing/min_maxes.pkl")
                .open("rb")
            )
            self.Transformers = {}
            for i, (key, quantiles) in enumerate(transformer_quantiles.items()):
                transformer_i = tfs.UpdatedTransformer(min_maxes=min_maxes)
                transformer_i.fit(quantiles, key)
                self.Transformers[key] = transformer_i
                if "DAUGHTER1" in key:
                    for Ni in [2, 3]:
                        self.Transformers[key.replace("DAUGHTER1", f"DAUGHTER{Ni}")] = (
                            self.Transformers[key]
                        )

        if "diffusion" in self.network_option:
            if "smear" in self.network_option:
                self.noise_scheduler = DDPMScheduler(
                    num_train_timesteps=model.gan.steps,
                    clip_sample=True,
                    clip_sample_range=5.5,
                    beta_schedule="squaredcos_cap_v2",
                )
                # https://huggingface.co/docs/diffusers/en/api/schedulers/ddpm#diffusers.DDPMScheduler.clip_sample there was a clip buired in here!!
            elif "reco" not in self.network_option:
                self.noise_scheduler = DDPMScheduler(
                    num_train_timesteps=model.gan.steps,
                    beta_schedule="squaredcos_cap_v2",
                )
            else:
                self.noise_scheduler = DDPMScheduler(
                    num_train_timesteps=model.gan.steps,
                    # beta_schedule="squaredcos_cap_v2",
                )
                # self.noise_scheduler = DDPMScheduler(num_train_timesteps=model.gan.steps, clip_sample=False)

    def on_train_epoch_end(self):
        print("\n[INFO] Switching dataset (epoch end):\n")
        for key in self.dataloaders:
            print(f"Dataloader: {key} (splits:{self.dataloaders[key].dataset.splits})")
            if self.dataloaders[key].dataset.splits != 1:
                new_dataset = self.dataloaders[key].dataset
                new_dataset.load_next()
                fully_reco_enhancement = [
                    self.enhance_fully_reco if x == 1.0 else 1.0
                    for x in new_dataset.options["fully_reco_bool"]
                ]
                if self.use_weights:
                    weights = new_dataset.options["training_weights"]
                    if self.enhance_fully_reco > 1.0:
                        weights = torch.multiply(weights, fully_reco_enhancement)
                    sampler = WeightedRandomSampler(
                        weights, num_samples=len(weights), replacement=True
                    )
                    dataloader = DataLoader(
                        new_dataset,
                        batch_size=self.training_batch_size,
                        sampler=sampler,
                    )
                else:
                    if self.enhance_fully_reco > 1.0:
                        sampler = WeightedRandomSampler(
                            fully_reco_enhancement,
                            num_samples=len(fully_reco_enhancement),
                            replacement=True,
                        )
                        dataloader = DataLoader(
                            new_dataset,
                            batch_size=self.training_batch_size,
                            sampler=sampler,
                        )
                    else:
                        dataloader = DataLoader(
                            new_dataset,
                            batch_size=self.training_batch_size,
                            shuffle=True,
                        )
                self.dataloaders[key] = dataloader

    def _loss_generator(self, y_pred):
        out = -torch.log(y_pred)
        return torch.mean(out, dim=-1)

    def forward(self, batch, blur_conditions=False, return_heteroscedastic=False):
        return self.gan.hetero_forward(
            batch,
            blur_conditions=blur_conditions,
            return_heteroscedastic=return_heteroscedastic,
        )

    def update_discriminator_eGAN(self, batch, gradient_penalty=False):
        device = batch["mother"].x.device

        try:
            batch["intermediate"].x
            intermediate_present = True
        except Exception:
            intermediate_present = False

        genbatch = batch.clone()

        x_mother = torch.randn(
            (genbatch["mother"].x.shape[0], self.gan.mother_latent_dims), device=device
        )  # * 0.25
        x_track = torch.randn(
            (genbatch["track"].x.shape[0], self.gan.track_latent_dims), device=device
        )  # * 0.25
        if intermediate_present:
            x_intermediate = torch.randn(
                (
                    genbatch["intermediate"].x.shape[0],
                    self.gan.intermediate_latent_dims,
                ),
                device=device,
            )  # * 0.25

        batch_size = genbatch["mother"].x.shape[0]

        # Initial latent container
        latent = {
            "mother": x_mother,
            "track": x_track,
        }
        if intermediate_present:
            latent["intermediate"] = x_intermediate

        noise = torch.rand(
            (genbatch["mother_conditions"].x.shape[0], 5),
            device=genbatch["mother_conditions"].x.device,
            dtype=genbatch["mother_conditions"].x.dtype,
        )
        genbatch["mother_conditions"].x = torch.cat(
            (genbatch["mother_conditions"].x, noise), dim=-1
        )
        if intermediate_present:
            noise = torch.rand(
                (genbatch["intermediate_conditions"].x.shape[0], 3),
                device=genbatch["intermediate_conditions"].x.device,
                dtype=genbatch["intermediate_conditions"].x.dtype,
            )
            genbatch["intermediate_conditions"].x = torch.cat(
                (genbatch["intermediate_conditions"].x, noise), dim=-1
            )
        noise = torch.rand(
            (genbatch["track_conditions"].x.shape[0], 2),
            device=genbatch["track_conditions"].x.device,
            dtype=genbatch["track_conditions"].x.dtype,
        )
        genbatch["track_conditions"].x = torch.cat(
            (genbatch["track_conditions"].x, noise), dim=-1
        )

        for t in reversed(range(self.noise_scheduler.config.num_train_timesteps)):
            timesteps = torch.full((batch_size,), t, device=device, dtype=torch.long)

            genbatch["mother"].x = latent["mother"]
            genbatch["track"].x = latent["track"]
            if intermediate_present:
                genbatch["intermediate"].x = latent["intermediate"]

            # Predict noise at current timestep
            noise_pred = self.gan.diffuser(
                batch=genbatch,
                timesteps=timesteps,
            )[0]

            # Denoise each component
            for node_type in latent:
                model_output = noise_pred[node_type]

                # Ensure shape matches expected sample shape
                if model_output.ndim == 1:
                    model_output = model_output.unsqueeze(-1)  # Or reshape accordingly

                latent[node_type] = self.noise_scheduler.step(
                    model_output=model_output, timestep=t, sample=latent[node_type]
                ).prev_sample

        genbatch["mother"].x = latent["mother"]
        genbatch["track"].x = latent["track"]
        if intermediate_present:
            genbatch["intermediate"].x = latent["intermediate"]
        # genbatch here is unnoised diffusion model output

        # renoise conditions
        noise = torch.rand(
            (genbatch["mother_conditions"].x.shape[0], 5),
            device=genbatch["mother_conditions"].x.device,
            dtype=genbatch["mother_conditions"].x.dtype,
        )
        genbatch["mother_conditions"].x[:, -5:] = noise
        if intermediate_present:
            noise = torch.rand(
                (genbatch["intermediate_conditions"].x.shape[0], 3),
                device=genbatch["intermediate_conditions"].x.device,
                dtype=genbatch["intermediate_conditions"].x.dtype,
            )
            genbatch["intermediate_conditions"].x[:, -3:] = noise
        noise = torch.rand(
            (genbatch["track_conditions"].x.shape[0], 2),
            device=genbatch["track_conditions"].x.device,
            dtype=genbatch["track_conditions"].x.dtype,
        )
        genbatch["track_conditions"].x[:, -2:] = noise

        epsilon = self.gan.generator(
            batch=genbatch,
        )[0]

        for node_type in epsilon:
            if epsilon[node_type].ndim == 1:
                epsilon[node_type] = epsilon[node_type].unsqueeze(
                    -1
                )  # Or reshape accordingly

        # remove noise from conditions
        genbatch["mother_conditions"].x = genbatch["mother_conditions"].x[:, :-5]
        if intermediate_present:
            genbatch["intermediate_conditions"].x = genbatch[
                "intermediate_conditions"
            ].x[:, :-3]
        genbatch["track_conditions"].x = genbatch["track_conditions"].x[:, :-2]

        generated_epsilon = genbatch.clone()
        generated_epsilon["mother"].x = epsilon["mother"]
        if intermediate_present:
            generated_epsilon["intermediate"].x = epsilon["intermediate"]
        generated_epsilon["track"].x = epsilon["track"]

        true_epsilon = genbatch.clone()
        true_epsilon["mother"].x = (batch["mother"].x - genbatch["mother"].x) * 10.0
        if intermediate_present:
            true_epsilon["intermediate"].x = (
                batch["intermediate"].x - genbatch["intermediate"].x
            ) * 10.0
        true_epsilon["track"].x = (batch["track"].x - genbatch["track"].x) * 10.0

        disc_out_fake = self.gan.discriminator(
            batch=generated_epsilon,
        )
        disc_out_real = self.gan.discriminator(
            batch=true_epsilon,
        )

        labels_fake = torch.ones(disc_out_fake.shape[0], 1).to(device) * 0.1
        labels_real = torch.ones(disc_out_real.shape[0], 1).to(device) * 0.9

        labels_D = torch.cat([labels_fake, labels_real], dim=0)
        preds_D = torch.cat([disc_out_fake, disc_out_real], dim=0)

        disc_loss_fn = nn.BCELoss()
        disc_loss = disc_loss_fn(preds_D.squeeze(), labels_D.squeeze())

        weight_balance = preds_D.squeeze().shape[0] / 2

        return disc_loss, weight_balance

    def update_discriminator(self, batch, gradient_penalty=False):
        # print(batch)
        # quit()
        # for idx, batch_i in enumerate(batch):

        device = batch["mother"].x.device

        try:
            batch["intermediate"].x
            intermediate_present = True
        except Exception:
            intermediate_present = False

        if intermediate_present:
            mother, intermediate, track = self.gan.generator(
                torch.randn(
                    (batch["mother"].x.shape[0], self.gan.mother_latent_dims)
                ).to(device),
                torch.randn((batch["track"].x.shape[0], self.gan.track_latent_dims)).to(
                    device
                ),
                torch.randn(
                    (
                        batch["intermediate"].x.shape[0],
                        self.gan.intermediate_latent_dims,
                    )
                ).to(device),
                batch["mother_conditions"],
                batch["track_conditions"],
                batch["intermediate_conditions"],
                batch["edge_index_tensors"],
                batch,
            )
        else:
            mother, intermediate, track = self.gan.generator(
                torch.randn(
                    (batch["mother"].x.shape[0], self.gan.mother_latent_dims)
                ).to(device),
                torch.randn((batch["track"].x.shape[0], self.gan.track_latent_dims)).to(
                    device
                ),
                None,
                batch["mother_conditions"],
                batch["track_conditions"],
                None,
                batch["edge_index_tensors"],
                batch,
            )

        mother_in = batch["mother"].clone()
        mother_in.x = mother

        track_in = batch["track"].clone()
        track_in.x = track

        if intermediate_present:
            intermediate_in = batch["intermediate"].clone()
            intermediate_in.x = intermediate

            disc_out_fake = self.gan.discriminator(
                mother_in,
                track_in,
                intermediate_in,
                batch["mother_conditions"],
                batch["track_conditions"],
                batch["intermediate_conditions"],
                batch["edge_index_tensors"],
                batch,
            )
            disc_out_real = self.gan.discriminator(
                batch["mother"],
                batch["track"],
                batch["intermediate"],
                batch["mother_conditions"],
                batch["track_conditions"],
                batch["intermediate_conditions"],
                batch["edge_index_tensors"],
                batch,
            )
        else:
            disc_out_fake = self.gan.discriminator(
                mother_in,
                track_in,
                None,
                batch["mother_conditions"],
                batch["track_conditions"],
                None,
                batch["edge_index_tensors"],
                batch,
            )
            disc_out_real = self.gan.discriminator(
                batch["mother"],
                batch["track"],
                None,
                batch["mother_conditions"],
                batch["track_conditions"],
                None,
                batch["edge_index_tensors"],
                batch,
            )

        labels_fake = torch.ones(disc_out_fake.shape[0], 1).to(device) * 0.1
        labels_real = torch.ones(disc_out_real.shape[0], 1).to(device) * 0.9

        labels_D = torch.cat([labels_fake, labels_real], dim=0)
        preds_D = torch.cat([disc_out_fake, disc_out_real], dim=0)

        disc_loss_fn = nn.BCELoss()
        disc_loss = disc_loss_fn(preds_D.squeeze(), labels_D.squeeze())

        weight_balance = preds_D.squeeze().shape[0] / 2

        return disc_loss, weight_balance

    def append_addition_vars_for_disc(self, in_batch, in_out):
        dtype = in_batch["11"].x.dtype
        device = in_batch["11"].x.device

        particle_types = ["11", "13", "211", "321", "2212"]
        for idx, particle_type in enumerate(particle_types):
            if idx == 0:
                true_mom = in_batch[f"{particle_type}_conditions"].x
                reco_mom = in_out[f"{particle_type}"].detach().cpu().numpy()
                for i in range(3):
                    transf_resfrac_px = self.Transformers[
                        f"{myGlobals.smearing_track_targets[i].replace('DAUGHTERN', 'DAUGHTER1')}_{particle_type}"
                    ]
                    reco_mom[:, i] = transf_resfrac_px.unprocess(reco_mom[:, i])
                reco_mom = torch.tensor(reco_mom)
                batch = in_batch[f"{particle_type}"].batch
            else:
                true_mom = torch.cat(
                    (true_mom, in_batch[f"{particle_type}_conditions"].x), dim=0
                )

                reco_mom_i = in_out[f"{particle_type}"].detach().cpu().numpy()
                for i in range(3):
                    transf_resfrac_px = self.Transformers[
                        f"{myGlobals.smearing_track_targets[i].replace('DAUGHTERN', 'DAUGHTER1')}_{particle_type}"
                    ]
                    reco_mom_i[:, i] = transf_resfrac_px.unprocess(reco_mom_i[:, i])
                reco_mom_i = torch.tensor(reco_mom_i)

                reco_mom = torch.cat((reco_mom, reco_mom_i), dim=0)
                batch = torch.cat((batch, in_batch[f"{particle_type}"].batch), dim=0)

        true_mom = true_mom[:, :3].to(device)
        # reco_mom is actually transformed resfrac_px
        resfrac = reco_mom

        transf_px_true = self.Transformers[
            myGlobals.smearing_track_conditions[0].replace("DAUGHTERN", "DAUGHTER1")
        ]
        px_true = transf_px_true.unprocess(true_mom[:, 0].clone().cpu().numpy())
        reco_px = resfrac[:, 0] * (px_true + 1e-4) + px_true
        reco_px = torch.tensor(reco_px, dtype=dtype).unsqueeze(1)

        transf_py_true = self.Transformers[
            myGlobals.smearing_track_conditions[1].replace("DAUGHTERN", "DAUGHTER1")
        ]
        py_true = transf_py_true.unprocess(true_mom[:, 1].clone().cpu().numpy())
        reco_py = resfrac[:, 1] * (py_true + 1e-4) + py_true
        reco_py = torch.tensor(reco_py, dtype=dtype).unsqueeze(1)

        transf_pz_true = self.Transformers[
            myGlobals.smearing_track_conditions[2].replace("DAUGHTERN", "DAUGHTER1")
        ]
        pz_true = transf_pz_true.unprocess(true_mom[:, 2].clone().cpu().numpy())
        reco_pz = resfrac[:, 2] * (pz_true + 1e-4) + pz_true
        reco_pz = torch.tensor(reco_pz, dtype=dtype).unsqueeze(1)

        true_mom = torch.cat(
            (
                torch.tensor(px_true, dtype=dtype).unsqueeze(1),
                torch.tensor(py_true, dtype=dtype).unsqueeze(1),
                torch.tensor(pz_true, dtype=dtype).unsqueeze(1),
            ),
            dim=1,
        ).to(device)
        reco_mom = torch.cat((reco_px, reco_py, reco_pz), dim=1).to(device)

        ratio_of_squares = reco_mom**2 / true_mom**2

        ratio_of_sum_of_squares = torch.sum(reco_mom**2, dim=1) / torch.sum(
            true_mom**2, dim=1
        )
        ratio_of_sum_of_squares = ratio_of_sum_of_squares.unsqueeze(1)

        extra_vars = torch.cat((ratio_of_squares, ratio_of_sum_of_squares), dim=1)

        extra_vars_out = {}
        index = 0
        for i in in_out:
            extra_vars_out[i] = extra_vars[index : in_out[i].shape[0] + index, :]
            index += in_out[i].shape[0]

        return extra_vars_out

    def update_discriminator_smearingnet(self, batch, gradient_penalty=False):
        # for idx, batch_i in enumerate(batch):
        device = batch["11"].x.device

        particle_types = ["11", "13", "211", "321", "2212"]
        track_latent = {}
        for particle_type in particle_types:
            track_latent[particle_type] = torch.randn(
                (
                    batch[particle_type].x.shape[0],
                    self.gan.track_latent_dims,
                )
            ).to(device)
        out = self.gan.generator(
            track_latent,
            batch=batch,
        )

        # if self.network_option == "mom_smear":

        #     with torch.no_grad():

        #         # batch_size = batch["11"].ptr.numel() - 1

        #         # sampled = self.gan.inference(batch_size, batch, self.noise_scheduler)

        #         true_mom, reco_mom, true_reco_mom, batch_idxs, masses = [], [], [], [], []
        #         dtype = batch["11"].x.dtype
        #         device = batch["11"].x.device

        #         PDG_MASSES = {
        #             "11": 0.000511 * 1e3,   # e-
        #             "13": 0.10566 * 1e3,    # mu-
        #             "211": 0.13957 * 1e3,   # pi+
        #             "321": 0.49367 * 1e3,   # K+
        #             "2212": 0.93827 * 1e3   # p+
        #         }

        #         for idx, p in enumerate(["11", "13", "211", "321", "2212"]):

        #             if p in out:

        #                 # Get true mom
        #                 true = batch[f"{p}_conditions"].x[:, :3]

        #                 pred_reco = out[p].detach().cpu().numpy()
        #                 true_reco = batch[p].x.detach().cpu().numpy()

        #                 for i in range(3):
        #                     tf = self.Transformers[
        #                         f"{myGlobals.smearing_track_targets[i].replace('DAUGHTERN', 'DAUGHTER1')}_{p}"
        #                     ]
        #                     pred_reco[:, i] = tf.unprocess(pred_reco[:, i])
        #                     true_reco[:, i] = tf.unprocess(true_reco[:, i])
        #                 pred_reco = torch.tensor(pred_reco, dtype=dtype)
        #                 true_reco = torch.tensor(true_reco, dtype=dtype)

        #                 batch_p = batch[p].batch

        #                 # Assign correct mass
        #                 mass_val = PDG_MASSES[p]
        #                 masses.append(torch.full((pred_reco.shape[0],), mass_val, dtype=dtype, device=device))

        #                 true_mom.append(true)
        #                 reco_mom.append(pred_reco)
        #                 true_reco_mom.append(true_reco)
        #                 batch_idxs.append(batch_p)

        #         # Stack across all particles
        #         true_mom = torch.cat(true_mom, dim=0).to(device)
        #         reco_mom = torch.cat(reco_mom, dim=0).to(device)
        #         true_reco_mom = torch.cat(true_reco_mom, dim=0).to(device)
        #         batch_idxs = torch.cat(batch_idxs, dim=0).to(device)
        #         masses = torch.cat(masses, dim=0).to(device)

        #         # Unprocess true values as well
        #         px_true = self.Transformers[myGlobals.smearing_track_conditions[0].replace("DAUGHTERN", "DAUGHTER1")].unprocess(true_mom[:, 0].cpu().numpy())
        #         py_true = self.Transformers[myGlobals.smearing_track_conditions[1].replace("DAUGHTERN", "DAUGHTER1")].unprocess(true_mom[:, 1].cpu().numpy())
        #         pz_true = self.Transformers[myGlobals.smearing_track_conditions[2].replace("DAUGHTERN", "DAUGHTER1")].unprocess(true_mom[:, 2].cpu().numpy())

        #         px_true = torch.tensor(px_true, dtype=dtype).to(device)
        #         py_true = torch.tensor(py_true, dtype=dtype).to(device)
        #         pz_true = torch.tensor(pz_true, dtype=dtype).to(device)

        #         reco_mom = self.recover_smeared_momentum_from_deltas(
        #             delta_output=reco_mom,  # your model output
        #             px_true=px_true,
        #             py_true=py_true,
        #             pz_true=pz_true
        #         )

        #         true_reco_mom = self.recover_smeared_momentum_from_deltas(
        #             delta_output=true_reco_mom,  # your model output
        #             px_true=px_true,
        #             py_true=py_true,
        #             pz_true=pz_true
        #         )

        #         # Compute invariant masses
        #         masses_reco = self.compute_invariant_masses(reco_mom, batch_idxs, masses)
        #         masses_true_reco = self.compute_invariant_masses(true_reco_mom, batch_idxs, masses)

        #         max_mass = 8000.
        #         masses_reco = torch.clamp(masses_reco, max=max_mass)
        #         masses_true_reco = torch.clamp(masses_true_reco, max=max_mass)

        #         # Normalize to [-1, 1] using (x / 5000) - 2
        #         masses_reco = (masses_reco / (max_mass/2.0)) - 2.0
        #         masses_true_reco = (masses_true_reco / (max_mass/2.0)) - 2.0

        #         for i in out:
        #             masses_reco_i = masses_reco[batch[i].batch].unsqueeze(1)
        #             out[i] = torch.cat((out[i], masses_reco_i), dim=1)

        #             masses_true_reco_i = masses_true_reco[batch[i].batch].unsqueeze(1)
        #             batch[i].x = torch.cat((batch[i].x, masses_true_reco_i), dim=1)

        # # ##### add vars
        # extra_vars_out = self.append_addition_vars_for_disc(batch, out)
        # for i in out:
        #     out[i] = torch.cat((out[i], extra_vars_out[i]), dim=1)

        # out_true = {}
        # for i in out:
        #     out_true[i] = batch[i].x
        # extra_vars_out = self.append_addition_vars_for_disc(batch, out_true)
        # for i in out:
        #     batch[i].x = torch.cat((batch[i].x, extra_vars_out[i]), dim=1)
        # # ##### add vars

        disc_out_real = self.gan.discriminator(
            batch=batch,
        )

        for particle_type in particle_types:
            batch[particle_type].x = out[particle_type]

        disc_out_fake = self.gan.discriminator(
            batch=batch,
        )

        labels_fake = torch.ones(disc_out_fake.shape[0], 1).to(device) * 0.1
        labels_real = torch.ones(disc_out_real.shape[0], 1).to(device) * 0.9

        labels_D = torch.cat([labels_fake, labels_real], dim=0)
        preds_D = torch.cat([disc_out_fake, disc_out_real], dim=0)

        disc_loss_fn = nn.BCELoss()
        disc_loss = disc_loss_fn(preds_D.squeeze(), labels_D.squeeze())

        weight_balance = preds_D.squeeze().shape[0] / 2

        # if idx == 0:
        #     total_disc_loss = disc_loss
        # else:
        #     total_disc_loss += disc_loss

        return disc_loss, weight_balance

    def update_generator_eGAN(self, batch, mode_seeking_term=False):
        # for idx, batch_i in enumerate(batch):
        device = batch["mother"].x.device

        try:
            batch["intermediate"].x
            intermediate_present = True
        except Exception:
            intermediate_present = False

        genbatch = batch.clone()

        x_mother = torch.randn(
            (genbatch["mother"].x.shape[0], self.gan.mother_latent_dims), device=device
        )  # * 0.25
        x_track = torch.randn(
            (genbatch["track"].x.shape[0], self.gan.track_latent_dims), device=device
        )  # * 0.25
        if intermediate_present:
            x_intermediate = torch.randn(
                (
                    genbatch["intermediate"].x.shape[0],
                    self.gan.intermediate_latent_dims,
                ),
                device=device,
            )  # * 0.25

        batch_size = genbatch["mother"].x.shape[0]

        # Initial latent container
        latent = {
            "mother": x_mother,
            "track": x_track,
        }
        if intermediate_present:
            latent["intermediate"] = x_intermediate

        noise = torch.rand(
            (genbatch["mother_conditions"].x.shape[0], 5),
            device=genbatch["mother_conditions"].x.device,
            dtype=genbatch["mother_conditions"].x.dtype,
        )
        genbatch["mother_conditions"].x = torch.cat(
            (genbatch["mother_conditions"].x, noise), dim=-1
        )
        if intermediate_present:
            noise = torch.rand(
                (genbatch["intermediate_conditions"].x.shape[0], 3),
                device=genbatch["intermediate_conditions"].x.device,
                dtype=genbatch["intermediate_conditions"].x.dtype,
            )
            genbatch["intermediate_conditions"].x = torch.cat(
                (genbatch["intermediate_conditions"].x, noise), dim=-1
            )
        noise = torch.rand(
            (genbatch["track_conditions"].x.shape[0], 2),
            device=genbatch["track_conditions"].x.device,
            dtype=genbatch["track_conditions"].x.dtype,
        )
        genbatch["track_conditions"].x = torch.cat(
            (genbatch["track_conditions"].x, noise), dim=-1
        )

        for t in reversed(range(self.noise_scheduler.config.num_train_timesteps)):
            timesteps = torch.full((batch_size,), t, device=device, dtype=torch.long)

            genbatch["mother"].x = latent["mother"]
            genbatch["track"].x = latent["track"]
            if intermediate_present:
                genbatch["intermediate"].x = latent["intermediate"]

            # Predict noise at current timestep
            noise_pred = self.gan.diffuser(
                batch=genbatch,
                timesteps=timesteps,
            )[0]

            # Denoise each component
            for node_type in latent:
                model_output = noise_pred[node_type]

                # Ensure shape matches expected sample shape
                if model_output.ndim == 1:
                    model_output = model_output.unsqueeze(-1)  # Or reshape accordingly

                latent[node_type] = self.noise_scheduler.step(
                    model_output=model_output, timestep=t, sample=latent[node_type]
                ).prev_sample

        genbatch["mother"].x = latent["mother"]
        genbatch["track"].x = latent["track"]
        if intermediate_present:
            genbatch["intermediate"].x = latent["intermediate"]
        # genbatch here is unnoised diffusion model output

        # renoise conditions
        noise = torch.rand(
            (genbatch["mother_conditions"].x.shape[0], 5),
            device=genbatch["mother_conditions"].x.device,
            dtype=genbatch["mother_conditions"].x.dtype,
        )
        genbatch["mother_conditions"].x[:, -5:] = noise
        if intermediate_present:
            noise = torch.rand(
                (genbatch["intermediate_conditions"].x.shape[0], 3),
                device=genbatch["intermediate_conditions"].x.device,
                dtype=genbatch["intermediate_conditions"].x.dtype,
            )
            genbatch["intermediate_conditions"].x[:, -3:] = noise
        noise = torch.rand(
            (genbatch["track_conditions"].x.shape[0], 2),
            device=genbatch["track_conditions"].x.device,
            dtype=genbatch["track_conditions"].x.dtype,
        )
        genbatch["track_conditions"].x[:, -2:] = noise

        epsilon = self.gan.generator(
            batch=genbatch,
        )[0]

        for node_type in epsilon:
            if epsilon[node_type].ndim == 1:
                epsilon[node_type] = epsilon[node_type].unsqueeze(
                    -1
                )  # Or reshape accordingly

        generated_epsilon = genbatch.clone()

        # remove noise from conditions
        generated_epsilon["mother_conditions"].x = generated_epsilon[
            "mother_conditions"
        ].x[:, :-5]
        if intermediate_present:
            generated_epsilon["intermediate_conditions"].x = generated_epsilon[
                "intermediate_conditions"
            ].x[:, :-3]
        generated_epsilon["track_conditions"].x = generated_epsilon[
            "track_conditions"
        ].x[:, :-2]

        generated_epsilon["mother"].x = epsilon["mother"]
        if intermediate_present:
            generated_epsilon["intermediate"].x = epsilon["intermediate"]
        generated_epsilon["track"].x = epsilon["track"]

        disc_out_train_VAE = self.gan.discriminator(generated_epsilon)

        adv_loss = -torch.mean(torch.log(disc_out_train_VAE.squeeze() + 1e-8))

        return adv_loss

    def update_generator(self, batch, mode_seeking_term=False):
        # for idx, batch_i in enumerate(batch):
        device = batch["mother"].x.device

        try:
            batch["intermediate"].x
            intermediate_present = True
        except Exception:
            intermediate_present = False

        latent_mother_A = torch.randn(
            (batch["mother"].x.shape[0], self.gan.mother_latent_dims)
        ).to(device)
        latent_track_A = torch.randn(
            (batch["track"].x.shape[0], self.gan.track_latent_dims)
        ).to(device)
        if intermediate_present:
            latent_intermediate_A = torch.randn(
                (
                    batch["intermediate"].x.shape[0],
                    self.gan.intermediate_latent_dims,
                )
            ).to(device)
            mother, intermediate, track = self.gan.generator(  # this is the generator
                latent_mother_A,
                latent_track_A,
                latent_intermediate_A,
                batch["mother_conditions"],
                batch["track_conditions"],
                batch["intermediate_conditions"],
                batch["edge_index_tensors"],
                batch,
            )
        else:
            mother, intermediate, track = self.gan.generator(  # this is the generator
                latent_mother_A,
                latent_track_A,
                None,
                batch["mother_conditions"],
                batch["track_conditions"],
                None,
                batch["edge_index_tensors"],
                batch,
            )

        mother_in = batch["mother"].clone()
        mother_in.x = mother

        track_in = batch["track"].clone()
        track_in.x = track

        if intermediate_present:
            intermediate_in = batch["intermediate"].clone()
            intermediate_in.x = intermediate

            disc_out_train_VAE = self.gan.discriminator(
                mother_in,
                track_in,
                intermediate_in,
                batch["mother_conditions"],
                batch["track_conditions"],
                batch["intermediate_conditions"],
                batch["edge_index_tensors"],
                batch,
            )
        else:
            disc_out_train_VAE = self.gan.discriminator(
                mother_in,
                track_in,
                None,
                batch["mother_conditions"],
                batch["track_conditions"],
                None,
                batch["edge_index_tensors"],
                batch,
            )

        adv_loss = -torch.mean(torch.log(disc_out_train_VAE.squeeze() + 1e-8))

        return adv_loss

    def update_generator_smearingnet(self, batch, mode_seeking_term=False):
        # for idx, batch_i in enumerate(batch):
        device = batch["11"].x.device

        particle_types = ["11", "13", "211", "321", "2212"]
        track_latent = {}
        for particle_type in particle_types:
            track_latent[particle_type] = torch.randn(
                (
                    batch[particle_type].x.shape[0],
                    self.gan.track_latent_dims,
                )
            ).to(device)
        out = self.gan.generator(
            track_latent,
            batch=batch,
        )

        # if self.network_option == "mom_smear":

        #     with torch.no_grad():

        #         true_mom, reco_mom, batch_idxs, masses = [], [], [], []
        #         dtype = batch["11"].x.dtype
        #         device = batch["11"].x.device

        #         PDG_MASSES = {
        #             "11": 0.000511 * 1e3,   # e-
        #             "13": 0.10566 * 1e3,    # mu-
        #             "211": 0.13957 * 1e3,   # pi+
        #             "321": 0.49367 * 1e3,   # K+
        #             "2212": 0.93827 * 1e3   # p+
        #         }

        #         for idx, p in enumerate(["11", "13", "211", "321", "2212"]):

        #             if p in out:

        #                 # Get true mom
        #                 true = batch[f"{p}_conditions"].x[:, :3]

        #                 pred_reco = out[p].detach().cpu().numpy()

        #                 for i in range(3):
        #                     tf = self.Transformers[
        #                         f"{myGlobals.smearing_track_targets[i].replace('DAUGHTERN', 'DAUGHTER1')}_{p}"
        #                     ]
        #                     pred_reco[:, i] = tf.unprocess(pred_reco[:, i])
        #                 pred_reco = torch.tensor(pred_reco, dtype=dtype)

        #                 batch_p = batch[p].batch

        #                 # Assign correct mass
        #                 mass_val = PDG_MASSES[p]
        #                 masses.append(torch.full((pred_reco.shape[0],), mass_val, dtype=dtype, device=device))

        #                 true_mom.append(true)
        #                 reco_mom.append(pred_reco)
        #                 batch_idxs.append(batch_p)

        #         # Stack across all particles
        #         true_mom = torch.cat(true_mom, dim=0).to(device)
        #         reco_mom = torch.cat(reco_mom, dim=0).to(device)
        #         batch_idxs = torch.cat(batch_idxs, dim=0).to(device)
        #         masses = torch.cat(masses, dim=0).to(device)

        #         # Unprocess true values as well
        #         px_true = self.Transformers[myGlobals.smearing_track_conditions[0].replace("DAUGHTERN", "DAUGHTER1")].unprocess(true_mom[:, 0].cpu().numpy())
        #         py_true = self.Transformers[myGlobals.smearing_track_conditions[1].replace("DAUGHTERN", "DAUGHTER1")].unprocess(true_mom[:, 1].cpu().numpy())
        #         pz_true = self.Transformers[myGlobals.smearing_track_conditions[2].replace("DAUGHTERN", "DAUGHTER1")].unprocess(true_mom[:, 2].cpu().numpy())

        #         px_true = torch.tensor(px_true, dtype=dtype).to(device)
        #         py_true = torch.tensor(py_true, dtype=dtype).to(device)
        #         pz_true = torch.tensor(pz_true, dtype=dtype).to(device)

        #         reco_mom = self.recover_smeared_momentum_from_deltas(
        #             delta_output=reco_mom,  # your model output
        #             px_true=px_true,
        #             py_true=py_true,
        #             pz_true=pz_true
        #         )

        #         # Compute invariant masses
        #         masses_reco = self.compute_invariant_masses(reco_mom, batch_idxs, masses)

        #         max_mass = 8000.
        #         masses_reco = torch.clamp(masses_reco, max=max_mass)

        #         # Normalize to [-1, 1] using (x / 5000) - 2
        #         masses_reco = (masses_reco / (max_mass/2.0)) - 2.0

        #         for i in out:
        #             masses_reco_i = masses_reco[batch[i].batch].unsqueeze(1)
        #             out[i] = torch.cat((out[i], masses_reco_i), dim=1)

        # # # ##### add vars
        # extra_vars_out = self.append_addition_vars_for_disc(batch, out)
        # for i in out:
        #     out[i] = torch.cat((out[i], extra_vars_out[i]), dim=1)
        # # # ##### add vars
        # # for i in out:
        # #     print(i, extra_vars_out[i][:5])

        for particle_type in particle_types:
            batch[particle_type].x = out[particle_type]

        disc_out_train_VAE = self.gan.discriminator(
            batch=batch,
        )

        targets = torch.ones(disc_out_train_VAE.shape[0], 1).squeeze().to(device)

        adv_loss_fn = nn.BCELoss()
        adv_loss = adv_loss_fn(disc_out_train_VAE.squeeze(), targets.squeeze())

        # i think this is bullshit when i have multiple samples... then need to cat disc out and compute cross entropy term all at once?
        # if idx == 0:
        #     total_adv_loss = adv_loss
        # else:
        #     total_adv_loss += adv_loss

        return adv_loss

    def heteroscedastic_loss(self, pred_mu, pred_logvar, target):
        # log σ and μ are predicted
        # loss = 0.5 * torch.exp(-pred_logvar) * (pred_mu - target)**2 + 0.5 * pred_logvar
        # return loss.mean()

        loss = (
            (target - pred_mu) ** 2 / torch.exp(2 * pred_logvar) + 2 * pred_logvar
        ).mean()
        # Optionally add:
        loss += 0.01 * (pred_logvar**2).mean()
        return loss

    def recover_smeared_momentum_from_deltas(
        self,
        delta_output: torch.Tensor,  # shape [N, 3]
        px_true: torch.Tensor,
        py_true: torch.Tensor,
        pz_true: torch.Tensor,
        eps: float = 1e-6,
    ) -> torch.Tensor:
        delta_px = delta_output[:, 0]
        delta_py = delta_output[:, 1]
        delta_pz = delta_output[:, 2]

        # PX and PY are additive
        px = px_true + delta_px
        py = py_true + delta_py
        pz = pz_true + delta_pz

        # # Total true P
        # p_true = torch.sqrt(px_true**2 + py_true**2 + pz_true**2 + eps)

        # # A^2 * P_true^2 - px^2 - py^2
        # pz_squared = preco_over_p**2 * p_true**2 - px**2 - py**2
        # pz_squared = torch.clamp(pz_squared, min=0.0)  # prevent sqrt of negative due to numerical error

        # pz = torch.sqrt(pz_squared + eps)

        reco = torch.stack([px, py, pz], dim=1)  # shape [N, 3]
        return reco

    def compute_invariant_masses(
        self, momentum: torch.Tensor, batch: torch.Tensor, masses: torch.Tensor
    ) -> torch.Tensor:
        px, py, pz = momentum[:, 0], momentum[:, 1], momentum[:, 2]
        E = torch.sqrt(px**2 + py**2 + pz**2 + masses**2)

        # Sum px, py, pz, E for each event
        px_sum = torch.zeros(batch.max() + 1, device=momentum.device).index_add(
            0, batch, px
        )
        py_sum = torch.zeros_like(px_sum).index_add(0, batch, py)
        pz_sum = torch.zeros_like(px_sum).index_add(0, batch, pz)
        E_sum = torch.zeros_like(px_sum).index_add(0, batch, E)

        # Invariant mass = sqrt(E^2 - |p|^2)
        mass_squared = E_sum**2 - (px_sum**2 + py_sum**2 + pz_sum**2)
        mass_squared = torch.clamp(mass_squared, min=0.0)

        return torch.sqrt(mass_squared)

    def myloss(self, pred_mu, target, weights):
        # log σ and μ are predicted
        loss = (pred_mu - target) ** 2
        loss = torch.multiply(loss, weights)
        return loss.mean()

    def training_step(self, batch, batch_idx):
        if self.network_option == "reco_vertex_diffusion":
            
            use_encoder = False
            # use_encoder = True

            optimizer = self.optimizers()
            self.gan.diffuser.train()
            if use_encoder:
                self.gan.encoder.train()

            total_loss = 0.0
            total_kl_loss = 0.0
            total_loss_ms = 0.0
            total_nodes = 0  # Optional: for weighted averaging if batch sizes differ

            for name, data in batch.items():  # e.g., name = 'event1', data = HeteroData
                intermediate_present = False
                try:
                    get_int = data["intermediate"].x
                    intermediate_present = True
                except:
                    pass

                batch_size = data["mother"].x.size(0)
                device = data["mother"].x.device

                # Get all node features
                x_mother = data["mother"].x
                if intermediate_present:
                    x_intermediate = data["intermediate"].x
                x_track = data["track"].x

                if use_encoder:
                    if "conditionless" in name:
                        encoded_target = self.gan.encoder(
                            data, add_condition_nodes=False
                        )[0]
                    else:
                        encoded_target = self.gan.encoder(
                            data, add_condition_nodes=True
                        )[0]

                # Get indices to segment x_track into per-sample chunks
                num_tracks_per_sample = x_track.size(0) // batch_size
                assert x_track.size(0) % batch_size == 0, (
                    "Track node count must be divisible by batch size"
                )

                # Sample a random timestep per sample
                timesteps = torch.randint(
                    low=0,
                    high=self.noise_scheduler.config.num_train_timesteps,
                    size=(batch_size,),
                    device=device,
                )

                # Initialize noisy versions
                noisy_mother = torch.zeros_like(x_mother)
                if intermediate_present:
                    noisy_intermediate = torch.zeros_like(x_intermediate)
                noisy_track = torch.zeros_like(x_track)

                noise_mother = torch.randn_like(x_mother)  # * 0.25
                if intermediate_present:
                    noise_intermediate = torch.randn_like(x_intermediate)  # * 0.25
                noise_track = torch.randn_like(x_track)  # * 0.25

                for i in range(batch_size):
                    t = timesteps[i]

                    # Add noise to each component for this sample
                    noisy_mother[i] = self.noise_scheduler.add_noise(
                        x_mother[i], noise_mother[i], t
                    )
                    if intermediate_present:
                        noisy_intermediate[i] = self.noise_scheduler.add_noise(
                            x_intermediate[i], noise_intermediate[i], t
                        )

                    track_start = i * num_tracks_per_sample
                    track_end = (i + 1) * num_tracks_per_sample

                    noisy_track[track_start:track_end] = self.noise_scheduler.add_noise(
                        x_track[track_start:track_end],
                        noise_track[track_start:track_end],
                        t,
                    )

                # Replace original node features with noised versions
                data["mother"].x = noisy_mother
                if intermediate_present:
                    data["intermediate"].x = noisy_intermediate
                data["track"].x = noisy_track

                noise = torch.rand(
                    (data["mother_conditions"].x.shape[0], self.gan.diffuser.L_mother),
                    device=data["mother_conditions"].x.device,
                    dtype=data["mother_conditions"].x.dtype,
                )
                if use_encoder:
                    extra_noise_mother = (
                        encoded_target["mother"][:, :, 0]
                        + torch.randn_like(encoded_target["mother"][:, :, 1])
                        * encoded_target["mother"][:, :, 1]
                    )
                    if extra_noise_mother.ndim == 1:
                        extra_noise_mother = extra_noise_mother.unsqueeze(-1)
                    noise[:, : extra_noise_mother.shape[1]] = extra_noise_mother
                data["mother_conditions"].x = torch.cat(
                    (data["mother_conditions"].x, noise), dim=-1
                )
                if intermediate_present:
                    noise = torch.rand(
                        (
                            data["intermediate_conditions"].x.shape[0],
                            self.gan.diffuser.L_intermediate,
                        ),
                        device=data["intermediate_conditions"].x.device,
                        dtype=data["intermediate_conditions"].x.dtype,
                    )
                    if use_encoder:
                        extra_noise_intermediate = (
                            encoded_target["intermediate"][:, :, 0]
                            + torch.randn_like(encoded_target["intermediate"][:, :, 1])
                            * encoded_target["intermediate"][:, :, 1]
                        )
                        if extra_noise_intermediate.ndim == 1:
                            extra_noise_intermediate = (
                                extra_noise_intermediate.unsqueeze(-1)
                            )
                        noise[:, : extra_noise_intermediate.shape[1]] = (
                            extra_noise_intermediate
                        )
                    data["intermediate_conditions"].x = torch.cat(
                        (data["intermediate_conditions"].x, noise), dim=-1
                    )
                noise = torch.rand(
                    (data["track_conditions"].x.shape[0], self.gan.diffuser.L_track),
                    device=data["track_conditions"].x.device,
                    dtype=data["track_conditions"].x.dtype,
                )
                if use_encoder:
                    extra_noise_track = (
                        encoded_target["track"][:, :, 0]
                        + torch.randn_like(encoded_target["track"][:, :, 1])
                        * encoded_target["track"][:, :, 1]
                    )
                    if extra_noise_track.ndim == 1:
                        extra_noise_track = extra_noise_track.unsqueeze(-1)
                    noise[:, : extra_noise_track.shape[1]] = extra_noise_track
                data["track_conditions"].x = torch.cat(
                    (data["track_conditions"].x, noise), dim=-1
                )

                # extra_noise_mother = encoded_target["mother"][:,:,0] + torch.randn_like(encoded_target["mother"][:,:,1])*encoded_target["mother"][:,:,1]
                # data["mother_conditions"].x = torch.cat((data["mother_conditions"].x, extra_noise_mother), dim=-1)
                # if intermediate_present:
                #     extra_noise_intermediate = encoded_target["intermediate"][:,:,0] + torch.randn_like(encoded_target["intermediate"][:,:,1])*encoded_target["intermediate"][:,:,1]
                #     # extra_noise_intermediate = torch.rand((data["intermediate_conditions"].x.shape[0], 3), device=data["intermediate_conditions"].x.device, dtype=data["intermediate_conditions"].x.dtype)
                #     data["intermediate_conditions"].x = torch.cat((data["intermediate_conditions"].x, extra_noise_intermediate), dim=-1)
                # extra_noise_track = encoded_target["track"][:,:,0] + torch.randn_like(encoded_target["track"][:,:,1])*encoded_target["track"][:,:,1]
                # # extra_noise_track = torch.rand_like(extra_noise_track) # WARNING THROWING AWAY ENCODED TRACK
                # if extra_noise_track.ndim == 1:
                #     extra_noise_track = extra_noise_track.unsqueeze(-1)
                # # extra_noise_track = torch.rand((data["track_conditions"].x.shape[0], 2), device=data["track_conditions"].x.device, dtype=data["track_conditions"].x.dtype)
                # data["track_conditions"].x = torch.cat((data["track_conditions"].x, extra_noise_track), dim=-1)

                # noise_pred = self.gan.diffuser(data, timesteps)[0]
                if "conditionless" in name:
                    noise_pred = self.gan.diffuser(
                        data, timesteps, add_condition_nodes=False
                    )[0]
                else:
                    noise_pred = self.gan.diffuser(
                        data, timesteps, add_condition_nodes=True
                    )[0]

                enhance_EVCHI2 = 2.  # v7
                enhance_IPCHI2 = 1.25  # v7
                # enhance_EVCHI2 = 3.# v8
                # enhance_EVCHI2 = 4.# v9
                # enhance_EVCHI2 = 5.# v10

                if intermediate_present:
                    noise_target = torch.cat(
                        [
                            noise_mother.flatten(),
                            noise_intermediate.flatten(),
                            noise_track.flatten(),
                        ]
                    )
                    noise_pred_flat = torch.cat(
                        [
                            noise_pred["mother"].flatten(),
                            noise_pred["intermediate"].flatten(),
                            noise_pred["track"].flatten(),
                        ]
                    )
                    if use_encoder:
                        mu_flat = torch.cat(
                            [
                                encoded_target["mother"][:, :, 0].flatten(),
                                encoded_target["intermediate"][:, :, 0].flatten(),
                                encoded_target["track"][:, :, 0].flatten(),
                            ]
                        )
                        logvar_mother = 2 * torch.log(
                            torch.clamp(encoded_target["mother"][:, :, 1], min=1e-4)
                            + 1e-8
                        )
                        logvar_intermediate = 2 * torch.log(
                            torch.clamp(
                                encoded_target["intermediate"][:, :, 1], min=1e-4
                            )
                            + 1e-8
                        )
                        logvar_track = 2 * torch.log(
                            torch.clamp(encoded_target["track"][:, :, 1], min=1e-4)
                            + 1e-8
                        )
                        logvar_flat = torch.cat(
                            [
                                logvar_mother.flatten(),
                                logvar_intermediate.flatten(),
                                logvar_track.flatten(),
                            ]
                        )

                    x_mother_like = torch.ones_like(x_mother)
                    x_mother_like[:, 3] = enhance_EVCHI2
                    x_mother_like[:, 4] = enhance_IPCHI2
                    x_mother_like = x_mother_like.flatten()

                    x_intermediate_like = torch.ones_like(x_intermediate)
                    x_intermediate_like[:, 0] = enhance_EVCHI2
                    x_intermediate_like[:, 1] = enhance_IPCHI2
                    x_intermediate_like = x_intermediate_like.flatten()

                    x_track_like = torch.ones_like(x_track).flatten()
                    weights_flat = torch.cat(
                        [x_mother_like, x_intermediate_like, x_track_like]
                    )
                else:
                    noise_target = torch.cat(
                        [noise_mother.flatten(), noise_track.flatten()]
                    )
                    noise_pred_flat = torch.cat(
                        [noise_pred["mother"].flatten(), noise_pred["track"].flatten()]
                    )
                    if use_encoder:
                        logvar_mother = 2 * torch.log(
                            torch.clamp(encoded_target["mother"][:, :, 1], min=1e-4)
                            + 1e-8
                        )
                        logvar_track = 2 * torch.log(
                            torch.clamp(encoded_target["track"][:, :, 1], min=1e-4)
                            + 1e-8
                        )
                        mu_flat = torch.cat(
                            [
                                encoded_target["mother"][:, :, 0].flatten(),
                                encoded_target["track"][:, :, 0].flatten(),
                            ]
                        )
                        logvar_flat = torch.cat(
                            [logvar_mother.flatten(), logvar_track.flatten()]
                        )

                    x_mother_like = torch.ones_like(x_mother)
                    x_mother_like[:, 3] = enhance_EVCHI2
                    x_mother_like[:, 4] = enhance_IPCHI2
                    x_mother_like = x_mother_like.flatten()
                    x_track_like = torch.ones_like(x_track).flatten()
                    weights_flat = torch.cat([x_mother_like, x_track_like])

                # loss = F.l1_loss(noise_pred_flat, noise_target, reduction='sum')  # Use 'sum' to combine across all events
                loss = F.l1_loss(
                    noise_pred_flat, noise_target, reduction="none"
                )  # Use 'sum' to combine across all events
                loss *= weights_flat
                loss = loss.sum()

                if use_encoder:
                    kl_loss = -0.5 * torch.sum(
                        1 + logvar_flat - mu_flat.pow(2) - torch.exp(logvar_flat),
                        dim=-1,
                    )

                    total_kl_loss += kl_loss

                total_loss += loss
                total_nodes += noise_target.numel()  # total number of values

            mean_loss = total_loss / total_nodes
            self.log("reco_loss", mean_loss, prog_bar=True)
            if use_encoder:
                mean_kl_loss = total_kl_loss / total_nodes
                self.log("kl_loss", mean_kl_loss, prog_bar=True)

            # beta = 0. # v20
            # beta = 1. # v21
            # beta = 10. # v22
            # beta = 25. # v23 broke
            # beta = 0.1 # v24
            #### above was before KL loss fix

            # beta = 0.1 # v29 # blury - latent space gaussian, but not using strucutre enough
            # sweet spot?
            # beta = 0.01 # 30 # should be too sharp - not too bad by eye, but latent space structure clearly non gaussian
            # beta = 0.001 # 31
            # beta = 0.0001 # 32 # very sharp

            # beta = 0.01 # v30
            # beta = 0.02 # v37 # non gaussian
            # beta = 0.04 # v38 # kinda non gaussian
            # beta = 0.06 # v35 # still kinda non gaussian
            # sweet spot? maybe not, EV/IP still not being impressed properly here
            # beta = 0.08 # v36 # gaussian
            # beta = 0.1 # v29

            # beta = 0.04 # v41
            # beta = 0.06 # v42
            # beta = 0.08 # v43

            # beta = 0.085 # v45
            # beta = 0.09 # v46
            # beta = 0.095 # v47

            # beta = 0.1 # v44

            # # _IPDIRA
            # # beta = 0.03 # v11
            # # beta = 0.05 # v12
            # # beta = 0.067 # v13
            # beta = 0.084 # v14

            # _IPDIRA
            # beta = 0.084 # v15
            # beta = 0.1 # v16
            # beta = 0.125 # v17
            # beta = 0.15 # v18

            # beta = 0.2 # v21
            # beta = 0.25 # v22
            # beta = 0.3 # v23
            # beta = 0.35 # v24

            beta = 0.1 # v25
            # beta = 0.15 # v26
            # beta = 0.2 # v27
            # beta = 0.25  # v28

            if use_encoder:
                backwards_loss = mean_loss + beta * mean_kl_loss
            else:
                backwards_loss = mean_loss

            optimizer.zero_grad()
            backwards_loss.backward()
            max_grad_norm = 3.0
            clip_grad_norm_(self.gan.diffuser.parameters(), max_grad_norm)
            optimizer.step()
            
            self.gan.EMA_diffuser.ema_model.to(device)
            self.gan.EMA_diffuser.update(self.gan.diffuser)

            sch = self.lr_schedulers()
            if sch:
                sch.step()

            self.gan.diffuser.eval()
            if use_encoder:
                self.gan.encoder.eval()

        elif "VAE" in self.network_option:
            optimizer = self.optimizers()
            self.gan.decoder.train()
            self.gan.encoder.train()

            particle_types = ["11", "13", "211", "321", "2212"]

            total_reco_loss = 0.0
            total_kl_loss = 0.0
            total_nodes = 0  # Optional: for weighted averaging if batch sizes differ

            for name, data in batch.items():
                try:
                    data_clone = data.clone()
                except:
                    data_clone = data

                device = data[
                    "11"
                ].x.device  # Use any node feature tensor to get device
                batch_size = data["11"].ptr.numel() - 1

                out, mu, logvar = self.gan.stacked(data)

                # Store targets/predictions for loss later
                target_flat = []
                pred_flat = []

                mu_flat = []
                logvar_flat = []

                for node_type in particle_types:
                    target_flat.append(data[node_type].x)
                    pred_flat.append(out[node_type])

                    mu_flat.append(mu[node_type])
                    logvar_flat.append(logvar[node_type])

                target_tensor = torch.cat(target_flat)
                pred_tensor = torch.cat(pred_flat)

                mu_tensor = torch.cat(mu_flat)
                logvar_tensor = torch.cat(logvar_flat)

                reco_loss = F.l1_loss(pred_tensor, target_tensor, reduce="sum")
                kl_loss = -0.5 * torch.sum(
                    1 + logvar_tensor - mu_tensor.pow(2) - torch.exp(logvar_tensor),
                    dim=-1,
                )
                kl_loss = kl_loss.sum()

                total_reco_loss += reco_loss
                total_kl_loss += kl_loss

                total_nodes += target_tensor.numel()

            # Backprop, optimizer
            mean_reco_loss = total_reco_loss / total_nodes
            mean_kl_loss = total_kl_loss / total_nodes

            # beta = 1.
            beta = 0.001

            mean_loss = mean_reco_loss + beta * mean_kl_loss

            self.log("reco_loss", mean_reco_loss, prog_bar=True)
            self.log("beta * mean_kl_loss", beta * mean_kl_loss, prog_bar=True)
            self.log("loss", mean_loss, prog_bar=True)

            optimizer.zero_grad()
            mean_loss.backward()
            # combined_loss.backward()
            # clip_grad_norm_(self.gan.diffuser.parameters(), 3.0)
            optimizer.step()
            # self.gan.EMA_diffuser.update(self.gan.diffuser)

            sch = self.lr_schedulers()
            if sch:
                sch.step()

        elif self.network_option == "reco_vertex_flowmatching":
            optimizer = self.optimizers()
            self.gan.diffuser.train()

            total_loss = 0.0
            total_loss_ms = 0.0
            total_nodes = 0  # Optional: for weighted averaging if batch sizes differ

            for name, data in batch.items():  # e.g., name = 'event1', data = HeteroData
                intermediate_present = False
                try:
                    get_int = data["intermediate"].x
                    intermediate_present = True
                except:
                    pass

                batch_size = data["mother"].x.size(0)
                device = data["mother"].x.device

                # # Get all node features
                # x_mother = data["mother"].x
                # if intermediate_present:
                #     x_intermediate = data["intermediate"].x
                # x_track = data["track"].x

                # # Get indices to segment x_track into per-sample chunks
                # num_tracks_per_sample = x_track.size(0) // batch_size
                # assert x_track.size(0) % batch_size == 0, "Track node count must be divisible by batch size"

                # Sample a random timestep per sample
                t = torch.rand((batch_size, 1), device=device)

                # noise_mother = torch.randn_like(x_mother) * 0.25
                # if intermediate_present:
                #     noise_intermediate = torch.randn_like(x_intermediate) * 0.25
                # noise_track = torch.randn_like(x_track) * 0.25

                for node_type in ["mother", "intermediate", "track"]:
                    if node_type == "intermediate" and not intermediate_present:
                        continue

                    x1 = data[node_type].x.to(torch.float32)
                    b = data[node_type].batch
                    tbatch = t[b]
                    x0 = torch.randn_like(
                        x1, dtype=torch.float32, device=device
                    )  # * 0.25

                    x_t = (1 - tbatch) * x0 + tbatch * x1
                    data[node_type].x = x_t

                    data[node_type].v_target = x1 - x0

                # if self.gan.diffuser.add_extra_noise:
                #     for node_type in data.node_types:
                #         if node_type.endswith("_conditions"):
                #             cond_x = data[node_type].x.to(torch.float32)
                #             extra_noise = torch.rand((cond_x.size(0), 25), device=device, dtype=cond_x.dtype)
                #             data[node_type].x = torch.cat([cond_x, extra_noise], dim=-1)

                extra_noise_mother = torch.rand(
                    (data["mother_conditions"].x.shape[0], 5),
                    device=data["mother_conditions"].x.device,
                    dtype=data["mother_conditions"].x.dtype,
                )
                data["mother_conditions"].x = torch.cat(
                    (data["mother_conditions"].x, extra_noise_mother), dim=-1
                )
                if intermediate_present:
                    extra_noise_intermediate = torch.rand(
                        (data["intermediate_conditions"].x.shape[0], 3),
                        device=data["intermediate_conditions"].x.device,
                        dtype=data["intermediate_conditions"].x.dtype,
                    )
                    data["intermediate_conditions"].x = torch.cat(
                        (data["intermediate_conditions"].x, extra_noise_intermediate),
                        dim=-1,
                    )
                extra_noise_track = torch.rand(
                    (data["track_conditions"].x.shape[0], 2),
                    device=data["track_conditions"].x.device,
                    dtype=data["track_conditions"].x.dtype,
                )
                data["track_conditions"].x = torch.cat(
                    (data["track_conditions"].x, extra_noise_track), dim=-1
                )

                # Predict velocity using flow model
                v_pred_dict = self.gan.diffuser(
                    data, t.squeeze(), add_condition_nodes=("conditionless" not in name)
                )[0]  # NOTE: t can be passed if needed for time conditioning

                if intermediate_present:
                    v_target = torch.cat(
                        [
                            data["mother"].v_target.flatten(),
                            data["intermediate"].v_target.flatten(),
                            data["track"].v_target.flatten(),
                        ]
                    )
                    v_pred_flat = torch.cat(
                        [
                            v_pred_dict["mother"].flatten(),
                            v_pred_dict["intermediate"].flatten(),
                            v_pred_dict["track"].flatten(),
                        ]
                    )
                else:
                    v_target = torch.cat(
                        [
                            data["mother"].v_target.flatten(),
                            data["track"].v_target.flatten(),
                        ]
                    )
                    v_pred_flat = torch.cat(
                        [
                            v_pred_dict["mother"].flatten(),
                            v_pred_dict["track"].flatten(),
                        ]
                    )

                total_loss = F.l1_loss(v_pred_flat, v_target, reduction="sum")
                total_nodes += v_target.numel()

            mean_loss = total_loss / total_nodes
            self.log("loss", mean_loss, prog_bar=True)

            optimizer.zero_grad()
            mean_loss.backward()
            max_grad_norm = 3.0
            clip_grad_norm_(self.gan.diffuser.parameters(), max_grad_norm)
            optimizer.step()
            self.gan.EMA_diffuser.update(self.gan.diffuser)

            sch = self.lr_schedulers()
            if sch:
                sch.step()

        elif self.network_option in ["mom_smear_diffusion", "PID_trig_diffusion"]:
            optimizer = self.optimizers()
            self.gan.diffuser.train()

            particle_types = ["11", "13", "211", "321", "2212"]

            total_loss = 0.0
            total_nodes = 0  # Optional: for weighted averaging if batch sizes differ

            masses_reco_total = torch.empty(0, device=self.device)
            masses_true_reco_total = torch.empty(0, device=self.device)

            for name, data in batch.items():  # e.g., name = 'event1', data = HeteroData
                # if self.network_option == "mom_smear_diffusion":
                #     for node_type in particle_types:
                #         data[node_type].x *= 0.2
                try:
                    data_clone = data.clone()
                except:
                    data_clone = data

                device = data[
                    "11"
                ].x.device  # Use any node feature tensor to get device
                batch_size = data["11"].ptr.numel() - 1

                # batch_size = 0
                # for particle_type in particle_types:
                #     if torch.amax(data[particle_type].batch) > batch_size:
                #         batch_size = int(torch.amax(data[particle_type].batch))
                # batch_size += 1

                timesteps = torch.randint(
                    low=0,
                    high=self.noise_scheduler.config.num_train_timesteps,
                    size=(batch_size,),
                    device=device,
                )

                # Store targets/predictions for loss later
                noise_target_flat = []
                noise_pred_flat = []

                loss_factors = torch.empty(0).to(self.device)

                # Add timestep embeddings (per-node) based on batch index
                # timestep_embedding = self.noise_scheduler._get_timestep_embedding(timesteps, embedding_dim=5)  # or whatever dim
                for node_type in particle_types:
                    x = data[node_type].x.to(torch.float32)
                    b = data[node_type].batch  # [N_nodes]

                    # Add noise
                    noise = torch.randn_like(x, dtype=x.dtype)
                    noisy_x = self.noise_scheduler.add_noise(x, noise, timesteps[b])
                    data[node_type].x = noisy_x

                    # Store the target noise for loss
                    noise_target_flat.append(noise.flatten())

                # Optionally append extra noise to *_conditions nodes (your custom condition embedding trick)
                for node_type in data.node_types:
                    if node_type.endswith("_conditions"):
                        cond_x = data[node_type].x.to(torch.float32)
                        extra_noise = torch.rand(
                            (cond_x.size(0), 3), device=device, dtype=cond_x.dtype
                        )
                        data[node_type].x = torch.cat([cond_x, extra_noise], dim=-1)

                # Run model
                noise_pred = self.gan.diffuser(
                    data, timesteps, add_condition_nodes=("conditionless" not in name)
                )[0]

                for node_type in noise_pred:
                    noise_pred_flat.append(noise_pred[node_type].flatten())
                    # if node_type == "11":
                    #     loss_factors = torch.cat((loss_factors, 5.*torch.ones((noise_pred[node_type].flatten().shape[0])).to(self.device)))
                    # else:
                    loss_factors = torch.cat(
                        (
                            loss_factors,
                            torch.ones((noise_pred[node_type].flatten().shape[0])).to(
                                self.device
                            ),
                        )
                    )

                # Compute loss
                noise_target_tensor = torch.cat(noise_target_flat)
                noise_pred_tensor = torch.cat(noise_pred_flat)
                loss = F.l1_loss(noise_pred_tensor, noise_target_tensor, reduce=False)
                loss = torch.sum(loss * loss_factors)

                total_loss += loss
                total_nodes += noise_target_tensor.numel()

            # Backprop, optimizer
            mean_loss = total_loss / total_nodes
            self.log("loss", mean_loss, prog_bar=True)

            # mmd_weight = 50.0
            # mmd = self.compute_mmd(masses_reco_total, masses_true_reco_total)
            # self.log("mmd_loss", mmd_weight*mmd, prog_bar=False)
            # combined_loss = mean_loss + mmd_weight * mmd

            # mmd_loss = 5.*mmd_loss

            # self.log("mmd_loss", mmd_loss, prog_bar=True)
            # combined_loss = mean_loss + mmd_loss

            optimizer.zero_grad()
            mean_loss.backward()
            # combined_loss.backward()
            # clip_grad_norm_(self.gan.diffuser.parameters(), 3.0)
            optimizer.step()
            self.gan.EMA_diffuser.update(self.gan.diffuser)

            sch = self.lr_schedulers()
            if sch:
                sch.step()

        elif (
            "flowmatching" in self.network_option
            and "reco_vertex" not in self.network_option
        ):
            optimizer = self.optimizers()
            self.gan.diffuser.train()

            particle_types = ["11", "13", "211", "321", "2212"]

            total_loss = 0.0
            total_nodes = 0

            masses_reco_total = torch.empty(0, device=self.device)
            masses_true_reco_total = torch.empty(0, device=self.device)

            for name, data in batch.items():  # e.g., name = 'event1', data = HeteroData
                try:
                    data_clone = data.clone()
                except:
                    data_clone = data

                device = data["11"].x.device
                batch_size = data["11"].ptr.numel() - 1

                valid_particle_types = [
                    ptype for ptype in particle_types if data[ptype].x.size(0) > 0
                ]

                # Sample t ~ Uniform[0, 1]
                t = torch.rand((batch_size, 1), device=device)

                # For flow matching: collect true data x1
                for node_type in particle_types:
                    if node_type in valid_particle_types:
                        # print(data[node_type].x.shape)
                        x1 = data[node_type].x.to(torch.float32)
                        b = data[node_type].batch

                        tbatch = t[b]

                        # Sample x0 from a base distribution (e.g., standard Gaussian)
                        x0 = torch.randn_like(x1, dtype=torch.float32, device=device)
                        x0[:, -2:] = x0[:, -2:] * 0.25

                        # if node_type == "11":

                        #     ##### ##### ##### ##### #####

                        #     sort_idx = torch.argsort(x1[:, 2])
                        #     x0_reordered = x0[sort_idx]
                        #     x0_new = x0.clone()
                        #     x0_new[:, 2] = x0[:, 2][sort_idx]
                        #     x0 = x0_new

                        #     ##### ##### ##### ##### #####
                        #     import ot

                        #     # Assume: x0, x1 both [N, D]
                        #     x0_np = x0.cpu().numpy()
                        #     x1_np = x1.cpu().numpy()

                        #     M = ot.dist(x0_np, x1_np)  # [N, N] cost matrix
                        #     a = b = np.ones((x0_np.shape[0],)) / x0_np.shape[0]

                        #     # faster for large grahps/batches
                        #     T = ot.sinkhorn(a, b, M, reg=0.1)
                        #     T_torch = torch.tensor(T, dtype=x1.dtype, device=x1.device)
                        #     x0_matched = (T_torch @ x0)  # soft match

                        #     x0 = x0_matched
                        #     ##### ##### ##### ##### #####

                        # Interpolate to x_t = (1 - t)x0 + tx1
                        x_t = (1 - tbatch) * x0 + tbatch * x1

                        # Replace x with x_t for forward pass
                        data[node_type].x = x_t

                        # Store target velocity for this node_type
                        data[node_type].v_target = x1 - x0
                    else:
                        data[node_type].v_target = data[node_type].x

                if self.gan.diffuser.add_extra_noise:
                    for node_type in data.node_types:
                        if node_type.endswith("_conditions"):
                            cond_x = data[node_type].x.to(torch.float32)
                            extra_noise = torch.rand(
                                (cond_x.size(0), 25), device=device, dtype=cond_x.dtype
                            )
                            data[node_type].x = torch.cat([cond_x, extra_noise], dim=-1)

                # Predict velocity using flow model
                v_pred_dict = self.gan.diffuser(
                    data, t.squeeze(), add_condition_nodes=("conditionless" not in name)
                )[0]  # NOTE: t can be passed if needed for time conditioning

                # Compute L2 loss between predicted and target velocity
                loss = 0.0
                # skloss = 0.0
                total_nodes_in_batch = 0
                # total_nodes_in_batch_sk = 0

                # sinkhorn = SamplesLoss("sinkhorn", p=2, blur=0.01)

                use_reco_mass_loss = False
                if "mom_smear" in self.network_option and use_reco_mass_loss:
                    # remove noise, it gets added later
                    for node_type in data.node_types:
                        if node_type.endswith("_conditions"):
                            data[node_type].x = data[node_type].x[:, :-25]

                    with torch.no_grad():
                        sampled = self.gan.inference(
                            batch_size, data, None, flowmatching=True
                        )

                        true_mom, reco_mom, true_reco_mom, batch, masses = (
                            [],
                            [],
                            [],
                            [],
                            [],
                        )
                        dtype = data["11"].x.dtype
                        device = data["11"].x.device

                        PDG_MASSES = {
                            "11": 0.000511 * 1e3,  # e-
                            "13": 0.10566 * 1e3,  # mu-
                            "211": 0.13957 * 1e3,  # pi+
                            "321": 0.49367 * 1e3,  # K+
                            "2212": 0.93827 * 1e3,  # p+
                        }

                        for idx, p in enumerate(["11", "13", "211", "321", "2212"]):
                            if p in sampled:
                                # Get true mom
                                true = data[f"{p}_conditions"].x[:, :25]

                                pred_reco = sampled[p].detach().cpu().numpy()
                                true_reco = data_clone[p].x.detach().cpu().numpy()

                                for i in range(3):
                                    if myGlobals.personalised_track_node_types:
                                        tf = self.Transformers[
                                            f"{myGlobals.smearing_track_targets[i].replace('DAUGHTERN', 'DAUGHTER1')}_{p}"
                                        ]
                                    else:
                                        tf = self.Transformers[
                                            f"{myGlobals.smearing_track_targets[i].replace('DAUGHTERN', 'DAUGHTER1')}"
                                        ]
                                    pred_reco[:, i] = tf.unprocess(pred_reco[:, i])
                                    true_reco[:, i] = tf.unprocess(true_reco[:, i])
                                pred_reco = torch.tensor(pred_reco, dtype=dtype)
                                true_reco = torch.tensor(true_reco, dtype=dtype)

                                batch_p = data[p].batch

                                # Assign correct mass
                                mass_val = PDG_MASSES[p]
                                masses.append(
                                    torch.full(
                                        (pred_reco.shape[0],),
                                        mass_val,
                                        dtype=dtype,
                                        device=device,
                                    )
                                )

                                true_mom.append(true)
                                reco_mom.append(pred_reco)
                                true_reco_mom.append(true_reco)
                                batch.append(batch_p)

                        # Stack across all particles
                        true_mom = torch.cat(true_mom, dim=0).to(device)
                        reco_mom = torch.cat(reco_mom, dim=0).to(device)
                        true_reco_mom = torch.cat(true_reco_mom, dim=0).to(device)
                        batch = torch.cat(batch, dim=0).to(device)
                        masses = torch.cat(masses, dim=0).to(device)

                        # Unprocess true values as well
                        px_true = self.Transformers[
                            myGlobals.smearing_track_conditions[0].replace(
                                "DAUGHTERN", "DAUGHTER1"
                            )
                        ].unprocess(true_mom[:, 0].cpu().numpy())
                        py_true = self.Transformers[
                            myGlobals.smearing_track_conditions[1].replace(
                                "DAUGHTERN", "DAUGHTER1"
                            )
                        ].unprocess(true_mom[:, 1].cpu().numpy())
                        pz_true = self.Transformers[
                            myGlobals.smearing_track_conditions[2].replace(
                                "DAUGHTERN", "DAUGHTER1"
                            )
                        ].unprocess(true_mom[:, 2].cpu().numpy())

                        px_true = torch.tensor(px_true, dtype=dtype).to(device)
                        py_true = torch.tensor(py_true, dtype=dtype).to(device)
                        pz_true = torch.tensor(pz_true, dtype=dtype).to(device)

                        reco_mom = self.recover_smeared_momentum_from_deltas(
                            delta_output=reco_mom,  # your model output
                            px_true=px_true,
                            py_true=py_true,
                            pz_true=pz_true,
                        )

                        true_reco_mom = self.recover_smeared_momentum_from_deltas(
                            delta_output=true_reco_mom,  # your model output
                            px_true=px_true,
                            py_true=py_true,
                            pz_true=pz_true,
                        )

                        # Compute invariant masses
                        masses_reco = self.compute_invariant_masses(
                            reco_mom, batch, masses
                        )
                        masses_true_reco = self.compute_invariant_masses(
                            true_reco_mom, batch, masses
                        )

                        masses_reco_total = torch.cat(
                            [masses_reco_total, masses_reco.detach()], dim=0
                        )
                        masses_true_reco_total = torch.cat(
                            [masses_true_reco_total, masses_true_reco.detach()], dim=0
                        )

                for node_type in valid_particle_types:
                    v_pred = v_pred_dict[node_type]
                    v_target = data[node_type].v_target

                    # loss += F.mse_loss(v_pred, v_target, reduction='sum')
                    loss += F.l1_loss(v_pred, v_target, reduction="sum")

                    # if node_type == "11":
                    #     skloss += sinkhorn(v_pred, v_target)
                    #     total_nodes_in_batch_sk += v_target.numel()

                    total_nodes_in_batch += v_target.numel()

                total_loss += loss
                # total_skloss += skloss
                total_nodes += total_nodes_in_batch
                # total_nodes_sk += total_nodes_in_batch_sk

            # Final averaged loss
            if use_reco_mass_loss:
                mass_loss = (
                    F.l1_loss(
                        masses_reco_total, masses_true_reco_total, reduction="mean"
                    )
                    / 1000.0
                )
                self.log("mass_loss", mass_loss, prog_bar=True)

            mean_loss = (
                total_loss / total_nodes
            )  # + 10000.*total_skloss / total_nodes_sk
            self.log("loss", total_loss / total_nodes, prog_bar=True)
            # self.log("sinkhorn", 10000.*total_skloss / total_nodes_sk, prog_bar=True)

            if use_reco_mass_loss:
                total_loss = mean_loss + mass_loss
            else:
                total_loss = mean_loss
            optimizer.zero_grad()
            # mean_loss.backward()
            total_loss.backward()

            # clip_grad_norm_(self.gan.diffuser.parameters(), 3.0)
            clip_grad_norm_(self.gan.diffuser.parameters(), 1.5)
            optimizer.step()
            self.gan.EMA_diffuser.update(self.gan.diffuser)

        else:  # GAN
            optimizer_g, optimizer_d = self.optimizers()
            # single scheduler
            sch = self.lr_schedulers()
            if sch:
                sch.step()

            # if self.step_counter % 2 == 0 or self.network_option != "reco_vertex" or self.step_counter == 0:
            # reduce number of trainings for D in vertex - D was overpowering
            self.gan.discriminator.train()
            self.gan.generator.eval()

            discriminator_losses = []
            weight_balances = []
            for idx, batch_i in enumerate(batch):
                if self.smearingnet:
                    discriminator_loss_i, weight_balance_i = (
                        self.update_discriminator_smearingnet(batch[batch_i])
                    )
                else:
                    if self.network_option == "reco_vertex_diffusion_eGAN":
                        discriminator_loss_i, weight_balance_i = (
                            self.update_discriminator_eGAN(batch[batch_i])
                        )
                    else:
                        discriminator_loss_i, weight_balance_i = (
                            self.update_discriminator(batch[batch_i])
                        )
                discriminator_losses.append(discriminator_loss_i)
                weight_balances.append(weight_balance_i)
            # discriminator_loss = torch.stack(discriminator_losses).mean() # this should be batchsize weighted mean?
            losses = torch.stack(discriminator_losses)  # shape: [N]
            weights = torch.tensor(
                weight_balances, device=losses.device, dtype=losses.dtype
            )  # shape: [N]
            weighted_sum = (losses * weights).sum()
            total_weight = weights.sum()
            discriminator_loss = weighted_sum / total_weight

            optimizer_d.zero_grad()
            discriminator_loss.backward()
            optimizer_d.step()

            self.log("loss/disc", discriminator_loss, prog_bar=True)
            self.log(
                "lr/disc", self.optimizers()[1].param_groups[0]["lr"], prog_bar=True
            )

            self.gan.discriminator.eval()
            self.gan.generator.train()

            # if self.network_option != "reco_vertex_diffusion_eGAN" or self.step_counter > 5:
            gen_losses = []
            for idx, batch_i in enumerate(batch):
                if self.smearingnet:
                    gen_loss_i = self.update_generator_smearingnet(
                        batch[batch_i],
                        mode_seeking_term=False,  # mode seeking term not observed to help
                    )  # vanilla GAN - need to change loss internally
                else:
                    if self.network_option == "reco_vertex_diffusion_eGAN":
                        gen_loss_i = self.update_generator_eGAN(batch[batch_i])
                    else:
                        gen_loss_i = self.update_generator(
                            batch[batch_i],
                            mode_seeking_term=False,  # mode seeking term not observed to help
                        )  # vanilla GAN - need to change loss internally
                gen_losses.append(gen_loss_i)
            losses = torch.stack(gen_losses)  # shape: [N]
            weighted_sum = (losses * weights).sum()
            total_weight = weights.sum()
            gen_loss = weighted_sum / total_weight

            optimizer_g.zero_grad()
            gen_loss.backward()
            optimizer_g.step()

            self.log("loss/gen", gen_loss, prog_bar=True)

            self.gan.discriminator.eval()
            self.gan.generator.eval()

            self.step_counter += 1

    def plot_loss(self):
        event_acc = event_accumulator.EventAccumulator(self.logger.log_dir)
        event_acc.Reload()  # Load the events

        try:
            train_loss = event_acc.Scalars("train_loss")
        except Exception:
            return

        train_loss_epochs = [item.step for item in train_loss]
        train_loss_values = [item.value for item in train_loss]

        # Plotting the losses
        plt.figure(figsize=(10, 6))
        plt.plot(train_loss_epochs, train_loss_values, label="Training Loss")
        plt.xlabel("Epoch")
        plt.ylabel("Loss")
        plt.legend()
        plt.savefig(f"{self.logger.log_dir}/loss.png", bbox_inches="tight")
        plt.close("all")

    def run_inference(self, batch, test_batch_size, add_condition_nodes=True):
        if "diffusion" in self.network_option:
            reconstructed_mother, reconstructed_intermediate, reconstructed_track = (
                self.models.gan.inference(
                    test_batch_size, batch, self.noise_scheduler, add_condition_nodes
                )
            )
        elif "flowmatching" in self.network_option:
            reconstructed_mother, reconstructed_intermediate, reconstructed_track = (
                self.models.gan.inference(
                    test_batch_size, batch, None, flowmatching=True
                )
            )
        else:
            reconstructed_mother, reconstructed_intermediate, reconstructed_track = (
                self.models.gan.inference(test_batch_size, batch)
            )

        N_daughters = int(reconstructed_track.shape[0] / reconstructed_mother.shape[0])
        particles_involved = range(N_daughters)

        if reconstructed_track is not None:
            reconstructed_track = reconstructed_track.cpu().detach().numpy()
            reconstructed_track_reshaped = reconstructed_track.reshape(
                test_batch_size,
                N_daughters * len(myGlobals.track_targets),
            )
            targets_node_i = [
                target.replace("DAUGHTERN", f"DAUGHTER{daughterN + 1}")
                for daughterN in particles_involved
                for target in self.models.branch_options["track_targets"]
            ]

        reconstructed_mother = reconstructed_mother.cpu().detach().numpy()
        if reconstructed_intermediate is not None:
            reconstructed_intermediate = (
                reconstructed_intermediate.cpu().detach().numpy()
            )

            N_intermediates = int(
                reconstructed_intermediate.shape[0] / reconstructed_mother.shape[0]
            )

            intermediate_targets_i = []
            for idx, i in enumerate(list(range(N_intermediates))):
                for ii in self.models.branch_options["intermediate_targets"]:
                    # if N_intermediates == 1:
                    #     intermediate_targets_i.append(ii)
                    # else:
                    intermediate_targets_i.append(
                        ii.replace("INTERMEDIATE", f"INTERMEDIATE{idx + 1}")
                    )

            # print(np.shape(reconstructed_track_reshaped))
            # print(np.shape(reconstructed_mother))
            # print(np.shape(reconstructed_intermediate))
            # print(N_intermediates)
            # print(intermediate_targets_i)
            if N_intermediates > 1:
                reconstructed_intermediate = reconstructed_intermediate.reshape(
                    test_batch_size,
                    N_intermediates * len(myGlobals.intermediate_targets),
                )
            # quit()

            gen_df_i = pd.DataFrame(
                np.concatenate(
                    (
                        reconstructed_track_reshaped,
                        reconstructed_mother,
                        reconstructed_intermediate,
                    ),
                    axis=1,
                ),
                columns=targets_node_i + self.mother_targets + intermediate_targets_i,
            )
        else:
            gen_df_i = pd.DataFrame(
                np.concatenate(
                    (reconstructed_track_reshaped, reconstructed_mother), axis=1
                ),
                columns=targets_node_i + self.mother_targets,
            )
            intermediate_targets_i = []

        return gen_df_i, targets_node_i, intermediate_targets_i

    def run_inference_smearingnet(
        self, batch, test_batch_size, add_condition_nodes=False
    ):
        if "diffusion" in self.network_option:
            out = self.models.gan.inference(
                test_batch_size, batch, self.noise_scheduler, add_condition_nodes
            )
        elif "flowmatching" in self.network_option:
            out = self.models.gan.inference(
                test_batch_size, batch, None, add_condition_nodes, flowmatching=True
            )
        else:
            out = self.models.gan.inference(test_batch_size, batch)

        for idx, key in enumerate(out):
            # print(out[key], out[key].shape, key)
            out[key] = torch.concat(
                (out[key], int(key) * torch.ones_like(out[key][:, 0]).unsqueeze(1)),
                dim=1,
            )
            # print(out[key].shape, key)

            # quit()
            if idx == 0:
                out_cat = out[key]
            else:
                out_cat = torch.cat((out_cat, out[key]), dim=0)

        reconstructed_track = out_cat.cpu().detach().numpy()

        # reconstructed_track_reshaped = reconstructed_track.reshape(
        #     test_batch_size,
        #     -1,
        # )

        # N_daughters = int(np.shape(reconstructed_track)[0]/np.shape(reconstructed_track_reshaped)[0])
        # particles_involved = range(N_daughters)

        targets_node_i = [
            target.replace("DAUGHTERN", "DAUGHTERN")
            # for daughterN in particles_involved
            for target in self.models.branch_options["track_targets"]
        ]
        targets_node_i.append("TRUEID")

        gen_df_i = pd.DataFrame(
            np.concatenate(
                (reconstructed_track,),
                axis=1,
            ),
            columns=targets_node_i,
        )
        # print(gen_df_i)
        # quit()
        return gen_df_i, targets_node_i

    def create_true_df(self, batch, N_daughters, test_batch_size, targets_node_i):
        N_daughters = int(batch["track"].x.shape[0] / batch["mother"].x.shape[0])
        particles_involved = range(N_daughters)

        if self.using_node_targets:
            track_targets = batch["track"].x.cpu().detach().numpy()
        mother_targets = batch["mother"].x.cpu().detach().numpy()
        try:
            intermediate_targets = batch["intermediate"].x.cpu().detach().numpy()
            N_intermediates = int(
                intermediate_targets.shape[0] / mother_targets.shape[0]
            )
        except Exception:
            intermediate_targets = None
            N_intermediates = 0

        if track_targets is not None:
            track_targets_reshaped = track_targets.reshape(
                test_batch_size,
                N_daughters * np.shape(track_targets)[-1],
            )
            targets_node_i = [
                target.replace("DAUGHTERN", f"DAUGHTER{daughterN + 1}")
                for daughterN in particles_involved
                for target in self.models.branch_options["track_targets"]
            ]

        intermediate_targets_i = []
        for idx, i in enumerate(list(range(N_intermediates))):
            for ii in self.models.branch_options["intermediate_targets"]:
                # if N_intermediates == 1:
                #     intermediate_targets_i.append(ii)
                # else:
                intermediate_targets_i.append(
                    ii.replace("INTERMEDIATE", f"INTERMEDIATE{idx + 1}")
                )

        if N_intermediates == 0:
            true_df_i = pd.DataFrame(
                np.concatenate((track_targets_reshaped, mother_targets), axis=1),
                columns=targets_node_i + self.mother_targets,
            )
        else:
            if N_intermediates > 1:
                intermediate_targets = intermediate_targets.reshape(
                    test_batch_size,
                    N_intermediates * len(myGlobals.intermediate_targets),
                )

            true_df_i = pd.DataFrame(
                np.concatenate(
                    (track_targets_reshaped, mother_targets, intermediate_targets),
                    axis=1,
                ),
                columns=targets_node_i + self.mother_targets + intermediate_targets_i,
            )

        return true_df_i

    def create_true_df_smearingnet(
        self, batch, N_daughters, test_batch_size, targets_node_i
    ):
        particle_types = ["11", "13", "211", "321", "2212"]

        for idx, particle_type in enumerate(particle_types):
            batch[particle_type].x = torch.concat(
                (
                    batch[particle_type].x,
                    int(particle_type)
                    * torch.ones_like(batch[particle_type].x[:, 0]).unsqueeze(1),
                ),
                dim=1,
            )
            if idx == 0:
                out_cat = batch[particle_type].x
            else:
                out_cat = torch.cat((out_cat, batch[particle_type].x), dim=0)

        track_targets = out_cat.cpu().detach().numpy()

        # track_targets_reshaped = track_targets.reshape(
        #     test_batch_size,
        #     -1,
        # )

        true_df_i = pd.DataFrame(
            track_targets,
            columns=targets_node_i,
        )

        return true_df_i

    def on_validation_epoch_start(self):
        if self.current_epoch != self.previous_epoch:
            self.plot_counter = 0
        self.plot_counter += 1
        print(f"Starting validation for epoch {self.current_epoch}")
        # copy scripts to version_x location

        # Ensure logging directory exists
        if self.logger is not None and not self.saved_code:
            save_dir = self.logger.log_dir  # Get the experiment save directory
            code_save_dir = os.path.join(save_dir, "code_backup")

            if not os.path.exists(code_save_dir):
                os.makedirs(code_save_dir)

            print("saving code to:", code_save_dir)
            script_files = [
                # "/users/am13743/Rex/training_scripts/train.py",
                # "/users/am13743/Rex/training_scripts/train_smearing.py",
                "/users/am13743/Rex/src/lhcb_rex/training/hetero_trainer.py",
                "/users/am13743/Rex/src/lhcb_rex/models/hetero_graph_based_GAN.py",
                "/users/am13743/Rex/src/lhcb_rex/models/hetero_graph_based_GAN_smearing.py",
                "/users/am13743/Rex/src/lhcb_rex/models/hetero_graph_based_diffusion_model.py",
                "/users/am13743/Rex/src/lhcb_rex/models/hetero_graph_based_diffusion_model_smearing.py",
                "/users/am13743/Rex/src/lhcb_rex/settings/default_model_parameters.json",
                "/users/am13743/Rex/src/lhcb_rex/settings/PVsmear_model_parameters.json",
                "/users/am13743/Rex/src/lhcb_rex/settings/smearing_model_parameters.json",
                "/users/am13743/Rex/src/lhcb_rex/settings/diffusion_model_parameters.json",
                "/users/am13743/Rex/src/lhcb_rex/settings/smear_diffusion_model_parameters.json",
            ]
            # Copy all relevant scripts
            for script in script_files:
                shutil.copy(script, code_save_dir)
            self.saved_code = True

        self.plot_loss()
        self.previous_epoch = self.current_epoch

    def validation_step_default(self, batch, batch_idx, dataloader_idx=0):
        # if "diffusion" in self.network_option:
        #     print("no validation")
        #     return

        if (
            "diffusion" in self.network_option or "flowmatching" in self.network_option
        ) and "GAN" not in self.network_option:
            self.models.gan.diffuser.eval()
        elif "VAE" in self.network_option:
            self.models.gan.decoder.eval()
            self.models.gan.encoder.eval()
        elif self.network_option in ["reco_vertex_diffusion_eGAN"]:
            self.models.gan.diffuser.eval()
            self.models.gan.generator.eval()
        else:
            self.models.gan.generator.eval()

        with torch.no_grad():
            label = (
                self.val_labels[dataloader_idx]
                if self.val_labels
                else f"val_{dataloader_idx}"
            )

            if "conditionless" in label:
                N_daughters = int(label.replace("_conditionless", "")[-1])
            else:
                N_daughters = int(label[-1])
            test_batch_size = batch["mother"].x.shape[0]

            if "conditionless" in label:
                gen_df_i, targets_node_i, targets_hyper_i = self.run_inference(
                    batch, test_batch_size, add_condition_nodes=False
                )
            else:
                gen_df_i, targets_node_i, targets_hyper_i = self.run_inference(
                    batch, test_batch_size, add_condition_nodes=True
                )

            # print(gen_df_i)
            # for key in gen_df_i:
            #     print(key)
            # quit()

            if batch_idx == 0:
                self.gen_data[label] = gen_df_i
                if "physics" in label:
                    gen_df_i = tfs.untransform_df(gen_df_i, self.Transformers)

                    validation_variables = (
                        batch["validation_variables"].x.detach().cpu().numpy()
                    )
                    validation_variables = np.reshape(
                        validation_variables, (gen_df_i.shape[0], -1)
                    )
                    for idx, vali_var in enumerate(myGlobals.validation_variables):
                        gen_df_i[vali_var] = validation_variables[:, idx]

                    self.gen_data_physical[label] = gen_df_i

            else:
                self.gen_data[label] = pd.concat(
                    (self.gen_data[label], gen_df_i), axis=0
                )
                if "physics" in label:
                    gen_df_i = tfs.untransform_df(gen_df_i, self.Transformers)

                    validation_variables = (
                        batch["validation_variables"].x.detach().cpu().numpy()
                    )
                    validation_variables = np.reshape(
                        validation_variables, (gen_df_i.shape[0], -1)
                    )
                    for idx, vali_var in enumerate(myGlobals.validation_variables):
                        gen_df_i[vali_var] = validation_variables[:, idx]

                    self.gen_data_physical[label] = pd.concat(
                        (self.gen_data_physical[label], gen_df_i), axis=0
                    )

            if self.current_epoch == 0:  # TRUE info
                true_df_i = self.create_true_df(
                    batch, N_daughters, test_batch_size, targets_node_i
                )

                if batch_idx == 0:
                    self.true_data[label] = true_df_i
                    if "physics" in label:
                        true_df_i = tfs.untransform_df(true_df_i, self.Transformers)

                        validation_variables = (
                            batch["validation_variables"].x.detach().cpu().numpy()
                        )
                        validation_variables = np.reshape(
                            validation_variables, (true_df_i.shape[0], -1)
                        )
                        for idx, vali_var in enumerate(myGlobals.validation_variables):
                            true_df_i[vali_var] = validation_variables[:, idx]

                        self.true_data_physical[label] = true_df_i

                else:
                    self.true_data[label] = pd.concat(
                        (self.true_data[label], true_df_i), axis=0
                    )
                    if "physics" in label:
                        true_df_i = tfs.untransform_df(true_df_i, self.Transformers)

                        validation_variables = (
                            batch["validation_variables"].x.detach().cpu().numpy()
                        )
                        validation_variables = np.reshape(
                            validation_variables, (true_df_i.shape[0], -1)
                        )
                        for idx, vali_var in enumerate(myGlobals.validation_variables):
                            true_df_i[vali_var] = validation_variables[:, idx]

                        self.true_data_physical[label] = pd.concat(
                            (self.true_data_physical[label], true_df_i), axis=0
                        )

    def validation_step_smearingnet(self, batch, batch_idx, dataloader_idx=0):
        label = (
            self.val_labels[dataloader_idx]
            if self.val_labels
            else f"val_{dataloader_idx}"
        )

        N_daughters = int(label[1])
        particle_types = ["11", "13", "211", "321", "2212"]
        test_batch_size = 0
        for particle_type in particle_types:
            try:
                if torch.amax(batch[particle_type].batch) > test_batch_size:
                    test_batch_size = int(torch.amax(batch[particle_type].batch))
            except:
                pass  # particle_type probably not in batch
        test_batch_size += 1

        if "conditionless" in label:
            gen_df_i, targets_node_i = self.run_inference_smearingnet(
                batch, test_batch_size, add_condition_nodes=False
            )
        else:
            gen_df_i, targets_node_i = self.run_inference_smearingnet(
                batch, test_batch_size, add_condition_nodes=True
            )

        if batch_idx == 0:
            self.gen_data[label] = gen_df_i
        else:
            self.gen_data[label] = pd.concat((self.gen_data[label], gen_df_i), axis=0)

        if self.current_epoch == 0:  # TRUE info
            true_df_i = self.create_true_df_smearingnet(
                batch, N_daughters, test_batch_size, targets_node_i
            )

            # if self.network_option == "mom_smear_diffusion":
            #     for branch in true_df_i:
            #         if "TRUEID" not in branch:
            #             true_df_i[branch] *= 0.2

            if batch_idx == 0:
                self.true_data[label] = true_df_i
            else:
                self.true_data[label] = pd.concat(
                    (self.true_data[label], true_df_i), axis=0
                )

    def validation_step(self, batch, batch_idx, dataloader_idx=0):
        with torch.no_grad():
            if self.smearingnet:
                self.validation_step_smearingnet(batch, batch_idx, dataloader_idx)
            else:
                # print(batch)
                # quit()
                self.validation_step_default(batch, batch_idx, dataloader_idx)

    def BDT_FoM(self, offline=False):
        from sklearn.ensemble import GradientBoostingClassifier
        from sklearn.metrics import roc_auc_score
        from sklearn.metrics import roc_curve

        if offline:
            pdf_name = "BDT.pdf"
        else:
            pdf_name = f"{self.logger.log_dir}/BDTs_epoch{self.current_epoch}_{self.plot_counter}.pdf"

        with PdfPages(pdf_name) as pdf:
            for label in self.gen_data:
                if label not in self.ROC_scores:
                    self.ROC_scores[label] = []

                images = np.asarray(self.gen_data[label])
                X_train_sample = np.asarray(self.true_data[label])

                print("\n")
                print(label)

                clf = GradientBoostingClassifier(
                    n_estimators=50, learning_rate=0.1, max_depth=3
                )

                bdt_train_size = int(np.shape(images)[0] / 2)
                if bdt_train_size > int(1e4):
                    bdt_train_size = int(1e4)

                real_training_data = np.squeeze(X_train_sample[:bdt_train_size])
                fake_training_data = np.squeeze(images[:bdt_train_size])

                if bdt_train_size == int(1e4):
                    real_test_data = np.squeeze(
                        X_train_sample[bdt_train_size : 2 * bdt_train_size]
                    )
                    fake_test_data = np.squeeze(
                        images[bdt_train_size : 2 * bdt_train_size]
                    )
                else:
                    real_test_data = np.squeeze(X_train_sample[bdt_train_size:])
                    fake_test_data = np.squeeze(images[bdt_train_size:])

                real_training_labels = np.ones(bdt_train_size)
                fake_training_labels = np.zeros(bdt_train_size)

                total_training_data = np.concatenate(
                    (real_training_data, fake_training_data)
                )
                total_training_labels = np.concatenate(
                    (real_training_labels, fake_training_labels)
                )

                print("Fitting BDT...")
                clf.fit(total_training_data, total_training_labels)

                print("Querying BDT...")
                out_real = clf.predict_proba(real_test_data)

                out_fake = clf.predict_proba(fake_test_data)

                print("Plotting BDT...")

                ROC_AUC_SCORE_curr = roc_auc_score(
                    np.append(
                        np.ones(np.shape(out_real[:, 1])),
                        np.zeros(np.shape(out_fake[:, 1])),
                    ),
                    np.append(out_real[:, 1], out_fake[:, 1]),
                )

                plt.figure(figsize=(6, 5))
                plt.hist(
                    [out_real[:, 1], out_fake[:, 1]],
                    bins=35,
                    label=["Real", "Generated"],
                    alpha=0.5,
                    histtype="stepfilled",
                )
                plt.xlabel("BDT Output")
                plt.ylabel("Entries")
                plt.title(label)

                ax1 = plt.gca()
                ax2 = ax1.twinx()

                y_true = np.append(
                    np.ones_like(out_real[:, 1]), np.zeros_like(out_fake[:, 1])
                )
                y_scores = np.append(out_real[:, 1], out_fake[:, 1])
                fpr, tpr, _ = roc_curve(y_true, y_scores)

                roc_label = f"ROC AUC = {ROC_AUC_SCORE_curr:.3f}"
                ax2.plot(fpr, tpr, color="tab:red", label=roc_label)
                ax2.set_ylabel("True Positive Rate")

                lines_1, labels_1 = ax1.get_legend_handles_labels()
                lines_2, labels_2 = ax2.get_legend_handles_labels()
                ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper center")

                plt.xlim(0, 1)
                pdf.savefig(bbox_inches="tight")
                plt.close()

                self.ROC_scores[label].append(ROC_AUC_SCORE_curr)

                plt.figure(figsize=(6, 5))
                plt.plot(self.ROC_scores[label])
                plt.title(label)
                plt.ylabel("ROC AUC")
                plt.xlabel("Steps")
                pdf.savefig(bbox_inches="tight")
                plt.close()

            plt.figure(figsize=(6, 5))
            for label in self.gen_data:
                if "conditionless" in label:
                    plt.plot(self.ROC_scores[label], label=label, ls="--", alpha=0.6)
                else:
                    plt.plot(self.ROC_scores[label], label=label)

            plt.ylim(0.5, 1.0)
            plt.legend()
            plt.ylabel("ROC AUC")
            plt.xlabel("Steps")
            pdf.savefig(bbox_inches="tight")
            plt.close()

            print(f"Plotted {pdf_name}.")

    def make_plots(self, offline=False):
        for label in self.gen_data:
            print(f"Plotting {label}...")
            if offline:
                pdf_name = f"{label.replace(' ', '_')}.pdf"
            else:
                pdf_name = f"{self.logger.log_dir}/{label.replace(' ', '_')}_epoch{self.current_epoch}_{self.plot_counter}.pdf"

            if "physics" in label:
                gen_df = self.gen_data_physical[label]
                true_df = self.true_data_physical[label]
                gen_df_processed = self.gen_data[label]
                true_df_processed = self.true_data[label]

                gen_df = gen_df.reset_index()
                true_df = true_df.reset_index()

                for df_i in [gen_df, true_df]:
                    df_i["MOTHER_ENDVERTEX_CHI2"] = (
                        df_i["MOTHER_ENDVERTEX_CHI2NDOF"] * 3
                    )
                    df_i["INTERMEDIATE_ENDVERTEX_CHI2"] = (
                        df_i["INTERMEDIATE_ENDVERTEX_CHI2NDOF"] * 1
                    )
                    df_i["MOTHER_ENDVERTEX_NDOF"] = 3

                    cuts = {}
                    cuts["MOTHER_FDCHI2_OWNPV"] = ">100."
                    cuts["MOTHER_DIRA_OWNPV"] = ">0.9995"
                    cuts["MOTHER_IPCHI2_OWNPV"] = "<25"
                    cuts["(MOTHER_ENDVERTEX_CHI2/MOTHER_ENDVERTEX_NDOF)"] = "<9"
                    cuts["INTERMEDIATE_FDCHI2_OWNPV"] = ">16"
                    cuts["INTERMEDIATE_IPCHI2_OWNPV"] = ">0"
                    for lepton in ["DAUGHTER2", "DAUGHTER3"]:
                        cuts[f"{lepton}_IPCHI2_OWNPV"] = ">9"
                    for hadron in ["DAUGHTER1"]:
                        cuts[f"{hadron}_IPCHI2_OWNPV"] = ">9"

                    if isinstance(cuts, dict):
                        cut_string = ""
                        for cut_idx, cut_i in enumerate(list(cuts.keys())):
                            if cut_idx > 0:
                                cut_string += " & "
                            if cut_i == "extra_cut":
                                cut_string += f"{cuts[cut_i]}"
                            else:
                                cut_string += f"{cut_i}{cuts[cut_i]}"
                        cuts_string = cut_string

                    cut_array = df_i.query(cuts_string)
                    stripped = np.zeros(df_i.shape[0])
                    stripped[np.asarray(cut_array.index)] = 1.0
                    df_i["stripped"] = stripped

                    BDT_targets = [
                        "MOTHER_ENDVERTEX_CHI2",
                        "MOTHER_IPCHI2_OWNPV",
                        "MOTHER_FDCHI2_OWNPV",
                        "MOTHER_DIRA_OWNPV",
                        "DAUGHTER1_IPCHI2_OWNPV",
                        "DAUGHTER1_TRACK_CHI2NDOF",
                        "DAUGHTER2_IPCHI2_OWNPV",
                        "DAUGHTER2_TRACK_CHI2NDOF",
                        "DAUGHTER3_IPCHI2_OWNPV",
                        "DAUGHTER3_TRACK_CHI2NDOF",
                        "INTERMEDIATE_FDCHI2_OWNPV",
                        "INTERMEDIATE_IPCHI2_OWNPV",
                    ]
                    clf = pickle.load(
                        open(
                            "/users/am13743/fast_vertexing_variables/publish/example/BDT_sig_comb_WGANcocktail_newconditions.pkl",
                            "rb",
                        )
                    )[0]["BDT"]

                    sample = df_i[BDT_targets]
                    sample = np.squeeze(np.asarray(sample[BDT_targets]))
                    nan_rows = np.unique(np.where(np.isnan(sample))[0])
                    bdt_responses = np.full(len(sample), np.nan)
                    non_nan_rows = np.setdiff1d(np.arange(len(sample)), nan_rows)
                    if len(non_nan_rows) > 0:
                        bdt_responses[non_nan_rows] = clf.predict_proba(
                            sample[non_nan_rows]
                        )[:, 1]
                    df_i["BDT"] = bdt_responses

                for_var = {}
                for_var["mkee"] = [4.5, 5.7]
                for_var["q2"] = [0, 23]
                for_var["mkl"] = [0, 5000]
                for_var["ctl"] = [-1, 1]

                with PdfPages(pdf_name) as pdf:
                    for var in for_var:
                        plt.figure(figsize=(12, 6))

                        # First subplot: Unchanged
                        plt.subplot(1, 2, 1)
                        hist = plt.hist(
                            true_df[var],
                            bins=15,
                            range=for_var[var],
                            color="k",
                            alpha=0.25,
                        )
                        plt.hist(
                            true_df.query("stripped==1")[var],
                            bins=hist[1],
                            color="tab:red",
                            alpha=0.25,
                        )
                        plt.hist(
                            true_df.query("stripped==1 and BDT>0.9")[var],
                            bins=hist[1],
                            color="tab:blue",
                            alpha=0.25,
                        )
                        plt.hist(
                            gen_df.query("stripped==1")[var],
                            bins=hist[1],
                            color="tab:red",
                            alpha=0.25,
                            histtype="step",
                        )
                        plt.hist(
                            gen_df.query("stripped==1 and BDT>0.9")[var],
                            bins=hist[1],
                            color="tab:blue",
                            alpha=0.25,
                            histtype="step",
                        )
                        plt.xlabel(var)
                        plt.xlim(for_var[var][0], for_var[var][1])

                        # Second subplot: Updated to include ratio plot
                        ax1 = plt.subplot(1, 2, 2)

                        # Get histogram data
                        true_vals = true_df.query("stripped==1 and BDT>0.9")[var]
                        gen_vals = gen_df.query("stripped==1 and BDT>0.9")[var]
                        bins = hist[1]

                        true_hist, _ = np.histogram(true_vals, bins=bins)
                        gen_hist, _ = np.histogram(gen_vals, bins=bins)

                        # Compute ratio (avoid division by zero)
                        ratio = np.divide(
                            gen_hist,
                            true_hist,
                            where=gen_hist != 0,
                            out=np.zeros_like(true_hist, dtype=float),
                        )
                        bin_centers = (bins[:-1] + bins[1:]) / 2

                        # Plot histograms on primary y-axis
                        ax1.hist(
                            true_vals,
                            bins=bins,
                            color="tab:blue",
                            label="true",
                            alpha=0.6,
                        )
                        ax1.hist(
                            gen_vals, bins=bins, color="k", histtype="step", label="gen"
                        )
                        ax1.set_xlabel(var)
                        ax1.set_ylabel("Counts")
                        ax1.set_xlim(for_var[var][0], for_var[var][1])
                        ax1.legend(loc="upper left")

                        # Create secondary y-axis for ratio plot
                        ax2 = ax1.twinx()
                        ax2.scatter(
                            bin_centers,
                            ratio,
                            color="tab:red",
                            marker="s",
                            label="true/gen",
                            alpha=0.6,
                        )
                        ax2.set_ylabel("Ratio")
                        ax2.axhline(
                            1, color="gray", linestyle="dashed", alpha=0.7
                        )  # Reference line at 1
                        ax2.set_ylim(0.5, 1.5)  # Adjust ratio range dynamically
                        ax2.legend(loc="upper right")

                        pdf.savefig(bbox_inches="tight")
                        plt.close()

                        # plt.figure(figsize=(12,6))

                        # plt.subplot(1,2,1)
                        # hist = plt.hist(true_df[var], bins=15, range=for_var[var], color='k', alpha=0.25)
                        # plt.hist(true_df.query('stripped==1')[var], bins=hist[1], color='tab:red', alpha=0.25)
                        # plt.hist(true_df.query('stripped==1 and BDT>0.9')[var], bins=hist[1], color='tab:blue', alpha=0.25)
                        # # plt.hist(gen_df[var], bins=hist[1], color='k', alpha=0.25,histtype='step')
                        # plt.hist(gen_df.query('stripped==1')[var], bins=hist[1], color='tab:red', alpha=0.25,histtype='step')
                        # plt.hist(gen_df.query('stripped==1 and BDT>0.9')[var], bins=hist[1], color='tab:blue', alpha=0.25,histtype='step')
                        # plt.xlabel(var)
                        # plt.xlim(for_var[var][0], for_var[var][1])

                        # plt.subplot(1,2,2)
                        # plt.hist(true_df.query('stripped==1 and BDT>0.9')[var], bins=hist[1], color='tab:blue', label='true')
                        # plt.hist(gen_df.query('stripped==1 and BDT>0.9')[var], bins=hist[1], color='k',histtype='step', label='gen')
                        # plt.legend()
                        # plt.xlabel(var)
                        # plt.xlim(for_var[var][0], for_var[var][1])

                        # pdf.savefig(bbox_inches="tight")
                        # plt.close()

                    for branch in gen_df_processed:
                        plt.title(branch)
                        plt.hist2d(
                            gen_df_processed[branch],
                            true_df_processed[branch],
                            bins=35,
                            range=[[-1, 1], [-1, 1]],
                        )
                        plt.xlabel("gen")
                        plt.ylabel("true")
                        pdf.savefig(bbox_inches="tight")
                        plt.close()
            else:
                with PdfPages(pdf_name) as pdf:
                    for branch in self.gen_data[label]:
                        gen_df = self.gen_data[label]
                        true_df = self.true_data[label]

                        plt.figure(figsize=(14, 6))
                        plt.subplot(1, 2, 1)
                        plt.title(branch)
                        plt.hist(
                            [gen_df[branch], true_df[branch]],
                            bins=35,
                            density=True,
                            histtype="step",
                            label=["gen", "true"],
                            range=[-1, 1],
                        )
                        plt.legend()
                        plt.subplot(1, 2, 2)
                        plt.title(branch)
                        plt.hist(
                            [gen_df[branch], true_df[branch]],
                            bins=50,
                            density=True,
                            histtype="step",
                            label=["gen", "true"],
                        )
                        plt.legend()
                        pdf.savefig(bbox_inches="tight")
                        plt.close()

                        plt.figure(figsize=(7, 6))
                        plt.title(branch)
                        plt.hist2d(
                            gen_df[branch],
                            true_df[branch],
                            bins=35,
                            # bins=100,
                            range=[[-1, 1], [-1, 1]],
                        )
                        plt.xlabel("gen")
                        plt.ylabel("true")
                        pdf.savefig(bbox_inches="tight")
                        plt.close()

                    # intermediate_targets = [
                    #     "INTERMEDIATE_ENDVERTEX_CHI2NDOF",
                    #     "INTERMEDIATE_IPCHI2_OWNPV",
                    #     "INTERMEDIATE_FDCHI2_OWNPV",
                    #     "INTERMEDIATE_DIRA_OWNPV",
                    # ]

                    # if "INTERMEDIATE_DIRA_OWNPV" in list(self.gen_data[label].keys()):
                    #     for intermediate_target in intermediate_targets:
                    #         plt.title(f"{intermediate_target} TRUE")
                    #         plt.hist2d(
                    #             true_df[intermediate_target],
                    #             true_df[
                    #                 intermediate_target.replace("INTERMEDIATE", "MOTHER")
                    #             ],
                    #             bins=35,
                    #             range=[[-1, 1], [-1, 1]],
                    #         )
                    #         plt.xlabel(intermediate_target)
                    #         plt.ylabel(
                    #             intermediate_target.replace("INTERMEDIATE", "MOTHER")
                    #         )
                    #         pdf.savefig(bbox_inches="tight")
                    #         plt.close()

                    #         plt.title(f"{intermediate_target} GEN")
                    #         plt.hist2d(
                    #             gen_df[intermediate_target],
                    #             gen_df[
                    #                 intermediate_target.replace("INTERMEDIATE", "MOTHER")
                    #             ],
                    #             bins=35,
                    #             range=[[-1, 1], [-1, 1]],
                    #         )
                    #         plt.xlabel(intermediate_target)
                    #         plt.ylabel(
                    #             intermediate_target.replace("INTERMEDIATE", "MOTHER")
                    #         )
                    #         pdf.savefig(bbox_inches="tight")
                    #         plt.close()

            print(f"Plotted {pdf_name}.")

    def make_plots_smearingnet(self, offline=False):
        for label in self.gen_data:
            print(f"Plotting {label}...")
            if offline:
                pdf_name = f"{label.replace(' ', '_')}.pdf"
            else:
                pdf_name = f"{self.logger.log_dir}/{label.replace(' ', '_')}_epoch{self.current_epoch}_{self.plot_counter}.pdf"

            with PdfPages(pdf_name) as pdf:
                for PID in [None, 11, 13, 211, 321, 2212]:
                    for branch in self.gen_data[label]:
                        if branch == "TRUEID":
                            continue
                        if (
                            branch not in myGlobals.smearing_track_targets
                            and not re.search("_PID.", branch)
                            and not re.search("_ProbNN.", branch)
                        ):
                            continue

                        gen_df = self.gen_data[label]
                        true_df = self.true_data[label]

                        if PID is not None:
                            gen_df = gen_df.query(f"TRUEID=={PID}")
                            true_df = true_df.query(f"TRUEID=={PID}")

                        plt.figure(figsize=(12, 6))
                        plt.subplot(1, 2, 1)
                        plt.title(f"{branch} {PID}")
                        plt.hist(
                            [gen_df[branch], true_df[branch]],
                            bins=35,
                            density=True,
                            histtype="step",
                            label=["gen", "true"],
                            range=[-1, 1],
                        )
                        plt.legend()
                        plt.subplot(1, 2, 2)
                        plt.title(f"{branch} {PID}")
                        plt.hist(
                            [gen_df[branch], true_df[branch]],
                            bins=100,
                            density=True,
                            histtype="step",
                            label=["gen", "true"],
                            range=[-5, 5],
                        )
                        plt.yscale("log")
                        plt.legend()
                        pdf.savefig(bbox_inches="tight")
                        plt.close()

                        plt.title(f"{branch} {PID}")
                        plt.hist2d(
                            gen_df[branch],
                            true_df[branch],
                            bins=35,
                            range=[[-1, 1], [-1, 1]],
                        )
                        plt.xlabel("gen")
                        plt.ylabel("true")
                        pdf.savefig(bbox_inches="tight")
                        plt.close()

            print(f"Plotted {pdf_name}.")

    def load(self, models_loc):
        print("Loading models...")
        self.models.load(models_loc)

    def on_validation_epoch_end(self):
        if self.initialisation:  # no need to run this stuff for the initialistion step.
            self.initialisation = False

            # self.make_plots()

            return

        # Make plots
        if self.smearingnet:
            self.make_plots_smearingnet()

        else:
            self.make_plots()
            self.BDT_FoM()

        if self.save_models:
            print("Saving models...")
            self.models.save(f"{self.logger.log_dir}/models.pkl")

        # Train BDT
        full_data_sets = {}

        for label in self.gen_data:
            # N = int(label.split("_")[-1])
            N = int(label[1])

            gen = np.asarray(self.gen_data[label])
            true = np.asarray(self.true_data[label])

            try:
                full_data_sets[N]["gen"] = np.concatenate(
                    (full_data_sets[N]["gen"], gen), axis=0
                )
                full_data_sets[N]["true"] = np.concatenate(
                    (full_data_sets[N]["true"], true), axis=0
                )
            except Exception:
                full_data_sets[N] = {}
                full_data_sets[N]["gen"] = gen
                full_data_sets[N]["true"] = true

    def configure_optimizers(self):
        learning_rate = 0.0002
        # if self.network_option == "reco_vertex":
        #     learning_rate = 1E-4

        if "diffusion" in self.network_option:
            opt_g = torch.optim.AdamW(
                # self.gan.diffuser.parameters(),
                list(self.gan.diffuser.parameters())
                + list(self.gan.encoder.parameters()),
                lr=1e-4,
                # lr=2e-5,
                betas=(0.9, 0.999),
                amsgrad=False,
            )
            # total_steps = 25000
            # cosine_scheduler = CosineAnnealingLR(opt_g, T_max=total_steps)
            # return [opt_g], [cosine_scheduler]

            return [opt_g], []

        elif self.network_option == "reco_vertex_flowmatching":
            opt_g = torch.optim.AdamW(
                self.gan.diffuser.parameters(),
                lr=1e-4,
                betas=(0.9, 0.999),
                amsgrad=False,
            )
            return [opt_g], []

        elif (
            "flowmatching" in self.network_option
            and "reco_vertex" not in self.network_option
        ):
            # opt_g = torch.optim.AdamW(
            #     self.gan.diffuser.parameters(),
            #     lr=1e-4,
            #     betas=(0.9, 0.999),
            #     amsgrad=False,
            # )

            params_11 = []
            params_rest = []

            # Collect from the single ModuleDicts
            module_dicts = [
                self.gan.diffuser.embedding_layer,
                self.gan.diffuser.condition_embedding_layer,
                self.gan.diffuser.embedding_pooling_attention_layer,
                self.gan.diffuser.embedding_pooling_collapsing_layer,
            ]

            for module_dict in module_dicts:
                for particle_type, layer in module_dict.items():
                    if particle_type == "11":
                        params_11.extend(layer.parameters())
                    else:
                        params_rest.extend(layer.parameters())

            # Collect from lists of ModuleDicts
            module_list_of_dicts = [
                self.gan.diffuser.selfloop_layers,
                self.gan.diffuser.communication_compressor_layers,
                self.gan.diffuser.x_compressor_layers,
                self.gan.diffuser.communication_atten_layers,
            ]

            for module_list in module_list_of_dicts:
                for module_dict in module_list:
                    for particle_type, layer in module_dict.items():
                        if particle_type == "11":
                            params_11.extend(layer.parameters())
                        else:
                            params_rest.extend(layer.parameters())

            # Get all parameters in the model
            all_params = list(self.gan.diffuser.parameters())

            # Remove duplicates and keep only remaining params
            params_11_ids = set(id(p) for p in params_11)
            params_rest_ids = set(id(p) for p in params_rest)

            params_remaining = []
            for p in all_params:
                if id(p) not in params_11_ids and id(p) not in params_rest_ids:
                    params_remaining.append(p)

            params_rest += params_remaining

            opt_g = torch.optim.AdamW(
                [
                    {"params": params_11, "lr": 3e-4},  # x3 the base LR
                    {"params": params_rest, "lr": 1e-4},
                ],
                betas=(0.9, 0.999),
                amsgrad=False,
            )

            total_params_model = sum(p.numel() for p in self.gan.diffuser.parameters())
            total_params_split = sum(p.numel() for p in params_11) + sum(
                p.numel() for p in params_rest
            )

            print("Model params:", total_params_model)
            print("Sum of param groups:", total_params_split)
            assert total_params_model == total_params_split

            return [opt_g], []

        elif self.network_option == "reco_vertex_diffusion_eGAN":
            opt_g = torch.optim.AdamW(
                self.gan.generator.parameters(),
                lr=1e-4,
                betas=(0.5, 0.999),
                amsgrad=True,
            )
            opt_d = torch.optim.Adam(
                self.gan.discriminator.parameters(),
                lr=1e-4 / 5.0,
                betas=(0.5, 0.999),
                amsgrad=True,
            )

            return [opt_g, opt_d], []

        elif "VAE" in self.network_option:
            opt_vae = torch.optim.AdamW(
                list(self.gan.encoder.parameters())
                + list(self.gan.decoder.parameters()),
                lr=1e-4,
                betas=(0.9, 0.999),
                amsgrad=False,
            )
            return [opt_vae], []

        opt_g = torch.optim.Adam(
            self.gan.generator.parameters(),
            lr=learning_rate,
            betas=(0.5, 0.999),
            amsgrad=True,
        )

        if self.network_option == "PID_trig":
            opt_d = torch.optim.Adam(
                self.gan.discriminator.parameters(),
                # lr=learning_rate / 3.0,
                lr=learning_rate / 10.0,
                # lr=learning_rate,
                betas=(0.5, 0.999),
                amsgrad=True,
            )
        elif self.network_option == "mom_smear":
            opt_d = torch.optim.Adam(
                self.gan.discriminator.parameters(),
                # lr=learning_rate / 10.0,
                lr=learning_rate,
                betas=(0.5, 0.999),
                amsgrad=True,
            )
        elif self.network_option == "reco_vertex":
            opt_d = torch.optim.Adam(
                self.gan.discriminator.parameters(),
                lr=learning_rate / 10.0,
                # lr=learning_rate,
                betas=(0.5, 0.999),
                amsgrad=True,
            )

            # def lr_lambda_d(step):
            #     steps_until_transition = 100
            #     number_of_steps_in_transition = 100
            #     initial_frac = 1.0
            #     final_frac = 10.0 # to realign with G

            #     if step < steps_until_transition:
            #         return initial_frac
            #     elif step < steps_until_transition + number_of_steps_in_transition:
            #         progress = (step - steps_until_transition) / number_of_steps_in_transition
            #         return initial_frac + progress * (final_frac - initial_frac)
            #     else:
            #         return final_frac

            # scheduler_d = {
            #     "scheduler": torch.optim.lr_scheduler.LambdaLR(opt_d, lr_lambda=lr_lambda_d),
            #     "interval": "step",  # Update every training step
            #     "name": "discriminator_lr",
            # }

            # return [opt_g, opt_d], [scheduler_d]

        return [opt_g, opt_d], []

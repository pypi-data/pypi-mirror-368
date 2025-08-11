import lhcb_rex.settings.globals as myGlobals

import pytorch_lightning as pl
import torch
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
from tensorboard.backend.event_processing import event_accumulator
import numpy as np
import torch.nn.functional as F
from torchmetrics.regression import MeanAbsolutePercentageError
import torch.nn as nn
from scipy.stats import norm
from diffusers import DDPMScheduler

mean_abs_percentage_error = MeanAbsolutePercentageError()


_EPSILON = 1e-7  # Small constant for numerical stability


class StdTrainerModule(pl.LightningModule):
    def __init__(self, model, dataloaders, val_dataloaders, network_option="PV_smear"):
        super(StdTrainerModule, self).__init__()

        self.dataloaders = dataloaders
        self.val_dataloaders = val_dataloaders
        self.models = model
        self.network_option = network_option

        self.targets_graph = model.branch_options["targets_graph"]

        self.gan = self.models.gan
        self.automatic_optimization = False

        self.learning_rate = self.models.lr

        self.beta = self.models.beta

        self.initialisation = True

    def _loss_generator(self, y_pred):
        # Clip predictions to avoid log(0)
        y_pred = torch.clamp(y_pred, _EPSILON, 1.0 - _EPSILON)
        # Calculate loss
        out = -torch.log(y_pred)
        # Return mean loss
        return torch.mean(out, dim=-1)

    def training_step(self, batch, batch_idx):
        if "diffusion" in self.network_option:
            optimizer = self.optimizers()
            self.gan.diffuser.train()

            device = batch["targets"].device

            batch_size_i = batch["targets"].shape[0]

            timesteps = torch.randint(
                low=0,
                high=self.gan.noise_scheduler.config.num_train_timesteps,
                size=(batch_size_i,),
                device=device,
            )

            # Add noise
            noise = self.gan.sample_starting_noise(
                batch["targets"].shape, device=device
            )
            noisy_batch = self.gan.noise_scheduler.add_noise(
                batch["targets"], noise, timesteps
            )

            # Gen latent
            latent = torch.randn(
                (batch_size_i, self.gan.latent_dims),
                dtype=noisy_batch.dtype,
                device=device,
            )

            current_state = torch.cat((noisy_batch, latent), dim=1)

            noise_pred = self.gan.diffuser(
                current_state, batch["conditions"], timesteps
            )

            loss = F.l1_loss(noise, noise_pred, reduction="mean")  # or mse?

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            self.gan.diffuser.eval()

            self.log("loss", loss, prog_bar=True)

        else:
            optimizer_g, optimizer_d = self.optimizers()
            self.gan.discriminator.train()
            self.gan.generator.eval()

            device = batch["targets"].device
            self.gan.generator.to(device)
            self.gan.discriminator.to(device)

            batch_size_i = int(batch["targets"].shape[0] / 3)

            sample_targets_train_B = batch["targets"][batch_size_i : 2 * batch_size_i]
            sample_conditions_train_A = batch["conditions"][:batch_size_i]
            sample_conditions_train_B = batch["conditions"][
                batch_size_i : 2 * batch_size_i
            ]
            sample_conditions_train_C = batch["conditions"][
                2 * batch_size_i : 3 * batch_size_i
            ]

            # Generate noise and conditions
            noise = torch.randn(batch_size_i, self.models.latent_dims).to(device)
            generated_images = self.gan.generator(noise, sample_conditions_train_A)

            # Concatenate inputs and labels for the discriminator
            in_values = torch.cat([generated_images, sample_targets_train_B], dim=0)
            in_values_labels = torch.cat(
                [sample_conditions_train_A, sample_conditions_train_B], dim=0
            )

            labels_D_0 = torch.zeros(batch_size_i, 1).to(device)
            labels_D_1 = torch.ones(batch_size_i, 1).to(device)
            labels_D = torch.cat([labels_D_0, labels_D_1], dim=0)

            # Discriminator loss
            out_values_choice = self.gan.discriminator(in_values, in_values_labels)
            disc_loss_fn = nn.BCELoss()

            disc_loss = disc_loss_fn(out_values_choice.squeeze(), labels_D.squeeze())

            # Backpropagation for discriminator
            optimizer_d.zero_grad()
            disc_loss.backward()
            optimizer_d.step()

            self.gan.discriminator.eval()
            self.gan.generator.train()

            # Generate noise and conditions for the generator
            noise_stacked = torch.randn(batch_size_i, self.models.latent_dims).to(
                device
            )

            # Generator loss
            fake_images2 = self.gan.generator(noise_stacked, sample_conditions_train_C)
            stacked_output_choice = self.gan.discriminator(
                fake_images2, sample_conditions_train_C
            )
            gen_loss = self._loss_generator(stacked_output_choice.squeeze())

            # Backpropagation for generator
            optimizer_g.zero_grad()
            gen_loss.backward()
            optimizer_g.step()

            self.gan.discriminator.eval()
            self.gan.generator.eval()

            self.log("disc_loss", disc_loss)
            self.log("gen_loss", gen_loss)

    def run_inference(self, batch, test_batch_size):
        reconstructed_graph = self.models.gan.inference(
            test_batch_size,
            batch["conditions"],
        )

        reconstructed_graph = reconstructed_graph.cpu().detach().numpy()

        gen_df_i = pd.DataFrame(
            reconstructed_graph,
            columns=self.targets_graph,
        )

        return gen_df_i

    def create_true_df(self, batch, test_batch_size):
        graph_targets = batch["targets"].cpu().detach().numpy()

        true_df_i = pd.DataFrame(
            graph_targets,
            columns=self.targets_graph,
        )

        return true_df_i

    def on_validation_epoch_start(self):
        print(f"Starting validation for epoch {self.current_epoch}")

    def validation_step(self, batch, batch_idx, dataloader_idx=0):
        test_batch_size = batch["targets"].shape[0]

        gen_df_i = self.run_inference(batch, test_batch_size)

        if batch_idx == 0:
            self.gen_data = gen_df_i
        else:
            self.gen_data = pd.concat((self.gen_data, gen_df_i), axis=0)

        if self.current_epoch == 0:  # TRUE info
            true_df_i = self.create_true_df(batch, test_batch_size)

            if batch_idx == 0:
                self.true_data = true_df_i
            else:
                self.true_data = pd.concat((self.true_data, true_df_i), axis=0)

    def make_plots(self):
        print("Plotting...")
        pdf_name = f"{self.logger.log_dir}/epoch{self.current_epoch}.pdf"

        with PdfPages(pdf_name) as pdf:
            for branch in self.gen_data:
                gen_df = self.gen_data
                # reco_df = self.reco_data
                true_df = self.true_data

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
                pdf.savefig(bbox_inches="tight")
                plt.close()

                plt.title(branch)
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
            return

        print("Saving models...")
        self.models.save(f"{self.logger.log_dir}/models.pkl")

        # Make plots
        self.make_plots()

    def configure_optimizers(self):
        if "diffusion" in self.network_option:
            opt_g = torch.optim.AdamW(
                self.gan.diffuser.parameters(),
                lr=1e-4,
                betas=(0.9, 0.999),
                amsgrad=False,
            )

            return [opt_g], []

        else:
            opt_g = torch.optim.Adam(
                self.gan.generator.parameters(),
                lr=0.0004,
                betas=(0.5, 0.999),
                amsgrad=True,
            )
            opt_d = torch.optim.Adam(
                self.gan.discriminator.parameters(),
                lr=0.0004,
                betas=(0.5, 0.999),
                amsgrad=True,
            )

            return [opt_g, opt_d], []

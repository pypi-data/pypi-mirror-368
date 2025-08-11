import lhcb_rex.settings.globals as myGlobals
import torch
import json

from lhcb_rex.models.hetero_graph_based_GAN import (
    gGAN as hetero_gGAN,
)
from lhcb_rex.models.hetero_graph_based_diffusion_model import (
    diffusion_model,
)
from lhcb_rex.models.hetero_graph_based_GAN_smearing import (
    gGAN as hetero_gGAN_smearing,
)
from lhcb_rex.models.hetero_graph_based_diffusion_model_smearing import (
    diffusion_model_smearing,
)
from lhcb_rex.models.hetero_graph_based_VAE_smearing import (
    VAE_smearing,
)
from lhcb_rex.models.vanilla_GAN import (
    vanillaGAN,
)
from lhcb_rex.models.vanilla_diffusion import (
    vanillaDiffusion,
)
import importlib.resources

from pydantic import BaseModel, validator
from typing import Dict, Optional
import lhcb_rex.processing.transformers as tfs
import pickle
import time
from pathlib import Path
from lhcb_rex.tools.get_weights import HuggingFacePath


class HeteroModelHandler(BaseModel):
    branch_options: Dict = None  # Field(default_factory=dict)
    network_option: str
    load_model: Optional[str] = None
    override_network_params: Optional[str] = None
    gan: Optional[object] = None  # Placeholder for model instance
    Transformers: Optional[dict] = None  # Placeholder for model instance
    model_parameters: Optional[str] = "default_model_parameters.json"
    silent: bool = False
    diffusion_model: Optional[str] = None

    @validator("load_model")
    def validate_load_model(cls, value):
        if value and not (value.endswith(".pickle") or value.endswith(".pkl")):
            raise ValueError("load_model must be a string ending in .pickle or .pkl")
        return value

    @validator("override_network_params")
    def validate_override_network_params(cls, value):
        if value and not value.endswith(".json"):
            raise ValueError("override_network_params must be a string ending in .json")
        return value

    def __init__(self, **data):
        super().__init__(**data)

        if self.branch_options is None:
            self.branch_options = {}
            if "reco_vertex" in self.network_option:
                self.branch_options["mother_targets"] = myGlobals.mother_targets
                self.branch_options["track_targets"] = myGlobals.track_targets
                self.branch_options["mother_conditions"] = myGlobals.mother_conditions
                self.branch_options["track_conditions"] = myGlobals.track_conditions
                self.branch_options["intermediate_targets"] = (
                    myGlobals.intermediate_targets
                )
                self.branch_options["intermediate_conditions"] = (
                    myGlobals.intermediate_conditions
                )
            elif "mom_smear" in self.network_option:
                self.branch_options["track_targets"] = myGlobals.smearing_track_targets
                self.branch_options["track_conditions"] = (
                    myGlobals.smearing_track_conditions
                )
                self.branch_options["edge_conditions"] = (
                    myGlobals.smearing_edge_conditions
                )
            elif "PID_trig" in self.network_option:
                self.branch_options["track_targets"] = myGlobals.PID_track_targets
                self.branch_options["track_conditions"] = myGlobals.PID_track_conditions
                self.branch_options["edge_conditions"] = myGlobals.PID_edge_conditions
            else:
                raise ValueError(
                    f"network_option={self.network_option} not implemented."
                )

        if self.model_parameters is not None:
            model_parameters = self.model_parameters
        with (
            importlib.resources.files("lhcb_rex")
            .joinpath(f"settings/{model_parameters}")
            .open("r") as file
        ):
            network_params = json.load(file)
        if self.override_network_params:
            network_params = json.load(self.override_network_params)

        for option in network_params:
            self.branch_options[option] = network_params[option]

        for option in [
            "mother_targets",
            "intermediate_targets",
            "track_targets",
            "mother_conditions",
            "intermediate_conditions",
            "track_conditions",
        ]:
            try:
                if isinstance(self.branch_options[option], tuple):
                    self.branch_options[option] = self.branch_options[option][0]
            except Exception:
                pass

        if self.network_option in ["mom_smear", "PID_trig"]:
            # add_physics_dims = self.network_option == "mom_smear"
            add_physics_dims = False
            self.gan = hetero_gGAN_smearing(
                track_targets_dims=len(self.branch_options["track_targets"]),
                track_conditions_dims=len(self.branch_options["track_conditions"]),
                hidden_channels=self.branch_options["hidden_channels"],
                track_latent_dims=self.branch_options["track_latent_dims"],
                edge_conditions_dims=len(self.branch_options["edge_conditions"]),
                silent=self.silent,
                # add_MBD=True,
                add_MBD=False,
                add_physics_dims=add_physics_dims,
            )

        elif self.network_option in [
            "mom_smear_diffusion",
            "mom_smear_flowmatching",
            "PID_trig_diffusion",
            "PID_trig_flowmatching",
        ]:
            self.gan = diffusion_model_smearing(
                track_targets_dims=len(self.branch_options["track_targets"]),
                track_conditions_dims=len(self.branch_options["track_conditions"]),
                hidden_channels=self.branch_options["hidden_channels"],
                track_latent_dims=len(self.branch_options["track_targets"]),
                edge_conditions_dims=len(self.branch_options["edge_conditions"]),
                steps=int(self.branch_options["steps"]),
                silent=self.silent,
            )
        elif self.network_option in [
            "reco_vertex_diffusion",
            "reco_vertex_flowmatching",
        ]:
            self.gan = diffusion_model(
                mother_targets_dims=len(self.branch_options["mother_targets"]),
                intermediate_targets_dims=int(
                    len(self.branch_options["intermediate_targets"])
                ),
                track_targets_dims=len(self.branch_options["track_targets"]),
                mother_conditions_dims=len(self.branch_options["mother_conditions"]),
                intermediate_conditions_dims=int(
                    len(self.branch_options["intermediate_conditions"])
                ),
                track_conditions_dims=len(self.branch_options["track_conditions"]),
                hidden_channels=self.branch_options["hidden_channels"],
                mother_latent_dims=len(self.branch_options["mother_targets"]),
                track_latent_dims=len(self.branch_options["track_targets"]),
                intermediate_latent_dims=int(
                    len(self.branch_options["intermediate_targets"])
                ),
                steps=int(self.branch_options["steps"]),
                silent=self.silent,
            )
        elif self.network_option in ["mom_smear_VAE"]:
            self.gan = VAE_smearing(
                track_targets_dims=len(self.branch_options["track_targets"]),
                track_conditions_dims=len(self.branch_options["track_conditions"]),
                hidden_channels=self.branch_options["hidden_channels"],
                track_latent_dims=len(self.branch_options["track_targets"]),
                edge_conditions_dims=len(self.branch_options["edge_conditions"]),
                steps=int(self.branch_options["steps"]),
                silent=self.silent,
            )

        elif self.network_option in ["reco_vertex_diffusion_eGAN"]:
            self.gan = diffusion_model(
                mother_targets_dims=len(self.branch_options["mother_targets"]),
                intermediate_targets_dims=int(
                    len(self.branch_options["intermediate_targets"])
                ),
                track_targets_dims=len(self.branch_options["track_targets"]),
                mother_conditions_dims=len(self.branch_options["mother_conditions"]),
                intermediate_conditions_dims=int(
                    len(self.branch_options["intermediate_conditions"])
                ),
                track_conditions_dims=len(self.branch_options["track_conditions"]),
                hidden_channels=self.branch_options["hidden_channels"],
                mother_latent_dims=len(self.branch_options["mother_targets"]),
                track_latent_dims=len(self.branch_options["track_targets"]),
                intermediate_latent_dims=int(
                    len(self.branch_options["intermediate_targets"])
                ),
                steps=int(self.branch_options["steps"]),
                silent=self.silent,
                eGAN=True,
            )
            try:
                if torch.cuda.is_available():
                    checkpoint = torch.load(self.diffusion_model)
                else:
                    checkpoint = torch.load(
                        self.diffusion_model, map_location=torch.device("cpu")
                    )
            except Exception:
                print(
                    f"WARNING: model ({self.diffusion_model}) not found, waiting 45 seconds and trying again (could be in process of being saved)."
                )
                time.sleep(45)
                checkpoint = torch.load(self.diffusion_model)
            try:
                self.gan.diffuser.load_state_dict(
                    checkpoint["diffuser_state_dict"]
                )  # Load only generator weights
            except Exception as e:  # legacy models
                print(f"{e}: probably legacy model")
                self.gan.diffuser.load_state_dict(
                    checkpoint["generator_state_dict"]
                )  # Load only generator weights
            self.gan.diffuser.eval()
            print(f"Loaded diffuser from {self.diffusion_model}...")

        else:
            self.gan = hetero_gGAN(
                mother_targets_dims=len(self.branch_options["mother_targets"]),
                intermediate_targets_dims=int(
                    len(self.branch_options["intermediate_targets"])
                ),
                track_targets_dims=len(self.branch_options["track_targets"]),
                mother_conditions_dims=len(self.branch_options["mother_conditions"]),
                intermediate_conditions_dims=int(
                    len(self.branch_options["intermediate_conditions"])
                ),
                track_conditions_dims=len(self.branch_options["track_conditions"]),
                hidden_channels=self.branch_options["hidden_channels"],
                mother_latent_dims=self.branch_options["mother_latent_dims"],
                track_latent_dims=self.branch_options["track_latent_dims"],
                intermediate_latent_dims=self.branch_options[
                    "intermediate_latent_dims"
                ],
                silent=self.silent,
            )

        self.gan.to(myGlobals.device)

        if self.load_model is not None:
            self.load(self.load_model)

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

    def save(self, save_loc):
        if (
            "diffusion" in self.network_option or "flowmatching" in self.network_option
        ) and "GAN" not in self.network_option:
            state_dict = {}
            # try:
            #     state_dict["EMAdiffuser_state_dict"] = (
            #         self.gan.EMA_diffuser.ema_model.state_dict()
            #     )
            # except Exception as e:
            #     print(f"EMA not found: {e}")
            #     pass
            state_dict["diffuser_state_dict"] = (
                self.gan.diffuser.state_dict()
            )  # Save only generator weights
            try:
                state_dict["encoder_state_dict"] = self.gan.encoder.state_dict()
            except Exception as e:
                print(f"Encoder not found {e}")
                pass
            state_dict["branch_options"] = self.branch_options
        elif "VAE" in self.network_option:
            state_dict = {
                "encoder_state_dict": self.gan.encoder.state_dict(),  # Save only generator weights
                "decoder_state_dict": self.gan.decoder.state_dict(),  # Save only generator weights
                "branch_options": self.branch_options,
            }
        else:
            state_dict = {
                # "model_state_dict": self.gan.state_dict(),  # Model's parameters
                "generator_state_dict": self.gan.generator.state_dict(),  # Save only generator weights
                "branch_options": self.branch_options,
            }
        torch.save(state_dict, save_loc)
        print(f"Model saved to {save_loc}")

    def load(self, load_loc, silent=False, ema=False):

        if isinstance(load_loc, HuggingFacePath):
            if torch.cuda.is_available():
                checkpoint = torch.load(load_loc.path)
            else:
                checkpoint = torch.load(load_loc.path, map_location=torch.device("cpu"))
            self.gan.diffuser.load_state_dict(checkpoint["model_state_dict"])
            return True

        if not Path(load_loc).exists():
            print(f"WARNING: Unable to load weights from {load_loc}")
            return False

        try:
            if torch.cuda.is_available():
                checkpoint = torch.load(load_loc)
            else:
                checkpoint = torch.load(load_loc, map_location=torch.device("cpu"))
        except Exception:
            print(
                f"WARNING: model ({load_loc}) not found, waiting 45 seconds and trying again (could be in process of being saved)."
            )
            time.sleep(45)
            checkpoint = torch.load(load_loc)

        try:  # for legacy models
            self.gan.load_state_dict(checkpoint["model_state_dict"])
        except Exception:
            if (
                "diffusion" in self.network_option
                or "flowmatching" in self.network_option
            ) and "GAN" not in self.network_option:
                if ema:
                    self.gan.diffuser.load_state_dict(
                        checkpoint["EMAdiffuser_state_dict"]
                    )  # Load only generator weights
                else:
                    self.gan.diffuser.load_state_dict(
                        checkpoint["diffuser_state_dict"]
                    )  # Load only generator weights
                try:
                    self.gan.encoder.load_state_dict(checkpoint["encoder_state_dict"])
                except Exception as e:
                    print(f"Unable to load encoder {e}")
                    pass
            elif "VAE" in self.network_option:
                self.gan.encoder.load_state_dict(checkpoint["encoder_state_dict"])
                self.gan.decoder.load_state_dict(checkpoint["decoder_state_dict"])
            else:
                self.gan.generator.load_state_dict(
                    checkpoint["generator_state_dict"]
                )  # Load only generator weights
        self.branch_options = checkpoint["branch_options"]
        if not silent:
            print(f"Model loaded from {load_loc}")
        return True


class ModelHandler:
    def __init__(
        self,
        branch_options={},
        graphify=True,
        hidden_channels=[256, 512, 256],
        graph_latent_dims=2,
        node_latent_dims=4,
        latent_dims=2,
        extra_latent_dims=0,
        beta=80.0,  # 60.
        lr=0.0001,
        N_graph_layers=3,
        use_batch_norm=False,
        use_dropout=False,
        load_loc=None,
        load_network_params=None,
        use_a_GAN=False,
        hypergraphs=False,
        silent=False,
        network_option="",
    ):
        self.silent = silent
        self.branch_options = branch_options
        if self.branch_options == {}:
            self.branch_options["targets_graph"] = myGlobals.smearPV_targets
            self.branch_options["conditions_graph"] = myGlobals.smearPV_conditions

        self.options = {
            "graphify": graphify,
            "hidden_channels": hidden_channels,
            "graph_latent_dims": graph_latent_dims,
            "node_latent_dims": node_latent_dims,
            "latent_dims": latent_dims,
            "extra_latent_dims": extra_latent_dims,
            "beta": beta,  # 60.
            "lr": lr,
            "N_graph_layers": N_graph_layers,
            "use_batch_norm": use_batch_norm,
            "use_dropout": use_dropout,
        }

        self.hidden_channels = self.options["hidden_channels"]
        self.graph_latent_dims = self.options["graph_latent_dims"]
        self.node_latent_dims = self.options["node_latent_dims"]
        self.N_graph_layers = self.options["N_graph_layers"]
        self.use_batch_norm = self.options["use_batch_norm"]
        self.use_dropout = self.options["use_dropout"]
        self.latent_dims = self.options["latent_dims"]
        self.extra_latent_dims = self.options["extra_latent_dims"]
        self.beta = self.options["beta"]
        self.lr = self.options["lr"]
        self.graphify = self.options["graphify"]

        self.loss_fn = torch.nn.MSELoss()

        if load_loc is not None:
            self.load_branch_options(load_loc)

        if load_network_params is not None:
            with open(load_network_params) as json_file:
                network_params = json.load(json_file)
            for option in network_params:
                self.options[option] = network_params[option]

        # print(self.options)
        self.options["targets_graph"] = self.branch_options["targets_graph"]
        self.options["conditions_graph"] = self.branch_options["conditions_graph"]

        if "diffusion" in network_option:
            self.gan = vanillaDiffusion(
                targets_dims=len(self.options["targets_graph"]),
                conditions_dims=len(self.options["conditions_graph"]),
                hidden_channels=self.options["hidden_channels"],
                latent_dims=self.extra_latent_dims,
                silent=self.silent,
            )

        else:
            self.gan = vanillaGAN(
                targets_dims=len(self.options["targets_graph"]),
                conditions_dims=len(self.options["conditions_graph"]),
                hidden_channels=self.options["hidden_channels"],
                latent_dims=self.options["latent_dims"] + self.extra_latent_dims,
                silent=self.silent,
            )

        self.optimizer = torch.optim.Adam(self.gan.parameters(), lr=self.lr)
        # self.gan.to(myGlobals.device)

        self.beta = self.options["beta"]
        self.graphify = self.options["graphify"]

        if load_loc is not None:
            self.load(load_loc)

    def save(self, save_loc):
        state_dict = {
            "model_state_dict": self.gan.state_dict(),  # Model's parameters
            "branch_options": self.branch_options,
        }
        torch.save(state_dict, save_loc)
        print(f"Model saved to {save_loc}")

    def load(self, load_loc, silent=False):

        if isinstance(load_loc, HuggingFacePath):
            if torch.cuda.is_available():
                checkpoint = torch.load(load_loc.path)
            else:
                checkpoint = torch.load(load_loc.path, map_location=torch.device("cpu"))
            self.gan.load_state_dict(checkpoint["model_state_dict"])
            return True

        if not Path(load_loc).exists():
            print(f"WARNING: Unable to load weights from {load_loc}")
            return False

        try:
            if torch.cuda.is_available():
                checkpoint = torch.load(load_loc)
            else:
                checkpoint = torch.load(load_loc, map_location=torch.device("cpu"))
        except Exception:
            print(
                f"WARNING: model ({load_loc}) not found, waiting 45 seconds and trying again (could be in process of being saved)."
            )
            time.sleep(45)
            checkpoint = torch.load(load_loc)

        self.gan.load_state_dict(checkpoint["model_state_dict"])
        self.branch_options = checkpoint["branch_options"]
        if not silent:
            print(f"Model loaded from {load_loc}")

        return True

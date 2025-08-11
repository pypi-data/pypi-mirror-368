import lhcb_rex.settings.globals as myGlobals
from pydantic import BaseModel, validator, root_validator
import glob
import lhcb_rex.training.dataloader_handler as dh
import lhcb_rex.models.model_handler as model_handler
import lhcb_rex.training.hetero_trainer as trainer
import lhcb_rex.training.trainer as stdtrainer
from pytorch_lightning.loggers import TensorBoardLogger
from typing import Union, Any, Dict
from pytorch_lightning import Trainer
from lhcb_rex.data.data_handler import DataHandler
import torch_geometric
from pytorch_lightning.utilities.combined_loader import CombinedLoader


class FastSimTrainer(BaseModel):
    gpu: int = 5
    batch_size: int = 256
    use_weights: bool = False
    load_physics_validation: bool = True
    data_locs: Union[
        Union[str, Dict[str, str]],  # single string path
        Dict[str, Dict[str, Union[str, int]]],  # dict with path + batch_size
    ]

    model_parameters: str = "default_model_parameters.json"
    network: str
    logs_dir: str = "/users/am13743/Rex/logs"
    log_tag: str
    diffusion_model: str = None

    # # placeholders
    dataloaders: Any = None
    val_dataloaders: Any = None
    trainer: Any = None
    TrainerModule: Any = None
    logger: Any = None
    Model: Any = None
    extra_val_data_locs: Any = None

    @root_validator(pre=True)
    def validate_data_locs(cls, values):
        network = values.get("network", None)
        data_locs = values.get("data_locs", None)
        extra_val_data_locs = values.get("extra_val_data_locs", None)

        if "PV_smear" in network:
            if not isinstance(data_locs, str):
                raise ValueError(
                    f"For network={network} need data_locs to be a string (.root)"
                )
            if data_locs and not data_locs.endswith(".root"):
                raise ValueError(
                    f"For network={network} need data_locs to be a .root file"
                )
        else:
            if not isinstance(data_locs, dict):
                raise ValueError(f"For network={network} need data_locs to be a dict")

            for data_item, loc in data_locs.items():
                if isinstance(loc, dict):
                    loc = loc["loc"]
                if len(glob.glob(f"{loc}/*")) == 0:
                    raise ValueError(f"need a processed directory in {loc}")
                if glob.glob(f"{loc}/*")[0].split("/")[-1] != "processed":
                    raise ValueError(f"need a processed directory in {loc}")
                files = glob.glob(f"{loc}/processed/data_*.pt")
                files = [i for i in files if "_val_" not in i]
                if len(files) == 0:
                    raise ValueError(f"no data_*.pt files in {loc}/processed/")

        return values

    @validator("model_parameters")
    def validate_model_parameters(cls, value):
        if value and not value.endswith(".json"):
            raise ValueError("model_parameters must be a string ending in .json")
        return value

    @validator("network")
    def validate_network(cls, value):
        network_options = [
            "PV_smear",
            "PV_smear_diffusion",
            "mom_smear",
            "mom_smear_diffusion",
            "mom_smear_VAE",
            "PID_trig",
            "PID_trig_diffusion",
            "reco_vertex",
            "reco_vertex_diffusion",
            "reco_vertex_diffusion_eGAN",
            "mom_smear_flowmatching",
            "PID_trig_flowmatching",
            "reco_vertex_flowmatching",
        ]
        if value not in network_options:
            raise ValueError(f"network option must be one of: {network_options}")
        return value

    def __init__(self, **data):
        super().__init__(**data)

        print(f"Training on gpu {self.gpu}")

        if "PV_smear" in self.network:
            data_handler = DataHandler(
                particles_involved=[1],
                path=self.data_locs,
                N=-1,
                targets_graph=myGlobals.smearPV_targets,
                conditions_graph=myGlobals.smearPV_conditions,
                cut="abs(MOTHER_TRUEID)==521 and MOTHER_TRUEP_Z>0",
            )

            data_train, data_test, data_test_raw, test_batch_size = (
                data_handler.get_loaders(batch_size=self.batch_size)
            )

            branch_options = {}
            branch_options["targets_graph"] = myGlobals.smearPV_targets
            branch_options["conditions_graph"] = myGlobals.smearPV_conditions

            if "diffusion" in self.network:
                self.Model = model_handler.ModelHandler(
                    branch_options=branch_options,
                    graphify=False,
                    hidden_channels=[256, 512, 256],
                    latent_dims=len(myGlobals.smearPV_targets),
                    extra_latent_dims=3,
                    beta=80.0,
                    lr=0.0001,
                    network_option=self.network,
                )

            else:
                self.Model = model_handler.ModelHandler(
                    branch_options=branch_options,
                    graphify=False,
                    hidden_channels=[256, 512, 256],
                    latent_dims=25,
                    beta=80.0,
                    lr=0.0001,
                    network_option=self.network,
                )

            self.TrainerModule = stdtrainer.StdTrainerModule(
                self.Model,
                data_train,
                data_test,
                network_option=self.network,
            )

            self.dataloaders = data_train
            self.val_dataloaders = data_test

        else:
            settings = {}
            for data_item, loc_item in self.data_locs.items():
                if isinstance(loc_item, dict):
                    loc = loc_item["loc"]
                else:
                    loc = loc_item
                files = glob.glob(f"{loc}/processed/data_*.pt")
                files = [i for i in files if "_val_" not in i]
                files = [int(file.split("_")[-1].split(".")[0]) for file in files]
                # splits = len(files)
                splits = max(files) + 1
                if "batch_size" in loc_item:
                    settings[data_item] = dh.create_settings(
                        loc, splits=splits, batch_size=loc_item["batch_size"]
                    )
                else:
                    settings[data_item] = dh.create_settings(loc, splits=splits)

            if self.network == "reco_vertex":
                self.dataloaders, self.val_dataloaders, branch_options = dh.get_loaders(
                    settings,
                    batch_size=self.batch_size,
                    verbose=True,
                    use_weights=self.use_weights,
                    load_physics_validation=self.load_physics_validation,
                )
            elif self.network == "reco_vertex_diffusion":
                enhance_fully_reco = 1.
                # enhance_fully_reco = 100.
                # enhance_fully_reco = 250.0
                self.dataloaders, self.val_dataloaders, branch_options = dh.get_loaders(
                    settings,
                    batch_size=self.batch_size,
                    verbose=True,
                    use_weights=self.use_weights,
                    enhance_fully_reco=enhance_fully_reco,
                    extra_val_data_locs=self.extra_val_data_locs,
                )

                keys_to_keep = [
                    # 'N3_topIdx2',
                    "N3_topIdx1",
                    # 'N3_topIdx1_conditionless',
                    "N3_topIdx1_Kee_N3_topIdx1",
                ]
                self.val_dataloaders = {
                    k: self.val_dataloaders[k]
                    for k in keys_to_keep
                    if k in self.val_dataloaders
                }

            else:
                self.dataloaders, self.val_dataloaders, branch_options = dh.get_loaders(
                    settings,
                    batch_size=self.batch_size,
                    verbose=True,
                    use_weights=self.use_weights,
                )
            
            self.Model = model_handler.HeteroModelHandler(
                branch_options=branch_options,
                network_option=self.network,
                model_parameters=self.model_parameters,
                diffusion_model=self.diffusion_model,
            )

            if self.network == "reco_vertex_diffusion":
                self.TrainerModule = trainer.TrainerModule(
                    self.Model,
                    self.dataloaders,
                    self.val_dataloaders,
                    training_batch_size=self.batch_size,
                    save_models=True,
                    use_weights=self.use_weights,
                    network_option=self.network,
                    enhance_fully_reco=enhance_fully_reco,
                )
            else:
                self.TrainerModule = trainer.TrainerModule(
                    self.Model,
                    self.dataloaders,
                    self.val_dataloaders,
                    training_batch_size=self.batch_size,
                    save_models=True,
                    use_weights=self.use_weights,
                    network_option=self.network,
                )

        self.logger = TensorBoardLogger(self.logs_dir, name=self.log_tag)

    def fit(
        self,
        max_epochs=int(1e30),
        val_check_interval=None,
        test_validation=False,
        pre_load=None,
        cap_validation=-1,
        load_ema=False,
    ):
        self.trainer = Trainer(
            max_epochs=max_epochs,
            accelerator="gpu",
            devices=[self.gpu],
            logger=self.logger,
            val_check_interval=val_check_interval,
            enable_checkpointing=False,  # Disable automatic checkpoint saving - models saved in TrainerModule() at end of epochs (save_models=True)
            log_every_n_steps=5,
        )
        # min_size
        # max_size_cycle

        if pre_load:
            print(f"Loading {pre_load}...")
            self.Model.load(pre_load, ema=load_ema)

        if cap_validation > 0 and "PV_smear" not in self.network:
            for name, dataloader in self.val_dataloaders.items():
                dataset = dataloader.dataset
                num_samples = len(dataset)
                print(f"{name}: {num_samples} samples")
                if num_samples > cap_validation:
                    print(f"  -> Capping {name} at {cap_validation} samples")
                    # Truncate the dataset
                    truncated_dataset = dataset[:cap_validation]
                    # Re-create the dataloader with the truncated dataset
                    self.val_dataloaders[name] = torch_geometric.loader.DataLoader(
                        truncated_dataset,
                        batch_size=dataloader.batch_size,
                    )
            for name, dataloader in self.val_dataloaders.items():
                dataset = dataloader.dataset
                num_samples = len(dataset)
                print(f"{name}: {num_samples} samples")

        if test_validation:
            self.trainer.initialisation = False
            self.trainer.validate(self.TrainerModule, self.val_dataloaders)
            # self.trainer.validate(self.TrainerModule, self.dataloaders)
            if "smear" in self.network:
                self.TrainerModule.make_plots_smearingnet()
            else:
                self.TrainerModule.make_plots()
            self.TrainerModule.BDT_FoM()
            quit()

        self.dataloaders = CombinedLoader(self.dataloaders, mode="min_size")
        # self.dataloaders = CombinedLoader(self.dataloaders, mode='max_size_cycle')
        # min_size
        # max_size_cycle

        self.trainer.fit(
            self.TrainerModule, self.dataloaders, val_dataloaders=self.val_dataloaders
        )

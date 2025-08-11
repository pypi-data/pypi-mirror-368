import lhcb_rex.data.graph_maker as graph_maker
from torch_geometric.loader import DataLoader
from torch.utils.data import Subset
from pydantic import BaseModel, Field
from typing import Dict
from rich import print
from torch.utils.data import WeightedRandomSampler
import os
import torch


class SettingConfig(BaseModel):
    file_name: str
    splits: int = Field(gt=0, description="Number of splits, must be > 0")
    batch_size: int = None


def create_settings(file: str, splits: int, batch_size: int = None) -> SettingConfig:
    """Helper function to create a settings configuration."""
    return SettingConfig(
        file_name=file,
        splits=splits,
        batch_size=batch_size,
    )


class DataLoaderSettings(BaseModel):
    settings: Dict[str, SettingConfig]


def get_loaders(
    settings: DataLoaderSettings,
    batch_size: int = 256,
    batch_size_val: int = -1,
    verbose: bool = False,
    use_weights: bool = False,
    load_physics_validation: bool = False,
    enhance_fully_reco=1.0,
    extra_val_data_locs=None,
):
    if batch_size_val == -1:
        batch_size_val = batch_size

    dataloaders = {}
    val_dataloaders = {}

    training_info = {}
    training_info["path"] = []
    training_info["particles_involved"] = []

    for setting in settings:
        root = settings[setting].file_name

        if settings[setting].batch_size:
            batch_size_to_use = settings[setting].batch_size
        else:
            batch_size_to_use = batch_size

        dataset = graph_maker.GENERALISED_HeteroGraphDataset(
            # config='/users/am13743/Rex/davinci/configs/configs_2_body/config_dict_B0_AAA+BBB-.pickle',
            root=root,
            mode="train",
            # max_N_samples_per=-1,
            splits=settings[setting].splits,
            use_weights=use_weights,
        )

        fully_reco_enhancement = [
            enhance_fully_reco if x == 1.0 else 1.0
            for x in dataset.options["fully_reco_bool"]
        ]
        dataloader = DataLoader(dataset, batch_size=batch_size_to_use, shuffle=True)
        if use_weights:
            weights = dataset.options["training_weights"]
            if enhance_fully_reco > 1.0:
                weights = torch.multiply(weights, fully_reco_enhancement)
            sampler = WeightedRandomSampler(
                weights, num_samples=len(weights), replacement=True
            )
            dataloader = DataLoader(
                dataset, batch_size=batch_size_to_use, sampler=sampler
            )
        else:
            if enhance_fully_reco > 1.0:
                sampler = WeightedRandomSampler(
                    fully_reco_enhancement,
                    num_samples=len(fully_reco_enhancement),
                    replacement=True,
                )
                dataloader = DataLoader(
                    dataset, batch_size=batch_size_to_use, sampler=sampler
                )
            else:
                dataloader = DataLoader(
                    dataset, batch_size=batch_size_to_use, shuffle=True
                )

        dataloaders[setting] = dataloader

        branch_options = dataset.options

        if branch_options != dataset.options:
            raise ValueError(
                "Attempt was made to load datasets with differing options/branches."
            )

        # print(branch_options.keys())
        # print(branch_options['settings'])
        # quit()

        training_info["path"].append(branch_options["path"])
        # training_info["particles_involved"].append(branch_options["particles_involved"])
        training_info["particles_involved"] = [
            i for i in branch_options["settings"]["branches"].keys() if "DAUGHTER" in i
        ]

        print(root)
        dataset = graph_maker.GENERALISED_HeteroGraphDataset(
            root=root,
            mode="test",
            # max_N_samples_per=-1,
            splits=settings[setting].splits,
            use_weights=False,
        )
        dataloader = DataLoader(dataset, batch_size=batch_size_val, shuffle=False)
        val_dataloaders[setting] = dataloader

    if extra_val_data_locs:
        for setting in extra_val_data_locs:
            dataset = graph_maker.GENERALISED_HeteroGraphDataset(
                root=extra_val_data_locs[setting]["loc"],
                mode="test",
                splits=1,
                use_weights=False,
            )
            dataloader = DataLoader(dataset, batch_size=256, shuffle=False)
            val_dataloaders[setting] = dataloader

    if load_physics_validation:
        root_dir = os.path.dirname(root)
        dataset = graph_maker.HeteroGraphDataset(
            root=f"{root_dir}/graphs_3_int_fullrecosequentialValidationKee_PID",
            mode="train",
            max_N_samples_per=-1,
            splits=1,
            use_weights=False,
        )
        subset_dataset = Subset(dataset, range(min(25000, len(dataset))))
        dataloader = DataLoader(subset_dataset, batch_size=256, shuffle=False)
        val_dataloaders["physics_Kee_3"] = dataloader

        root_dir = os.path.dirname(root)
        dataset = graph_maker.HeteroGraphDataset(
            root=f"{root_dir}/graphs_3_int_fullrecosequentialValidationKstee_PID",
            mode="train",
            max_N_samples_per=-1,
            splits=1,
            use_weights=False,
        )
        subset_dataset = Subset(dataset, range(min(25000, len(dataset))))
        dataloader = DataLoader(subset_dataset, batch_size=256, shuffle=False)
        val_dataloaders["physics_Kstee_3"] = dataloader

        root_dir = os.path.dirname(root)
        dataset = graph_maker.HeteroGraphDataset(
            root=f"{root_dir}/graphs_3_int_fullrecosequentialValidationBuD0piKenu_PID",
            mode="train",
            max_N_samples_per=-1,
            splits=1,
            use_weights=False,
        )
        subset_dataset = Subset(dataset, range(min(25000, len(dataset))))
        dataloader = DataLoader(subset_dataset, batch_size=256, shuffle=False)
        val_dataloaders["physics_BuD0piKenu_3"] = dataloader

        root_dir = os.path.dirname(root)
        dataset = graph_maker.HeteroGraphDataset(
            root=f"{root_dir}/graphs_3_int_fullrecosequentialValidationKmumu_PID",
            mode="train",
            max_N_samples_per=-1,
            splits=1,
            use_weights=False,
        )
        subset_dataset = Subset(dataset, range(min(25000, len(dataset))))
        dataloader = DataLoader(subset_dataset, batch_size=256, shuffle=False)
        val_dataloaders["physics_Kmumu_3"] = dataloader

        # root_dir = os.path.dirname(root)
        # dataset = graph_maker.HeteroGraphDataset(
        #     root=f'{root_dir}/graphs_3_int_fullrecoValidationKJpsiee',
        #     mode="train",
        #     max_N_samples_per=-1,
        #     splits=1,
        #     use_weights=False,
        # )
        # dataloader = DataLoader(dataset, batch_size=256, shuffle=False)
        # val_dataloaders["physics_KJpsiee_3"] = dataloader

    branch_options["path"] = training_info["path"]
    branch_options["particles_involved"] = training_info["particles_involved"]

    if verbose:
        for option in branch_options:
            if option != "training_weights" and option != "fully_reco_bool":
                print("\n\n", option, "\n", branch_options[option])

    return dataloaders, val_dataloaders, branch_options

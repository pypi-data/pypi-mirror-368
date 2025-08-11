import lhcb_rex.settings.globals as myGlobals
from pydantic import BaseModel, validator
import lhcb_rex.models.model_handler as model_handler
from typing import Any
import lhcb_rex.processing.transformers as tfs
import pickle
import importlib.resources
import re
import torch
import pandas as pd
from rich import print
import numpy as np
import itertools
import lhcb_rex.tools.display as display
from diffusers import DDPMScheduler
from typing import Union
from lhcb_rex.tools.get_weights import HuggingFacePath

class DataContainer:
    def __init__(self):
        self.x = None
        self.data = {}

    def __setattr__(self, key, value):
        if key in ["x", "data"]:
            super().__setattr__(key, value)
        else:
            self.data[key] = value

    def __getattr__(self, key):
        if key in self.data:
            return self.data[key]
        raise AttributeError(f"'DataContainer' object has no attribute '{key}'")

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __contains__(self, key):
        return key in self.data


def batchify(edge, single_graph, batch_size, N_nodes=None):
    origin_N = N_nodes[edge[0]]
    destin_N = N_nodes[edge[-1]]

    batched_edges = []

    for i in range(batch_size):
        offset_origin = i * origin_N  # Shift nodes for each graph
        offset_destin = i * destin_N  # Shift nodes for each graph

        single_graph_offset = single_graph.clone()
        single_graph_offset[0] += offset_origin
        single_graph_offset[1] += offset_destin

        batched_edges.append(single_graph_offset)

    return torch.cat(batched_edges, dim=1)  # Concatenate along columns


class Network(BaseModel):
    network: str
    model_parameters: str = "default_model_parameters.json"
    pkl: Union[str, HuggingFacePath]
    Nparticles: int
    physical_units: str = "GeV"
    daughter_particle_names: list
    transformer_file: str = "transfomer_quantiles.pkl"
    EMA: bool = False
    N_diffusion_steps: int = 25

    Transformers: Any = None
    Model: Any = None
    conditions: Any = None
    edge_conditions: Any = None
    transformers: Any = None  # personalised
    edge_transformers: Any = None  # personalised
    query_network: Any = None
    targets: Any = None
    targets_full: Any = None

    mother_targets: Any = None
    intermediate_targets: Any = None
    track_targets: Any = None
    mother_conditions: Any = None
    intermediate_conditions: Any = None
    track_conditions: Any = None

    internal_daughter_particle_names: Any = None
    intermediate_particle_name: Any = None

    class Config:
        arbitrary_types_allowed = True

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
            "PID_trig",
            "reco_vertex",
            "reco_vertex_diffusion",
            "mom_smear_diffusion",
            "PID_trig_diffusion",
            "mom_smear_flowmatching",
            "PID_trig_flowmatching",
            "reco_vertex_flowmatching",
        ]
        if value not in network_options:
            raise ValueError(f"network option must be one of: {network_options}")
        return value

    @validator("pkl")
    def validate_pkl(cls, value):
        if isinstance(value, HuggingFacePath): return value
        if not value.endswith(".pkl") and not value.endswith(".pickle"):
            raise ValueError("pkl should point to a pickle of network state")
        return value

    def rapidsimify_branches(self, branches):
        branches_prime = []
        for branch in branches:
            if match := re.search(r"_(TRUEP)(_?[A-Z]?)$", branch):
                replacement = f"_P{match.group(2).replace('_', '')}_TRUE"
                branches_prime.append(re.sub(r"_TRUEP(_?[A-Z]?)$", replacement, branch))
            elif match := re.search(r"_(TRUEE)(_?[A-Z]?)$", branch):
                replacement = f"_E{match.group(2).replace('_', '')}_TRUE"
                branches_prime.append(re.sub(r"_TRUEE(_?[A-Z]?)$", replacement, branch))
            elif match := re.search(r"_(TRUEENDVERTEX)(_?[A-Z]?)$", branch):
                replacement = f"_vtx{match.group(2).replace('_', '')}_TRUE"
                branches_prime.append(
                    re.sub(r"_(TRUEENDVERTEX)(_?[A-Z]?)$", replacement, branch)
                )
            elif match := re.search(r"_(TRUEORIGINVERTEX)(_?[A-Z]?)$", branch):
                replacement = f"_orig{match.group(2).replace('_', '')}_TRUE"
                branches_prime.append(
                    re.sub(r"_(TRUEORIGINVERTEX)(_?[A-Z]?)$", replacement, branch)
                )
            else:
                branches_prime.append(branch)
        return branches_prime

    def mom_branch_filter(self, branch):
        if re.search(r"delta_P[A-Z]", branch):
            return True
        if branch.endswith("TRUEP"):
            return True
        if branch.endswith("_P"):
            return True
        if branch.endswith("_PT"):
            return True
        if branch.endswith("_TRUEE"):
            return True
        if branch.endswith("_missing_P"):
            return True
        if branch.endswith("_missing_PT"):
            return True
        if re.search(r"TRUEP_[A-Z]", branch):
            return True
        if (
            re.search(r"_P[A-Z]", branch)
            and "PID" not in branch
            and "frac" not in branch
        ):
            return True
        if branch.endswith("_M"):
            return True
        if branch.endswith("_M_reco"):
            return True
        if branch.endswith("_mass"):
            return True
        if re.search(r"deltaEV_[A-Z]", branch):
            return True
        else:
            return False

    def load_transformers(self):
        transformer_quantiles = pickle.load(
            importlib.resources.files("lhcb_rex")
            .joinpath(f"processing/{self.transformer_file}")
            .open("rb")
        )
        min_maxes = pickle.load(
            importlib.resources.files("lhcb_rex")
            .joinpath("processing/min_maxes.pkl")
            .open("rb")
        )
        self.Transformers = {}
        for i, (key, quantiles) in enumerate(transformer_quantiles.items()):
            if "reco_vertex" in self.network or "PV_smear" in self.network:
                transformer_i = tfs.UpdatedTransformer(
                    min_maxes=min_maxes, use_min_max_for_mom_deltas=False
                )
            else:
                transformer_i = tfs.UpdatedTransformer(
                    min_maxes=min_maxes, use_min_max_for_mom_deltas=True
                )

            unit_converter = 1.0
            if self.physical_units == "GeV":
                if self.mom_branch_filter(key):
                    unit_converter = 1000.0  # 1000. means that this transformer (that was fit to MeV MC) will transform GeV branches - transformer(data*unit_converter)

            transformer_i.fit(quantiles, key, unit_converter=unit_converter)
            self.Transformers[key] = transformer_i

        return self.Transformers

    def initialise_PV_smearer(self):
        if "diffusion" in self.network:
            self.Model = model_handler.ModelHandler(
                graphify=False,
                hidden_channels=[256, 512, 256],
                latent_dims=len(myGlobals.smearPV_targets),
                extra_latent_dims=3,
                beta=80.0,
                lr=0.0001,
                silent=True,
                network_option=self.network,
            )
            success = self.Model.load(self.pkl, silent=True)
            if success:
                if isinstance(self.pkl, HuggingFacePath):
                    display.info_print(f"Model loaded from {self.pkl.path}")
                else:
                    display.info_print(f"Model loaded from {self.pkl}")
            self.Model.gan.diffuser.eval()
        else:
            self.Model = model_handler.ModelHandler(
                graphify=False,
                hidden_channels=[256, 512, 256],
                latent_dims=25,
                beta=80.0,
                lr=0.0001,
                silent=True,
                network_option=self.network,
            )
            success = self.Model.load(self.pkl, silent=True)
            if success:
                if isinstance(self.pkl, HuggingFacePath):
                    display.info_print(f"Model loaded from {self.pkl.path}")
                else:
                    display.info_print(f"Model loaded from {self.pkl}")
            self.Model.gan.generator.eval()
            self.Model.gan.discriminator.eval()

        self.transformers = self.Transformers

        targets_raw = self.Model.branch_options["targets_graph"]
        self.targets = self.rapidsimify_branches(targets_raw)
        for idx, target in enumerate(self.targets):
            self.transformers[target] = self.transformers[targets_raw[idx]]

        conditions_raw = self.Model.branch_options["conditions_graph"]
        self.conditions = self.rapidsimify_branches(conditions_raw)

        for idx, cond in enumerate(self.conditions):
            self.transformers[cond] = self.transformers[conditions_raw[idx]]
        self.query_network = self.query_network_vanilla

    def initialise_hetero_model(self):
        Model = model_handler.HeteroModelHandler(
            network_option=self.network,
            model_parameters=self.model_parameters,
            silent=True,
        )
        success = Model.load(self.pkl, silent=True, ema=self.EMA)
        if success:
            if isinstance(self.pkl, HuggingFacePath):
                display.info_print(f"Model loaded from {self.pkl.path}")
            else:
                display.info_print(f"Model loaded from {self.pkl}, ema:{self.EMA}")


        if "diffusion" not in self.network and "flowmatching" not in self.network:
            Model.gan.generator.eval()
            Model.gan.discriminator.eval()
        else:
            Model.gan.diffuser.eval()

        return Model

    def initialise_unique_node_hetero_model(self):
        self.targets = self.Model.branch_options["track_targets"]
        conditions_raw = self.Model.branch_options["track_conditions"]
        conditions = self.rapidsimify_branches(conditions_raw)
        self.Model.branch_options["edge_conditions"] = self.Model.branch_options[
            "edge_conditions"
        ][0]
        edge_conditions = self.Model.branch_options["edge_conditions"]
        if not isinstance(edge_conditions, list): 
            edge_conditions = [edge_conditions]

        self.transformers = self.Transformers

        self.conditions = []
        for particle in self.internal_daughter_particle_names:
            for cond in conditions:
                self.conditions.append(cond.replace("DAUGHTERN", particle))

        self.targets_full = []
        for particle in self.internal_daughter_particle_names:
            for targ in self.targets:
                self.targets_full.append(targ.replace("DAUGHTERN", particle))

        self.edge_conditions = []
        self.edge_transformers = {}
        for i in range(self.Nparticles):
            for j in range(self.Nparticles):
                if i != j:
                    for cond in edge_conditions:
                        self.edge_conditions.append(
                            cond.replace(
                                "DAUGHTERN_DAUGHTERN",
                                f"{self.internal_daughter_particle_names[i]}_{self.internal_daughter_particle_names[j]}",
                            )
                        )
                        self.edge_transformers[
                            cond.replace(
                                "DAUGHTERN_DAUGHTERN",
                                f"{self.internal_daughter_particle_names[i]}_{self.internal_daughter_particle_names[j]}",
                            )
                        ] = self.transformers[cond]

        for idx, cond in enumerate(conditions):
            for i in range(self.Nparticles):
                self.transformers[
                    cond.replace("DAUGHTERN", self.internal_daughter_particle_names[i])
                ] = self.transformers[
                    conditions_raw[idx].replace("DAUGHTERN", "DAUGHTER1")
                ]

        self.query_network = self.query_network_smearing

    def vtx_get_conditional_variables(self):
        mother_conditions = self.rapidsimify_branches(
            self.Model.branch_options["mother_conditions"]
        )
        for idx, cond in enumerate(mother_conditions):
            if cond != "N_daughters":
                self.transformers[cond] = self.transformers[
                    self.Model.branch_options["mother_conditions"][idx]
                ]

        intermediate_conditions = self.rapidsimify_branches(
            self.Model.branch_options["intermediate_conditions"]
        )
        for idx, cond in enumerate(intermediate_conditions):
            if cond != "N_daughters":
                self.transformers[cond] = self.transformers[
                    self.Model.branch_options["intermediate_conditions"][idx].replace(
                        "INTERMEDIATE", "MOTHER"
                    )
                ]

        track_conditions = self.rapidsimify_branches(
            self.Model.branch_options["track_conditions"]
        )
        for idx, cond in enumerate(track_conditions):
            self.transformers[cond.replace("DAUGHTERN", "DAUGHTER1")] = (
                self.transformers[
                    self.Model.branch_options["track_conditions"][idx].replace(
                        "DAUGHTERN", "DAUGHTER1"
                    )
                ]
            )
        return mother_conditions, intermediate_conditions, track_conditions

    def __init__(self, **data):
        super().__init__(**data)

        self.Transformers = self.load_transformers()

        self.internal_daughter_particle_names = list(
            myGlobals.particle_map["fromDAUGHTERS"].keys()
        )
        self.intermediate_particle_name = list(
            myGlobals.particle_map["fromINTERMEDIATES"].keys()
        )

        if "PV_smear" in self.network:
            self.initialise_PV_smearer()
        else:
            self.Model = self.initialise_hetero_model()

            if self.network in [
                "mom_smear",
                "PID_trig",
                "mom_smear_diffusion",
                "PID_trig_diffusion",
                "mom_smear_flowmatching",
                "PID_trig_flowmatching",
            ]:
                self.initialise_unique_node_hetero_model()

            elif "reco_vertex" in self.network:
                self.transformers = self.Transformers

                ##### Organise lists of conditional objects

                self.mother_conditions, intermediate_conditions, track_conditions = (
                    self.vtx_get_conditional_variables()
                )

                self.intermediate_conditions = []
                self.track_conditions = []

                for intermediate in self.intermediate_particle_name:
                    for cond in intermediate_conditions:
                        self.intermediate_conditions.append(
                            cond.replace("INTERMEDIATE", intermediate)
                        )

                for track in self.internal_daughter_particle_names:
                    for cond in track_conditions:
                        self.track_conditions.append(cond.replace("DAUGHTERN", track))

                self.mother_targets = self.Model.branch_options["mother_targets"]
                self.intermediate_targets = []
                self.track_targets = []

                for intermediate in self.intermediate_particle_name:
                    for target in self.Model.branch_options["intermediate_targets"]:
                        self.intermediate_targets.append(
                            target.replace("INTERMEDIATE", intermediate)
                        )

                for track in self.internal_daughter_particle_names:
                    for target in self.Model.branch_options["track_targets"]:
                        self.track_targets.append(target.replace("DAUGHTERN", track))

                ##### Then add transformers

                for track in self.internal_daughter_particle_names:
                    for idx, cond in enumerate(
                        track_conditions + self.Model.branch_options["track_targets"]
                    ):
                        if "DAUGHTERN" in cond:
                            self.transformers[cond.replace("DAUGHTERN", track)] = (
                                self.transformers[
                                    cond.replace("DAUGHTERN", "DAUGHTER1")
                                ]
                            )

                for inter in self.intermediate_particle_name:
                    for cond in self.intermediate_conditions:
                        if "INTERMEDIATE" in cond:
                            pattern = r"INTERMEDIATE\d*"
                            mother_key = re.sub(pattern, "MOTHER", cond)
                            inter_key = re.sub(pattern, inter, cond)
                            self.transformers[inter_key] = self.transformers[mother_key]

                    for targ in self.intermediate_targets:
                        if "INTERMEDIATE" in targ:
                            pattern = r"INTERMEDIATE\d*"
                            mother_key = re.sub(pattern, "MOTHER", targ)
                            inter_key = re.sub(pattern, inter, targ)
                            self.transformers[inter_key] = self.transformers[mother_key]

                # self.query_network = self.query_network_vtx

    def gen_latent(self, chunks, Nparticles):
        # Generate latent noise tensor
        mother_noise = []
        intermediate_noise = []
        track_noise = []
        for i in range(len(chunks)):
            mother_noise.append(np.random.normal(
                0,
                1,
                size=(
                    np.shape(chunks[i])[0],
                    self.Model.gan.mother_latent_dims,
                ),
            ))

            intermediate_noise.append(np.random.normal(
                0,
                1,
                size=(
                    np.shape(chunks[i])[0],
                    self.Model.gan.intermediate_latent_dims,
                ),
            ))

            track_noise.append(np.random.normal(
                0,
                1,
                size=(
                    np.shape(chunks[i])[0],
                    Nparticles,
                    self.Model.gan.track_latent_dims,
                ),
            ))

        return mother_noise, intermediate_noise, track_noise

    def initialise_data_object(self, graph_structure, batch_size):
        empty = torch.tensor([[], []], dtype=torch.long)
        N_nodes = graph_structure.N_nodes

        data = {}
        # self loop
        data["track", "self", "track"] = DataContainer()
        data["track", "self", "track"].edge_index = batchify(
            ("track", "self", "track"),
            torch.tensor([[i, i] for i in range(N_nodes["track"])]).t(),
            batch_size=batch_size,
            N_nodes=N_nodes,
        ).to(myGlobals.device)

        if N_nodes["intermediate"] > 0:
            data["intermediate", "self", "intermediate"] = DataContainer()
            data["intermediate", "self", "intermediate"].edge_index = batchify(
                ("intermediate", "self", "intermediate"),
                torch.tensor([[i, i] for i in range(N_nodes["intermediate"])]).t(),
                batch_size=batch_size,
                N_nodes=N_nodes,
            ).to(myGlobals.device)

        data["mother", "self", "mother"] = DataContainer()
        data["mother", "self", "mother"].edge_index = batchify(
            ("mother", "self", "mother"),
            torch.tensor([[i, i] for i in range(N_nodes["mother"])]).t(),
            batch_size=batch_size,
            N_nodes=N_nodes,
        ).to(myGlobals.device)

        edge_types = [
            ["track", "up", "intermediate"],
            ["track", "up", "mother"],
            ["intermediate", "up", "mother"],
            ["intermediate", "up", "intermediate"],
            ["intermediate", "down", "track"],
            ["mother", "down", "track"],
            ["mother", "down", "intermediate"],
            ["intermediate", "down", "intermediate"],
        ]
        continued = []
        for edge_type in edge_types:
            if edge_type[1] == "up":
                generated_edge_index_tensors = graph_structure.edge_index_tensors_up
            elif edge_type[1] == "down":
                generated_edge_index_tensors = graph_structure.edge_index_tensors_down

            generated_edge_index_tensor = generated_edge_index_tensors[
                (edge_type[0], edge_type[1], edge_type[2])
            ]

            if all(
                isinstance(item, list) and not item
                for item in generated_edge_index_tensor
            ):
                continued.append([edge_type[0], edge_type[1], edge_type[2]])
                continue

            data[edge_type[0], edge_type[1], edge_type[2]] = DataContainer()
            list_of_edges = []
            for edge in generated_edge_index_tensor:
                if edge == []:
                    list_of_edges.append(empty)
                else:
                    list_of_edges.append(
                        batchify(
                            (edge_type[0], edge_type[1], edge_type[2]),
                            torch.tensor(edge).t(),
                            batch_size=batch_size,
                            N_nodes=N_nodes,
                        ).to(myGlobals.device)
                    )
            data[edge_type[0], edge_type[1], edge_type[2]].edge_index = list_of_edges
        for edge_type in continued:
            data[edge_type[0], edge_type[1], edge_type[2]] = DataContainer()
            data[edge_type[0], edge_type[1], edge_type[2]].edge_index = [
                [] for i in range(len(list_of_edges))
            ]

        return data

    def query_network_vtx(
        self,
        graph_structure,
        mother_conditions,
        intermediate_conditions,
        track_conditions,
        Nparticles,
    ):
        with torch.no_grad():
            batch_size = 25000

            mother_chunks = [
                mother_conditions[i : i + batch_size]
                for i in range(0, len(mother_conditions), batch_size)
            ]
            intermediate_chunks = [
                intermediate_conditions[i : i + batch_size]
                for i in range(0, len(intermediate_conditions), batch_size)
            ]
            track_chunks = [
                track_conditions[i : i + batch_size]
                for i in range(0, len(track_conditions), batch_size)
            ]

            mother_noise, intermediate_noise, track_noise = self.gen_latent(
                mother_chunks, Nparticles
            )

            N_nodes = graph_structure.N_nodes
            Ndaughter_counts = graph_structure.Ndaughter_counts


            if len(mother_noise) > 1:
                data = self.initialise_data_object(graph_structure, batch_size)

            self.Model.gan.to(myGlobals.device)

            for i in range(len(mother_noise)):
                print(f"{i}/{len(mother_noise)} chunks processed ...")

                batch_size_i = np.shape(mother_chunks[i])[0]
                if (
                    i + 1 == len(mother_noise) and batch_size_i != batch_size
                ):  # last batch, if different size to others remake edge index tensors
                    data = self.initialise_data_object(graph_structure, batch_size_i)

                track_noise_i = np.reshape(
                    track_noise[i], (-1, self.Model.gan.track_latent_dims)
                )
                track_chunks_i = np.reshape(
                    track_chunks[i], (-1, self.Model.gan.track_conditions_dims)
                )

                if N_nodes["intermediate"] > 0:
                    intermediate_noise_i = intermediate_noise[i]
                    intermediate_chunks_i = intermediate_chunks[i]
                    if N_nodes["intermediate"] > 1:
                        intermediate_noise_i = np.reshape(
                            intermediate_noise_i,
                            (-1, self.Model.gan.intermediate_latent_dims),
                        )
                        if "N_daughters" in self.intermediate_conditions:
                            intermediate_chunks_i = np.reshape(
                                intermediate_chunks_i,
                                (-1, N_nodes["intermediate"], self.Model.gan.intermediate_conditions_dims-1),
                            )
                        else:
                            intermediate_chunks_i = np.reshape(
                                intermediate_chunks_i,
                                (-1, self.Model.gan.intermediate_conditions_dims),
                            )
                    if "N_daughters" in self.intermediate_conditions:
                        if N_nodes["intermediate"] > 1:
                            Ndaughter_array = np.empty((np.shape(intermediate_chunks_i)[0], N_nodes["intermediate"], 1))
                            idx = 0
                            for key in Ndaughter_counts:
                                if key != graph_structure.mother_name:
                                    Ndaughter_array[:,idx,:] = Ndaughter_counts[key]
                                    idx += 1
                            intermediate_chunks_i = np.concatenate((intermediate_chunks_i, Ndaughter_array), axis=-1)
                            intermediate_chunks_i = np.reshape(
                                    intermediate_chunks_i,
                                    (-1, self.Model.gan.intermediate_conditions_dims),
                                )
                        else:
                            Ndaughter_array = np.empty((np.shape(intermediate_chunks_i)[0], 1))
                            idx = 0
                            for key in Ndaughter_counts:
                                if key != graph_structure.mother_name:
                                    Ndaughter_array[:,idx] = Ndaughter_counts[key]
                            intermediate_chunks_i = np.concatenate((intermediate_chunks_i, Ndaughter_array), axis=-1)
   
                if "N_daughters" in self.mother_conditions:
                    Ndaughter_mother = Ndaughter_counts[graph_structure.mother_name]
                    mother_chunks[i] = np.concatenate((mother_chunks[i], Ndaughter_mother*np.ones((np.shape(mother_chunks[i])[0], 1))), axis=-1)

                mother_conditions_obj = DataContainer()
                mother_conditions_obj.x = torch.tensor(
                    mother_chunks[i], dtype=torch.float32
                ).to(myGlobals.device)
                track_conditions_obj = DataContainer()
                track_conditions_obj.x = torch.tensor(
                    track_chunks_i, dtype=torch.float32
                ).to(myGlobals.device)
                if N_nodes["intermediate"] > 0:
                    intermediate_conditions_obj = DataContainer()
                    intermediate_conditions_obj.x = torch.tensor(
                        intermediate_chunks_i, dtype=torch.float32
                    ).to(myGlobals.device)

                if "diffusion" in self.network or "flowmatching" in self.network:
                    if "diffusion" in self.network:
                        mother_obj = DataContainer()
                        mother_obj.x = torch.randn(
                            (
                                mother_chunks[i].shape[0],
                                self.Model.gan.mother_targets_dims,
                            ),
                            dtype=torch.float32,
                        ).to(myGlobals.device)

                        track_obj = DataContainer()
                        track_obj.x = torch.randn(
                            (
                                track_chunks_i.shape[0],
                                self.Model.gan.track_targets_dims,
                            ),
                            dtype=torch.float32,
                        ).to(myGlobals.device)

                        if N_nodes["intermediate"] > 0:
                            intermediate_obj = DataContainer()
                            intermediate_obj.x = torch.randn(
                                (
                                    intermediate_chunks_i.shape[0],
                                    self.Model.gan.intermediate_targets_dims,
                                ),
                                dtype=torch.float32,
                            ).to(myGlobals.device)
                    else:
                        mother_obj = DataContainer()
                        mother_obj.x = (
                            torch.randn(
                                (
                                    mother_chunks[i].shape[0],
                                    self.Model.gan.mother_targets_dims,
                                ),
                                dtype=torch.float32,
                            ).to(myGlobals.device)
                            * 0.25
                        )

                        track_obj = DataContainer()
                        track_obj.x = (
                            torch.randn(
                                (
                                    track_chunks_i.shape[0],
                                    self.Model.gan.track_targets_dims,
                                ),
                                dtype=torch.float32,
                            ).to(myGlobals.device)
                            * 0.25
                        )

                        intermediate_obj = DataContainer()
                        intermediate_obj.x = (
                            torch.randn(
                                (
                                    intermediate_chunks_i.shape[0],
                                    self.Model.gan.intermediate_targets_dims,
                                ),
                                dtype=torch.float32,
                            ).to(myGlobals.device)
                            * 0.25
                        )

                    data["mother"] = mother_obj
                    data["track"] = track_obj
                    if N_nodes["intermediate"] > 0:
                        data["intermediate"] = intermediate_obj
                    data["mother_conditions"] = mother_conditions_obj
                    data["track_conditions"] = track_conditions_obj
                    if N_nodes["intermediate"] > 0:
                        data["intermediate_conditions"] = intermediate_conditions_obj
                    self.Model.gan.steps = self.N_diffusion_steps
                    if "flowmatching" in self.network:
                        mother, intermediate, track = self.Model.gan.inference(
                            batch_size_i, data, None, flowmatching=True
                        )
                    else:
                        mother, intermediate, track = self.Model.gan.inference(
                            batch_size_i,
                            data,
                            DDPMScheduler(
                                num_train_timesteps=self.Model.gan.steps,
                                # beta_schedule="squaredcos_cap_v2",
                            ),
                            use_encoder=False,
                        )
                    mother = mother.cpu().detach().numpy()
                    if N_nodes["intermediate"] > 0:
                        intermediate = intermediate.cpu().detach().numpy()
                    track = track.cpu().detach().numpy()

                else:
                    mother, intermediate, track = self.Model.gan.generator.forward(
                        torch.tensor(mother_noise[i], dtype=torch.float32).to(
                            myGlobals.device
                        ),
                        torch.tensor(track_noise_i, dtype=torch.float32).to(
                            myGlobals.device
                        ),
                        torch.tensor(intermediate_noise_i, dtype=torch.float32).to(
                            myGlobals.device
                        ),
                        mother_conditions_obj,
                        track_conditions_obj,
                        intermediate_conditions_obj,
                        None,
                        data,  # contains all edge_index information
                    )

                    mother = mother.cpu().detach().numpy()
                    intermediate = intermediate.cpu().detach().numpy()
                    track = track.cpu().detach().numpy()

                if i == 0:
                    if N_nodes["intermediate"] > 0:
                        vertexing_output = np.concatenate(
                            (
                                mother,
                                intermediate.reshape(mother.shape[0], -1),
                                track.reshape(mother.shape[0], -1),
                            ),
                            axis=1,
                        )
                    else:
                        vertexing_output = np.concatenate(
                            (mother, track.reshape(mother.shape[0], -1)),
                            axis=1,
                        )
                else:
                    if N_nodes["intermediate"] > 0:
                        vertexing_output_i = np.concatenate(
                            (
                                mother,
                                intermediate.reshape(mother.shape[0], -1),
                                track.reshape(mother.shape[0], -1),
                            ),
                            axis=1,
                        )
                    else:
                        vertexing_output_i = np.concatenate(
                            (mother, track.reshape(mother.shape[0], -1)),
                            axis=1,
                        )
                    vertexing_output = np.concatenate(
                        (vertexing_output, vertexing_output_i), axis=0
                    )

            if N_nodes["intermediate"] > 0:
                out_processed = pd.DataFrame(
                    vertexing_output,
                    columns=self.mother_targets
                    + self.intermediate_targets
                    + self.track_targets,
                )
            else:
                out_processed = pd.DataFrame(
                    vertexing_output,
                    columns=self.mother_targets + self.track_targets,
                )

            out_unprocessed = tfs.untransform_df(out_processed, self.transformers)

            for key in out_unprocessed:
                if "ENDVERTEX_CHI2NDOF" in key:
                    particle = key.replace("_ENDVERTEX_CHI2NDOF", "")
                    if "INTERMEDIATE" in key:
                        particle = myGlobals.particle_map["fromINTERMEDIATES"][
                            particle
                        ]  # daughter_counts dict has user names
                    else:
                        particle = graph_structure.mother_name
                    Ntracks = graph_structure.daughter_counts[particle]
                    NDOF = Ntracks * 2 - 3
                    out_unprocessed[
                        key.replace("ENDVERTEX_CHI2NDOF", "ENDVERTEX_CHI2")
                    ] = out_unprocessed[key] * NDOF

            return out_unprocessed

    def query_network_smearing(self, true_PID_scheme, node_conditions, edge_conditions):
        max_batch_size = 25000

        num_batches = (len(node_conditions) + max_batch_size - 1) // max_batch_size

        # Create lists of batches
        node_conditions_batches = [
            node_conditions[i * max_batch_size : (i + 1) * max_batch_size]
            for i in range(num_batches)
        ]
        edge_conditions_batches = [
            edge_conditions[i * max_batch_size : (i + 1) * max_batch_size]
            for i in range(num_batches)
        ]

        out_unprocessed_batches = []

        for i in range(num_batches):
            node_conditions = node_conditions_batches[i]
            edge_conditions = edge_conditions_batches[i]

            with torch.no_grad():
                dtype = torch.float32
                events_transformed_node = np.asarray(node_conditions).reshape(
                    -1,
                    self.Nparticles,
                    len(self.Model.branch_options["track_conditions"]),
                )
                events_transformed_node = torch.tensor(
                    events_transformed_node, dtype=dtype
                ).to(myGlobals.device)

                N_nodes = {}
                for PID in myGlobals.particle_universe:
                    N_nodes[str(PID)] = 0
                track_PIDs = []
                for particle in true_PID_scheme:
                    if any(
                        myGlobals.particle_map["toDAUGHTERS"][name] in particle
                        for name in self.daughter_particle_names
                    ):
                        PID = abs(true_PID_scheme[particle])
                        N_nodes[str(PID)] += 1
                        track_PIDs.append(PID)

                # possible edges
                ordered_pairs = list(
                    itertools.product(
                        list(map(str, myGlobals.particle_universe)), repeat=2
                    )
                )
                batch_size = events_transformed_node.shape[0]

                data = {}

                for particle_type in myGlobals.particle_universe:
                    data[f"{particle_type}_conditions"] = DataContainer()
                    data[f"{particle_type}_trackidx"] = DataContainer()

                    data[f"{particle_type}_conditions"].x = torch.empty(
                        (0, len(self.Model.branch_options["track_conditions"])),
                        dtype=dtype,
                    ).to(myGlobals.device)

                for track_global_index, track_PID in enumerate(track_PIDs):
                    data[f"{str(track_PID)}_conditions"].x = []
                for track_global_index, track_PID in enumerate(track_PIDs):
                    data[f"{str(track_PID)}_conditions"].x.append(
                        events_transformed_node[:, track_global_index]
                    )
                for particle_type in myGlobals.particle_universe:
                    if particle_type in track_PIDs:
                        if len(data[f"{particle_type}_conditions"].x) == 1:
                            combined = data[f"{particle_type}_conditions"].x[0]
                        else:
                            combined = torch.stack(
                                tuple(data[f"{str(particle_type)}_conditions"].x), dim=1
                            ).to(myGlobals.device)
                            combined = combined.reshape(-1, combined.shape[-1])
                        data[f"{str(particle_type)}_conditions"].x = combined

                particle_types = ["11", "13", "211", "321", "2212"]

                if "diffusion" in self.network or "flowmatching" in self.network:
                    # Add .batch for each particle type
                    for particle_type in particle_types:
                        node_count = data[f"{str(particle_type)}_conditions"].x.shape[0]
                        if node_count > 0:
                            # Repeat batch indices (0 to batch_size-1) for each node in the batch
                            # This assumes the data is laid out in batch-major order
                            # You must know or ensure how data is ordered!
                            counts_per_batch = (
                                node_count // batch_size
                            )  # Assuming equal distribution
                            batch_tensor = torch.arange(
                                batch_size, device=myGlobals.device
                            ).repeat_interleave(counts_per_batch)

                            # If there's a mismatch (edge case), pad or truncate
                            if batch_tensor.shape[0] < node_count:
                                extra = torch.full(
                                    (node_count - batch_tensor.shape[0],),
                                    batch_size - 1,
                                    device=myGlobals.device,
                                )
                                batch_tensor = torch.cat([batch_tensor, extra])
                            elif batch_tensor.shape[0] > node_count:
                                batch_tensor = batch_tensor[:node_count]

                            data[particle_type] = (
                                DataContainer()
                                if particle_type not in data
                                else data[particle_type]
                            )
                            data[particle_type].batch = batch_tensor
                        else:
                            data[particle_type] = DataContainer()

                for pair in ordered_pairs:
                    data[pair[0], "to", pair[1]] = DataContainer()

                for pair in ordered_pairs:
                    data[pair[0], "to", pair[1]].edge_index = torch.empty(
                        (2, 0), dtype=torch.long
                    ).to(myGlobals.device)
                    data[pair[0], "to", pair[1]].edge_attr = []

                ##### empty batch object created...

                edges_by_index = list(
                    itertools.product(range(len(track_PIDs)), repeat=2)
                )

                index_by_appearence = []
                index_counters = {11: 0, 13: 0, 211: 0, 321: 0, 2212: 0}
                for item in track_PIDs:
                    index_by_appearence.append(index_counters[item])
                    index_counters[item] += 1

                for edge_by_index in edges_by_index:
                    origin = str(track_PIDs[edge_by_index[0]])
                    destination = str(track_PIDs[edge_by_index[1]])
                    origin_idx = index_by_appearence[edge_by_index[0]]
                    destination_idx = index_by_appearence[edge_by_index[1]]

                    if origin != destination or origin_idx != destination_idx:
                        origin_name = self.internal_daughter_particle_names[
                            edge_by_index[0]
                        ]
                        destination_name = self.internal_daughter_particle_names[
                            edge_by_index[1]
                        ]

                        edge_conditions_i = [
                            cond
                            for cond in self.edge_conditions
                            if f"{origin_name}_{destination_name}" in cond
                        ]

                        edge_attr_i = torch.tensor(
                            np.asarray(edge_conditions[edge_conditions_i]), dtype=dtype
                        ).to(myGlobals.device)
                        data[origin, "to", destination].edge_attr.append(edge_attr_i)

                        edge_i = (
                            torch.tensor(
                                [[origin_idx, destination_idx]], dtype=torch.long
                            )
                            .t()
                            .to(myGlobals.device)
                        )
                        data[origin, "to", destination].edge_index = torch.cat(
                            (data[origin, "to", destination].edge_index, edge_i), dim=1
                        )

                for pair in ordered_pairs:
                    if len(data[pair[0], "to", pair[1]].edge_attr) == 0:
                        data[pair[0], "to", pair[1]].edge_attr = torch.empty(
                            (0, len(self.Model.branch_options["edge_conditions"])),
                            dtype=dtype,
                        ).to(myGlobals.device)
                    else:
                        combined = (
                            torch.stack(
                                tuple(data[pair[0], "to", pair[1]].edge_attr), dim=1
                            )
                            .reshape(-1, 1)
                            .to(myGlobals.device)
                        )
                        data[pair[0], "to", pair[1]].edge_attr = combined

                for pair in ordered_pairs:
                    if data[pair[0], "to", pair[1]].edge_index.shape[1] > 0:
                        data[pair[0], "to", pair[1]].edge_index = batchify(
                            (pair[0], "to", pair[1]),
                            data[pair[0], "to", pair[1]].edge_index,
                            batch_size=batch_size,
                            N_nodes=N_nodes,
                        )

                track_latent = {}
                for particle_type in myGlobals.particle_universe:
                    track_latent[str(particle_type)] = torch.randn(
                        (
                            data[f"{str(particle_type)}_conditions"].x.shape[0],
                            self.Model.gan.track_latent_dims,
                        ),
                        dtype=dtype,
                    ).to(myGlobals.device)

                self.Model.gan.to(myGlobals.device)

                if "diffusion" in self.network:
                    for particle_type in particle_types:
                        # data[particle_type] = DataContainer()
                        data[particle_type].x = torch.randn(
                            (
                                data[f"{particle_type}_conditions"].x.shape[0],
                                self.Model.gan.track_targets_dims,
                            ),
                            dtype=dtype,
                        ).to(myGlobals.device)

                    self.Model.gan.diffuser.to(myGlobals.device)

                    self.Model.gan.steps = self.N_diffusion_steps
                    if "PID" in self.network:
                        out = self.Model.gan.inference(
                            batch_size,
                            data,
                            DDPMScheduler(
                                num_train_timesteps=self.Model.gan.steps,
                                beta_schedule="squaredcos_cap_v2",
                            ),
                        )
                    else:
                        out = self.Model.gan.inference(
                            batch_size,
                            data,
                            DDPMScheduler(
                                num_train_timesteps=self.Model.gan.steps,
                                clip_sample=True,
                                clip_sample_range=5.5,
                                beta_schedule="squaredcos_cap_v2",
                            ),
                        )

                    # out = out.cpu().detach().numpy()
                    # out = {k: v.cpu().detach().numpy() for k, v in out.items()}
                elif "flowmatching" in self.network:
                    for particle_type in particle_types:
                        data[particle_type].x = torch.randn(
                            (
                                data[f"{particle_type}_conditions"].x.shape[0],
                                self.Model.gan.track_targets_dims,
                            ),
                            dtype=dtype,
                        ).to(myGlobals.device)
                    self.Model.gan.diffuser.to(myGlobals.device)
                    out = self.Model.gan.inference(
                        batch_size, data, None, flowmatching=True
                    )

                else:
                    out = self.Model.gan.generator(
                        track_latent,
                        batch=data,
                    )

                for i in out:
                    i_out = out[i].cpu().detach().numpy()
                    for idx in range(len(self.targets)):
                        if myGlobals.personalised_track_node_types:
                            i_out[:, idx] = self.Transformers[
                                f"{self.targets[idx].replace('DAUGHTERN', 'DAUGHTER1')}_{i}"
                            ].unprocess(i_out[:, idx])
                        else:
                            i_out[:, idx] = self.Transformers[
                                f"{self.targets[idx].replace('DAUGHTERN', 'DAUGHTER1')}"
                            ].unprocess(i_out[:, idx])
                    out[i] = i_out

                for i in out:
                    if N_nodes[i] > 0:
                        out[i] = out[i].reshape(-1, N_nodes[i], len(self.targets))

                N_nodes_out = {}
                for PID in myGlobals.particle_universe:
                    N_nodes_out[str(PID)] = 0

                for idx, item in enumerate(track_PIDs):
                    if idx == 0:
                        out_ordered = np.expand_dims(out[str(item)][:, 0], 1)
                    else:
                        out_ordered = np.concatenate(
                            (
                                out_ordered,
                                np.expand_dims(
                                    out[str(item)][:, N_nodes_out[str(item)]], 1
                                ),
                            ),
                            axis=1,
                        )
                    N_nodes_out[str(item)] += 1

                out_ordered = out_ordered.reshape(
                    -1, len(self.targets) * len(track_PIDs)
                )

                out_unprocessed = pd.DataFrame(out_ordered, columns=self.targets_full)

                out_unprocessed_batches.append(out_unprocessed)

        out_unprocessed = pd.concat(out_unprocessed_batches, ignore_index=True)

        return out_unprocessed

    def query_network_vanilla(self, conditions):
        if "diffusion" in self.network:
            with torch.no_grad():
                self.Model.gan.to(myGlobals.device)

                conditions = torch.tensor(conditions, dtype=torch.float32).to(
                    myGlobals.device
                )

                reconstructed = self.Model.gan.inference(
                    conditions.shape[0], conditions
                )

                reconstructed = reconstructed.detach().cpu().numpy()
                reconstructed = pd.DataFrame(reconstructed, columns=self.targets)
                output = tfs.untransform_df(reconstructed, self.transformers)

            return output

        else:
            with torch.no_grad():
                self.Model.gan.to(myGlobals.device)

                conditions = torch.tensor(conditions, dtype=torch.float32).to(
                    myGlobals.device
                )
                z = torch.randn((conditions.shape[0], self.Model.gan.latent_dims)).to(
                    myGlobals.device
                )

                reconstructed = self.Model.gan.generator(z, conditions)

                reconstructed = reconstructed.detach().cpu().numpy()
                reconstructed = pd.DataFrame(reconstructed, columns=self.targets)
                output = tfs.untransform_df(reconstructed, self.transformers)

            return output

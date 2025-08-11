import lhcb_rex.settings.globals as myGlobals

from torch_geometric.data import InMemoryDataset
import pickle
import os

from lhcb_rex.data.data_handler import (
    # DataHandler,
    # HyperDataHandler,
    HeteroDataHandler,
)
from lhcb_rex.data.data_handlerGENERALISED import (
    HeteroDataHandlerGENERALISED,
)
import os.path
import shutil
from pathlib import Path
import importlib.resources


class GENERALISED_HeteroGraphDataset(InMemoryDataset):
    path = ""
    splits = 1
    max_N_samples_per = -1

    def __init__(
        self,
        root,  # storage location
        config=None,
        force_reload=False,
        path="",  # path to root file
        mode="build_graphs",
        mother_targets=[],
        intermediate_targets=[],
        track_targets=[],
        mother_conditions=[],
        intermediate_conditions=[],
        track_conditions=[],
        edge_conditions=[],
        use_weights=True,
        splits=1,
        processID=-1,
        smearingnet=False,
        PIDnet=False,
        require_validation_variables=False,
    ):
        if config:
            with open(config, "rb") as handle:
                self.setting = pickle.load(handle)
                self.setting = self.setting[list(self.setting.keys())[0]]

            print("\n####### ####### ####### ####### #######")
            for item in self.setting:
                print(item, self.setting[item])
            print("####### ####### ####### ####### #######\n")
            # quit()

        if smearingnet or PIDnet:
            myGlobals.personalised_track_node_types = True

        GENERALISED_HeteroGraphDataset.path = path

        GENERALISED_HeteroGraphDataset.mother_targets = mother_targets
        GENERALISED_HeteroGraphDataset.intermediate_targets = intermediate_targets
        GENERALISED_HeteroGraphDataset.track_targets = track_targets
        GENERALISED_HeteroGraphDataset.mother_conditions = mother_conditions
        GENERALISED_HeteroGraphDataset.intermediate_conditions = intermediate_conditions
        GENERALISED_HeteroGraphDataset.track_conditions = track_conditions
        GENERALISED_HeteroGraphDataset.edge_conditions = edge_conditions

        GENERALISED_HeteroGraphDataset.splits = splits

        GENERALISED_HeteroGraphDataset.processID = processID

        GENERALISED_HeteroGraphDataset.root = root
        GENERALISED_HeteroGraphDataset.smearingnet = smearingnet
        GENERALISED_HeteroGraphDataset.PIDnet = PIDnet
        GENERALISED_HeteroGraphDataset.require_validation_variables = (
            require_validation_variables
        )

        self.use_weights = use_weights
        self.split_idx = 0
        self.splits = splits

        super().__init__(root, force_reload=force_reload)

        self.mode = mode

        print("self.processed_paths[2]:", self.processed_paths[2])
        filehandler = open(self.processed_paths[2], "rb")
        self.options = pickle.load(filehandler)

        if os.path.isfile(f"{self.processed_paths[0]}"):
            pass
        else:
            print(
                f"{self.processed_paths[0]} doesnt exist: fail, adding +1 to split_idx"
            )
            self.load_next()

        if mode == "train" or mode == "build_graphs":
            self.load(self.processed_paths[0])
        if mode == "test" or mode == "build_graphs":
            self.load(self.processed_paths[1])

        if (mode == "train" or mode == "build_graphs") and self.use_weights:
            filehandler = open(self.processed_paths[3], "rb")
            weights = pickle.load(filehandler)
            self.options["training_weights"] = weights

        try:
            if mode == "train" or mode == "build_graphs":
                filehandler = open(self.processed_paths[-2], "rb")
                fully_reco_bool = pickle.load(filehandler)
                self.options["fully_reco_bool"] = fully_reco_bool
            if mode == "test" or mode == "build_graphs":
                filehandler = open(self.processed_paths[-1], "rb")
                fully_reco_bool = pickle.load(filehandler)
                self.options["fully_reco_bool"] = fully_reco_bool
        except Exception:
            pass

        my_file = Path(
            self.processed_paths[2].split("options.pt")[0] + "transfomer_quantiles.pkl"
        )
        if not my_file.is_file():
            print(
                "copying transformers to: ",
                self.processed_paths[2].split("options.pt")[0]
                + "transfomer_quantiles.pkl",
            )
            transformers = importlib.resources.files("lhcb_rex").joinpath(
                "processing/transfomer_quantiles.pkl"
            )
            shutil.copyfile(
                transformers,
                self.processed_paths[2].split("options.pt")[0]
                + "transfomer_quantiles.pkl",
            )

        my_file = Path(self.processed_paths[2].split("options.pt")[0] + "min_maxes.pkl")
        if not my_file.is_file():
            print(
                "copying min_maxes to: ",
                self.processed_paths[2].split("options.pt")[0] + "min_maxes.pkl",
            )
            min_maxes = importlib.resources.files("lhcb_rex").joinpath(
                "processing/min_maxes.pkl"
            )
            shutil.copyfile(
                min_maxes,
                self.processed_paths[2].split("options.pt")[0] + "min_maxes.pkl",
            )

    def get_paths(self, dir_path):
        while 1 == 1:
            if self.split_idx >= self.splits - 1:
                self.split_idx = 0
            processed_paths_i = [
                (
                    file.replace(".pt", f"_{self.split_idx}.pt")
                    if file != "options.pt"
                    else file
                )
                for file in self.files
            ]
            if os.path.isfile(f"{dir_path}/{processed_paths_i[0]}"):
                break
            else:
                print(
                    f"{dir_path}/{processed_paths_i[0]} doesnt exist: fail, adding +1 to split_idx"
                )
                self.split_idx += 1

        print(processed_paths_i)
        return processed_paths_i

    def load_next(self):
        self.split_idx += 1
        if self.split_idx >= self.splits - 1:
            self.split_idx = 0
        print(f"Loading split {self.split_idx} of {self.splits}...")
        dir_path = os.path.dirname(self.processed_paths[0])

        processed_paths_i = self.get_paths(dir_path)

        if self.mode == "train" or self.mode == "build_graphs":
            self.load(f"{dir_path}/{processed_paths_i[0]}")
        if self.mode == "test" or self.mode == "build_graphs":
            self.load(f"{dir_path}/{processed_paths_i[1]}")

        if (self.mode == "train" or self.mode == "build_graphs") and self.use_weights:
            filehandler = open(f"{dir_path}/{processed_paths_i[3]}", "rb")
            weights = pickle.load(filehandler)
            self.options["training_weights"] = weights

        try:
            if self.mode == "train" or self.mode == "build_graphs":
                filehandler = open(f"{dir_path}/{processed_paths_i[-2]}", "rb")
                fully_reco_bool = pickle.load(filehandler)
                self.options["fully_reco_bool"] = fully_reco_bool

            if self.mode == "test" or self.mode == "build_graphs":
                filehandler = open(f"{dir_path}/{processed_paths_i[-1]}", "rb")
                fully_reco_bool = pickle.load(filehandler)
                self.options["fully_reco_bool"] = fully_reco_bool
        except Exception:
            pass

        # self.processed_paths = processed_paths_i

    @property
    def processed_file_names(self):
        self.files = [
            "data.pt",
            "data_val.pt",
            "options.pt",
        ]
        if self.use_weights:
            self.files.append("train_weights.pt")
        self.files.append("fully_reco_bool_train.pt")
        self.files.append("fully_reco_bool_test.pt")

        paths = [
            file.replace(".pt", "_0.pt") if file != "options.pt" else file
            for file in self.files
        ]
        return paths

    def process(self):
        data_handler = HeteroDataHandlerGENERALISED(
            config=self.setting,
            path=GENERALISED_HeteroGraphDataset.path,
            N=int(GENERALISED_HeteroGraphDataset.max_N_samples_per),
            mother_targets=GENERALISED_HeteroGraphDataset.mother_targets,
            intermediate_targets=GENERALISED_HeteroGraphDataset.intermediate_targets,
            track_targets=GENERALISED_HeteroGraphDataset.track_targets,
            mother_conditions=GENERALISED_HeteroGraphDataset.mother_conditions,
            intermediate_conditions=GENERALISED_HeteroGraphDataset.intermediate_conditions,
            track_conditions=GENERALISED_HeteroGraphDataset.track_conditions,
            edge_conditions=GENERALISED_HeteroGraphDataset.edge_conditions,
            testing_frac=0.1,
            use_weights=self.use_weights,
            splits=GENERALISED_HeteroGraphDataset.splits,
            processID=GENERALISED_HeteroGraphDataset.processID,
            smearingnet=GENERALISED_HeteroGraphDataset.smearingnet,
            PIDnet=GENERALISED_HeteroGraphDataset.PIDnet,
            require_validation_variables=GENERALISED_HeteroGraphDataset.require_validation_variables,
        )
        # if HeteroGraphDataset.processID == -1:
        # for split in range(HeteroGraphDataset.splits):

        split = GENERALISED_HeteroGraphDataset.processID

        print(f"split number (process): {split}")

        # data_handler.make_split(split)
        print(self.processed_paths[0].replace("_0.pt", f"_{split}.pt"))

        if self.use_weights:
            weights_i = data_handler.data_train_list_weights
            filehandler = open(
                self.processed_paths[3].replace("_0.pt", f"_{split}.pt"), "wb"
            )
            pickle.dump(weights_i, filehandler)

        self.save(
            data_handler.data_train,
            self.processed_paths[0].replace("_0.pt", f"_{split}.pt"),
        )
        self.save(
            data_handler.data_test,
            self.processed_paths[1].replace("_0.pt", f"_{split}.pt"),
        )

        fully_reco_bool_train = data_handler.data_train_list_full_reco
        fully_reco_bool_test = data_handler.data_test_list_full_reco
        filehandler = open(
            self.processed_paths[-2].replace("_0.pt", f"_{split}.pt"), "wb"
        )
        pickle.dump(fully_reco_bool_train, filehandler)
        filehandler = open(
            self.processed_paths[-1].replace("_0.pt", f"_{split}.pt"), "wb"
        )
        pickle.dump(fully_reco_bool_test, filehandler)

        options = {}
        options["path"] = GENERALISED_HeteroGraphDataset.path
        # options["particles_involved"] = GENERALISED_HeteroGraphDataset.particles_involved
        options["settings"] = self.setting

        options["mother_targets"] = (GENERALISED_HeteroGraphDataset.mother_targets,)
        options["intermediate_targets"] = (
            GENERALISED_HeteroGraphDataset.intermediate_targets,
        )
        options["track_targets"] = (GENERALISED_HeteroGraphDataset.track_targets,)
        options["mother_conditions"] = (
            GENERALISED_HeteroGraphDataset.mother_conditions,
        )
        options["intermediate_conditions"] = (
            GENERALISED_HeteroGraphDataset.intermediate_conditions,
        )
        options["track_conditions"] = (GENERALISED_HeteroGraphDataset.track_conditions,)
        options["edge_conditions"] = (GENERALISED_HeteroGraphDataset.edge_conditions,)

        filehandler = open(self.processed_paths[2], "wb")
        pickle.dump(options, filehandler)


class HeteroGraphDataset(InMemoryDataset):
    particles_involved = [1, 2]
    fully_reco = False
    max_N_samples_per = 1000
    path = ""
    splits = 1

    def __init__(
        self,
        root,  # storage location
        max_N_samples_per=-1,  # limit to number of graphs to create
        fully_reco=False,
        force_reload=False,
        path="",  # path to root file
        particles_involved=[1, 2],
        intermediates=[],
        mode="build_graphs",
        mother_targets=[],
        intermediate_targets=[],
        track_targets=[],
        mother_conditions=[],
        intermediate_conditions=[],
        track_conditions=[],
        edge_conditions=[],
        use_weights=True,
        splits=1,
        mother_N=3,
        intermediate_N=[],
        processID=-1,
        smearingnet=False,
        PIDnet=False,
        require_validation_variables=False,
    ):
        if smearingnet or PIDnet:
            myGlobals.personalised_track_node_types = True

        HeteroGraphDataset.particles_involved = particles_involved
        HeteroGraphDataset.intermediates = intermediates
        HeteroGraphDataset.N = len(particles_involved)
        HeteroGraphDataset.max_N_samples_per = max_N_samples_per
        HeteroGraphDataset.fully_reco = fully_reco
        HeteroGraphDataset.path = path

        HeteroGraphDataset.mother_targets = mother_targets
        HeteroGraphDataset.intermediate_targets = intermediate_targets
        HeteroGraphDataset.track_targets = track_targets
        HeteroGraphDataset.mother_conditions = mother_conditions
        HeteroGraphDataset.intermediate_conditions = intermediate_conditions
        HeteroGraphDataset.track_conditions = track_conditions
        HeteroGraphDataset.edge_conditions = edge_conditions

        HeteroGraphDataset.splits = splits
        HeteroGraphDataset.mother_N = mother_N
        HeteroGraphDataset.intermediate_N = intermediate_N

        HeteroGraphDataset.processID = processID

        HeteroGraphDataset.root = root
        HeteroGraphDataset.smearingnet = smearingnet
        HeteroGraphDataset.PIDnet = PIDnet
        HeteroGraphDataset.require_validation_variables = require_validation_variables

        self.use_weights = use_weights
        self.split_idx = 0
        self.splits = splits

        super().__init__(root, force_reload=force_reload)

        self.mode = mode

        filehandler = open(self.processed_paths[2], "rb")
        self.options = pickle.load(filehandler)

        if os.path.isfile(f"{self.processed_paths[0]}"):
            pass
        else:
            print(
                f"{self.processed_paths[0]} doesnt exist: fail, adding +1 to split_idx"
            )
            self.load_next()

        if mode == "train" or mode == "build_graphs":
            self.load(self.processed_paths[0])
        if mode == "test" or mode == "build_graphs":
            self.load(self.processed_paths[1])

        if (mode == "train" or mode == "build_graphs") and self.use_weights:
            filehandler = open(self.processed_paths[3], "rb")
            weights = pickle.load(filehandler)
            self.options["training_weights"] = weights

        try:
            if mode == "train" or mode == "build_graphs":
                filehandler = open(self.processed_paths[-2], "rb")
                fully_reco_bool = pickle.load(filehandler)
                self.options["fully_reco_bool"] = fully_reco_bool
            if mode == "test" or mode == "build_graphs":
                filehandler = open(self.processed_paths[-1], "rb")
                fully_reco_bool = pickle.load(filehandler)
                self.options["fully_reco_bool"] = fully_reco_bool
        except Exception:
            pass

    def get_paths(self, dir_path):
        while 1 == 1:
            if self.split_idx >= self.splits - 1:
                self.split_idx = 0
            processed_paths_i = [
                (
                    file.replace(".pt", f"_{self.split_idx}.pt")
                    if file != "options.pt"
                    else file
                )
                for file in self.files
            ]
            if os.path.isfile(f"{dir_path}/{processed_paths_i[0]}"):
                break
            else:
                print(
                    f"{dir_path}/{processed_paths_i[0]} doesnt exist: fail, adding +1 to split_idx"
                )
                self.split_idx += 1

        print(processed_paths_i)
        return processed_paths_i

    def load_next(self):
        self.split_idx += 1
        if self.split_idx >= self.splits - 1:
            self.split_idx = 0
        print(f"Loading split {self.split_idx} of {self.splits}...")
        dir_path = os.path.dirname(self.processed_paths[0])

        processed_paths_i = self.get_paths(dir_path)

        if self.mode == "train" or self.mode == "build_graphs":
            self.load(f"{dir_path}/{processed_paths_i[0]}")
        if self.mode == "test" or self.mode == "build_graphs":
            self.load(f"{dir_path}/{processed_paths_i[1]}")

        if self.mode == "train" or self.mode == "build_graphs":
            filehandler = open(f"{dir_path}/{processed_paths_i[3]}", "rb")
            weights = pickle.load(filehandler)
            self.options["training_weights"] = weights

        try:
            if self.mode == "train" or self.mode == "build_graphs":
                filehandler = open(f"{dir_path}/{processed_paths_i[-2]}", "rb")
                fully_reco_bool = pickle.load(filehandler)
                self.options["fully_reco_bool"] = fully_reco_bool

            if self.mode == "test" or self.mode == "build_graphs":
                filehandler = open(f"{dir_path}/{processed_paths_i[-1]}", "rb")
                fully_reco_bool = pickle.load(filehandler)
                self.options["fully_reco_bool"] = fully_reco_bool
        except Exception:
            pass

    @property
    def processed_file_names(self):
        self.files = [
            "data.pt",
            "data_val.pt",
            "options.pt",
            # "train_weights.pt",
            "fully_reco_bool_train.pt",
            "fully_reco_bool_test.pt",
        ]
        if self.use_weights:
            self.files.append("train_weights.pt")

        # if HeteroGraphDataset.splits == 1:
        #     return self.files
        # else:
        # return ["data_0.pt", "data_val_0.pt", "options.pt", "train_weights_0.pt"]

        paths = [
            file.replace(".pt", "_0.pt") if file != "options.pt" else file
            for file in self.files
        ]
        # path_there = []
        # for path in paths:
        #     print(f'path: {path} ',os.path.isfile(f'{HeteroGraphDataset.root}/processed/{path}'))
        #     path_there.append(os.path.isfile(f'{HeteroGraphDataset.root}/processed/{path}'))
        # if False in path_there:
        #     raise ValueError("Missing file")

        return paths

    def process(self):
        data_handler = HeteroDataHandler(
            particles_involved=HeteroGraphDataset.particles_involved,
            intermediates=HeteroGraphDataset.intermediates,
            path=HeteroGraphDataset.path,
            N=int(HeteroGraphDataset.max_N_samples_per),
            mother_targets=HeteroGraphDataset.mother_targets,
            intermediate_targets=HeteroGraphDataset.intermediate_targets,
            track_targets=HeteroGraphDataset.track_targets,
            mother_conditions=HeteroGraphDataset.mother_conditions,
            intermediate_conditions=HeteroGraphDataset.intermediate_conditions,
            track_conditions=HeteroGraphDataset.track_conditions,
            edge_conditions=HeteroGraphDataset.edge_conditions,
            graphify=True,
            testing_frac=0.1,
            # cut=cut,
            use_weights=self.use_weights,
            splits=HeteroGraphDataset.splits,
            mother_N=HeteroGraphDataset.mother_N,
            intermediate_N=HeteroGraphDataset.intermediate_N,
            processID=HeteroGraphDataset.processID,
            smearingnet=HeteroGraphDataset.smearingnet,
            PIDnet=HeteroGraphDataset.PIDnet,
            require_validation_variables=HeteroGraphDataset.require_validation_variables,
        )

        # if HeteroGraphDataset.processID == -1:
        # for split in range(HeteroGraphDataset.splits):

        split = HeteroGraphDataset.processID

        print(f"split number (process): {split}")

        # data_handler.make_split(split)
        print(self.processed_paths[0].replace("_0.pt", f"_{split}.pt"))

        if self.use_weights:
            weights_i = data_handler.data_train_list_weights
            filehandler = open(
                self.processed_paths[3].replace("_0.pt", f"_{split}.pt"), "wb"
            )
            pickle.dump(weights_i, filehandler)

        self.save(
            data_handler.data_train,
            self.processed_paths[0].replace("_0.pt", f"_{split}.pt"),
        )
        self.save(
            data_handler.data_test,
            self.processed_paths[1].replace("_0.pt", f"_{split}.pt"),
        )

        fully_reco_bool_train = data_handler.data_train_list_full_reco
        fully_reco_bool_test = data_handler.data_test_list_full_reco
        filehandler = open(
            self.processed_paths[-2].replace("_0.pt", f"_{split}.pt"), "wb"
        )
        pickle.dump(fully_reco_bool_train, filehandler)
        filehandler = open(
            self.processed_paths[-1].replace("_0.pt", f"_{split}.pt"), "wb"
        )
        pickle.dump(fully_reco_bool_test, filehandler)

        options = {}
        options["path"] = HeteroGraphDataset.path
        options["particles_involved"] = HeteroGraphDataset.particles_involved
        options["intermediates"] = HeteroGraphDataset.intermediates

        options["mother_targets"] = (HeteroGraphDataset.mother_targets,)
        options["intermediate_targets"] = (HeteroGraphDataset.intermediate_targets,)
        options["track_targets"] = (HeteroGraphDataset.track_targets,)
        options["mother_conditions"] = (HeteroGraphDataset.mother_conditions,)
        options["intermediate_conditions"] = (
            HeteroGraphDataset.intermediate_conditions,
        )
        options["track_conditions"] = (HeteroGraphDataset.track_conditions,)
        options["edge_conditions"] = (HeteroGraphDataset.edge_conditions,)

        filehandler = open(self.processed_paths[2], "wb")
        pickle.dump(options, filehandler)


# class GraphDataset(InMemoryDataset):

#     particles_involved = [1, 2]
#     fully_reco = False
#     max_N_samples_per = 1000
#     path = ""

#     def __init__(
#         self,
#         root,  # storage location
#         max_N_samples_per=-1,  # limit to number of graphs to create
#         fully_reco=False,
#         force_reload=False,
#         path="",  # path to root file
#         particles_involved=[1, 2],
#         mode="build_graphs",
#         targets_graph=[],
#         targets_node=[],
#         conditions_graph=[],
#         conditions_node=[],
#         conditions_edge=[],
#         use_weights=True,
#     ):

#         GraphDataset.particles_involved = particles_involved
#         GraphDataset.N = len(particles_involved)
#         GraphDataset.max_N_samples_per = max_N_samples_per
#         GraphDataset.fully_reco = fully_reco
#         GraphDataset.path = path
#         GraphDataset.targets_graph = targets_graph
#         GraphDataset.targets_node = targets_node
#         GraphDataset.conditions_graph = conditions_graph
#         GraphDataset.conditions_node = conditions_node
#         GraphDataset.conditions_edge = conditions_edge

#         self.use_weights = use_weights

#         super().__init__(root, force_reload=force_reload)

#         if mode == "train" or mode == "build_graphs":
#             self.load(self.processed_paths[0])
#         if mode == "test" or mode == "build_graphs":
#             self.load(self.processed_paths[1])

#         filehandler = open(self.processed_paths[2], "rb")
#         self.options = pickle.load(filehandler)

#         # # Shorten
#         # N_nodes = int(np.shape(self.data.targets)[0]/np.shape(self.data.N_daughters)[0])
#         # if N_nodes == 2: N_edges = 2
#         # if N_nodes == 3: N_edges = 6
#         # if N_nodes == 4:  N_edges = 12
#         # N_samples = np.shape(self.data.N_daughters)[0]
#         # if max_N_samples_per != -1:
#         #     if N_samples < max_N_samples_per:
#         #         pass
#         #     else:

#         #         self.data.edge_index = self.data.edge_index[:, :N_edges * max_N_samples_per]
#         #         self.data.targets = self.data.targets[:N_nodes * max_N_samples_per, :]
#         #         self.data.conditions = self.data.conditions[:N_nodes * max_N_samples_per, :]
#         #         self.data.node_targets = self.data.node_targets[:N_nodes * max_N_samples_per, :]
#         #         self.data.graph_targets = self.data.graph_targets[:max_N_samples_per, :]
#         #         self.data.N_daughters = self.data.N_daughters[:max_N_samples_per]
#         #         self.data.particles_involved = self.data.particles_involved[:max_N_samples_per]

#         #         # for a test:
#         #         # self.data.node_targets[:,1:] = torch.randn(self.data.node_targets[:, 1:].shape)/4.

#         #         print(f"Loaded only the first {max_N_samples_per} of {N_samples} graphs")

#         #         # Truncate slices
#         #         for key, slice_tensor in self.slices.items():
#         #             if key == 'edge_index':
#         #                 self.slices[key] = slice_tensor[:max_N_samples_per + 1]  # Include boundary
#         #             elif key in ['targets', 'conditions', 'node_targets']:
#         #                 self.slices[key] = slice_tensor[:N_nodes * max_N_samples_per + 1]
#         #             elif key in ['graph_targets', 'N_daughters', 'particles_involved']:
#         #                 self.slices[key] = slice_tensor[:max_N_samples_per + 1]

#     @property
#     def processed_file_names(self):
#         return ["data.pt", "data_val.pt", "options.pt"]

#     def process(self):

#         data_list = []
#         data_list_val = []

#         if GraphDataset.fully_reco:
#             cut = "fully_reco>0.5"
#         else:
#             cut = "fully_reco<0.5"

#         data_handler = DataHandler(
#             particles_involved=GraphDataset.particles_involved,
#             path=GraphDataset.path,
#             N=int(GraphDataset.max_N_samples_per),
#             targets_graph=GraphDataset.targets_graph,
#             targets_node=GraphDataset.targets_node,
#             conditions_graph=GraphDataset.conditions_graph,
#             conditions_node=GraphDataset.conditions_node,
#             conditions_edge=GraphDataset.conditions_edge,
#             graphify=True,
#             testing_frac=0.1,
#             cut=cut,
#             use_weights=self.use_weights,
#         )
#         data_list_i = data_handler.data_train
#         data_list += data_list_i

#         if self.use_weights:
#             weights = data_handler.data_train_list_weights

#         data_list_val_i = data_handler.data_test
#         data_list_val += data_list_val_i

#         self.save(data_list, self.processed_paths[0])
#         self.save(data_list_val, self.processed_paths[1])

#         options = {}
#         options["path"] = GraphDataset.path
#         options["particles_involved"] = GraphDataset.particles_involved
#         options["targets_graph"] = GraphDataset.targets_graph
#         options["targets_node"] = GraphDataset.targets_node
#         options["conditions_graph"] = GraphDataset.conditions_graph
#         options["conditions_node"] = GraphDataset.conditions_node
#         options["conditions_edge"] = GraphDataset.conditions_edge
#         options["training_weights"] = weights

#         filehandler = open(self.processed_paths[2], "wb")
#         pickle.dump(options, filehandler)

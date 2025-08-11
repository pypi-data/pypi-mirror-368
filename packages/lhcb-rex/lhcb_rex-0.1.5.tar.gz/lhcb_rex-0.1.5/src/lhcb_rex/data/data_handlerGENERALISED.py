import uproot
import lhcb_rex.settings.globals as myGlobals
from rich.progress import Progress
import torch
from torch_geometric.data import Data
from torch_geometric.loader import DataLoader as geoDataLoader
from torch.utils.data import DataLoader
import pickle
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from rich import print
from torch_geometric.data import HeteroData

# import fast_vertex_quality_training.tools.globals as myGlobals
import lhcb_rex.data.loader as loader
import pandas as pd
import itertools


class StandardDataset(torch.utils.data.Dataset):
    """Dataset class for non-graph data."""

    def __init__(self, data, targets_graph, conditions_graph):
        self.graph_features_full = torch.tensor(
            data[targets_graph].values, dtype=torch.float
        )  # .to(myGlobals.device)
        self.graph_conditions_full = torch.tensor(
            data[conditions_graph].values, dtype=torch.float
        )  # .to(myGlobals.device)

        self.targets_graph = targets_graph
        self.conditions_graph = conditions_graph

    def __len__(self):
        return self.graph_features_full.shape[0]

    def __getitem__(self, idx):
        return {
            "targets": self.graph_features_full[idx],
            "conditions": self.graph_conditions_full[idx],
        }


class CustomHeteroData(HeteroData):
    def __init__(self):
        super().__init__()

    def __inc__(self, key, value, store=None):
        """
        Customizes how to adjust the node indices for each batch.
        Returns the increment tensor to adjust node indices when batching.
        """
        try:
            return super().__inc__(key, value, store)
        except Exception:
            store = store["edge_index"]
            return super().__inc__(key, value, store)


class HeteroDataHandlerGENERALISED:
    def __init__(
        self,
        config,
        path,
        N=-1,
        entry_start=-1,
        mother_targets=[],
        intermediate_targets=[],
        track_targets=[],
        mother_conditions=[],
        intermediate_conditions=[],
        track_conditions=[],
        edge_conditions=[],
        inference=False,
        testing_frac=0.1,
        cut="",
        use_weights=True,
        splits=1,
        processID=-1,
        smearingnet=False,
        PIDnet=False,
        require_validation_variables=False,
        graphify=True,
    ):
        self.printed = False
        self.smearingnet = smearingnet
        self.PIDnet = PIDnet

        self.use_weights = use_weights

        self.first_row_printed = False

        self.config = config

        self.config["edge_index_tensors_up"] = self.convert_edge_index_tensors(
            self.config["edge_index_tensors_up"]
        )
        self.config["edge_index_tensors_down"] = self.convert_edge_index_tensors(
            self.config["edge_index_tensors_down"]
        )

        self.particles_involved = [
            i for i in self.config["branches"].keys() if "DAUGHTER" in i
        ]
        self.intermediates = [
            i for i in self.config["branches"].keys() if "INTERMEDIATE" in i
        ]
        self.N_daughters = len(self.particles_involved)

        # self.intermediates = ['INTERMEDIATE']

        print(self.config["full_list_of_decays_i"])
        # particle_labels mother 0

        # self.config['structure']

        self.mother_N = 0
        self.intermediate_N = {}
        for intermediate in self.intermediates:
            self.intermediate_N[intermediate] = 0
        for edge in self.config["structure"]:
            if edge[0] == 0:
                self.mother_N += 1
            for intermediate_idx in range(len(self.intermediates)):
                if edge[0] == intermediate_idx + 1 + self.N_daughters:
                    self.intermediate_N[self.intermediates[intermediate_idx]] += 1

        self.mother_targets = mother_targets

        self.full_track_targets = []
        self.track_targets = track_targets
        for i in self.particles_involved:
            for ii in track_targets:
                self.full_track_targets.append(ii.replace("DAUGHTERN", f"{i}"))

        self.full_track_conditions = []
        self.track_conditions = track_conditions
        for i in self.particles_involved:
            for ii in track_conditions:
                if "DAUGHTERN" in ii:
                    self.full_track_conditions.append(ii.replace("DAUGHTERN", f"{i}"))
                else:
                    self.full_track_conditions.append(ii)

        self.edge_conditions = []
        self.len_edge_conditions = len(edge_conditions)
        if len(edge_conditions) > 0:
            for idx_i, i in enumerate(self.particles_involved):
                for idx_j, j in enumerate(self.particles_involved):
                    if idx_i != idx_j:
                        for ii in edge_conditions:
                            self.edge_conditions.append(
                                ii.replace("DAUGHTERN_DAUGHTERN", f"{i}_{j}")
                            )

        self.mother_conditions = [
            i.replace("N_daughters", "MOTHER_N_daughters") for i in mother_conditions
        ]

        self.full_intermediate_targets = []
        self.full_intermediate_conditions = []
        self.intermediate_targets = intermediate_targets
        self.intermediate_conditions = intermediate_conditions
        self.intermediate_names = []
        for idx, i in enumerate(self.intermediates):
            for ii in intermediate_targets:
                self.full_intermediate_targets.append(
                    ii.replace("INTERMEDIATE", f"{i}")
                )
            for ii in intermediate_conditions:
                self.full_intermediate_conditions.append(
                    ii.replace("INTERMEDIATE", f"{i}").replace(
                        "N_daughters", f"{i}_N_daughters"
                    )
                )

            self.intermediate_names.append(f"{i}")

        self.graphify = graphify

        print("\n track_targets:", self.full_track_targets)
        print("\n mother_targets:", self.mother_targets)
        print("\n intermediate_targets:", self.full_intermediate_targets)
        print("\n track_conditions:", self.full_track_conditions)
        print("\n mother_conditions:", self.mother_conditions)
        print("\n intermediate_conditions:", self.full_intermediate_conditions)
        print("\n edge_conditions:", self.edge_conditions)

        file = uproot.open(path)["DecayTree"]
        branches = (
            self.full_track_targets
            + self.mother_targets
            + self.full_intermediate_targets
            + self.full_track_conditions
            + self.mother_conditions
            + self.full_intermediate_conditions
            + self.edge_conditions
        )
        self.require_validation_variables = require_validation_variables
        if self.require_validation_variables:
            branches.extend(myGlobals.validation_variables)

        if self.use_weights:
            branches += ["weight"]
        branches += ["fully_reco"]

        if entry_start == -1:
            entry_start = None
        else:
            N += entry_start

        load_branches = branches
        print("loading events")
        print(f"file.num_entries: {file.num_entries}")

        if processID != -1:
            print(f"processID: {processID}")
            self.num_entries = file.num_entries
            print(f"num_entries, {self.num_entries}")
            self.num_entries_per_split = int(np.floor(self.num_entries / splits)) + 1
            start_entry = self.num_entries_per_split * processID
            end_entry = min(
                self.num_entries - 1, self.num_entries_per_split * (processID + 1)
            )
            if N != -1:
                end_entry = start_entry + N
            print(f"start_entry, {start_entry}")
            print(f"end_entry, {end_entry}")
        else:
            start_entry, end_entry = (
                entry_start,
                None if cut != "" or N <= 0 or N > file.num_entries else N,
            )

        if self.smearingnet or self.PIDnet:
            extra_PID_branches = [
                f"DAUGHTER{D + 1}_TRUEID" for D in range(self.N_daughters)
            ]
            load_branches += extra_PID_branches

        branches_to_array = [b for b in load_branches if "N_daughters" not in b]
        branches_to_array = list(np.unique(branches_to_array))
        events = file.arrays(
            branches_to_array,
            library="pd",
            entry_start=start_entry,
            entry_stop=end_entry,
        )

        print("events loaded")

        print(events.shape, cut)

        events = events.loc[:, ~events.columns.str.contains("^Unnamed")]

        if cut != "" and processID == -1:
            events = events.query(cut)
            events = events.reset_index(drop=True)
            events = events.head(N)

        events["MOTHER_N_daughters"] = self.mother_N
        branches += ["MOTHER_N_daughters"]
        for intermediate in self.intermediates:
            events[f"{intermediate}_N_daughters"] = self.intermediate_N[intermediate]
            branches += [f"{intermediate}_N_daughters"]

        self.data = loader.Dataset(
            particles_involved=self.particles_involved, filename=path
        )

        if inference:
            self.branches = branches
            self.data.fill(events, testing_frac=0.0)
            return
        self.data.fill(events, testing_frac=testing_frac)

        # print(branches)
        # for key in self.data.all_data["physical"].keys():
        # # for key in self.data.all_data["processed"].keys():
        #     print(key)
        # quit()
        data_train = self.data.get_branches(branches, option="training")
        data_test = self.data.get_branches(branches, option="testing")

        # data_train.to_pickle("data_train.pkl")
        # branches = [
        #     "DAUGHTER1_delta_PX",
        #     "DAUGHTER1_delta_PY",
        #     "DAUGHTER1_delta_PZ",
        #     "DAUGHTER1_TRACK_CHI2NDOF",
        #     "DAUGHTER1_TRACK_GhostProb",
        #     "DAUGHTER1_TRUEP_X",
        #     "DAUGHTER1_TRUEP_Y",
        #     "DAUGHTER1_TRUEP_Z",
        #     "DAUGHTER1_TRUEP",
        #     "DAUGHTER1_TRUEE",
        #     "DAUGHTER1_TRUEID",
        # ]
        # print(data_train.shape)
        # with PdfPages("making_graphs.pdf") as pdf:
        #     data_train_i = data_train.query('DAUGHTER1_TRUEID==-1')
        #     print(data_train_i.shape)
        #     for branch in data_train_i:
        #         if branch in branches and "TRUEID" not in branch:

        #             plt.title(branch)
        #             plt.hist(data_train_i[branch], bins=35)
        #             pdf.savefig(bbox_inches="tight")
        #             plt.close()
        # print('data_handlerGENERALISED.py')
        # quit()

        if self.smearingnet or self.PIDnet:
            self.extra_PID_branches = []
            for D in range(self.N_daughters):
                self.extra_PID_branches.append(f"DAUGHTER{D + 1}_TRUEID")
            data_train = data_train.drop(self.extra_PID_branches, axis=1)
            data_train_extra = self.data.get_branches(
                self.extra_PID_branches, option="training", processed=False
            )
            data_train = data_train.reset_index(drop=True)
            data_train_extra = data_train_extra.reset_index(drop=True)
            data_train = pd.concat((data_train, data_train_extra), axis=1)
            data_test = data_test.drop(self.extra_PID_branches, axis=1)
            data_test_extra = self.data.get_branches(
                self.extra_PID_branches, option="testing", processed=False
            )
            data_test = data_test.reset_index(drop=True)
            data_test_extra = data_test_extra.reset_index(drop=True)
            data_test = pd.concat((data_test, data_test_extra), axis=1)

        print(data_train)
        print(data_train.keys())

        if splits != 1 and processID == -1:
            print(
                f"Requested {splits} splits, exiting before making graphs, make graphs with make_split()"
            )
            self.data_train = data_train
            self.data_test = data_test

            self.data_train_N = self.data_train.shape[0]
            self.data_test_N = self.data_test.shape[0]
            self.N_train_per_split = int(np.floor(self.data_train_N / splits)) + 1
            self.N_test_per_split = int(np.floor(self.data_test_N / splits)) + 1

            return

        # data_train.to_pickle("./info_that_goes_into_graph.pkl")
        # data_train = self.data.get_branches(branches, option="training", processed=False)
        # data_train.to_pickle("./info_that_goes_into_graph_physical.pkl")
        # quit()
        # print(data_train["edge_angle_DAUGHTER1_DAUGHTER3"])
        # print(data_train["edge_angle_DAUGHTER2_DAUGHTER3"])
        # quit()

        # print(np.unique(data_train['DAUGHTER1_TRUEID']))
        # data_train_np = self.data.get_branches(branches, option="training", processed=False)
        # print(np.unique(data_train_np['DAUGHTER1_TRUEID']))

        # for key in data_train.keys():
        #     if 'N_daughters' in key:
        #         print(key)
        # quit()
        # quit()
        if self.graphify:
            data_train_list = []
            data_train_list_weights = []
            data_train_list_full_reco = []
            with Progress() as progress:
                task = progress.add_task(
                    "Processing graphs (train)...", total=len(data_train)
                )

                for _, row in data_train.iterrows():
                    if self.smearingnet or self.PIDnet:
                        graph_i = self.create_data_from_row_smearingnet(row)
                    else:
                        # graph_i = self.create_data_from_row_uniquetracks(row)
                        graph_i = self.create_data_from_row(row)
                    if graph_i is not None:
                        data_train_list.append(graph_i)
                        if self.use_weights:
                            data_train_list_weights.append(row.weight)
                            # if not self.smearingnet and not self.PIDnet:
                            data_train_list_full_reco.append(row.fully_reco)
                    progress.update(task, advance=1)

            # torch.save((data_train_list, data_train), "data.pkl")
            print(f"(data_train_list length) {len(data_train_list)}")
            data_test_list = []
            data_test_list_full_reco = []
            with Progress() as progress:
                task = progress.add_task(
                    "Processing graphs (test)...", total=len(data_test)
                )

                for _, row in data_test.iterrows():
                    if self.smearingnet or self.PIDnet:
                        graph_i = self.create_data_from_row_smearingnet(row)
                    else:
                        # graph_i = self.create_data_from_row_uniquetracks(row)
                        graph_i = self.create_data_from_row(row)
                    if graph_i is not None:
                        data_test_list.append(graph_i)
                        # if not self.smearingnet and not self.PIDnet:
                        data_test_list_full_reco.append(row.fully_reco)
                    progress.update(task, advance=1)
            # torch.save((data_test_list, data_test), "data_test.pkl")

            self.data_train = data_train_list
            self.data_test = data_test_list
            self.data_train_list_full_reco = data_train_list_full_reco
            self.data_test_list_full_reco = data_test_list_full_reco
            if self.use_weights:
                self.data_train_list_weights = data_train_list_weights

        else:
            self.data_train = data_train
            self.data_test = data_test
            self.data_test_raw = data_test

    def convert_edge_index_tensors(self, edge_index_dict):
        empty = torch.tensor([[], []], dtype=torch.long)
        converted = {}

        for edge_type, edge_lists in edge_index_dict.items():
            converted[edge_type] = []
            for edge_list in edge_lists:
                if len(edge_list) == 0:
                    converted[edge_type].append(empty)
                else:
                    edge_tensor = (
                        torch.tensor(edge_list, dtype=torch.long).t().contiguous()
                    )
                    converted[edge_type].append(edge_tensor)

        return converted

    def make_split(self, split):
        start = self.N_train_per_split * split
        end = self.N_train_per_split * (split + 1)
        if end >= self.data_train_N:
            end = self.data_train_N - 1
        print(split, start, end, f"N: {end - start}")
        data_train_i = self.data_train.iloc[int(start) : int(end)]

        start = self.N_test_per_split * split
        end = self.N_test_per_split * (split + 1)
        if end >= self.data_test_N:
            end = self.data_test_N - 1
        print(split, start, end, f"N: {end - start}")
        data_test_i = self.data_test.iloc[int(start) : int(end)]

        data_train_list = []
        data_train_list_weights = []
        with Progress() as progress:
            task = progress.add_task(
                "Processing graphs (train)...", total=len(data_train_i)
            )

            for _, row in data_train_i.iterrows():
                if self.smearingnet or self.PIDnet:
                    graph_i = self.create_data_from_row_smearingnet(row)
                else:
                    # graph_i = self.create_data_from_row_uniquetracks(row)
                    graph_i = self.create_data_from_row(row)
                if graph_i is not None:
                    data_train_list.append(graph_i)
                    if self.use_weights:
                        data_train_list_weights.append(row.weight)
                progress.update(task, advance=1)

        data_test_list = []
        with Progress() as progress:
            task = progress.add_task(
                "Processing graphs (test)...", total=len(data_test_i)
            )

            for _, row in data_test_i.iterrows():
                if self.smearingnet or self.PIDnet:
                    graph_i = self.create_data_from_row_smearingnet(row)
                else:
                    # graph_i = self.create_data_from_row_uniquetracks(row)
                    graph_i = self.create_data_from_row(row)
                if graph_i is not None:
                    data_test_list.append(graph_i)
                progress.update(task, advance=1)

        self.data_train_i = data_train_list
        self.data_test_i = data_test_list
        if self.use_weights:
            self.data_train_list_weights_i = data_train_list_weights

    def plot(
        self,
        filename,
        variables=None,
        overlay=None,
        bins=50,
        label=None,
    ):
        if overlay:
            if not isinstance(overlay, list):
                overlay = [overlay]

        if variables is None:
            variables = list(self.data.all_data["physical"].keys())

        with PdfPages(filename) as pdf:
            for variable in variables:
                try:
                    plt.figure(figsize=(10, 8))

                    plt.subplot(2, 2, 1)
                    plt.title(variable)
                    if overlay:
                        info = [self.data.all_data["physical"][variable]]
                        for overlay_i in overlay:
                            info.append(overlay_i.data.all_data["physical"][variable])
                        plt.hist(
                            info, bins=bins, density=True, histtype="step", label=label
                        )
                    else:
                        plt.hist(
                            self.data.all_data["physical"][variable],
                            bins=bins,
                            density=True,
                            histtype="step",
                            label=label,
                        )

                    if label:
                        plt.legend()

                    plt.subplot(2, 2, 2)
                    plt.title(f"{variable} processed")
                    if overlay:
                        info = [self.data.all_data["processed"][variable]]
                        for overlay_i in overlay:
                            info.append(overlay_i.data.all_data["processed"][variable])
                        plt.hist(info, bins=bins, density=True, histtype="step")
                    else:
                        plt.hist(
                            self.data.all_data["processed"][variable],
                            bins=bins,
                            density=True,
                            histtype="step",
                            range=[-1, 1],
                        )

                    plt.subplot(2, 2, 3)
                    if overlay:
                        info = [self.data.all_data["physical"][variable]]
                        for overlay_i in overlay:
                            info.append(overlay_i.all_data["physical"][variable])
                        plt.hist(info, bins=bins, density=True, histtype="step")
                    else:
                        plt.hist(
                            self.data.all_data["physical"][variable],
                            bins=bins,
                            density=True,
                            histtype="step",
                        )
                    plt.yscale("log")

                    plt.subplot(2, 2, 4)
                    if overlay:
                        info = [self.data.all_data["processed"][variable]]
                        for overlay_i in overlay:
                            info.append(overlay_i.data.all_data["processed"][variable])
                        plt.hist(info, bins=bins, density=True, histtype="step")
                    else:
                        plt.hist(
                            self.data.all_data["processed"][variable],
                            bins=bins,
                            density=True,
                            histtype="step",
                            range=[-1, 1],
                        )
                    plt.yscale("log")

                    pdf.savefig(bbox_inches="tight")
                    plt.close()

                except Exception:
                    pdf.savefig(bbox_inches="tight")
                    plt.close()
                    pass

    def save_graphs(self, save_loc):
        data = {
            "data_train": self.data_train,
            "data_test": self.data_test,
        }

        # Save the dictionary to a .pkl file
        with open(save_loc, "wb") as f:
            pickle.dump(data, f)

    def load_graphs(self, save_loc):
        # Load the data from the specified .pkl file
        with open(save_loc, "rb") as f:
            data = pickle.load(f)

        # Assign loaded data to the corresponding attributes
        self.data_train = data.get("data_train")
        self.data_test = data.get("data_test")

    def create_data_from_row(self, row):
        nan_cols = row.index[row.isna()].tolist()  # Get column names with NaNs
        if nan_cols:  # If there are any NaNs
            print(f"Row has NaNs in columns: {nan_cols}")
            return None

        data = CustomHeteroData()  # allows for edge_index to be list

        track_targets = torch.tensor(
            row[self.full_track_targets].values, dtype=torch.float
        )
        track_targets = track_targets.view(-1, len(self.track_targets))
        data["track"].x = track_targets  # [num_tracks, track_targets]
        track_conditions = torch.tensor(
            row[self.full_track_conditions].values, dtype=torch.float
        )
        track_conditions = track_conditions.view(-1, len(self.track_conditions))
        data["track_conditions"].x = track_conditions  # [num_tracks, track_conditions]

        if len(self.full_intermediate_targets) > 0:
            intermediate_targets = torch.tensor(
                row[self.full_intermediate_targets].values, dtype=torch.float
            )
            intermediate_targets = intermediate_targets.view(
                -1, len(self.intermediate_targets)
            )
            data[
                "intermediate"
            ].x = intermediate_targets  # [num_intermediates, intermediate_targets]

            intermediate_conditions = torch.tensor(
                row[self.full_intermediate_conditions].values, dtype=torch.float
            )
            intermediate_conditions = intermediate_conditions.view(
                -1, len(self.intermediate_conditions)
            )

            if "N_daughters" in self.intermediate_conditions:
                idx = self.intermediate_conditions.index("N_daughters")
                for int_idx, N in enumerate(self.intermediate_N):
                    intermediate_conditions[int_idx][idx] = self.intermediate_N[N]
            data[
                "intermediate_conditions"
            ].x = (
                intermediate_conditions  # [num_intermediates, intermediate_conditions]
            )
        # print(intermediate_conditions)

        if len(self.mother_targets) > 0:
            mother_targets = torch.tensor(
                row[self.mother_targets].values, dtype=torch.float
            )
            mother_targets = mother_targets.view(-1, len(self.mother_targets))
            data["mother"].x = mother_targets  # [num_mothers, mother_targets]
            mother_conditions = torch.tensor(
                row[self.mother_conditions].values, dtype=torch.float
            )
            mother_conditions = mother_conditions.view(-1, len(self.mother_conditions))
            if "N_daughters" in self.mother_conditions:
                idx = self.mother_conditions.index("N_daughters")
                mother_conditions[0][idx] = self.mother_N
            data[
                "mother_conditions"
            ].x = mother_conditions  # [num_mothers, mother_conditions]
        # print(mother_conditions)
        # quit()
        if self.require_validation_variables:
            validation_variables = torch.tensor(
                row[myGlobals.validation_variables].values, dtype=torch.float
            )
            data["validation_variables"].x = validation_variables

        empty = torch.tensor([[], []], dtype=torch.long)

        int_self_loops = []
        for idx, intermediate in enumerate(self.intermediates):
            int_self_loops.append([idx, idx])
        daught_self_loops = []
        for idx, daughter in enumerate(self.particles_involved):
            daught_self_loops.append([idx, idx])

        data["track", "self", "track"].edge_index = (
            torch.tensor(daught_self_loops, dtype=torch.long).t().contiguous()
        )
        if int_self_loops != []:
            data["intermediate", "self", "intermediate"].edge_index = (
                torch.tensor(int_self_loops, dtype=torch.long).t().contiguous()
            )
        else:
            data["intermediate", "self", "intermediate"].edge_index = empty

        data["mother", "self", "mother"].edge_index = (
            torch.tensor([[0, 0]], dtype=torch.long).t().contiguous()
        )

        for edge_type in self.config["edge_index_tensors_up"]:
            data[edge_type].edge_index = self.config["edge_index_tensors_up"][edge_type]
        for edge_type in self.config["edge_index_tensors_down"]:
            data[edge_type].edge_index = self.config["edge_index_tensors_down"][
                edge_type
            ]

        daught_self_loops = []
        for idx, daughter in enumerate(self.particles_involved):
            daught_self_loops.append([idx, idx])

        data["track_conds", "self", "track"].edge_index = data[
            "track", "self", "track"
        ].edge_index
        data["intermediate_conds", "self", "intermediate"].edge_index = data[
            "intermediate", "self", "intermediate"
        ].edge_index
        data["mother_conds", "self", "mother"].edge_index = data[
            "mother", "self", "mother"
        ].edge_index

        return data

    def create_data_from_row_smearingnet(self, row):
        # print('\n\n\n')
        # print(row)
        # print(self.edge_conditions)
        # quit()

        particle_types = ["11", "13", "211", "321", "2212"]
        # particle_types = ["11", "13", "211", "321"]

        nan_cols = row.index[row.isna()].tolist()  # Get column names with NaNs
        if nan_cols:  # If there are any NaNs
            print(f"Row has NaNs in columns: {nan_cols}")
            return None

        data = CustomHeteroData()  # allows for edge_index to be list

        track_targets = torch.tensor(
            row[self.full_track_targets].values, dtype=torch.float
        )
        track_targets = track_targets.view(-1, len(self.track_targets))
        track_conditions = torch.tensor(
            row[self.full_track_conditions].values, dtype=torch.float
        )
        track_conditions = track_conditions.view(-1, len(self.track_conditions))

        for particle_type in particle_types:
            data[particle_type].x = torch.empty(
                (0, track_targets.shape[-1]), dtype=torch.long
            )
            data[f"{particle_type}_conditions"].x = torch.empty(
                (0, track_conditions.shape[-1]), dtype=torch.long
            )
            data[f"{particle_type}_trackidx"].x = torch.empty((0), dtype=torch.long)

        track_PIDs = np.abs(np.asarray(row[self.extra_PID_branches].values)).astype(int)

        for track_global_index, track_PID in enumerate(track_PIDs):
            data[str(track_PID)].x = torch.cat(
                (
                    data[str(track_PID)].x,
                    torch.unsqueeze(track_targets[track_global_index], dim=0),
                ),
                dim=0,
            )
            data[f"{str(track_PID)}_conditions"].x = torch.cat(
                (
                    data[f"{str(track_PID)}_conditions"].x,
                    torch.unsqueeze(track_conditions[track_global_index], dim=0),
                ),
                dim=0,
            )
            track_global_index = torch.tensor([track_global_index], dtype=torch.long)
            data[f"{str(track_PID)}_trackidx"].x = torch.cat(
                (data[f"{str(track_PID)}_trackidx"].x, track_global_index), dim=0
            )

        ordered_pairs = list(itertools.product(particle_types, repeat=2))

        for pair in ordered_pairs:
            data[pair[0], "to", pair[1]].edge_index = torch.empty(
                (2, 0), dtype=torch.long
            )
            data[pair[0], "to", pair[1]].edge_attr = torch.empty(
                (0, self.len_edge_conditions), dtype=torch.long
            )

        edges_by_index = list(itertools.product(range(len(track_PIDs)), repeat=2))

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
                edge_i = torch.tensor(
                    [[origin_idx, destination_idx]], dtype=torch.long
                ).t()
                data[origin, "to", destination].edge_index = torch.cat(
                    (data[origin, "to", destination].edge_index, edge_i), dim=1
                )

                edge_attr_i = torch.tensor(
                    [
                        row[
                            f"edge_angle_DAUGHTER{edge_by_index[0] + 1}_DAUGHTER{edge_by_index[1] + 1}_TRUE"
                        ]
                    ],
                    dtype=torch.float,
                ).unsqueeze(0)
                data[origin, "to", destination].edge_attr = torch.cat(
                    (data[origin, "to", destination].edge_attr, edge_attr_i), dim=0
                )

        return data

    def create_graphs(
        self,
        targets_graph,
        targets_node,
        conditions_graph,
        conditions_node,
        N_daughters_override=None,
        fully_reco_override=None,
    ):  # used by inference.py
        self.targets_graph = targets_graph
        self.targets_node = targets_node
        self.conditions_graph = conditions_graph
        self.conditions_node = conditions_node

        branches = (
            self.targets_graph
            + self.targets_node
            + self.conditions_graph
            + self.conditions_node
        )

        data_test = self.data.get_branches(branches)

        if N_daughters_override is not None:
            data_test["N_daughters"] = N_daughters_override
        if fully_reco_override is not None:
            data_test["fully_reco"] = fully_reco_override

        data_test_list = []
        with Progress() as progress:
            task = progress.add_task(
                "Processing graphs (test)...", total=len(data_test)
            )

            for _, row in data_test.iterrows():
                if self.smearingnet:
                    data_test_list.append(self.create_data_from_row_smearingnet(row))
                else:
                    # data_test_list.append(self.create_data_from_row_uniquetracks(row))
                    data_test_list.append(self.create_data_from_row(row))
                progress.update(task, advance=1)

        self.data_test = data_test_list
        self.data_test_raw = data_test

        return len(data_test_list)

    def get_loaders(
        self, batch_size, only_test=False, graphify=False
    ):  # used by inference.py
        if graphify:
            self.graphify = graphify

        if self.graphify:
            if not only_test:
                loader_train = geoDataLoader(
                    self.data_train, batch_size=batch_size, shuffle=True
                )
            test_batch_size = len(self.data_test)
            loader_test = geoDataLoader(
                self.data_test, batch_size=test_batch_size, shuffle=False
            )
        else:
            if not only_test:
                train_dataset = StandardDataset(
                    self.data_train, self.targets_graph, self.conditions_graph
                )
                loader_train = DataLoader(
                    train_dataset, batch_size=batch_size, shuffle=True
                )

            test_dataset = StandardDataset(
                self.data_test, self.targets_graph, self.conditions_graph
            )
            test_batch_size = len(test_dataset)
            loader_test = DataLoader(
                test_dataset, batch_size=test_batch_size, shuffle=False
            )
        if only_test:
            return loader_test
        else:
            return loader_train, loader_test, self.data_test_raw, test_batch_size

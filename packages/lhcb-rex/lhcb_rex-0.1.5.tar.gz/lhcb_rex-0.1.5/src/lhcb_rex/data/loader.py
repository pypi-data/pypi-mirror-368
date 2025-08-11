import lhcb_rex.settings.globals as myGlobals
import pandas as pd
import numpy as np
import lhcb_rex.processing.transformers as tfs
import pickle
import re
import uproot
import importlib.resources


class NoneError(Exception):
    pass


class Dataset:
    def __init__(self, particles_involved, filename, transformers=None):
        self.Transformers = transformers

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

        self.all_data = {"processed": None, "physical": None}

        self.filename = filename

        self.mother_particle = "MOTHER"
        self.daughter_particles = []
        for idx in particles_involved:
            self.daughter_particles.append(f"DAUGHTER{idx}")

    def pre_process(self, physical_data):
        df = {}

        if self.Transformers is None:
            self.Transformers = {}

        for column in list(physical_data.keys()):
            if column[:4] == "edge":
                transformer_column = re.sub(
                    r"DAUGHTER\d+_DAUGHTER\d+", "DAUGHTERN_DAUGHTERN", column
                )
            else:
                transformer_column = re.sub(r"DAUGHTER\d+", "DAUGHTER1", column)
                # transformer_column = re.sub(r"INTERMEDIATE\d+", "INTERMEDIATE", transformer_column)
                transformer_column = re.sub(
                    r"INTERMEDIATE\d+", "MOTHER", transformer_column
                )
                transformer_column = re.sub(
                    r"delta_\d+_P", "delta_0_P", transformer_column
                )
                transformer_column = re.sub(
                    r"delta_\d+_PT", "delta_0_PT", transformer_column
                )

            # print(column, transformer_column)
            if (  # personalised transformers
                "residualfrac" in column
                or "_Preco_overP" in column
                or "delta_PX" in column
                or "delta_PY" in column
                or "delta_PZ" in column
                or re.search("_PID.", column)
                or re.search("_ProbNN.", column)
                or "TRACK_CHI2NDOF" in column
                or "TRACK_GhostProb" in column
            ) and myGlobals.personalised_track_node_types:
                print(f"using personalised_track_node_types {column}")
                physical_data_i = np.asarray(physical_data[column]).copy()
                pid_column = np.abs(
                    np.asarray(physical_data[f"{column[:9]}_TRUEID"]).copy()
                )

                try:
                    out = np.zeros_like(physical_data_i)
                    for particle_type in [11, 13, 211, 321, 2212]:
                        where = np.where(pid_column == particle_type)
                        out[where] = self.Transformers[
                            f"{transformer_column}_{particle_type}"
                        ].process(physical_data_i[where])
                    df[column] = out

                except Exception:
                    # print(f"FAIL, {column}")
                    pass
            else:
                print(f"not using personalised_track_node_types {column}")
                physical_data_i = np.asarray(physical_data[column]).copy()

                if (
                    column == "file"
                    or column == "pass_stripping"
                    or column == "training_weight"
                    or column == "weight"
                    or column == "in_training"
                    or "N_daughters" in column
                    or column == "fully_reco"
                    or column in myGlobals.validation_variables
                ):
                    df[column] = physical_data_i
                if "DAUGHTER" in column and "_TRUEID" in column:
                    df[column] = self.Transformers[transformer_column].process(
                        physical_data_i
                    )
                else:
                    try:
                        df[column] = self.Transformers[transformer_column].process(
                            physical_data_i
                        )
                    except Exception:
                        # print(f"FAIL, {column}")
                        pass

        return pd.DataFrame.from_dict(df)

    def produce_physics_variables(self):
        for particle_i in self.daughter_particles:
            self.all_data["physical"][f"{particle_i}_P"] = np.sqrt(
                self.all_data["physical"][f"{particle_i}_PX"] ** 2
                + self.all_data["physical"][f"{particle_i}_PY"] ** 2
                + self.all_data["physical"][f"{particle_i}_PZ"] ** 2
            )

            self.all_data["physical"][f"{particle_i}_PT"] = np.sqrt(
                self.all_data["physical"][f"{particle_i}_PX"] ** 2
                + self.all_data["physical"][f"{particle_i}_PY"] ** 2
            )

            self.all_data["physical"][f"{particle_i}_TRUE_P"] = np.sqrt(
                self.all_data["physical"][f"{particle_i}_TRUEP_X"] ** 2
                + self.all_data["physical"][f"{particle_i}_TRUEP_Y"] ** 2
                + self.all_data["physical"][f"{particle_i}_TRUEP_Z"] ** 2
            )

            self.all_data["physical"][f"{particle_i}_TRUEP_T"] = np.sqrt(
                self.all_data["physical"][f"{particle_i}_TRUEP_X"] ** 2
                + self.all_data["physical"][f"{particle_i}_TRUEP_Y"] ** 2
            )

            self.all_data["physical"][f"{particle_i}_eta"] = -np.log(
                np.tan(
                    np.arcsin(
                        self.all_data["physical"][f"{particle_i}_PT"]
                        / self.all_data["physical"][f"{particle_i}_P"]
                    )
                    / 2.0
                )
            )

            self.all_data["physical"][f"{particle_i}_eta_TRUE"] = -np.log(
                np.tan(
                    np.arcsin(
                        self.all_data["physical"][f"{particle_i}_TRUEP_T"]
                        / self.all_data["physical"][f"{particle_i}_TRUE_P"]
                    )
                    / 2.0
                )
            )

        self.all_data["physical"]["kFold"] = np.random.randint(
            low=0,
            high=9,
            size=np.shape(
                self.all_data["physical"][f"{self.daughter_particles[0]}_PX"]
            )[0],
        )

    def check_TRUE_branches(self):
        for particle in self.daughter_particles + [self.mother_particle]:
            for dim in ["X", "Y", "Z"]:
                if f"{particle}_TRUEP_{dim}" not in list(
                    self.all_data["physical"].keys()
                ):
                    self.all_data["physical"][f"{particle}_TRUEP_{dim}"] = (
                        1000.0 * self.all_data["physical"][f"{particle}_P{dim}_TRUE"]
                    )
                    self.all_data["physical"][f"{particle}_P{dim}"] = (
                        1000.0 * self.all_data["physical"][f"{particle}_P{dim}"]
                    )
            if f"{particle}_TRUEID" not in list(self.all_data["physical"].keys()):
                self.all_data["physical"][f"{particle}_TRUEID"] = self.all_data[
                    "physical"
                ][f"{particle}_ID_TRUE"]
            if f"{particle}_mass" not in list(self.all_data["physical"].keys()):
                self.all_data["physical"][f"{particle}_mass"] = self.all_data[
                    "physical"
                ][f"{particle}_M"]

    def fill(self, data, testing_frac=0.1):
        if not isinstance(data, pd.DataFrame):
            raise NoneError("Dataset must be a pd.dataframe.")

        in_training = np.ones(data.shape[0])
        in_training[-int(testing_frac * data.shape[0]) :] = 0
        data["in_training"] = in_training

        self.all_data["physical"] = data

        ####
        # self.check_TRUE_branches()
        # self.produce_physics_variables()
        ####

        self.all_data["physical"] = self.all_data["physical"].loc[
            :, ~self.all_data["physical"].columns.str.contains("^Unnamed")
        ]

        self.all_data["processed"] = self.pre_process(self.all_data["physical"])

    def overwrite_branch_processed(self, data, branch):
        transformer_column = re.sub(r"DAUGHTER\d+", "DAUGHTER1", branch)
        # transformer_column = re.sub(r"INTERMEDIATE\d+", "INTERMEDIATE", transformer_column)
        transformer_column = re.sub(r"INTERMEDIATE\d+", "MOTHER", transformer_column)
        transformer_column = re.sub(r"delta_\d+_P", "delta_0_P", transformer_column)
        transformer_column = re.sub(r"delta_\d+_PT", "delta_0_PT", transformer_column)

        self.all_data["processed"][branch] = data
        self.all_data["physical"][branch] = self.Transformers[
            transformer_column
        ].unprocess(np.asarray(self.all_data["processed"][branch]).copy())

    def print_branches(self):
        for key in list(self.all_data["physical"].keys()):
            print(key)

    def get_branches(self, branches, processed=True, option=""):
        if not isinstance(branches, list):
            branches = [branches]

        if processed:
            missing = list(
                set(branches).difference(set(list(self.all_data["processed"].keys())))
            )
            branches = list(
                set(branches).intersection(set(list(self.all_data["processed"].keys())))
            )

            if len(missing) > 0:
                print(f"missing branches: {missing}\n {self.filename} \n")

            if option != "":
                output = self.all_data["processed"][branches + ["in_training"]]
            else:
                output = self.all_data["processed"][branches]

        else:
            missing = list(
                set(branches).difference(set(list(self.all_data["physical"].keys())))
            )
            branches = list(
                set(branches).intersection(set(list(self.all_data["physical"].keys())))
            )

            if len(missing) > 0:
                print(f"missing branches: {missing}\n {self.filename} \n")

            if option != "":
                output = self.all_data["physical"][branches + ["in_training"]]
            else:
                output = self.all_data["physical"][branches]

        if option == "training":
            output = output.query("in_training==1.0")
            output = output[branches]
        elif option == "testing":
            output = output.query("in_training==0.0")
            output = output[branches]

        return output

    def write_to_file(self, filename):
        print(f"Writting {filename}...")
        with uproot.recreate(filename) as new_file:
            new_file["DecayTree"] = self.all_data["physical"]
        print("Done.")

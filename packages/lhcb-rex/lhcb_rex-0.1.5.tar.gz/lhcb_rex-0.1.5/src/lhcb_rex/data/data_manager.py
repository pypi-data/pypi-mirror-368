import numpy as np
import uproot
import re
import pandas as pd

import lhcb_rex.processing.transformers as tfs
import lhcb_rex.tools.variables_tools as pts
from lhcb_rex.rapidsim.rapidsim_tools import compute_combined_param
import lhcb_rex.settings.globals as myGlobals
import lhcb_rex.tools.display as display

masses = {}
masses[321] = 493.677
masses[211] = 139.57039
masses[13] = 105.66
masses[11] = 0.51099895000  # * 1e-3
pid_list = [11, 13, 211, 321]


rapidsim_conventions = {}

rapidsim_conventions["momenta_component"] = "{particle}_P"
rapidsim_conventions["true_momenta_component"] = "{particle}_P_TRUE"

rapidsim_conventions["momenta_component"] = "{particle}_P{dim}"
rapidsim_conventions["true_momenta_component"] = "{particle}_P{dim}_TRUE"

rapidsim_conventions["pid"] = "{particle}_ID"
rapidsim_conventions["true_pid"] = "{particle}_ID_TRUE"

rapidsim_conventions["mass"] = "{particle}_M"
rapidsim_conventions["true_mass"] = "{particle}_M_TRUE"

rapidsim_conventions["origin"] = "{particle}_orig{dim}"
rapidsim_conventions["true_origin"] = "{particle}_orig{dim}_TRUE"

rapidsim_conventions["vertex"] = "{particle}_vtx{dim}"
rapidsim_conventions["true_vertex"] = "{particle}_vtx{dim}_TRUE"


class tuple_manager:
    def map_branch_names(self):
        branch_names = list(self.tuple.keys())
        branch_names = [
            branch.replace(self.mother_particle_name, self.mother)
            for branch in branch_names
        ]
        # if self.intermediate_particle_name:
        #     branch_names = [
        #         branch.replace(self.intermediate_particle_name, self.intermediate)
        #         for branch in branch_names
        #     ]
        temps = []
        for i in range(self.Nparticles):  # Nparticles
            if (
                self.particles[i] in self.daughter_particle_names
                and self.particles[i] == self.daughter_particle_names[i]
            ):
                # all good - no need really even to replace
                replace_string = self.particles[i]
            else:
                replace_string = f"{self.particles[i][0]}_temp_{self.particles[i][1:]}"
                temps.append(i)
            branch_names = [
                branch.replace(self.daughter_particle_names[i], replace_string)
                for branch in branch_names
            ]
        for i in temps:
            replace_string = f"{self.particles[i][0]}_temp_{self.particles[i][1:]}"
            branch_names = [
                branch.replace(replace_string, self.particles[i])
                for branch in branch_names
            ]
        self.tuple.columns = branch_names

    def map_branch_names_list(self, branch_names):
        branch_names = [
            branch.replace(self.mother_particle_name, self.mother)
            for branch in branch_names
        ]
        # if self.intermediate_particle_name:
        #     branch_names = [
        #         branch.replace(self.intermediate_particle_name, self.intermediate)
        #         for branch in branch_names
        #     ]

        print(myGlobals.particle_map["toDAUGHTERS"].keys())
        print(myGlobals.particle_map["fromDAUGHTERS"].keys())
        #
        quit()

        temps = []
        for i in range(self.Nparticles):  # Nparticles
            if (
                self.particles[i] in self.daughter_particle_names
                and self.particles[i] == self.daughter_particle_names[i]
            ):
                # all good - no need really even to replace
                replace_string = self.particles[i]
            else:
                replace_string = f"{self.particles[i][0]}_temp_{self.particles[i][1:]}"
                temps.append(i)
            branch_names = [
                branch.replace(self.daughter_particle_names[i], replace_string)
                for branch in branch_names
            ]
        for i in temps:
            replace_string = f"{self.particles[i][0]}_temp_{self.particles[i][1:]}"
            branch_names = [
                branch.replace(replace_string, self.particles[i])
                for branch in branch_names
            ]
        return branch_names

    # def smearelectronE(self, E_smearing_output, particle):
    #     for column in E_smearing_output.columns:
    #         dim = column[-1]
    #         self.tuple[f"{particle}_P{dim}"] = (
    #             E_smearing_output[column]
    #             * (self.tuple[f"{particle}_P{dim}_TRUE"] + 1e-4)
    #         ) + self.tuple[f"{particle}_P{dim}_TRUE"]

    # def propagate_smearing(self, smearing_output, Nparticles=3):

    #     for idx in range(Nparticles):
    #         for dim in ["X", "Y"]:
    #             self.tuple[f"DAUGHTER{idx + 1}_P{dim}"] = (
    #                 smearing_output[f"DAUGHTER{idx + 1}_delta_P{dim}"]
    #                 + self.tuple[f"DAUGHTER{idx + 1}_P{dim}_TRUE"]
    #             )

    #     for idx in range(Nparticles):
    #         true_P = np.sqrt(
    #             self.tuple[f"DAUGHTER{idx + 1}_PX_TRUE"] ** 2
    #             + self.tuple[f"DAUGHTER{idx + 1}_PY_TRUE"] ** 2
    #             + self.tuple[f"DAUGHTER{idx + 1}_PZ_TRUE"] ** 2
    #         )
    #         A_sq = smearing_output[f"DAUGHTER{idx + 1}_Preco_overP"] ** 2
    #         self.tuple[f"DAUGHTER{idx + 1}_PZ"] = np.sqrt(
    #             A_sq * true_P**2
    #             - self.tuple[f"DAUGHTER{idx + 1}_PX"] ** 2
    #             - self.tuple[f"DAUGHTER{idx + 1}_PY"] ** 2
    #         )

    #     for idx in range(Nparticles):
    #         self.tuple[f"DAUGHTER{idx + 1}_TRACK_CHI2NDOF"] = smearing_output[f"DAUGHTER{idx + 1}_TRACK_CHI2NDOF"]
    #         self.tuple[f"DAUGHTER{idx + 1}_TRACK_GhostProb"] = smearing_output[f"DAUGHTER{idx + 1}_TRACK_GhostProb"]

    def propagate_smearing(self, smearing_output, Nparticles=3):
        for idx in range(Nparticles):
            for dim in ["X", "Y", "Z"]:
                self.tuple[f"DAUGHTER{idx + 1}_P{dim}"] = (
                    smearing_output[f"DAUGHTER{idx + 1}_delta_P{dim}"]
                    + self.tuple[f"DAUGHTER{idx + 1}_P{dim}_TRUE"]
                )

        for idx in range(Nparticles):
            self.tuple[f"DAUGHTER{idx + 1}_TRACK_CHI2NDOF"] = smearing_output[
                f"DAUGHTER{idx + 1}_TRACK_CHI2NDOF"
            ]
            self.tuple[f"DAUGHTER{idx + 1}_TRACK_GhostProb"] = smearing_output[
                f"DAUGHTER{idx + 1}_TRACK_GhostProb"
            ]

        # smearing_output[f"DAUGHTER{idx + 1}_Preco_overP"]

        for idx in range(Nparticles):
            self.tuple[f"DAUGHTER{idx + 1}_P"] = np.sqrt(
                (
                    self.tuple[f"DAUGHTER{idx + 1}_PX"] ** 2
                    + self.tuple[f"DAUGHTER{idx + 1}_PY"] ** 2
                    + self.tuple[f"DAUGHTER{idx + 1}_PZ"] ** 2
                )
            )
            self.tuple[f"DAUGHTER{idx + 1}_TRUEP"] = np.sqrt(
                (
                    self.tuple[f"DAUGHTER{idx + 1}_PX_TRUE"] ** 2
                    + self.tuple[f"DAUGHTER{idx + 1}_PY_TRUE"] ** 2
                    + self.tuple[f"DAUGHTER{idx + 1}_PZ_TRUE"] ** 2
                )
            )
            self.tuple[f"DAUGHTER{idx + 1}_Preco_overP"] = (
                self.tuple[f"DAUGHTER{idx + 1}_P"]
                / self.tuple[f"DAUGHTER{idx + 1}_TRUEP"]
            )

    def recompute_combined_particles(self, combined_particles, daughter_particle_names):
        # Recompute variables of reconstructed particles
        branches = []
        for combined_particle in combined_particles:
            daughter_info = {}
            for daughter in combined_particles[combined_particle]:
                daughter_info[daughter] = {}
                for param in ["M", "PX", "PY", "PZ"]:
                    daughter_info[daughter][param] = self.tuple[f"{daughter}_{param}"]
            for param in ["M", "PX", "PY", "PZ"]:
                self.tuple[f"{combined_particle}_{param}"] = compute_combined_param(
                    daughter_info, param
                )
            self.tuple[f"{combined_particle}_P"] = np.sqrt(
                self.tuple[f"{combined_particle}_PX"] ** 2
                + self.tuple[f"{combined_particle}_PY"] ** 2
                + self.tuple[f"{combined_particle}_PZ"] ** 2
            )
            self.tuple[f"{combined_particle}_PT"] = np.sqrt(
                self.tuple[f"{combined_particle}_PX"] ** 2
                + self.tuple[f"{combined_particle}_PY"] ** 2
            )

            branches.extend([f"{combined_particle}_{param}" for param in ["P", "PT", "M", "PX", "PY", "PZ"]])
        return branches
        
    def recompute_reconstructed_mass(self):
        df = self.tuple.copy()

        for _idx, particle in enumerate(self.particles):
            if _idx == 0:
                PE = np.sqrt(
                    df[f"{particle}_M"] ** 2
                    + df[f"{particle}_PX"] ** 2
                    + df[f"{particle}_PY"] ** 2
                    + df[f"{particle}_PZ"] ** 2
                )
                PX = df[f"{particle}_PX"]
                PY = df[f"{particle}_PY"]
                PZ = df[f"{particle}_PZ"]
            else:
                PE += np.sqrt(
                    df[f"{particle}_M"] ** 2
                    + df[f"{particle}_PX"] ** 2
                    + df[f"{particle}_PY"] ** 2
                    + df[f"{particle}_PZ"] ** 2
                )
                PX += df[f"{particle}_PX"]
                PY += df[f"{particle}_PY"]
                PZ += df[f"{particle}_PZ"]

        mass = np.sqrt((PE**2 - PX**2 - PY**2 - PZ**2))

        return mass

    def ensure_consistent_final_state(self, tag=""):
        indices_to_drop = set()  # Store indices to drop later

        true_PID_scheme = {}
        for idx, particle in enumerate(self.particles):
            masses = np.ones_like(self.tuple[f"{tag}{particle}_ID_TRUE"])
            PIDs_present = []

            for PID in myGlobals.particle_universe:
                where = np.where(
                    np.abs(self.tuple[f"{tag}{particle}_ID_TRUE"].astype(int)) == PID
                )
                masses[where] = myGlobals.masses[PID]
                if np.shape(where)[1] > 0:
                    PIDs_present.append(PID)

            if len(PIDs_present) != 1:
                display.warning_print(PIDs_present)
                PIDs_present, counts = np.unique(
                    np.abs(self.tuple[f"{tag}{particle}_ID_TRUE"].astype(int)),
                    return_counts=True,
                )
                where = np.where(counts == np.amax(counts))
                select = PIDs_present[where][0]

                display.warning_print(
                    "WARNING: particle type cannot change, TRUEID for each final state particle must be the same throughout the tuple."
                )
                display.warning_print(
                    f"present in {particle} {PIDs_present} (counts: {counts})"
                )
                display.warning_print(
                    f"Marking rows for removal where {tag}{particle}_ID_TRUE != {select}"
                )

                # Identify indices to drop
                drop_indices = self.tuple.index[
                    np.abs(self.tuple[f"{tag}{particle}_ID_TRUE"]) != select
                ].tolist()
                indices_to_drop.update(drop_indices)

            true_PID_scheme[particle] = np.abs(
                self.tuple[f"{tag}{particle}_ID_TRUE"].astype(int)
            )[0]

        # Drop rows at the end
        if indices_to_drop:
            display.warning_print(
                f"Dropping {len(indices_to_drop)} rows at the end of processing."
            )
            self.tuple = self.tuple.drop(index=indices_to_drop).reset_index(drop=True)

        return true_PID_scheme

    def __init__(
        self,
        tuple_location,
        mother_particle_name,
        daughter_particle_names,
        combined_particles,
        tree="DecayTree",
        branch_naming_structure=None,
        mass_hypotheses=None,
    ):
        # print("Class `tuple_manager` initialised with the following inputs:")
        # for arg_name, arg_value in locals().items():
        #     print(f"  {arg_name} = {arg_value}")

        self.mother = "MOTHER"

        raw_tuple = uproot.open(tuple_location)[tree]
        self.tuple_location = tuple_location
        list_of_branches = list(raw_tuple.keys())
        list_of_branches = [
            branch
            for branch in list_of_branches
            if "COV" not in branch and branch != "index"
        ]
        arrays = raw_tuple.arrays(list_of_branches, library="np")
        self.tuple = pd.DataFrame(arrays)
        if branch_naming_structure:
            self.convert_branch_aliases(branch_naming_structure, to_rapidsim=True)

        self.original_branches = list(self.tuple.keys())

        # # code to replace names
        # new_branches = []
        # for branch in self.tuple:
        #     branch.replace(mother_particle_name,'MOTHER')
        #     for combined_particle in combined_particles:
        #         if combined_particle == "MOTHER":
        #             branch = branch.replace(mother_particle_name,combined_particle)
        #         else:
        #             branch = branch.replace(myGlobals.particle_map['fromINTERMEDIATES'][combined_particle],combined_particle)
        #     for particle in list(myGlobals.particle_map['toDAUGHTERS'].keys()):
        #         branch = branch.replace(particle, myGlobals.particle_map['toDAUGHTERS'][particle])
        #     new_branches.append(branch)
        # self.tuple.columns = new_branches

        # code to replace names
        new_branches = []
        temp_particles = {}
        for idx, particle in enumerate(
            list(myGlobals.particle_map["toDAUGHTERS"].keys())
        ):
            temp_particles[particle] = str(np.random.randint(0, 99999999))

        for branch in self.tuple:
            branch.replace(mother_particle_name, "MOTHER")
            for combined_particle in combined_particles:
                if combined_particle == "MOTHER":
                    branch = branch.replace(mother_particle_name, combined_particle)
                else:
                    branch = branch.replace(
                        myGlobals.particle_map["fromINTERMEDIATES"][combined_particle],
                        combined_particle,
                    )
            for particle in list(myGlobals.particle_map["toDAUGHTERS"].keys()):
                branch = branch.replace(particle, temp_particles[particle])
            for particle in list(myGlobals.particle_map["toDAUGHTERS"].keys()):
                branch = branch.replace(
                    temp_particles[particle],
                    myGlobals.particle_map["toDAUGHTERS"][particle],
                )
            new_branches.append(branch)
        # for new_branche in new_branches:
        #     print(new_branche)
        # quit()
        self.tuple.columns = new_branches

        self.particles = [
            myGlobals.particle_map["toDAUGHTERS"][daughter]
            for daughter in daughter_particle_names
        ]

        for _idx, particle in enumerate(self.particles):
            if f"{particle}_M" not in self.tuple:
                if mass_hypotheses is not None:
                    if particle in mass_hypotheses:
                        if (
                            myGlobals.rapidsim_settings["RAPIDSIM_particles_df"][
                                (
                                    myGlobals.rapidsim_settings[
                                        "RAPIDSIM_particles_df"
                                    ]["part"]
                                    == mass_hypotheses[particle]
                                )
                            ].shape[0]
                            == 1
                        ):
                            pdg = int(
                                myGlobals.rapidsim_settings["RAPIDSIM_particles_df"][
                                    (
                                        myGlobals.rapidsim_settings[
                                            "RAPIDSIM_particles_df"
                                        ]["part"]
                                        == mass_hypotheses[particle]
                                    )
                                ].ID
                            )
                        elif (
                            myGlobals.rapidsim_settings["RAPIDSIM_particles_df"][
                                (
                                    myGlobals.rapidsim_settings[
                                        "RAPIDSIM_particles_df"
                                    ]["anti"]
                                    == mass_hypotheses[particle]
                                )
                            ].shape[0]
                            == 1
                        ):
                            pdg = int(
                                myGlobals.rapidsim_settings["RAPIDSIM_particles_df"][
                                    (
                                        myGlobals.rapidsim_settings[
                                            "RAPIDSIM_particles_df"
                                        ]["anti"]
                                        == mass_hypotheses[particle]
                                    )
                                ].ID
                                * -1
                            )

                        pdg = int(pdg)
                    else:
                        pdg = int(self.tuple[f"{particle}_ID"][0])
                else:
                    pdg = int(self.tuple[f"{particle}_ID"][0])

                self.tuple[f"{particle}_M"] = masses[abs(pdg)]

            if f"{particle}_ID_TRUE" not in self.tuple:
                self.tuple[f"{particle}_ID_TRUE"] = self.tuple[f"{particle}_ID"]
                if mass_hypotheses is not None:
                    if particle in mass_hypotheses:
                        self.tuple[f"{particle}_ID"] = pdg

        self.true_PID_scheme = self.ensure_consistent_final_state()
        self.recompute_combined_particles(combined_particles, daughter_particle_names)

    def convert_physical_units(self, conversion, specific_tuple=None):
        if conversion not in ["from_MeV", "back_to_MeV"]:
            print("conversion not valid")
            raise

        if specific_tuple is not None:
            tuple_to_update = specific_tuple
        else:
            tuple_to_update = self.tuple

        # do this before and after
        if conversion == "from_MeV":
            self.branches_for_conversion = []
            for branch in tuple_to_update:
                for (
                    branch_naming_structure,
                    pattern,
                ) in rapidsim_conventions.items():
                    if branch_naming_structure in [
                        "momenta_component",
                        "true_momenta_component",
                        "mass",
                        "true_mass",
                    ]:
                        regex_pattern = (
                            pattern.replace("{particle}", r"(?P<particle>\w+)").replace(
                                "{dim}", r"(?P<dim>\w)"
                            )
                            + r"$"
                        )  # Only a single character for {dim}
                        match = re.match(regex_pattern, branch)

                        if match:
                            self.branches_for_conversion.append(branch)

            for branch in self.branches_for_conversion:
                # tuple_to_update.loc[:, branch] *= 1e-3
                tuple_to_update.loc[:, branch] = tuple_to_update.loc[:, branch] * 1e-3
        else:
            for branch in self.branches_for_conversion:
                # tuple_to_update.loc[:, branch] *= 1e3
                tuple_to_update.loc[:, branch] = tuple_to_update.loc[:, branch] * 1e3

    def convert_branch_aliases(
        self, branch_naming_structures, to_rapidsim, specific_tuple=None
    ):
        if specific_tuple is not None:
            tuple_to_update = specific_tuple
        else:
            tuple_to_update = self.tuple

        if to_rapidsim:
            new_branches = []
            for branch in tuple_to_update:
                new_branch = branch

                for (
                    branch_naming_structure,
                    pattern,
                ) in branch_naming_structures.items():
                    regex_pattern = (
                        pattern.replace("{particle}", r"(?P<particle>\w+)").replace(
                            "{dim}", r"(?P<dim>\w)"
                        )
                        + r"$"
                    )  # Only a single character for {dim}
                    match = re.match(regex_pattern, branch)

                    if match:
                        particle = match.group("particle")
                        try:
                            dim = match.group("dim")
                        except Exception:
                            dim = ""  # no dim, for example mass branch
                        updated_branch = rapidsim_conventions[
                            branch_naming_structure
                        ].format(particle=particle, dim=dim)
                        new_branch = updated_branch
                        break
                new_branches.append(new_branch)

            tuple_to_update.columns = new_branches
        else:
            new_branches = []

            for branch in tuple_to_update:
                new_branch = branch

                for (
                    branch_naming_structure,
                    custom_pattern,
                ) in branch_naming_structures.items():
                    pattern = rapidsim_conventions[branch_naming_structure]

                    regex_pattern = (
                        pattern.replace("{particle}", r"(?P<particle>\w+)").replace(
                            "{dim}", r"(?P<dim>\w)"
                        )
                        + r"$"
                    )  # Only a single character for {dim}
                    match = re.match(regex_pattern, branch)

                    if match:
                        particle = match.group("particle")
                        try:
                            dim = match.group("dim")
                        except Exception:
                            dim = ""  # no dim, for example mass branch
                        updated_branch = custom_pattern.format(
                            particle=particle, dim=dim
                        )
                        new_branch = updated_branch
                        break

                new_branches.append(new_branch)

            tuple_to_update.columns = new_branches

    def write(
        self,
        new_branches_to_keep,
        output_location=None,
        keep_vertex_info=False,
        keep_tuple_structure=False,
        extra_branches=[],
    ):
        branches = self.original_branches + new_branches_to_keep

        if not keep_tuple_structure:
            # re-name columns
            branch_swaps = {}
            branch_swaps[self.mother] = self.mother_particle_name
            if self.intermediate_particle_name:
                if isinstance(self.intermediate_particle_name, list):
                    for inter in self.intermediate_particle_name:
                        branch_swaps[inter] = inter
                else:
                    branch_swaps[self.intermediate_particle_name] = (
                        self.intermediate_particle_name
                    )
            branch_swaps[self.particles[0]] = self.daughter_particle_names[0]
            branch_swaps[self.particles[1]] = self.daughter_particle_names[1]
            branch_swaps[self.particles[2]] = self.daughter_particle_names[2]
            # add rest to list - will only be others if dropMissing=False
            if isinstance(self.intermediate_particle_name, list):
                named_particles = (
                    [self.mother] + self.intermediate_particle_name + self.particles
                )
            else:
                named_particles = (
                    [self.mother] + [self.intermediate_particle_name] + self.particles
                )
            unnamed_particles = list(set(self.list_of_particles) - set(named_particles))
            for unnamed_particle in unnamed_particles:
                branch_swaps[unnamed_particle] = unnamed_particle

        tuple_to_write = self.tuple[branches]

        if not keep_tuple_structure:
            columns = list(tuple_to_write.columns)
            new_columns = []
            for column in columns:
                for to_swap in list(branch_swaps.keys()):
                    if column[: len(to_swap)] == to_swap:
                        new_columns.append(
                            column.replace(to_swap, branch_swaps[to_swap])
                        )
                        break

            # drop columns that might hang on but are not related to an individual particle, MCorr and nEvent for example
            drop_list = []
            for i in tuple_to_write.columns:
                # if i not in new_columns:
                if not any(s in i for s in list(branch_swaps.keys())):
                    drop_list.append(i)
            tuple_to_write = tuple_to_write.drop(drop_list, axis=1)

            tuple_to_write.columns = new_columns

            if not keep_vertex_info:
                for dim in ["X", "Y", "Z"]:
                    tuple_to_write = tuple_to_write.drop(
                        columns=[
                            col for col in tuple_to_write.columns if f"_vtx{dim}" in col
                        ]
                    )
                    tuple_to_write = tuple_to_write.drop(
                        columns=[
                            col
                            for col in tuple_to_write.columns
                            if f"_orig{dim}" in col
                        ]
                    )

            # re-order columns
            columns = tuple_to_write.columns
            if self.intermediate_particle_name:
                prefix_order = [self.mother_particle_name]
                if not isinstance(self.intermediate_particle_name, list):
                    prefix_order.append(self.intermediate_particle_name)
                else:
                    prefix_order.extend(self.intermediate_particle_name)
                prefix_order.extend(
                    [
                        self.daughter_particle_names[0],
                        self.daughter_particle_names[1],
                        self.daughter_particle_names[2],
                    ]
                )
            else:
                prefix_order = [
                    self.mother_particle_name,
                    self.daughter_particle_names[0],
                    self.daughter_particle_names[1],
                    self.daughter_particle_names[2],
                ]

            for unnamed_particle in unnamed_particles:
                prefix_order.append(unnamed_particle)

            ordered_columns = []
            for prefix in prefix_order:
                cols_with_prefix = [col for col in columns if col.startswith(prefix)]
                ordered_columns.extend(cols_with_prefix)
            tuple_to_write = tuple_to_write[ordered_columns]

        # if self.physical_units != "GeV":
        #     self.convert_physical_units(
        #         conversion="back_to_MeV", specific_tuple=tuple_to_write
        #     )

        if self.branch_naming_structure:
            self.convert_branch_aliases(
                self.branch_naming_structure,
                to_rapidsim=False,
                specific_tuple=tuple_to_write,
            )

        if len(extra_branches) > 0:
            tuple_to_write = tuple_to_write.drop(
                columns=extra_branches, errors="ignore"
            )
            tuple_to_write = pd.concat(
                [tuple_to_write, self.tuple[extra_branches]], axis=1
            )

        if not output_location:
            output_location = f"{self.tuple_location[:-5]}_reco.root"
        pts.write_df_to_root(tuple_to_write, output_location, self.tree)
        return output_location

    def add_branches(self, data_to_add, append_to_leaf_vector=False):
        if append_to_leaf_vector:
            for branch, data in data_to_add.items():
                # If the branch already exists, append_to_leaf_vector
                if branch in self.tuple.columns:
                    current_data = np.asarray(self.tuple[branch])

                    current_data = np.vstack(current_data)

                    if len(np.shape(current_data)) == 1:
                        current_data = np.expand_dims(current_data, 1)
                    if len(np.shape(data)) == 1:
                        data = np.expand_dims(data, 1)
                    new_branch_vector = np.concatenate((current_data, data), axis=1)

                    self.tuple[branch] = [list(row) for row in new_branch_vector]

                else:
                    # If the branch doesn't exist, add it as a new column
                    self.tuple[branch] = pd.DataFrame({branch: data})
        else:
            # Initialize a dictionary to collect the new columns
            columns_i = {}

            # Loop over the items in `data_to_add`
            for branch, data in data_to_add.items():
                if branch in self.tuple.columns:
                    # If the branch already exists, overwrite the column with new data
                    self.tuple[branch + "_OLD"] = self.tuple[branch].copy()
                    self.tuple[branch] = data
                else:
                    # If the branch doesn't exist, add it to the dictionary for future concatenation
                    columns_i[branch] = data

            # After the loop, concatenate the new columns in `columns_i` to the existing DataFrame
            if columns_i:
                new_columns_df = pd.DataFrame(columns_i)
                self.tuple = pd.concat([self.tuple, new_columns_df], axis=1)

    def get_branches(
        self,
        branches,
        transformers=None,
        numpy=False,
        scale_factor=1.0,
        transform_by_index=False,
        tag="",
        external_tuple=None,
        change_units={},
    ):
        if external_tuple is not None:
            working_tuple = external_tuple
        else:
            working_tuple = self.tuple

        try:
            data = working_tuple[branches] * scale_factor
        except Exception as e:
            for branch in branches:
                try:
                    working_tuple[branch]
                except Exception as e:
                    print(branch, f"not there {e}")
            print(f"quitting... {e}")
            raise Exception("branches not in working_tuple")

        for item in change_units:
            data[item] *= change_units[item]

        if transformers:
            data = tfs.transform_df(
                data, transformers, transform_by_index=transform_by_index, tag=tag
            )

        if numpy:
            data = np.asarray(data[branches])

        return data

    def get_condition_chunks(
        self, network, particles_involved, batch_size, name="MOTHER", mother=True
    ):
        plot_conditions = False
        if plot_conditions:
            save_cond_info = {}
            save_cond_info["processed"] = {}
            save_cond_info["physical"] = {}

        Nparticles = len(network.branch_options["particles_involved"][0])

        self.tuple["N_daughters"] = Nparticles

        conditions_graph = []
        personalised_transformers = {}
        for condition in network.branch_options["mother_conditions"]:
            conditions_graph.append(condition)
            if condition != "N_daughters":
                personalised_transformers[condition] = network.Transformers[condition]
        mother_conditions = self.get_branches(
            conditions_graph,
            personalised_transformers,
            numpy=True,
            # numpy=False,
        )

        conditions_graph = []
        personalised_transformers = {}
        for condition in network.branch_options["intermediate_conditions"]:
            conditions_graph.append(condition)
            if condition != "N_daughters":
                personalised_transformers[condition] = network.Transformers[condition]
        intermediate_conditions = self.get_branches(
            conditions_graph,
            personalised_transformers,
            numpy=True,
            # numpy=False,
        )

        conditions_graph = []
        personalised_transformers = {}
        for condition in network.branch_options["track_conditions"]:
            for i in range(Nparticles):
                conditions_graph.append(
                    condition.replace("DAUGHTERN", f"DAUGHTER{i + 1}")
                )
                if condition != "N_daughters":
                    personalised_transformers[
                        condition.replace("DAUGHTERN", f"DAUGHTER{i + 1}")
                    ] = network.Transformers[
                        condition.replace("DAUGHTERN", "DAUGHTER1")
                    ]
        track_conditions = self.get_branches(
            conditions_graph,
            personalised_transformers,
            numpy=True,
            # numpy=False,
        )
        track_conditions = np.reshape(
            track_conditions, (np.shape(track_conditions)[0], Nparticles, -1)
        )

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

        # Handle the last chunk if it's smaller than 1000 rows
        N_in_final_chunk = int(mother_chunks[-1].shape[0])
        if N_in_final_chunk < batch_size:
            last_chunk = mother_chunks.pop(-1)
            shape = np.asarray(np.shape(last_chunk))
            shape[0] = batch_size
            padded_chunk = np.zeros(tuple(shape))
            padded_chunk[: last_chunk.shape[0]] = last_chunk
            mother_chunks.append(padded_chunk)

            last_chunk = intermediate_chunks.pop(-1)
            shape = np.asarray(np.shape(last_chunk))
            shape[0] = batch_size
            padded_chunk = np.zeros(tuple(shape))
            padded_chunk[: last_chunk.shape[0]] = last_chunk
            intermediate_chunks.append(padded_chunk)

            last_chunk = track_chunks.pop(-1)
            shape = np.asarray(np.shape(last_chunk))
            shape[0] = batch_size
            padded_chunk = np.zeros(tuple(shape))
            padded_chunk[: last_chunk.shape[0]] = last_chunk
            track_chunks.append(padded_chunk)

        return (
            mother_chunks,
            intermediate_chunks,
            track_chunks,
            N_in_final_chunk,
            personalised_transformers,
        )

    def gen_latent(self, network, chunks):
        Nparticles = len(network.branch_options["particles_involved"][0])

        # Generate latent noise tensor
        mother_noise = np.random.normal(
            0,
            1,
            size=(
                np.shape(chunks)[0],
                np.shape(chunks[0])[0],
                network.branch_options["mother_latent_dims"],
            ),
        )

        intermediate_noise = np.random.normal(
            0,
            1,
            size=(
                np.shape(chunks)[0],
                np.shape(chunks[0])[0],
                network.branch_options["intermediate_latent_dims"],
            ),
        )

        track_noise = np.random.normal(
            0,
            1,
            size=(
                np.shape(chunks)[0],
                np.shape(chunks[0])[0],
                Nparticles,
                network.branch_options["track_latent_dims"],
            ),
        )

        return mother_noise, intermediate_noise, track_noise

    def smearPV(self, smeared_PV_output):
        # print("Need to implement function to move the origin vertex too")

        distance_buffer = {}
        for particle in self.particles:
            for coordinate in ["X", "Y", "Z"]:
                distance_buffer[f"{particle}_{coordinate}"] = np.asarray(
                    self.tuple[f"{particle}_orig{coordinate}_TRUE"]
                    - self.tuple[f"{self.mother}_vtx{coordinate}_TRUE"]
                )

        B_plus_TRUEORIGINVERTEX = [
            self.tuple[f"{self.mother}_origX_TRUE"],
            self.tuple[f"{self.mother}_origY_TRUE"],
            self.tuple[f"{self.mother}_origZ_TRUE"],
        ]
        B_plus_TRUEENDVERTEX = [
            self.tuple[f"{self.mother}_vtxX_TRUE"],
            self.tuple[f"{self.mother}_vtxY_TRUE"],
            self.tuple[f"{self.mother}_vtxZ_TRUE"],
        ]
        theta, phi = pts.compute_angles(B_plus_TRUEORIGINVERTEX, B_plus_TRUEENDVERTEX)

        for branch in list(smeared_PV_output.keys()):
            self.tuple[branch] = smeared_PV_output[branch]

        B_plus_TRUEORIGINVERTEX = [
            self.tuple[f"{self.mother}_origX_TRUE"],
            self.tuple[f"{self.mother}_origY_TRUE"],
            self.tuple[f"{self.mother}_origZ_TRUE"],
        ]
        (
            self.tuple[f"{self.mother}_vtxX_TRUE"],
            self.tuple[f"{self.mother}_vtxY_TRUE"],
            self.tuple[f"{self.mother}_vtxZ_TRUE"],
        ) = pts.redefine_endpoint(
            B_plus_TRUEORIGINVERTEX, theta, phi, self.tuple[f"{self.mother}_TRUE_FD"]
        )

        for particle in self.particles:
            for coordinate in ["X", "Y", "Z"]:
                self.tuple[f"{particle}_orig{coordinate}_TRUE"] = (
                    self.tuple[f"{self.mother}_vtx{coordinate}_TRUE"]
                    + distance_buffer[f"{particle}_{coordinate}"]
                    # - distance_buffer[f"{particle}_{coordinate}"] # should be plus
                )

    def updated_smearPV(self, smeared_PV_output):
        # print("Need to implement function to move the origin vertex too")

        for branch in smeared_PV_output:
            self.tuple[branch] = smeared_PV_output[branch]

    def append_trackchi2_conditional_information(self, external_tuple=None, tag=""):
        if external_tuple is not None:
            working_tuple = external_tuple
        else:
            working_tuple = self.tuple

        for idx, particle in enumerate(self.particles):
            working_tuple[f"{tag}{particle}_TRUEID"] = working_tuple[
                f"{particle}_ID_TRUE"
            ]

        for particle in self.particles:
            PT = working_tuple.eval(f"sqrt({particle}_PX**2 + {particle}_PY**2)")

            P = working_tuple.eval(
                f"sqrt({particle}_PX**2 + {particle}_PY**2 + {particle}_PZ**2)"
            )

            working_tuple[f"{tag}{particle}_eta"] = -np.log(
                np.tan(np.arcsin(PT / P) / 2.0)
            )

    def append_initial_conditional_information(
        self, true_PID_scheme, external_tuple=None, tag=""
    ):
        if external_tuple is not None:
            working_tuple = external_tuple
        else:
            working_tuple = self.tuple

        # indices_to_drop = set()  # Store indices to drop later

        for idx, particle in enumerate(self.particles):
            masses = (
                np.ones_like(working_tuple[f"{tag}{particle}_ID_TRUE"])
                * myGlobals.masses[true_PID_scheme[particle]]
            )
            # PIDs_present = []

            # for PID in myGlobals.particle_universe:
            #     where = np.where(
            #         np.abs(working_tuple[f"{tag}{particle}_ID_TRUE"].astype(int)) == PID
            #     )
            #     masses[where] = myGlobals.masses[PID]
            #     if np.shape(where)[1] > 0:
            #         PIDs_present.append(PID)

            # if len(PIDs_present) != 1:
            #     display.warning_print(PIDs_present)
            #     PIDs_present, counts = np.unique(
            #         np.abs(working_tuple[f"{tag}{particle}_ID_TRUE"].astype(int)),
            #         return_counts=True,
            #     )
            #     where = np.where(counts == np.amax(counts))
            #     select = PIDs_present[where][0]

            #     display.warning_print(
            #         "WARNING: particle type cannot change, TRUEID for each final state particle must be the same throughout the tuple."
            #     )
            #     display.warning_print(f"present in {particle} {PIDs_present} (counts: {counts})")
            #     display.warning_print(
            #         f"Marking rows for removal where {tag}{particle}_ID_TRUE != {select}"
            #     )

            #     # Identify indices to drop
            #     drop_indices = working_tuple.index[
            #         np.abs(working_tuple[f"{tag}{particle}_ID_TRUE"]) != select
            #     ].tolist()
            #     indices_to_drop.update(drop_indices)

            # Assign masses after the selection logic
            working_tuple[f"{tag}{particle}_mass"] = masses
            working_tuple[f"{tag}{particle}_E_TRUE"] = pts.compute_TRUEE(
                working_tuple, particle, RapidSim=True
            )
            working_tuple[f"{tag}{particle}_P_TRUE"] = pts.compute_TRUEP(
                working_tuple, particle, RapidSim=True
            )

        # Compute edge angles
        for i, particle_i in enumerate(self.particles):
            for j, particle_j in enumerate(self.particles):
                if i != j:
                    working_tuple[f"edge_angle_{particle_i}_{particle_j}_TRUE"] = (
                        pts.compute_angle(
                            working_tuple,
                            f"{particle_i}",
                            f"{particle_j}",
                            true_vars=True,
                            RapidSim=True,
                        )
                    )

        # # Drop rows at the end
        # if indices_to_drop:
        #     display.warning_print(f"Dropping {len(indices_to_drop)} rows at the end of processing.")
        #     working_tuple = working_tuple.drop(index=indices_to_drop).reset_index(
        #         drop=True
        #     )

    def append_mother_flight(self, external_tuple=None, tag=""):
        if external_tuple is not None:
            working_tuple = external_tuple
        else:
            working_tuple = self.tuple

        mother = "MOTHER"

        A = pts.compute_distance(
            working_tuple, mother, "vtx", mother, "orig", RapidSim=True, true_vars=True
        )
        A = np.asarray(A)
        A[np.where(A == 0)] = 5e-5
        working_tuple[f"{mother}_FLIGHT"] = A

    def append_secondary_conditional_information(self, external_tuple=None, tag=""):
        if external_tuple is not None:
            working_tuple = external_tuple
        else:
            working_tuple = self.tuple

        for particle in self.particles:
            for dim in ["X", "Y", "Z"]:
                working_tuple[f"{particle}_delta_P{dim}"] = (
                    working_tuple[f"{particle}_P{dim}"]
                    - working_tuple[f"{particle}_P{dim}_TRUE"]
                )
            PX = working_tuple[f"{particle}_PX_TRUE"]
            PY = working_tuple[f"{particle}_PY_TRUE"]
            PZ = working_tuple[f"{particle}_PZ_TRUE"]
            PX_reco = working_tuple[f"{particle}_PX"]
            PY_reco = working_tuple[f"{particle}_PY"]
            PZ_reco = working_tuple[f"{particle}_PZ"]

            working_tuple[f"{particle}_P"] = np.sqrt(
                (PX_reco**2 + PY_reco**2 + PZ_reco**2)
            )
            working_tuple[f"{particle}_TRUEP"] = np.sqrt((PX**2 + PY**2 + PZ**2))
            working_tuple[f"{particle}_P_TRUE"] = np.sqrt((PX**2 + PY**2 + PZ**2))
            working_tuple[f"{particle}_Preco_overP"] = (
                working_tuple[f"{particle}_P"] / working_tuple[f"{particle}_TRUEP"]
            )

            working_tuple[f"{particle}_IP"] = pts.compute_impactParameter_i(
                working_tuple,
                "MOTHER",
                f"{particle}",
                true_vertex=True,
                true_vars=False,
                RapidSim=True,
            )
            working_tuple[f"{particle}_IP_TRUE"] = pts.compute_impactParameter_i(
                working_tuple,
                "MOTHER",
                f"{particle}",
                true_vertex=True,
                true_vars=True,
                RapidSim=True,
            )

            working_tuple[f"{particle}_angle_wrt_mother"] = pts.compute_angle(
                working_tuple, "MOTHER", f"{particle}", RapidSim=True
            )
            working_tuple[f"{particle}_angle_wrt_mother_reco"] = pts.compute_angle(
                working_tuple, "MOTHER", f"{particle}", true_vars=False, RapidSim=True
            )

            PT = working_tuple.eval(
                f"sqrt({particle}_PX_TRUE**2 + {particle}_PY_TRUE**2)"
            )
            P = working_tuple.eval(
                f"sqrt({particle}_PX_TRUE**2 + {particle}_PY_TRUE**2 + {particle}_PZ_TRUE**2)"
            )
            working_tuple[f"{particle}_eta_TRUE"] = -np.log(
                np.tan(np.arcsin(PT / P) / 2.0)
            )

            PT = working_tuple.eval(f"sqrt({particle}_PX**2 + {particle}_PY**2)")
            P = working_tuple.eval(
                f"sqrt({particle}_PX**2 + {particle}_PY**2 + {particle}_PZ**2)"
            )
            working_tuple[f"{particle}_eta"] = -np.log(np.tan(np.arcsin(PT / P) / 2.0))

    def append_tertiary_conditional_information(
        self,
        combined_particles,
        true_PID_scheme,
        daughter_particle_names,
        external_tuple=None,
        tag="",
    ):
        if external_tuple is not None:
            working_tuple = external_tuple
        else:
            working_tuple = self.tuple

        mother = "MOTHER"

        # compute distance mother flies before decay
        A = pts.compute_distance(
            working_tuple, mother, "vtx", mother, "orig", RapidSim=True, true_vars=True
        )
        A = np.asarray(A)
        A[np.where(A == 0)] = 5e-5
        working_tuple[f"{mother}_FLIGHT"] = A

        working_tuple[f"{mother}_P_TRUE"] = np.sqrt(
            working_tuple[f"{mother}_PX_TRUE"] ** 2
            + working_tuple[f"{mother}_PY_TRUE"] ** 2
            + working_tuple[f"{mother}_PZ_TRUE"] ** 2
        )
        working_tuple[f"{mother}_PT_TRUE"] = np.sqrt(
            working_tuple[f"{mother}_PX_TRUE"] ** 2
            + working_tuple[f"{mother}_PY_TRUE"] ** 2
        )

        for combined_particle in combined_particles:
            recipe = combined_particles[combined_particle]

            if combined_particle != "MOTHER":
                working_tuple[f"{combined_particle}_PX_TRUE"] = np.zeros(
                    np.shape(working_tuple["MOTHER_PX_TRUE"])
                )
                working_tuple[f"{combined_particle}_PY_TRUE"] = np.zeros(
                    np.shape(working_tuple["MOTHER_PY_TRUE"])
                )
                working_tuple[f"{combined_particle}_PZ_TRUE"] = np.zeros(
                    np.shape(working_tuple["MOTHER_PZ_TRUE"])
                )
                working_tuple[f"{combined_particle}_PX"] = np.zeros(
                    np.shape(working_tuple["MOTHER_PX_TRUE"])
                )
                working_tuple[f"{combined_particle}_PY"] = np.zeros(
                    np.shape(working_tuple["MOTHER_PY_TRUE"])
                )
                working_tuple[f"{combined_particle}_PZ"] = np.zeros(
                    np.shape(working_tuple["MOTHER_PZ_TRUE"])
                )
                for particle in recipe:
                    particle_i = f"DAUGHTER{np.where(np.asarray(daughter_particle_names) == particle)[0][0] + 1}"
                    # print(particle, particle_i)

                    working_tuple[f"{combined_particle}_PX_TRUE"] += working_tuple[
                        f"{particle_i}_PX_TRUE"
                    ]
                    working_tuple[f"{combined_particle}_PY_TRUE"] += working_tuple[
                        f"{particle_i}_PY_TRUE"
                    ]
                    working_tuple[f"{combined_particle}_PZ_TRUE"] += working_tuple[
                        f"{particle_i}_PZ_TRUE"
                    ]
                    working_tuple[f"{combined_particle}_PX"] += working_tuple[
                        f"{particle_i}_PX"
                    ]
                    working_tuple[f"{combined_particle}_PY"] += working_tuple[
                        f"{particle_i}_PY"
                    ]
                    working_tuple[f"{combined_particle}_PZ"] += working_tuple[
                        f"{particle_i}_PZ"
                    ]

        for combined_particle in combined_particles:
            recipe = combined_particles[combined_particle]

            recipe_i = []
            for recipe_ingredient_i in recipe:
                particle_i = f"DAUGHTER{np.where(np.asarray(daughter_particle_names) == recipe_ingredient_i)[0][0] + 1}"
                recipe_i.append(particle_i)

            working_tuple[f"{combined_particle}_DIRA"] = pts.compute_DIRA(
                working_tuple,
                mother,
                recipe_i,
                true_vertex=True,
                true_vars=False,
                RapidSim=True,
            )
            working_tuple[f"{combined_particle}_DIRA_TRUE"] = pts.compute_DIRA(
                working_tuple,
                mother,
                recipe_i,
                true_vertex=True,
                true_vars=True,
                RapidSim=True,
            )
            working_tuple[f"{combined_particle}_IP"] = pts.compute_impactParameter(
                working_tuple,
                mother,
                recipe_i,
                true_vertex=True,
                true_vars=False,
                RapidSim=True,
            )
            working_tuple[f"{combined_particle}_IP_TRUE"] = pts.compute_impactParameter(
                working_tuple,
                mother,
                recipe_i,
                true_vertex=True,
                true_vars=True,
                RapidSim=True,
            )
            (
                working_tuple[f"{combined_particle}_missing_P"],
                working_tuple[f"{combined_particle}_missing_PT"],
            ) = pts.compute_missing_momentum(
                working_tuple, combined_particle, recipe_i, RapidSim=True
            )

        for idx, particle in enumerate(self.particles):
            A = pts.compute_distance(
                working_tuple,
                particle,
                "orig",
                mother,
                "vtx",
                RapidSim=True,
                true_vars=True,
            )
            A = np.asarray(A)
            A[np.where(A == 0)] = 5e-5
            working_tuple[f"{particle}_FLIGHT"] = A

            TRUEID = true_PID_scheme[daughter_particle_names[idx]]
            working_tuple[f"{particle}_TRUEID"] = TRUEID

            working_tuple[f"{particle}_deltaEV_X"] = (
                working_tuple[f"{particle}_origX_TRUE"]
                - working_tuple[f"{mother}_vtxX_TRUE"]
            )
            working_tuple[f"{particle}_deltaEV_Y"] = (
                working_tuple[f"{particle}_origY_TRUE"]
                - working_tuple[f"{mother}_vtxY_TRUE"]
            )
            working_tuple[f"{particle}_deltaEV_Z"] = (
                working_tuple[f"{particle}_origZ_TRUE"]
                - working_tuple[f"{mother}_vtxZ_TRUE"]
            )
            working_tuple[f"{particle}_deltaEV_T"] = np.sqrt(
                working_tuple[f"{particle}_deltaEV_X"] ** 2
                + working_tuple[f"{particle}_deltaEV_Y"] ** 2
            )

            (
                working_tuple[f"{particle}_delta_P"],
                working_tuple[f"{particle}_delta_PT"],
            ) = pts.compute_reconstructed_momentum_residual(
                working_tuple, particle, RapidSim=True
            )

            for dim in ["X", "Y", "Z"]:
                residual_frac = (
                    working_tuple[f"{particle}_P{dim}"]
                    - working_tuple[f"{particle}_P{dim}_TRUE"]
                ) / (working_tuple[f"{particle}_P{dim}_TRUE"] + 1e-4)

                _residualfrac_limit = 5.0
                limit = _residualfrac_limit
                residual_frac[residual_frac < (limit * -1.0)] = -limit
                residual_frac[residual_frac > limit] = limit

                working_tuple[f"{particle}_residualfrac_P{dim}"] = residual_frac

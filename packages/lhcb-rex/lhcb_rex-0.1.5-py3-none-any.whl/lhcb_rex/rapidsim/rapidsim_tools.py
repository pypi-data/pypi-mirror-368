import numpy as np
import re
import uproot
import os
import pandas as pd
import lhcb_rex.tools.display as display
import lhcb_rex.settings.globals as myGlobals


def find_closing_bracket_index(s, opening_index):
    # Check if the index is valid
    if s[opening_index] != "{":
        raise ValueError("The provided index does not point to an opening bracket.")

    stack = []

    for i in range(opening_index, len(s)):
        if s[i] == "{":
            stack.append(i)
        elif s[i] == "}":
            stack.pop()
            # If the stack is empty, we found the closing bracket
            if not stack:
                return i

    # If we finish the loop without finding a closing bracket
    return -1


def get_rapidsim_indicies(decay_string):
    decay_string = re.sub(r"\{(?!\s)", r"{ ", decay_string)
    decay_string = re.sub(r"(?<!\s)\}", r" }", decay_string)

    mother = decay_string.split("->")[0].replace(" ", "")

    daughter_string = decay_string[decay_string.find("->") + 2 :]
    if daughter_string[0] == " ":
        daughter_string = daughter_string[1:]

    labels = np.asarray([0 for i in daughter_string])

    for level in range(8):
        for idx, character in enumerate(daughter_string):
            if labels[idx] == level:
                if character == "{":
                    start_idx = idx
                    end_idx = find_closing_bracket_index(daughter_string, start_idx)
                    mother_in_level = daughter_string[start_idx + 1 : end_idx].split(
                        "->"
                    )[0]
                    labels[start_idx + 1 + len(mother_in_level) : end_idx] += (
                        1  # dont label the brackets # also bring mother down a level
                    )

    label_string = ""
    # convert labels into strings
    for idx, thing in enumerate(daughter_string):
        if thing == " ":
            label_string += " "
        else:
            label_string += str(labels[idx])

    daughter_split = daughter_string.split(" ")
    label_split = label_string.split(" ")

    ordering = np.empty((0, 2))
    for idx in range(len(daughter_split)):
        if daughter_split[idx] not in ["{", "}", "->", ""]:
            ordering = np.append(
                ordering, [[int(label_split[idx][0]), int(-1)]], axis=0
            )

    rapidsim_idx = 1  # mother is 0
    for level in range(8):
        for row in range(np.shape(ordering)[0]):
            if ordering[row][0] == level:
                ordering[row][1] = rapidsim_idx
                rapidsim_idx += 1

    # ordering[:,0] = order
    # ordering[:,1] = rapidsim index

    ordering_string = ""
    idx = 0
    for item in decay_string.split(" "):
        if item in ["{", "}", "->", ""]:
            ordering_string += item + " "
        elif item == mother:
            ordering_string += str(0) + " "
        else:
            ordering_string += str(int(ordering[idx][1])) + " "
            idx += 1
    ordering_string = ordering_string[:-1]  # remove last space

    stability_string = ""
    for idx in range(len(decay_string.split(" "))):
        if decay_string.split(" ")[idx] in ["{", "}", "->", ""]:
            stability_string += decay_string.split(" ")[idx] + " "
        else:
            if idx + 1 == len(decay_string.split(" ")):
                stability_string += "S" + " "  # stable, end of decay string
            elif decay_string.split(" ")[idx + 1] == "->":
                stability_string += "U" + " "
            else:
                stability_string += "S" + " "

    return (
        decay_string,
        ordering_string,
        stability_string,
        daughter_string,
        label_string,
    )


def compute_combined_param(daughter_info, param):
    daughters = list(daughter_info.keys())

    values = np.zeros(np.shape(daughter_info[daughters[0]]["M"]))
    if param in ["PX", "PY", "PZ"]:
        for daughter in daughters:
            values += daughter_info[daughter][param]
    elif param == "M":
        PE = values.copy()
        PX = values.copy()
        PY = values.copy()
        PZ = values.copy()

        for daughter in daughters:
            PE += np.sqrt(
                daughter_info[daughter]["M"] ** 2
                + daughter_info[daughter]["PX"] ** 2
                + daughter_info[daughter]["PY"] ** 2
                + daughter_info[daughter]["PZ"] ** 2
            )
            PX += daughter_info[daughter]["PX"]
            PY += daughter_info[daughter]["PY"]
            PZ += daughter_info[daughter]["PZ"]

        values = np.sqrt((PE**2 - PX**2 - PY**2 - PZ**2))

    return values


def organise_output_tuple(
    fileName,
    dropMissing,
    naming_scheme,
    mass_hypotheses,
    combined_particles,
    true_PID_scheme,
):
    # Open the input file and access the TTree
    with uproot.open(fileName) as f:
        # Get the tree
        tree = f["DecayTree"]

        # Load tree into numpy
        if dropMissing:
            branches_to_keep = []
            for particle in naming_scheme.values():
                branches_to_keep.extend(
                    [
                        branch
                        for branch in tree.keys()
                        if branch[: len(particle)] == particle
                    ]
                )
        else:
            branches_to_keep = tree.keys()

        map_NA_codes = {}
        idx = 0
        for branch in branches_to_keep:
            if "origX_TRUE" in branch:
                if (
                    re.match(r"^NA_\d{8}$", naming_scheme[idx])
                    or naming_scheme[idx] == "NA"
                ):
                    map_NA_codes[naming_scheme[idx]] = branch.replace("_origX_TRUE", "")
                idx += 1

        branches = {
            branch: tree[branch].array(library="np") for branch in branches_to_keep
        }

        # Reset mass hypotheses
        if mass_hypotheses:
            for mass_hypothesis in mass_hypotheses:
                particle = mass_hypotheses[mass_hypothesis]
                filtered_df = myGlobals.rapidsim_settings["RAPIDSIM_particles_df"][
                    (
                        myGlobals.rapidsim_settings["RAPIDSIM_particles_df"]["part"]
                        == particle
                    )
                    | (
                        myGlobals.rapidsim_settings["RAPIDSIM_particles_df"]["anti"]
                        == particle
                    )
                ]
                new_mass = float(filtered_df.mass)
                branches[f"{mass_hypothesis}_M"] = (
                    np.ones(np.shape(branches[f"{mass_hypothesis}_M"])) * new_mass
                )

        # Recompute variables of reconstructed particles
        if combined_particles:
            for combined_particle in combined_particles:
                particle_daughters = combined_particles[combined_particle]
                daughter_info = {}
                for daughter in particle_daughters:
                    daughter_info[daughter] = {}
                    for param in ["M", "PX", "PY", "PZ"]:
                        daughter_info[daughter][param] = branches[f"{daughter}_{param}"]
                for param in ["M", "PX", "PY", "PZ"]:
                    branches[f"{combined_particle}_{param}"] = compute_combined_param(
                        daughter_info, param
                    )
                branches[f"{combined_particle}_P"] = np.sqrt(
                    branches[f"{combined_particle}_PX"] ** 2
                    + branches[f"{combined_particle}_PY"] ** 2
                    + branches[f"{combined_particle}_PZ"] ** 2
                )
                branches[f"{combined_particle}_PT"] = np.sqrt(
                    branches[f"{combined_particle}_PX"] ** 2
                    + branches[f"{combined_particle}_PY"] ** 2
                )

        # True PID
        for particle in true_PID_scheme:
            if f"{particle}_PX" in list(branches.keys()):
                branches[f"{particle}_ID_TRUE"] = (
                    np.ones(np.shape(branches[f"{particle}_PX"]))
                    * true_PID_scheme[particle]
                )
                # maybe only want to write this out for final state particles?
                branches[f"{particle}_ID"] = (
                    np.ones(np.shape(branches[f"{particle}_PX"]))
                    * true_PID_scheme[particle]
                )
            if particle in map_NA_codes:
                if f"{map_NA_codes[particle]}_PX" in list(branches.keys()):
                    branches[f"{map_NA_codes[particle]}_ID_TRUE"] = (
                        np.ones(np.shape(branches[f"{map_NA_codes[particle]}_PX"]))
                        * true_PID_scheme[particle]
                    )

        # PID from mass hypotheses
        if mass_hypotheses:
            for particle in mass_hypotheses:
                if (
                    myGlobals.rapidsim_settings["RAPIDSIM_particles_df"][
                        (
                            myGlobals.rapidsim_settings["RAPIDSIM_particles_df"]["part"]
                            == mass_hypotheses[particle]
                        )
                    ].shape[0]
                    == 1
                ):
                    pdg = int(
                        myGlobals.rapidsim_settings["RAPIDSIM_particles_df"][
                            (
                                myGlobals.rapidsim_settings["RAPIDSIM_particles_df"][
                                    "part"
                                ]
                                == mass_hypotheses[particle]
                            )
                        ].ID
                    )
                elif (
                    myGlobals.rapidsim_settings["RAPIDSIM_particles_df"][
                        (
                            myGlobals.rapidsim_settings["RAPIDSIM_particles_df"]["anti"]
                            == mass_hypotheses[particle]
                        )
                    ].shape[0]
                    == 1
                ):
                    pdg = int(
                        myGlobals.rapidsim_settings["RAPIDSIM_particles_df"][
                            (
                                myGlobals.rapidsim_settings["RAPIDSIM_particles_df"][
                                    "anti"
                                ]
                                == mass_hypotheses[particle]
                            )
                        ].ID
                        * -1
                    )
                else:
                    display.error_splash(
                        post_message=f"{particle} not found in {myGlobals.rapidsim_settings['RAPIDSIM_ROOT']}/config/particles.dat, or listed multiple times."
                    )
                branches[f"{particle}_ID"] = (
                    np.ones(np.shape(branches[f"{particle}_PX"])) * pdg
                )

        # Reorder the columns alphabetically
        branches = pd.DataFrame(branches)
        branches = branches[sorted(branches.columns)]
        branches = {col: branches[col].to_numpy() for col in branches.columns}

        # Open the output file and write the new tree with the selected branches
        with uproot.recreate(fileName.replace(".root", "_temp.root")) as new_file:
            new_file["DecayTree"] = branches

    os.system(f"mv {fileName.replace('.root', '_temp.root')} {fileName}")

    return map_NA_codes


def check_params(line, checked_lines, key, params_list):
    var_list = line[line.find(":") + 1 :].replace(",", "").replace("\n", "").split(" ")
    try:
        var_list.remove("")
    except Exception:
        pass
    var_list.extend(params_list)
    var_list = np.unique(var_list)

    line = line[: line.find(":") + 1]
    for var in var_list:
        line += f" {var},"
    line = line[:-1] + "\n"  # remove last comma
    checked_lines[key] = True
    return line, checked_lines


def check_line(checked_lines, option, choice):
    line = f"{option} : {choice}\n"
    checked_lines[option] = True
    return line, checked_lines


def write_line(checked_lines, option, choice, f):
    line = f"{option} : {choice}\n"
    checked_lines[option] = True
    f.write(line)
    return checked_lines


def check_config(
    config,
    USE_EVTGEN,
    naming_scheme,
    model_scheme=None,
    geometry="LHCb",
    acceptance="AllIn",
    useEvtGen="TRUE",
    evtGenUsePHOTOS="TRUE",
    dropMissing=True,
):
    blocked_settings = [
        "paramsTwoBody",
        "paramsThreeBody",
        "paramsFourBody",
        "paramsFiveBody",
        "paramsSixBody",
    ]  # temporarily blocking this function in rapidsim

    settings = {}
    settings[-1] = {}
    for key in naming_scheme:
        settings[int(key)] = {}

    particle_index = 0
    current_particle = -1

    f = open(config, "r")
    f_lines = f.readlines()
    for idx, line in enumerate(f_lines):
        if ":" in line:
            option = line.split(":")[0].replace(" ", "").replace("\t", "")
            setting = (
                line.split(":")[-1]
                .replace(" ", "")
                .replace("\n", "")
                .replace(",", ", ")
            )
            settings[current_particle][option] = setting
        elif f"@{particle_index}" in line:
            current_particle = particle_index
            particle_index += 1

    # particle names
    for key in naming_scheme:
        # if naming_scheme[key] != 'NA':
        if (
            not re.match(r"^NA_\d{8}$", naming_scheme[key])
            and naming_scheme[key] != "NA"
        ):
            settings[int(key)]["name"] = naming_scheme[key]
        else:
            settings[int(key)]["invisible"] = (
                "true"  # dont include these in mother mass variables
            )

    # EVTGEN models
    for key in model_scheme:
        if not USE_EVTGEN and model_scheme[key] not in ["PHSP", "NA"]:
            print(
                f"Cannot use {model_scheme[key]}, $EVTGEN_ROOT not set. Using PHSP instead."
            )
            settings[int(key)]["evtGenModel"] = "PHSP"
        else:
            settings[int(key)]["evtGenModel"] = model_scheme[key]

    # geometry
    settings[-1]["geometry"] = geometry

    # acceptance
    settings[-1]["acceptance"] = acceptance

    # useEvtGen
    if not USE_EVTGEN and useEvtGen == "TRUE":
        print("Cannot set useEvtGen : TRUE, $EVTGEN_ROOT not set.")
    else:
        settings[-1]["useEvtGen"] = useEvtGen

    # evtGenUsePHOTOS
    if evtGenUsePHOTOS != "TRUE":
        pass  # dont set as setting option to anything sets photos.
    elif not USE_EVTGEN and evtGenUsePHOTOS == "TRUE":
        print("Cannot set evtGenUsePHOTOS : TRUE, $EVTGEN_ROOT not set.")
    else:
        settings[-1]["evtGenUsePHOTOS"] = evtGenUsePHOTOS

    paramsDecaying = [
        "M",
        "P",
        "PT",
        "PX",
        "PY",
        "PZ",
        "vtxX",
        "vtxY",
        "vtxZ",
        "origX",
        "origY",
        "origZ",
    ]
    paramsStable = ["M", "P", "PT", "PX", "PY", "PZ", "origX", "origY", "origZ"]

    # paramsStable
    if "paramsStable" in settings[-1].keys():
        settings[-1]["paramsStable"] = (
            settings[-1]["paramsStable"].replace(" ", "").split(",")
        )
        settings[-1]["paramsStable"].extend(paramsStable)
        settings[-1]["paramsStable"] = np.unique(settings[-1]["paramsStable"])
        line = ""
        for var in settings[-1]["paramsStable"]:
            line += f" {var},"
        line = line[1:-1] + "\n"  # remove last comma and initial space
        settings[-1]["paramsStable"] = line
    else:
        settings[-1]["paramsStable"] = paramsStable

    # paramsDecaying
    if "paramsDecaying" in settings[-1].keys():
        settings[-1]["paramsDecaying"] = (
            settings[-1]["paramsDecaying"].replace(" ", "").split(",")
        )
        settings[-1]["paramsDecaying"].extend(paramsDecaying)
        settings[-1]["paramsDecaying"] = np.unique(settings[-1]["paramsDecaying"])
        line = ""
        for var in settings[-1]["paramsDecaying"]:
            line += f" {var},"
        line = line[1:-1] + "\n"  # remove last comma and initial space
        settings[-1]["paramsDecaying"] = line
    else:
        settings[-1]["paramsDecaying"] = paramsDecaying

    with open(config.replace(".config", "_temp.config"), "w") as f_out:
        for key in [-1] + list(range(np.amax(list(naming_scheme.keys())) + 1)):
            if key != -1:
                line = f"@{int(key)}\n"
                f_out.write(line)

            for option in list(settings[int(key)].keys()):
                setting = settings[int(key)][option]
                if key != -1:
                    if option == "evtGenModel":
                        line = f"\t{option} : {setting.replace('_', ' ')}\n"  # replace _ in evtgenmodel name
                    else:
                        line = f"\t{option} : {setting}\n"
                else:
                    if option not in blocked_settings:
                        line = f"{option} : {setting}\n"

                f_out.write(line)

    os.system(f"mv {config.replace('.config', '_temp.config')} {config}")

    return settings

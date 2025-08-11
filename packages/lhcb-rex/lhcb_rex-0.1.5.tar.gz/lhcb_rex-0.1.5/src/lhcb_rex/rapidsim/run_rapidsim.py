import os
import numpy as np
import uproot
from pathlib import Path
from typing import Optional
import re

# def run_rapidsim():
# os.system(
#     f"/users/am13743/RapidSim/bin/RapidSim.exe TEST 100 1"
# )


import lhcb_rex.settings.globals as myGlobals
import lhcb_rex.rapidsim.rapidsim_tools as tools
import lhcb_rex.tools.display as display
# import fast_vertex_quality_inference.tools.globals as myGlobals
# import fast_vertex_quality_inference.rapidsim.rapidsim_tools as tools
# import fast_vertex_quality_inference.tools.display as display
import subprocess
import sys
import time

# Constants
DEFAULT_GEOMETRY = "LHCb"
DEFAULT_ACCEPTANCE = "AllIn"
DEFAULT_EVTGEN_USE = "TRUE"
DEFAULT_EVTGEN_USE_PHOTOS = "TRUE"


# Helper Functions
def remove_file(file_path: Path) -> None:
    if file_path.is_file():
        file_path.unlink()


def organize_rapidsim_configuration(loc: str, decay: str) -> None:
    os.makedirs(
        loc[: loc.rfind("/")], exist_ok=True
    )  # Create directory if it doesn't exist
    remove_file(Path(f"{loc}.DEC"))
    with open(f"{loc}.decay", "w") as decay_file:
        decay_file.write(decay)

def run_rapidsim_command(loc: str, events: int, status=None):

    def update_status(percent):

        elapsed = time.time() - start_time
        if events_run_so_far > 0:
            remaining_time = elapsed / (events_run_so_far / events) - elapsed
        else:
            remaining_time = 0

        elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed))
        eta_str = time.strftime("%H:%M:%S", time.gmtime(max(remaining_time, 0)))

        if status:
            status.update(
                f"[bold slate_blue3]Running RapidSim... "
                f"{percent:.2f}% complete | Elapsed: {elapsed_str} | ETA: {eta_str}"
            )

    exe = myGlobals.rapidsim_settings['rapidsim_exe']
    events_run_so_far = 0
    start_time = time.time()
    
    process = subprocess.Popen(
        [exe, loc, str(events), "1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    if events > 1:

        stdout_file = open(f"{loc}_RapidSim.stdout", "w")
        stderr_file = open(f"{loc}_RapidSim.stderr", "w")

        info_pattern = re.compile(r"INFO\s+n\s*:\s*(\d+)")

        for line in process.stdout:
            stdout_file.write(line)
            line = line.strip()
            match = info_pattern.search(line)
            if match:
                events_run_so_far = int(match.group(1))
                percent = (events_run_so_far / events) * 100

                update_status(percent)


        for line in process.stderr:
            stderr_file.write(line)

        if status:
            update_status(100.)

        stdout_file.close()
        stderr_file.close()

    process.wait()


def extract_model_blocks(models):
    if not models:
        return []

    # Match [[...]] blocks OR individual non-space tokens
    pattern = r"\[\[.*?\]\]|\S+"
    matches = re.findall(pattern, models)

    # Remove structural tokens
    cleaned = [
        m.strip("[]") if m.startswith("[[") and m.endswith("]]") else m
        for m in matches
        if m not in {"{", "}", "->"}
    ]

    return cleaned


def run_rapidsim(
    loc: str,
    events: int,
    decay: str,
    naming: str,
    models: Optional[str] = None,
    mass_hypotheses: Optional[dict] = None,
    intermediate_particle: Optional[dict] = None,
    geometry: str = DEFAULT_GEOMETRY,
    acceptance: str = DEFAULT_ACCEPTANCE,
    useEvtGen: str = DEFAULT_EVTGEN_USE,
    evtGenUsePHOTOS: str = DEFAULT_EVTGEN_USE_PHOTOS,
    dropMissing: bool = True,
    clean_up_files: bool = True,
) -> tuple:
    if not myGlobals.rapidsim_settings["imported"]:
        display.error_splash(pre_message="$RAPIDSIM not set!")

    cleanup_files(loc)

    with display.status_execution_rapidsim(
        status_message="[bold green]Running RapidSim...",
        complete_message="[bold green]RapidSim stage complete :white_check_mark:",
    ) as status:
        myGlobals.stopwatches.click("RapidSim - config")
        with display.log_execution("Organizing RapidSim configuration"):
            organize_rapidsim_configuration(loc, decay)
            run_rapidsim_command(loc, events=1)

            (
                decay_string,
                ordering_string,
                stability_string,
                daughter_string,
                label_string,
            ) = tools.get_rapidsim_indicies(decay)
            rapidsim_names = [
                i for i in naming.split() if i not in ["{", "}", "", "->"]
            ]
            rapidsim_indicies = [
                int(i) for i in ordering_string.split() if i not in ["{", "}", "", "->"]
            ]
            naming_scheme = dict(zip(rapidsim_indicies, rapidsim_names))
            # give IDs to NA particles:
            for particle, name in naming_scheme.items():
                if name == "NA":
                    naming_scheme[particle] = (
                        f"NA_{np.random.randint(10000000, 99999999)}"  # 8 figure code
                    )
            rapidsim_names = list(naming_scheme.values())

            decay_strings = [
                i for i in decay_string.split() if i not in ["{", "}", "", "->"]
            ]
            true_PID_scheme = {}

            for key in rapidsim_names:
                particle = decay_strings[rapidsim_names.index(key)]
                try:
                    pdg = get_particle_id(particle)
                    true_PID_scheme[key] = pdg
                except ValueError as e:
                    display.error_splash(post_message=str(e))
                    raise

            stability_scheme = dict(
                zip(
                    rapidsim_indicies,
                    [
                        i
                        for i in stability_string.split(" ")
                        if i not in ["{", "}", "", "->"]
                    ],
                )
            )
            nPositive_missing_particles, nNegative_missing_particles, N_miss = (
                calculate_missing_particles(
                    stability_scheme, decay_strings, naming_scheme
                )
            )
            fully_reco = 0 if N_miss > 0 else 1

            model_scheme = None
            if models:
                model_names = extract_model_blocks(models)
                model_scheme = dict(zip(rapidsim_indicies, model_names))

            config = f"{loc}.config"
            tools.check_config(
                config,
                myGlobals.rapidsim_settings["USE_EVTGEN"],
                naming_scheme,
                model_scheme,
                geometry,
                acceptance,
                useEvtGen,
                evtGenUsePHOTOS,
                dropMissing=dropMissing,
            )

        display.print_decay_splash(
            decay_strings,
            daughter_string,
            label_string,
            ordering_string,
            naming_scheme,
            mass_hypotheses,
            model_scheme,
        )
        myGlobals.stopwatches.click("RapidSim - config")

        myGlobals.stopwatches.click("RapidSim - generation")
        combined_particles, mother_particle, daughter_particles = prepare_particle_data(
            naming_scheme, intermediate_particle
        )

        with display.log_execution("Running RapidSim generation"):
            raw_rapidsim = f"{loc.split('/')[-1]}_tree.root"
            remove_file(Path(raw_rapidsim))
            run_rapidsim_command(loc, events, status=status)
        myGlobals.stopwatches.click("RapidSim - generation")

        myGlobals.stopwatches.click("RapidSim - processing")
        if Path(raw_rapidsim).is_file():  # a root file was created
            with display.log_execution("Manipulating RapidSim tuple"):
                map_NA_codes = process_rapidsim_output(
                    raw_rapidsim,
                    dropMissing,
                    naming_scheme,
                    mass_hypotheses,
                    combined_particles,
                    true_PID_scheme,
                )
        else:
            display.error_splash(
                stderr=f"{loc}_RapidSim.stderr",
                pre_message=f"when running RapidSim, here follows {loc}_RapidSim.stderr:",
                post_message=f"{raw_rapidsim} was never created.",
            )

        myGlobals.stopwatches.click("RapidSim - processing")

    if clean_up_files:
        cleanup_files(loc)

    # print(raw_rapidsim)
    # print(fully_reco)
    # print(nPositive_missing_particles)
    # print(nNegative_missing_particles)
    # print(mother_particle)
    # print(daughter_particles)
    # print(true_PID_scheme)
    # print(combined_particles)
    # print(map_NA_codes)
    # quit()

    return (
        raw_rapidsim,
        fully_reco,
        nPositive_missing_particles,
        nNegative_missing_particles,
        mother_particle,
        daughter_particles,
        true_PID_scheme,
        combined_particles,
        map_NA_codes,
    )


def get_particle_id(particle: str) -> int:
    """Get the particle ID from the particles DataFrame."""
    match = myGlobals.rapidsim_settings["RAPIDSIM_particles_df"][
        (myGlobals.rapidsim_settings["RAPIDSIM_particles_df"]["part"] == particle)
        | (myGlobals.rapidsim_settings["RAPIDSIM_particles_df"]["anti"] == particle)
    ]

    if match.shape[0] != 1:
        raise ValueError(
            f"{particle} not found or listed multiple times in {myGlobals.rapidsim_settings['RAPIDSIM_particles']}."
        )

    # Access the first element of the Series safely using iloc[0]
    particle_id = match.ID.iloc[0]
    return int(particle_id) if match["part"].iloc[0] == particle else -int(particle_id)


def calculate_missing_particles(
    stability_scheme: dict, decay_strings: list, naming_scheme: dict
) -> tuple:
    """Calculate the number of missing particles."""
    N_miss = 0
    nPositive_missing_particles = 0
    nNegative_missing_particles = 0
    for idx, key in enumerate(stability_scheme):
        if (
            key != 0
            and stability_scheme[key] == "S"
            and (
                re.match(r"^NA_\d{8}$", naming_scheme[key])
                or naming_scheme[key] == "NA"
            )
        ):
            N_miss += 1
            particle = decay_strings[idx]
            charge = get_particle_charge(particle)
            if charge == -1:
                nNegative_missing_particles += 1
            elif charge == 1:
                nPositive_missing_particles += 1
    return nPositive_missing_particles, nNegative_missing_particles, N_miss


def get_particle_charge(particle: str) -> int:
    """Get the charge of the particle."""
    match = myGlobals.rapidsim_settings["RAPIDSIM_particles_df"][
        (myGlobals.rapidsim_settings["RAPIDSIM_particles_df"]["part"] == particle)
        | (myGlobals.rapidsim_settings["RAPIDSIM_particles_df"]["anti"] == particle)
    ]
    if match.shape[0] != 1:
        raise ValueError(f"Charge for {particle} not found or listed multiple times.")
    return (
        int(match.charge) if match["part"].iloc[0] == particle else -int(match.charge)
    )


def prepare_particle_data(naming_scheme: dict, intermediate_particle: dict) -> tuple:
    """Prepare combined particles data."""
    combined_particles = {}
    default_daughters = np.asarray(list(naming_scheme.values()))
    # combined_particles[naming_scheme[0]] = default_daughters[np.where((default_daughters != 'NA') & (default_daughters != naming_scheme[0]))]

    combined_particles[naming_scheme[0]] = default_daughters[
        np.where(
            (~np.array([bool(re.match(r"^NA_\d{8}$", x)) for x in default_daughters]))
            & (default_daughters != naming_scheme[0])
            & (default_daughters != "NA")
        )
    ]
    if intermediate_particle:
        for particle in intermediate_particle:
            combined_particles[particle] = intermediate_particle[particle]

    mother_particle = naming_scheme[0]
    daughter_particles = combined_particles[naming_scheme[0]]
    return combined_particles, mother_particle, daughter_particles


def process_rapidsim_output(
    raw_rapidsim: str,
    dropMissing: bool,
    naming_scheme: dict,
    mass_hypotheses: Optional[dict],
    combined_particles: dict,
    true_PID_scheme: dict,
) -> None:
    """Process the output from RapidSim."""
    with uproot.open(f"{raw_rapidsim}:DecayTree") as file:
        if file.num_entries <= 0:  # file was empty
            display.error_splash(post_message="was created, but is empty.")
        map_NA_codes = tools.organise_output_tuple(
            raw_rapidsim,
            dropMissing,
            naming_scheme,
            mass_hypotheses,
            combined_particles,
            true_PID_scheme,
        )
    return map_NA_codes


def cleanup_files(loc: str) -> None:
    """Remove temporary files."""
    remove_file(Path(f"{loc}_RapidSim.stderr"))
    remove_file(Path(f"{loc}_RapidSim.stdout"))
    remove_file(Path(f"{loc}.DEC"))
    remove_file(Path(f"{loc}.config"))
    remove_file(Path(f"{loc}.decay"))
    remove_file(Path(f"{loc}_hists.root"))

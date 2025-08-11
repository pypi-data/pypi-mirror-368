import lhcb_rex.settings.globals as myGlobals
from lhcb_rex.rapidsim.run_rapidsim import run_rapidsim
from lhcb_rex.inference.run_network import run_inference_from_tuple as run_network
import lhcb_rex.tools.display as display

import lhcb_rex.inference.params as p


def run_from_tuple(**kwargs):
    with p.execute_command(kwargs, p.lhcbsim_runFromTupleParameters) as params:

        # Run network with rapidsim output
        rapidsim_tuple_reco = run_network(
            params["tuple_location"],
            mother_particle=params["mother_particle"],
            daughter_particles=params["daughter_particles"],
            # intermediate_particles=params["intermediate_particles"],
            branch_naming_structure=params["branch_naming_structure"],
            reconstruction_topology=params["reconstruction_topology"],
            stages=params["stages"],  # dont run smearing networks
            physical_units=params["physical_units"],
            mass_hypotheses=params["mass_hypotheses"],
        )

        # Display timing and file information
        total_time = display.timings_table(only_vertexing=True)
        display.print_file_info(rapidsim_tuple_reco, time=total_time)


def run(**kwargs):
    with p.execute_command(kwargs, p.lhcbsim_runParameters) as params:
        
        # Set verbosity if needed
        if params["verbose"]:
            myGlobals._verbose = True

        # Unpack the required parameters for run_rapidsim and run_network
        rapidsim_output = run_rapidsim(
            params["workingDir"],
            params["events"],
            params["decay"],
            params["naming_scheme"],
            params["decay_models"],
            params["mass_hypotheses"],
            params["intermediate_particles"],
            params["geometry"],
            params["acceptance"],
            params["useEvtGen"],
            params["evtGenUsePHOTOS"],
            params["dropMissing"],
            params["clean_up_files"],
        )

        (
            rapidsim_tuple,
            fully_reco,
            nPositive_missing_particles,
            nNegative_missing_particles,
            mother_particle,
            daughter_particles,
            true_PID_scheme,
            combined_particles,
            map_NA_codes,
        ) = rapidsim_output


        # Display events table
        display.events_table(params["events"], rapidsim_tuple)

        if params["only_rapidsim"]:
            total_time = display.timings_table(only_rapidsim=params["only_rapidsim"])
            display.print_file_info(rapidsim_tuple, time=total_time)
            return

        # intermediate_particles = combined_particles.copy()
        # del intermediate_particles["MOTHER"]

        rapidsim_tuple_reco = run_network(
            rapidsim_tuple,
            mother_particle=mother_particle,
            daughter_particles=daughter_particles,
            # intermediate_particles=intermediate_particles,
            reconstruction_topology=params["reconstruction_topology"],
            stages=[
                "smearPV",
                "smearMomenta",
                "genPID",
                "runVertexing",
            ],  # dont run smearing networks
            physical_units="GeV",  # RapidSim
            mass_hypotheses=params["mass_hypotheses"],
        )

        # Display timing and file information
        total_time = display.timings_table()
        display.print_file_info(rapidsim_tuple_reco, time=total_time)

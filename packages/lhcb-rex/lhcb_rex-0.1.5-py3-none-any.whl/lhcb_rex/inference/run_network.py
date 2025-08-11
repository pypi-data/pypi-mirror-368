import lhcb_rex.settings.globals as myGlobals
from lhcb_rex.data.data_manager import tuple_manager
from lhcb_rex.inference.inference_network_manager import Network
from lhcb_rex.inference.inference_graph_constructor import GraphConstructor
import lhcb_rex.tools.display as display
import lhcb_rex.tools.variables_tools as pts
import numpy as np
import pandas as pd
import warnings
import lhcb_rex.tools.get_weights as get_weights


warnings.simplefilter(action="ignore", category=pd.errors.PerformanceWarning)
warnings.simplefilter(action="ignore", category=RuntimeWarning)
warnings.simplefilter(action="ignore", category=UserWarning)
warnings.simplefilter(action="ignore", category=FutureWarning)


def run_inference_from_tuple(
    tuple_location,
    mother_particle,
    daughter_particles,
    # intermediate_particles=None,
    branch_naming_structure=None,
    reconstruction_topology=None,
    physical_units="GeV",
    mass_hypotheses=None,
    stages=["smearPV", "smearMomenta", "genPID", "runVertexing"],
):

    hf_model_paths = get_weights.get_model_paths()

    if reconstruction_topology is None:
        daughters_str = " ".join(daughter_particles)
        reconstruction_topology = f"{mother_particle} -> {daughters_str}"
    graph_structure = GraphConstructor(reconstruction_topology)
    # print('plotting', reconstruction_topology)
    # graph_structure.plot()
    # quit()
    intermediate_particles = graph_structure.intermediate_particles

    new_branches_to_keep = []

    myGlobals.particle_map = {}  # 2 two way map to translate between particle names
    myGlobals.particle_map["toDAUGHTERS"] = {}
    myGlobals.particle_map["fromDAUGHTERS"] = {}
    for idx, daughter_particle in enumerate(daughter_particles):
        myGlobals.particle_map["fromDAUGHTERS"][f"DAUGHTER{idx + 1}"] = (
            daughter_particle
        )
        myGlobals.particle_map["toDAUGHTERS"][daughter_particle] = f"DAUGHTER{idx + 1}"
    myGlobals.particle_map["toINTERMEDIATES"] = {}
    myGlobals.particle_map["fromINTERMEDIATES"] = {}
    if intermediate_particles is not None:
        for idx, intermediate_particle in enumerate(intermediate_particles):
            # ridx = random.randint(1000000, 9999999)
            myGlobals.particle_map["fromINTERMEDIATES"][f"INTERMEDIATE{idx}"] = (
                intermediate_particle
            )
            myGlobals.particle_map["toINTERMEDIATES"][intermediate_particle] = (
                f"INTERMEDIATE{idx}"
            )

    Nparticles = len(list(myGlobals.particle_map["fromDAUGHTERS"].keys()))

    if physical_units == "GeV":
        myGlobals.masses = myGlobals.masses_GeV
        myGlobals.particle_masses_dict_mothers = (
            myGlobals.particle_masses_dict_mothers_GeV
        )

    combined_particles = {}
    combined_particles["MOTHER"] = list(myGlobals.particle_map["fromDAUGHTERS"].keys())
    if intermediate_particles is not None:
        for intermediate_particle, daughters in intermediate_particles.items():
            combined_particles[
                myGlobals.particle_map["toINTERMEDIATES"][intermediate_particle]
            ] = [
                myGlobals.particle_map["toDAUGHTERS"][daughter]
                for daughter in daughters
            ]

    with (
        myGlobals.stopwatches.timer("Networks - processing"),
        display.status_execution(
            status_message="[bold green]Staging tuple...",
            complete_message="[bold green]Tuple staged :white_check_mark:",
        ),
        display.log_execution("Reading tuple"),
    ):
        data_tuple = tuple_manager(
            tuple_location=tuple_location,
            mother_particle_name=mother_particle,
            daughter_particle_names=daughter_particles,
            combined_particles=combined_particles,
            branch_naming_structure=branch_naming_structure,
            mass_hypotheses=mass_hypotheses,
        )
    # run some pytests for this function

    with (
        myGlobals.stopwatches.timer("Networks - config"),
        display.status_execution(
            status_message="[bold green]Initialising networks...",
            complete_message="[bold green]Networks initialised :white_check_mark:",
        ),
    ):
        if "smearPV" in stages:
            with display.log_execution("Initialising PV smearing network"):
                PVModel = Network(
                    network="PV_smear_diffusion",
                    model_parameters="PVsmear_model_parameters.json",
                    # pkl="/users/am13743/Rex/logs/July_pv_smear/version_23/models.pkl",  # normal
                    pkl=hf_model_paths["smearPV"],
                    Nparticles=Nparticles,
                    physical_units=physical_units,
                    daughter_particle_names=list(daughter_particles),
                )

        if "smearMomenta" in stages:
            with display.log_execution("Initialising momentum smearing network"):
                smearModel = Network(
                    network="mom_smear_diffusion",
                    model_parameters="diffusion_model_parameters.json",
                    # pkl="/users/am13743/Rex/logs/July_smear_diffusion2/version_0/models.pkl",
                    pkl=hf_model_paths["smearMomenta"],
                    N_diffusion_steps=50,
                    # N_diffusion_steps=1,
                    Nparticles=Nparticles,
                    physical_units=physical_units,
                    daughter_particle_names=list(daughter_particles),
                    EMA=True,
                )

        if "genPID" in stages:
            with display.log_execution("Initialising PID network"):
                PIDModel = Network(
                    network="PID_trig_diffusion",
                    model_parameters="diffusion_model_parameters.json",
                    # pkl="/users/am13743/Rex/logs/PID_diffusion/version_0/models.pkl",
                    pkl=hf_model_paths["genPID"],
                    N_diffusion_steps=50,
                    # N_diffusion_steps=1,
                    Nparticles=Nparticles,
                    physical_units=physical_units,
                    daughter_particle_names=list(daughter_particles),
                    EMA=False,
                )

        if "runVertexing" in stages:
            with display.log_execution("Initialising vertexing network"):
                vtxModel = Network(
                    network="reco_vertex_diffusion",
                    model_parameters="diffusion_model_parameters_vtx.json",
                    pkl=hf_model_paths["runVertexing"],
                    # pkl="/users/am13743/Rex/logs/AllVars/version_3/models_yes_20_1.pkl", # keep
                    # pkl="/users/am13743/Rex/logs/AllVars/version_1/models.pkl",
                    N_diffusion_steps=50,
                    # N_diffusion_steps=25,
                    # N_diffusion_steps=1,
                    Nparticles=Nparticles,
                    physical_units=physical_units,
                    daughter_particle_names=list(daughter_particles),
                    EMA=False,
                )

    with myGlobals.stopwatches.timer("Networks - processing"):
        data_tuple.append_initial_conditional_information(data_tuple.true_PID_scheme)
        data_tuple.append_mother_flight()

    if "smearPV" in stages:
        with (
            myGlobals.stopwatches.timer("Networks - generation"),
            display.status_execution(
                status_message="[bold green]Smearing primary vertex...",
                complete_message="[bold green]Primary vertex smeared :white_check_mark:",
            ),
        ):
            smearingPV_conditions = data_tuple.get_branches(
                PVModel.conditions,
                PVModel.transformers,
                numpy=True,
            )

            smeared_PV_output = PVModel.query_network(
                smearingPV_conditions,
            )

            data_tuple.smearPV(smeared_PV_output)

    if "smearMomenta" in stages:
        with (
            myGlobals.stopwatches.timer("Networks - generation"),
            display.status_execution(
                status_message="[bold green]Smearing momenta...",
                complete_message="[bold green]Momenta smeared :white_check_mark:",
            ),
        ):
            smearing_node_conditions = data_tuple.get_branches(
                smearModel.conditions,
                smearModel.transformers,
                numpy=True,
            )

            smearing_edge_conditions = data_tuple.get_branches(
                smearModel.edge_conditions,
                smearModel.edge_transformers,
                numpy=False,
            )

            myGlobals.personalised_track_node_types = True
            mom_smearing_output = smearModel.query_network(
                data_tuple.true_PID_scheme,
                smearing_node_conditions,
                smearing_edge_conditions,
            )
            myGlobals.personalised_track_node_types = False

            data_tuple.propagate_smearing(mom_smearing_output, Nparticles=Nparticles)
            recomputed_branches = data_tuple.recompute_combined_particles(
                combined_particles, list(myGlobals.particle_map["fromDAUGHTERS"].keys())
            )
            new_branches_to_keep.extend([i for i in mom_smearing_output.keys() if "delta" not in i])
            new_branches_to_keep.extend(recomputed_branches)
            
    with myGlobals.stopwatches.timer("Networks - processing"):
        data_tuple.append_secondary_conditional_information()

    if "genPID" in stages:
        with (
            myGlobals.stopwatches.timer("Networks - generation"),
            display.status_execution(
                status_message="[bold green]Applying PID and triger...",
                complete_message="[bold green]PID and triger applied :white_check_mark:",
            ),
        ):
            pid_node_conditions = data_tuple.get_branches(
                PIDModel.conditions,
                PIDModel.transformers,
                numpy=True,
            )

            pid_edge_conditions = data_tuple.get_branches(
                PIDModel.edge_conditions,
                PIDModel.edge_transformers,
                numpy=False,
            )

            myGlobals.personalised_track_node_types = True
            pid_trigger_output = PIDModel.query_network(
                data_tuple.true_PID_scheme, pid_node_conditions, pid_edge_conditions
            )
            myGlobals.personalised_track_node_types = False

            data_tuple.add_branches(pid_trigger_output)
            new_branches_to_keep.extend(list(pid_trigger_output.keys()))

    with myGlobals.stopwatches.timer("Networks - processing"):
        data_tuple.append_tertiary_conditional_information(
            combined_particles,
            data_tuple.true_PID_scheme,
            list(myGlobals.particle_map["fromDAUGHTERS"].keys()),
        )

    if "runVertexing" in stages:
        with (
            myGlobals.stopwatches.timer("Networks - generation"),
            display.status_execution(
                status_message="[bold green]Running vertexing...",
                complete_message="[bold green]Vertexing complete :white_check_mark:",
            ),
        ):
            vtx_mother_conditions = data_tuple.get_branches(
                [cond for cond in vtxModel.mother_conditions if cond != "N_daughters"],
                vtxModel.transformers,
                numpy=False,
            )
            vtx_intermediate_conditions = data_tuple.get_branches(
                [cond for cond in vtxModel.intermediate_conditions if cond != "N_daughters"],
                vtxModel.transformers,
                numpy=False,
            )
            vtx_track_conditions = data_tuple.get_branches(
                vtxModel.track_conditions,
                vtxModel.transformers,
                numpy=False,
            )

            vtx_mother_conditions = np.asarray(
                vtx_mother_conditions[[cond for cond in vtxModel.mother_conditions if cond != "N_daughters"]]
            )
            vtx_intermediate_conditions = np.asarray(
                vtx_intermediate_conditions[[cond for cond in vtxModel.intermediate_conditions if cond != "N_daughters"]]
            )
            vtx_track_conditions = np.asarray(
                vtx_track_conditions[vtxModel.track_conditions]
            )
            # np.save('vtx_mother_conditions_RS.npy', vtx_mother_conditions)
            # np.save('vtx_intermediate_conditions_RS.npy', vtx_intermediate_conditions)
            # np.save('vtx_track_conditions_RS.npy', vtx_track_conditions)
            # quit()

            vtx_track_conditions = np.reshape(
                vtx_track_conditions, (-1, Nparticles, len(myGlobals.track_conditions))
            )

            out_df = vtxModel.query_network_vtx(
                graph_structure,
                vtx_mother_conditions,
                vtx_intermediate_conditions,
                vtx_track_conditions,
                Nparticles=Nparticles,
            )

            data_tuple.add_branches(out_df)
            new_branches_to_keep.extend(list(out_df.keys()))

    with myGlobals.stopwatches.timer("Networks - processing"):

        new_branches_to_keep_user_naming = []

        new_branches = []
        temp_particles = {}
        for idx, particle in enumerate(
            list(myGlobals.particle_map["toDAUGHTERS"].keys())
        ):
            temp_particles[particle] = str(np.random.randint(0, 99999999))
        temp_combined_particles = {}
        for idx, combined_particle in enumerate(combined_particles):
            if combined_particle != "MOTHER":
                temp_combined_particles[
                    myGlobals.particle_map["fromINTERMEDIATES"][combined_particle]
                ] = str(np.random.randint(0, 99999999))

        for branch in data_tuple.tuple:
            branch_in = branch
            for combined_particle in combined_particles:
                if combined_particle == "MOTHER":
                    branch = branch.replace(combined_particle, mother_particle)
                else:
                    branch = branch.replace(
                        combined_particle,
                        temp_combined_particles[
                            myGlobals.particle_map["fromINTERMEDIATES"][
                                combined_particle
                            ]
                        ],
                    )

            for combined_particle in combined_particles:
                if combined_particle != "MOTHER":
                    branch = branch.replace(
                        temp_combined_particles[
                            myGlobals.particle_map["fromINTERMEDIATES"][
                                combined_particle
                            ]
                        ],
                        myGlobals.particle_map["fromINTERMEDIATES"][combined_particle],
                    )

            for particle in list(myGlobals.particle_map["toDAUGHTERS"].keys()):
                branch = branch.replace(
                    myGlobals.particle_map["toDAUGHTERS"][particle],
                    temp_particles[particle],
                )
            for particle in list(myGlobals.particle_map["toDAUGHTERS"].keys()):
                branch = branch.replace(temp_particles[particle], particle)
            new_branches.append(branch)
            if branch_in in new_branches_to_keep:
                new_branches_to_keep_user_naming.append(branch)

        data_tuple.tuple.columns = new_branches

        data_tuple.tuple = data_tuple.tuple[
            data_tuple.original_branches + new_branches_to_keep_user_naming
        ]

        # re-order columns
        columns = data_tuple.tuple.columns
        prefix_order = [mother_particle]
        for intermediate in combined_particles:
            if intermediate != "MOTHER":
                prefix_order.append(
                    myGlobals.particle_map["fromINTERMEDIATES"][intermediate]
                )
        for daughter_particle in daughter_particles:
            prefix_order.append(daughter_particle)

        ordered_columns = []
        for prefix in prefix_order:
            cols_with_prefix = [col for col in columns if col.startswith(prefix)]
            ordered_columns.extend(cols_with_prefix)
        data_tuple.tuple = data_tuple.tuple[ordered_columns]

        output_location = f"{data_tuple.tuple_location[:-5]}_reco.root"

        pts.write_df_to_root(data_tuple.tuple, output_location, "DecayTree")

    print(f"Saving every branch to {output_location}")

    return output_location

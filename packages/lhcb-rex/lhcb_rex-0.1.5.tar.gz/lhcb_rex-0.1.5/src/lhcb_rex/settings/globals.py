from rich.console import Console
from lhcb_rex.tools.stopwatch import stopwatch
import os
import pandas as pd
import torch

particle_universe = [11, 13, 211, 321, 2212]

masses = {}
masses[321] = 493.677
masses[211] = 139.57039
masses[13] = 105.66
masses[11] = 0.51099895000
masses[2212] = 938.272

particle_masses_dict_mothers = {}
particle_masses_dict_mothers[411] = 1869.62
particle_masses_dict_mothers[421] = 1864.84
particle_masses_dict_mothers[431] = 1968.47

particle_masses_dict_mothers[511] = 5279.65
particle_masses_dict_mothers[521] = 5279.34
particle_masses_dict_mothers[531] = 5366.88
particle_masses_dict_mothers[541] = 6274.9


masses_GeV = {}
masses_GeV[321] = 493.677 * 1e-3
masses_GeV[211] = 139.57039 * 1e-3
masses_GeV[13] = 105.66 * 1e-3
masses_GeV[11] = 0.51099895000 * 1e-3
masses_GeV[2212] = 938.272 * 1e-3

particle_masses_dict_mothers_GeV = {}
particle_masses_dict_mothers_GeV[411] = 1869.62 * 1e-3
particle_masses_dict_mothers_GeV[421] = 1864.84 * 1e-3
particle_masses_dict_mothers_GeV[431] = 1968.47 * 1e-3

particle_masses_dict_mothers_GeV[511] = 5279.65 * 1e-3
particle_masses_dict_mothers_GeV[521] = 5279.34 * 1e-3
particle_masses_dict_mothers_GeV[531] = 5366.88 * 1e-3
particle_masses_dict_mothers_GeV[541] = 6274.9 * 1e-3


personalised_track_node_types = False

if torch.cuda.is_available():
    device = torch.device("cuda:5")
else:
    device = torch.device("cpu")
    print("EXECUTING ON CPU")


stopwatches = stopwatch()

console = Console()

my_decay_splash = []


# Check environment variables
def get_environment_variable(var_name: str) -> str:
    value = os.environ.get(var_name)
    if value is None:
        print(f"Environment variable ${var_name} not set.")
    return value


rapidsim_settings = {}
rapidsim_settings["imported"] = False

if os.environ.get("RAPIDSIM_ROOT"):
    PARTICLES_FILE = "config/particles.dat"
    EVTGEN_ROOT_ENV = "EVTGEN_ROOT"
    RAPIDSIM_EXECUTABLE = "/build/src/RapidSim.exe"

    rapidsim_settings["RAPIDSIM_ROOT"] = os.environ.get("RAPIDSIM_ROOT")
    rapidsim_settings["RAPIDSIM_particles"] = (
        os.environ.get("RAPIDSIM_ROOT") + "/" + PARTICLES_FILE
    )
    rapidsim_settings["RAPIDSIM_particles_df"] = pd.read_csv(
        rapidsim_settings["RAPIDSIM_particles"], sep=r"\s+"
    )
    rapidsim_settings["USE_EVTGEN"] = (
        get_environment_variable(EVTGEN_ROOT_ENV) is not None
    )
    rapidsim_settings["rapidsim_exe"] = (
        f"{rapidsim_settings['RAPIDSIM_ROOT']}{RAPIDSIM_EXECUTABLE}"
    )
    rapidsim_settings["imported"] = True

else:
    print("RapidSim not present")
    # Running without RapidSim


def global_print_my_decay_splash():
    if len(my_decay_splash) > 0:
        for counts, line in enumerate(my_decay_splash):
            if counts % 2 == 0:
                console.print("")
            console.print(line)
        console.print("")


smearPV_targets = [
    "MOTHER_TRUE_FD",
    # "MOTHER_TRUEENDVERTEX_X",
    # "MOTHER_TRUEENDVERTEX_Y",
    # "MOTHER_TRUEENDVERTEX_Z",
    "MOTHER_TRUEORIGINVERTEX_X",
    "MOTHER_TRUEORIGINVERTEX_Y",
    "MOTHER_TRUEORIGINVERTEX_Z",
]
smearPV_conditions = [
    "MOTHER_TRUEP",
    "MOTHER_TRUEP_T",
    "MOTHER_TRUEP_X",
    "MOTHER_TRUEP_Y",
    "MOTHER_TRUEP_Z",
]


# smearPV_targets = [
#     "MOTHER_TRUEORIGINVERTEX_X",
#     "MOTHER_TRUEORIGINVERTEX_Y",
#     "MOTHER_TRUEORIGINVERTEX_Z",
#     "MOTHER_OWNPV_X",
#     "MOTHER_OWNPV_Y",
#     "MOTHER_OWNPV_Z",
#     "MOTHER_TRUEENDVERTEX_X",
#     "MOTHER_TRUEENDVERTEX_Y",
#     "MOTHER_TRUEENDVERTEX_Z",
#     "MOTHER_ENDVERTEX_X",
#     "MOTHER_ENDVERTEX_Y",
#     "MOTHER_ENDVERTEX_Z",
# ]
# smearPV_conditions = [
#     "MOTHER_FLIGHT",
# ]


smearing_track_targets = [
    "DAUGHTERN_delta_PX",
    "DAUGHTERN_delta_PY",
    # "DAUGHTERN_Preco_overP",
    "DAUGHTERN_delta_PZ",
    "DAUGHTERN_TRACK_CHI2NDOF",
    "DAUGHTERN_TRACK_GhostProb",
]
smearing_track_conditions = [
    "DAUGHTERN_TRUEP_X",
    "DAUGHTERN_TRUEP_Y",
    "DAUGHTERN_TRUEP_Z",
    "DAUGHTERN_TRUEP",
    "DAUGHTERN_TRUEE",
]
smearing_edge_conditions = [
    "edge_angle_DAUGHTERN_DAUGHTERN_TRUE",
]


PID_track_targets = [
    "DAUGHTERN_PIDe",
    "DAUGHTERN_PIDmu",
    "DAUGHTERN_PIDK",
    "DAUGHTERN_PIDp",
    "DAUGHTERN_MC15TuneV1_ProbNNe",
    "DAUGHTERN_MC15TuneV1_ProbNNmu",
    "DAUGHTERN_MC15TuneV1_ProbNNpi",
    "DAUGHTERN_MC15TuneV1_ProbNNk",
    "DAUGHTERN_MC15TuneV1_ProbNNp",
    # "DAUGHTERN_L0HadronDecision_TIS",
    # "DAUGHTERN_L0HadronDecision_TOS",
    # "DAUGHTERN_L0ElectronDecision_TIS",
    # "DAUGHTERN_L0ElectronDecision_TOS",
    # "DAUGHTERN_L0MuonDecision_TIS",
    # "DAUGHTERN_L0MuonDecision_TOS",
    # "DAUGHTERN_L0PhotonDecision_TIS",
    # "DAUGHTERN_L0PhotonDecision_TOS",
]

PID_track_conditions = [
    "DAUGHTERN_TRUEP_X",
    "DAUGHTERN_TRUEP_Y",
    "DAUGHTERN_TRUEP_Z",
    "DAUGHTERN_TRUEP",
    "DAUGHTERN_TRUEE",
    "DAUGHTERN_delta_PX",
    "DAUGHTERN_delta_PY",
    "DAUGHTERN_Preco_overP",
    "DAUGHTERN_IP",
    "DAUGHTERN_IP_TRUE",
    "DAUGHTERN_angle_wrt_mother",
    "DAUGHTERN_angle_wrt_mother_reco",
    "DAUGHTERN_eta",
    "DAUGHTERN_eta_TRUE",
    "DAUGHTERN_TRACK_CHI2NDOF",
    "DAUGHTERN_TRACK_GhostProb",
]
PID_edge_conditions = [
    "edge_angle_DAUGHTERN_DAUGHTERN_TRUE",
]


option = "A"  # standard
# option = "B" # no vertex information
# option = "C" # predict vertex information


mother_targets = [
    "MOTHER_VTXISOBDTHARDFIRSTVALUE",
    "MOTHER_VTXISOBDTHARDSECONDVALUE",
    "MOTHER_VTXISOBDTHARDTHIRDVALUE",
    "MOTHER_ENDVERTEX_CHI2NDOF",
    # "MOTHER_ENDVERTEX_CHI2",
    "MOTHER_IPCHI2_OWNPV",
    "MOTHER_FDCHI2_OWNPV",
    "MOTHER_DIRA_OWNPV",
]
intermediate_targets = [
    "INTERMEDIATE_ENDVERTEX_CHI2NDOF",
    # "INTERMEDIATE_ENDVERTEX_CHI2",
    "INTERMEDIATE_IPCHI2_OWNPV",
    "INTERMEDIATE_FDCHI2_OWNPV",
    "INTERMEDIATE_DIRA_OWNPV",
]
track_targets = [
    "DAUGHTERN_IPCHI2_OWNPV",
    # "DAUGHTERN_TRACK_CHI2NDOF",
    # "DAUGHTERN_TRACK_GhostProb",
]

if option == "C":
    mother_targets.extend(
        [
            "MOTHER_TRUEENDVERTEX_X",
            "MOTHER_TRUEENDVERTEX_Y",
            "MOTHER_TRUEENDVERTEX_Z",
            "MOTHER_TRUEORIGINVERTEX_X",
            "MOTHER_TRUEORIGINVERTEX_Y",
            "MOTHER_TRUEORIGINVERTEX_Z",
            "MOTHER_DIRA",
            "MOTHER_DIRA_TRUE",
            "MOTHER_IP",
            "MOTHER_IP_TRUE",
        ]
    )
    intermediate_targets.extend(
        [
            "INTERMEDIATE_DIRA",
            "INTERMEDIATE_DIRA_TRUE",
            "INTERMEDIATE_IP",
            "INTERMEDIATE_IP_TRUE",
        ]
    )
    track_targets.extend(
        [
            "DAUGHTERN_IP",
            "DAUGHTERN_IP_TRUE",
        ]
    )

if option == "A":
    mother_conditions = [  # these things are not accessible to intermediate - intermediate might not exist
        "MOTHER_TRUEENDVERTEX_X",
        "MOTHER_TRUEENDVERTEX_Y",
        "MOTHER_TRUEENDVERTEX_Z",
        # "MOTHER_TRUEORIGINVERTEX_X",
        # "MOTHER_TRUEORIGINVERTEX_Y",
        "MOTHER_TRUEORIGINVERTEX_Z",
        "MOTHER_TRUEP",
        "MOTHER_TRUEP_T",
        "MOTHER_TRUEP_X",
        "MOTHER_TRUEP_Y",
        "MOTHER_TRUEP_Z",
        "MOTHER_FLIGHT",
        "MOTHER_DIRA",
        "MOTHER_DIRA_TRUE",
        "MOTHER_IP",
        "MOTHER_IP_TRUE",
        "MOTHER_P",
        "MOTHER_PT",
        "MOTHER_PX",
        "MOTHER_PY",
        "MOTHER_PZ",
        "MOTHER_missing_P", 
        "MOTHER_missing_PT", 
        "N_daughters", # align with training (i picked the wrong set)
    ]  # N_daughters must be the last condition
    intermediate_conditions = [
        "INTERMEDIATE_DIRA",
        "INTERMEDIATE_DIRA_TRUE",
        "INTERMEDIATE_IP",
        "INTERMEDIATE_IP_TRUE",
        "INTERMEDIATE_P",
        "INTERMEDIATE_PT",
        "INTERMEDIATE_PX",
        "INTERMEDIATE_PY",
        "INTERMEDIATE_PZ",
        "N_daughters", 
    ]  # N_daughters must be the last condition
    track_conditions = [
        "DAUGHTERN_FLIGHT",
        "DAUGHTERN_IP",
        "DAUGHTERN_IP_TRUE",
        "DAUGHTERN_PX",
        "DAUGHTERN_PY",
        "DAUGHTERN_PZ",
        "DAUGHTERN_TRUEP_X",
        "DAUGHTERN_TRUEP_Y",
        "DAUGHTERN_TRUEP_Z",
        "DAUGHTERN_angle_wrt_mother",
        "DAUGHTERN_angle_wrt_mother_reco",
        "DAUGHTERN_delta_P", # in new arch # align with training (i picked the wrong set)
        "DAUGHTERN_delta_PT", # in new arch # align with training (i picked the wrong set)
        "DAUGHTERN_eta",
        "DAUGHTERN_eta_TRUE",
        "DAUGHTERN_residualfrac_PX",
        "DAUGHTERN_residualfrac_PY",
        "DAUGHTERN_residualfrac_PZ",
        # # PID variables
        # "DAUGHTERN_PIDe",
        # "DAUGHTERN_PIDmu",
        # "DAUGHTERN_PIDK",
        # "DAUGHTERN_PIDp",
        # "DAUGHTERN_MC15TuneV1_ProbNNe",
        # "DAUGHTERN_MC15TuneV1_ProbNNmu",
        # "DAUGHTERN_MC15TuneV1_ProbNNpi",
        # "DAUGHTERN_MC15TuneV1_ProbNNk",
        # "DAUGHTERN_MC15TuneV1_ProbNNp",
        "DAUGHTERN_TRACK_CHI2NDOF", # in new arch
        "DAUGHTERN_TRACK_GhostProb", # in new arch
    ]
else:
    mother_conditions = [  # these things are not accessible to intermediate - intermediate might not exist
        # "MOTHER_TRUEENDVERTEX_X",
        # "MOTHER_TRUEENDVERTEX_Y",
        # "MOTHER_TRUEENDVERTEX_Z",
        # "MOTHER_TRUEORIGINVERTEX_X",
        # "MOTHER_TRUEORIGINVERTEX_Y",
        # "MOTHER_TRUEORIGINVERTEX_Z",
        "MOTHER_TRUEP",
        "MOTHER_TRUEP_T",
        "MOTHER_TRUEP_X",
        "MOTHER_TRUEP_Y",
        "MOTHER_TRUEP_Z",
        "MOTHER_FLIGHT",
        # "MOTHER_DIRA",
        # "MOTHER_DIRA_TRUE",
        # "MOTHER_IP",
        # "MOTHER_IP_TRUE",
        "MOTHER_P",
        "MOTHER_PT",
        "MOTHER_PX",
        "MOTHER_PY",
        "MOTHER_PZ",
        "MOTHER_missing_P",
        "MOTHER_missing_PT",
        "N_daughters",
    ]  # N_daughters must be the last condition
    intermediate_conditions = [
        # "INTERMEDIATE_DIRA",
        # "INTERMEDIATE_DIRA_TRUE",
        # "INTERMEDIATE_IP",
        # "INTERMEDIATE_IP_TRUE",
        "INTERMEDIATE_P",
        "INTERMEDIATE_PT",
        "INTERMEDIATE_PX",
        "INTERMEDIATE_PY",
        "INTERMEDIATE_PZ",
        "N_daughters",
    ]  # N_daughters must be the last condition
    track_conditions = [
        "DAUGHTERN_FLIGHT",
        # "DAUGHTERN_IP",
        # "DAUGHTERN_IP_TRUE",
        "DAUGHTERN_PX",
        "DAUGHTERN_PY",
        "DAUGHTERN_PZ",
        "DAUGHTERN_TRUEP_X",
        "DAUGHTERN_TRUEP_Y",
        "DAUGHTERN_TRUEP_Z",
        "DAUGHTERN_angle_wrt_mother",
        "DAUGHTERN_angle_wrt_mother_reco",
        "DAUGHTERN_delta_P",
        "DAUGHTERN_delta_PT",
        "DAUGHTERN_eta",
        "DAUGHTERN_eta_TRUE",
        "DAUGHTERN_residualfrac_PX",
        "DAUGHTERN_residualfrac_PY",
        "DAUGHTERN_residualfrac_PZ",
        # # PID variables
        # "DAUGHTERN_PIDe",
        # "DAUGHTERN_PIDmu",
        # "DAUGHTERN_PIDK",
        # "DAUGHTERN_PIDp",
        # "DAUGHTERN_MC15TuneV1_ProbNNe",
        # "DAUGHTERN_MC15TuneV1_ProbNNmu",
        # "DAUGHTERN_MC15TuneV1_ProbNNpi",
        # "DAUGHTERN_MC15TuneV1_ProbNNk",
        # "DAUGHTERN_MC15TuneV1_ProbNNp",
        # "DAUGHTERN_TRACK_CHI2NDOF",
        # "DAUGHTERN_TRACK_GhostProb",
    ]

validation_variables = [
    "mkl",
    "q2",
    "mkee",
    "ctl",
]

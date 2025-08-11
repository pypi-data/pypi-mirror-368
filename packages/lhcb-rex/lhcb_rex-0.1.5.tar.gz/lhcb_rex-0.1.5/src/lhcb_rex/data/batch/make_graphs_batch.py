import lhcb_rex.data.graph_maker as graph_maker
import argparse
import json
import lhcb_rex.settings.globals as myGlobals


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


# --processID 0 --config_file "./davinci/configs/configs_4_body/config_dict_B0_AAA+int(DDD-int(->BBB-CCC+)).pickle" --file_name "/dice/users/am13743/fast_vertex_quality/GENERALISED/N4_topIdx4_head_more_vars.root" --splits 5


def parse_args():
    parser = argparse.ArgumentParser(
        description="Load settings from command line arguments."
    )
    parser.add_argument(
        "--file_name", type=str, required=True, help="Path to the input ROOT file"
    )
    parser.add_argument(
        "--config_file", type=str, required=True, help="Path to the input ROOT file"
    )
    parser.add_argument("--root", type=str, required=True, help="Root directory path")
    parser.add_argument("--splits", type=int, required=True)
    parser.add_argument("--save_string", type=str, required=True)
    parser.add_argument("--extra_tag", type=str, required=True)
    parser.add_argument("--use_weights", type=str2bool, required=True)
    parser.add_argument("--smearingnet", type=str2bool, required=True)
    parser.add_argument("--PIDnet", type=str2bool, required=True)
    parser.add_argument("--processID", type=int, required=True)
    parser.add_argument("--require_validation_variables", type=str2bool, required=True)
    return parser.parse_args()


args = parse_args()

output_path = args.root + f"_{args.extra_tag}/"

if args.smearingnet:
    mother_targets = []
    intermediate_targets = []
    track_targets = myGlobals.smearing_track_targets
    mother_conditions = []
    intermediate_conditions = []
    track_conditions = myGlobals.smearing_track_conditions
    edge_conditions = myGlobals.smearing_edge_conditions
elif args.PIDnet:
    mother_targets = []
    intermediate_targets = []
    track_targets = myGlobals.PID_track_targets
    mother_conditions = []
    intermediate_conditions = []
    track_conditions = myGlobals.PID_track_conditions
    edge_conditions = myGlobals.PID_edge_conditions
else:
    mother_targets = myGlobals.mother_targets
    intermediate_targets = myGlobals.intermediate_targets
    track_targets = myGlobals.track_targets
    mother_conditions = myGlobals.mother_conditions
    intermediate_conditions = myGlobals.intermediate_conditions
    track_conditions = myGlobals.track_conditions
    edge_conditions = []


graph_maker.GENERALISED_HeteroGraphDataset(
    path=args.file_name,
    root=output_path,
    config=args.config_file,
    splits=args.splits,
    use_weights=args.use_weights,
    smearingnet=args.smearingnet,
    PIDnet=args.PIDnet,
    processID=args.processID,
    require_validation_variables=args.require_validation_variables,
    force_reload=True,
    mother_targets=mother_targets,
    intermediate_targets=intermediate_targets,
    track_targets=track_targets,
    mother_conditions=mother_conditions,
    intermediate_conditions=intermediate_conditions,
    track_conditions=track_conditions,
    edge_conditions=edge_conditions,
)

# quit()


# settings = {}
# settings[args.save_string] = {
#     "file_name": args.file_name,
#     "particles_involved": args.particles_involved,
#     "intermediates": json.loads(args.intermediates),
#     "mother_N": args.mother_N,
#     "intermediate_N": json.loads(args.intermediate_N),
#     "root": args.root,
# }

# print(json.dumps(settings, indent=4))

# max_N = args.max_N
# splits = args.splits
# extra_tag = args.extra_tag
# use_weights = args.use_weights
# full_reco = args.full_reco
# smearingnet = args.smearingnet
# require_validation_variables = args.require_validation_variables
# PIDnet = args.PIDnet

# if smearingnet and PIDnet:
#     print("smearingnet and PIDnet, pick one")
#     raise Exception

# print(max_N)
# print(splits)
# print(extra_tag)
# print(use_weights)
# print(full_reco)


# processID = args.processID
# print("processID", processID)

# # edge_conditions = [
# #     "edge_angle_DAUGHTERN_DAUGHTERN",
# #     "edge_angle_DAUGHTERN_DAUGHTERN_TRUE",
# # ]

# for setting in settings:
#     print(f"\n\n\n {settings[setting]}")

#     file_name = settings[setting]["file_name"]
#     particles_involved = settings[setting]["particles_involved"]
#     intermediates = settings[setting]["intermediates"]
#     mother_N = settings[setting]["mother_N"]
#     intermediate_N = settings[setting]["intermediate_N"]
#     root = settings[setting]["root"]

#     print(f"\n {full_reco}")

#     if full_reco:
#         reco_tag = "fullreco"
#     else:
#         reco_tag = "partreco"

#     splits_in = splits

#     output_path = root + f"_{reco_tag}{extra_tag}/"
#     if smearingnet:
#         output_path = root + f"_{reco_tag}{extra_tag}smearingnet/"

#     if smearingnet:
#         mother_targets = []
#         intermediate_targets = []
#         track_targets = myGlobals.smearing_track_targets
#         mother_conditions = []
#         intermediate_conditions = []
#         track_conditions = myGlobals.smearing_track_conditions
#         edge_conditions = myGlobals.smearing_edge_conditions
#     elif PIDnet:
#         mother_targets = []
#         intermediate_targets = []
#         track_targets = myGlobals.PID_track_targets
#         mother_conditions = []
#         intermediate_conditions = []
#         track_conditions = myGlobals.PID_track_conditions
#         edge_conditions = myGlobals.PID_edge_conditions
#     else:
#         mother_targets = myGlobals.mother_targets
#         intermediate_targets = myGlobals.intermediate_targets
#         track_targets = myGlobals.track_targets
#         mother_conditions = myGlobals.mother_conditions
#         intermediate_conditions = myGlobals.intermediate_conditions
#         track_conditions = myGlobals.track_conditions
#         edge_conditions = []

#     graph_maker.HeteroGraphDataset(
#         root=output_path,
#         particles_involved=particles_involved,
#         intermediates=intermediates,
#         fully_reco=full_reco,
#         max_N_samples_per=max_N,
#         force_reload=True,
#         path=file_name,
#         mother_targets=mother_targets,
#         intermediate_targets=intermediate_targets,
#         track_targets=track_targets,
#         mother_conditions=mother_conditions,
#         intermediate_conditions=intermediate_conditions,
#         track_conditions=track_conditions,
#         edge_conditions=edge_conditions,
#         use_weights=use_weights,
#         splits=splits_in,
#         mother_N=mother_N,
#         intermediate_N=intermediate_N,
#         processID=processID,
#         smearingnet=smearingnet,
#         PIDnet=PIDnet,
#         require_validation_variables=require_validation_variables,
#     )

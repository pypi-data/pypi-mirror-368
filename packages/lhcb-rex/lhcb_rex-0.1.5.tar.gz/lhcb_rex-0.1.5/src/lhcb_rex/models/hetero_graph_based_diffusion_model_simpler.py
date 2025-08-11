import torch
import torch.nn as nn
import torch.nn.functional as F

from torch_geometric.nn import GATConv, HeteroConv

from torch import Tensor
from typing import Tuple, Optional, List, Dict
import pytorch_lightning as pl

import warnings

from torch_geometric.nn.conv import MessagePassing
from torch_geometric.nn.module_dict import ModuleDict
from torch_geometric.typing import EdgeType, NodeType
from torch_geometric.utils.hetero import check_add_self_loops


def print_heterogenous_representation(rep):
    for key in rep:
        print(f"{key}:   {rep[key].shape}     (sum: {torch.sum(rep[key])})")
    print("\n")

class TimeEmbedding(nn.Module):
    def __init__(self, embedding_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(1, embedding_dim),
            nn.SiLU(),
            nn.Linear(embedding_dim, embedding_dim),
        )

    def forward(self, t):
        return self.net(t.unsqueeze(-1).float())



def heterogenous_layer_wrapper(
    layer,
    x,
    edge_index,
):
    edge_index = {key: val for key, val in edge_index.items() if val.numel() != 0}
    outputs = layer(x, edge_index)

    for node_type in x.keys():
        if node_type in outputs:
            mask = outputs[node_type].abs().sum(dim=1) == 0
            outputs[node_type][mask] = x[node_type][mask]
        else:
            outputs[node_type] = x[node_type]

    return outputs


class SimpleHeteroGenerator(pl.LightningModule):
    # def __init__(
    #     self,
    #     input_dims,
    #     condition_dims,
    #     output_dims,
    #     hidden_dim=128,
    #     time_embedding_dim=16,
    #     use_time=True,
    #     use_condition=True,
    #     n_layers=2,
    # ):
        
    def __init__(
        self,
        mother_targets_dims,
        intermediate_targets_dims,
        track_targets_dims,
        mother_conditions_dims,
        intermediate_conditions_dims,
        track_conditions_dims,
        hidden_channels,
        mother_latent_dims,
        track_latent_dims,
        intermediate_latent_dims,
        conditonless=False,
        diffuser=False,
    ):
                
        super().__init__()
        use_time = True
        use_condition = True
        n_layers = 2
        self.use_time = use_time
        self.use_condition = use_condition
        self.n_layers = n_layers
        hidden_dim = 128

        self.L_mother = mother_latent_dims
        self.L_intermediate = intermediate_latent_dims
        self.L_track = track_latent_dims

        input_dims = {}
        input_dims["track"] = track_targets_dims
        input_dims["intermediate"] = intermediate_targets_dims
        input_dims["mother"] = mother_targets_dims
        condition_dims = {}
        condition_dims["track"] = track_conditions_dims + track_latent_dims
        condition_dims["intermediate"] = intermediate_conditions_dims + intermediate_latent_dims
        condition_dims["mother"] = mother_conditions_dims + mother_latent_dims
        output_dims = {}
        output_dims["track"] = track_targets_dims
        output_dims["intermediate"] = intermediate_targets_dims
        output_dims["mother"] = mother_targets_dims
        time_embedding_dim = 5

        node_types = input_dims.keys()
        self.embedding_layers = nn.ModuleDict()
        self.condition_layers = nn.ModuleDict()
        self.output_layers = nn.ModuleDict()

        combined_input_dim = {}
        for ntype in node_types:
            dim = input_dims[ntype]
            if use_time:
                dim += time_embedding_dim
            if use_condition:
                dim += condition_dims[ntype]
            combined_input_dim[ntype] = dim

            self.embedding_layers[ntype] = nn.Linear(dim, hidden_dim)
            self.output_layers[ntype] = nn.Linear(hidden_dim, output_dims[ntype])

        self.time_embed = TimeEmbedding(time_embedding_dim) if use_time else None

        # Build GNN layers (shared for forward/backward)
        self.gnn_layers_forward = nn.ModuleList()
        self.gnn_layers_backward = nn.ModuleList()
        for _ in range(n_layers):
            self.gnn_layers_forward.append(
                HeteroConv({
                    ("track", "up", "intermediate"): GATConv(hidden_dim, hidden_dim, add_self_loops=False),
                    ("intermediate", "up", "mother"): GATConv(hidden_dim, hidden_dim, add_self_loops=False),
                    ("track", "up", "mother"): GATConv(hidden_dim, hidden_dim, add_self_loops=False),
                    ("intermediate", "up", "intermediate"): GATConv(hidden_dim, hidden_dim, add_self_loops=False),
                }, aggr="sum")
            )
            self.gnn_layers_backward.append(
                HeteroConv({
                    ("mother", "down", "intermediate"): GATConv(hidden_dim, hidden_dim, add_self_loops=False),
                    ("intermediate", "down", "track"): GATConv(hidden_dim, hidden_dim, add_self_loops=False),
                    ("mother", "down", "track"): GATConv(hidden_dim, hidden_dim, add_self_loops=False),
                    ("intermediate", "down", "intermediate"): GATConv(hidden_dim, hidden_dim, add_self_loops=False),
                }, aggr="sum")
            )

    # def forward(
    #     self,
    #     x_dict,
    #     condition_dict,
    #     edge_index_dicts_forward,
    #     edge_index_dicts_backward,
    #     timesteps=None,
    # ):
        
    def forward(
        self,
        batch,
        timesteps=None,
        add_condition_nodes=False,
        offline_query_mode=False,
    ) -> Tuple[Tensor, Tensor, Tensor]:
        
        conditions = {
            "track": batch["track_conditions"].x[:, : -self.L_track],
            "mother": batch["mother_conditions"].x[:, : -self.L_mother],
        }
        extra_latent = {
            "track": batch["track_conditions"].x[:, -self.L_track :],
            "mother": batch["mother_conditions"].x[:, -self.L_mother :],
        }
        current_x = {
            "track": batch["track"].x,
            "mother": batch["mother"].x,
        }
        intermediate_present = False
        try:
            conditions["intermediate"] = batch["intermediate_conditions"].x[
                :, : -self.L_intermediate
            ]
            extra_latent["intermediate"] = batch["intermediate_conditions"].x[
                :, -self.L_intermediate :
            ]
            current_x["intermediate"] = batch["intermediate"].x
            intermediate_present = True
        except:
            pass

        edge_index_dict_self_loop = {
            ("track", "self", "track"): batch["track", "self", "track"]["edge_index"],
            ("mother", "self", "mother"): batch["mother", "self", "mother"][
                "edge_index"
            ],
        }
        if intermediate_present:
            edge_index_dict_self_loop[("intermediate", "self", "intermediate")] = batch[
                "intermediate", "self", "intermediate"
            ]["edge_index"]

        edge_index_dicts_forward = []
        edge_types_forward = [
            ("track", "up", "intermediate"),
            ("intermediate", "up", "intermediate"),
            ("intermediate", "up", "mother"),
            ("track", "up", "mother"),
        ]
        for sequential_message_idx in range(
            len(batch["track", "up", "intermediate"]["edge_index"])
        ):
            edge_index_dict = {}
            for edge_type in edge_types_forward:
                try:
                    if "edge_index" in batch[edge_type]:
                        if (
                            batch[edge_type]["edge_index"][sequential_message_idx].dim()
                            > 1
                        ):
                            edge_index_dict[edge_type] = batch[edge_type]["edge_index"][
                                sequential_message_idx
                            ]
                except Exception:
                    pass
            edge_index_dicts_forward.append(edge_index_dict)

        edge_index_dicts_backward = []
        edge_types_backward = [
            ("intermediate", "down", "track"),
            ("intermediate", "down", "intermediate"),
            ("mother", "down", "intermediate"),
            ("mother", "down", "track"),
        ]
        for sequential_message_idx in range(
            len(batch["intermediate", "down", "track"]["edge_index"])
        ):
            edge_index_dict = {}
            for edge_type in edge_types_backward:
                try:
                    if "edge_index" in batch[edge_type]:
                        if (
                            batch[edge_type]["edge_index"][sequential_message_idx].dim()
                            > 1
                        ):
                            edge_index_dict[edge_type] = batch[edge_type]["edge_index"][
                                sequential_message_idx
                            ]
                except Exception:
                    pass
            edge_index_dicts_backward.append(edge_index_dict)


        # 1. Time Embedding
        if self.use_time:
            t_embed = self.time_embed(timesteps)
        else:
            t_embed = None

        # print_heterogenous_representation(current_x)

        # 2. Initial Embedding
        h = {}
        for ntype, x in current_x.items():
            features = [x]
            if self.use_condition:
                features.append(conditions[ntype])
                features.append(extra_latent[ntype])
            if self.use_time:
                # Repeat t_embed if needed
                if x.shape[0] != t_embed.shape[0]:
                    t_repeat = t_embed.repeat_interleave(x.shape[0] // t_embed.shape[0], dim=0)
                else:
                    t_repeat = t_embed
                features.append(t_repeat)
            concat = torch.cat(features, dim=1)

            h[ntype] = F.relu(self.embedding_layers[ntype](concat))

        # print_heterogenous_representation(h)

        # 3. Sequential GNN Message Passing
        for layer_idx in range(self.n_layers):
            # Backward pass
            for edge_index_dict in edge_index_dicts_backward:
                h = heterogenous_layer_wrapper(self.gnn_layers_backward[layer_idx], h, edge_index_dict)

            # Forward pass
            for edge_index_dict in edge_index_dicts_forward:
                h = heterogenous_layer_wrapper(self.gnn_layers_forward[layer_idx], h, edge_index_dict)

            # Optional: Activation
            for ntype in h:
                h[ntype] = F.relu(h[ntype])

        # 4. Output layer
        out = {}
        for ntype in h:
            out[ntype] = self.output_layers[ntype](h[ntype])
        return [out]
    
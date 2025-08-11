import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import global_mean_pool, global_add_pool, global_max_pool
from torch_geometric.nn import GATConv, HeteroConv
from torch import Tensor
from typing import Tuple, Optional, List, Dict
import pytorch_lightning as pl

from collections import defaultdict
from rich import print as rprint
from torch_geometric.utils import to_dense_batch

import warnings


from torch_geometric.nn.conv import MessagePassing
from torch_geometric.nn.module_dict import ModuleDict
from torch_geometric.typing import EdgeType, NodeType
from torch_geometric.utils.hetero import check_add_self_loops
from diffusers import DDIMScheduler, DDPMScheduler
import itertools


class myHeteroConv(torch.nn.Module):
    def __init__(
        self,
        convs: Dict[EdgeType, MessagePassing],
        aggr: Optional[str] = "sum",
    ):
        super().__init__()

        for edge_type, module in convs.items():
            check_add_self_loops(module, [edge_type])

        src_node_types = {key[0] for key in convs.keys()}
        dst_node_types = {key[-1] for key in convs.keys()}
        if len(src_node_types - dst_node_types) > 0:
            warnings.warn(
                f"There exist node types ({src_node_types - dst_node_types}) "
                f"whose representations do not get updated during message "
                f"passing as they do not occur as destination type in any "
                f"edge type. This may lead to unexpected behavior."
            )

        self.convs = ModuleDict(convs)
        self.aggr = aggr

    def reset_parameters(self):
        r"""Resets all learnable parameters of the module."""
        for conv in self.convs.values():
            conv.reset_parameters()

    def forward(
        self,
        *args_dict,
        **kwargs_dict,
    ) -> Dict[NodeType, Tensor]:
        out_dict: Dict[str, List[Tensor]] = {}
        if not isinstance(self.aggr, list):
            self.aggr = [self.aggr]

        for edge_type, conv in self.convs.items():
            src, rel, dst = edge_type

            has_edge_level_arg = False

            args = []
            for value_dict in args_dict:
                if edge_type in value_dict:
                    has_edge_level_arg = True
                    args.append(value_dict[edge_type])
                elif src == dst and src in value_dict:
                    args.append(value_dict[src])
                elif src in value_dict or dst in value_dict:
                    args.append(
                        (
                            value_dict.get(src, None),
                            value_dict.get(dst, None),
                        )
                    )

            kwargs = {}
            for arg, value_dict in kwargs_dict.items():
                if not arg.endswith("_dict"):
                    raise ValueError(
                        f"Keyword arguments in '{self.__class__.__name__}' "
                        f"need to end with '_dict' (got '{arg}')"
                    )
                arg = arg[:-5]  # `{*}_dict`
                if edge_type in value_dict:
                    has_edge_level_arg = True
                    kwargs[arg] = value_dict[edge_type]
                elif src == dst and src in value_dict:
                    kwargs[arg] = value_dict[src]
                elif src in value_dict or dst in value_dict:
                    kwargs[arg] = (
                        value_dict.get(src, None),
                        value_dict.get(dst, None),
                    )

            if not has_edge_level_arg:
                continue

            in_values = args_dict[0]
            edge_indicies = args[1]
            out_indices = edge_indicies[1]

            out = conv(*args, **kwargs)

            out_indices = torch.reshape(out_indices, (out.shape[0], out.shape[1]))
            # out_indices = edge_indicies[1]

            if dst not in out_dict:
                out_dict[dst] = [[out, out_indices]]
            else:
                out_dict[dst].append([out, out_indices])

        out_values = {}
        for dst in out_dict:
            for idx, item in enumerate(out_dict[dst]):
                item[0] = torch.reshape(item[0], (-1, item[0].shape[-1]))
                item[1] = torch.flatten(item[1])
                if idx == 0:
                    concat_item = [item[0], item[1]]
                else:
                    concat_item[0] = torch.cat((concat_item[0], item[0]), dim=0)
                    concat_item[1] = torch.cat((concat_item[1], item[1]), dim=0)

            if rel == "down" or self.aggr == ["sum"]:  # no aggr required
                zeros = torch.zeros(in_values[dst].shape, device=out.device)
                out = zeros.scatter_add(
                    0,
                    concat_item[1].unsqueeze(-1).expand_as(concat_item[0]),
                    concat_item[0],
                )
                out_values[dst] = out
            else:
                for idx, aggr in enumerate(self.aggr):
                    if aggr == "sum":
                        zeros = torch.zeros(in_values[dst].shape, device=out.device)
                        aggr_out = zeros.scatter_add(
                            0,
                            concat_item[1].unsqueeze(-1).expand_as(concat_item[0]),
                            concat_item[0],
                        )
                    elif aggr == "mean":
                        zeros = torch.zeros(in_values[dst].shape, device=out.device)
                        sum_out = zeros.scatter_add(
                            0,
                            concat_item[1].unsqueeze(-1).expand_as(concat_item[0]),
                            concat_item[0],
                        )
                        ones = torch.ones_like(concat_item[0])
                        count = zeros.scatter_add(
                            0,
                            concat_item[1].unsqueeze(-1).expand_as(concat_item[0]),
                            ones,
                        )
                        aggr_out = sum_out / count.clamp(min=1)  # Avoid divide-by-zero
                    elif aggr == "max":
                        max_out = torch.zeros_like(zeros)
                        aggr_out = max_out.scatter_reduce(
                            0,
                            concat_item[1].unsqueeze(-1).expand_as(concat_item[0]),
                            concat_item[0],
                            reduce="amax",
                            include_self=True,
                        )

                    if idx == 0:
                        total_aggre = aggr_out
                    else:
                        total_aggre = torch.cat((total_aggre, aggr_out), dim=1)

                aggr_attention = kwargs_dict["aggr_attention_dict"]
                mask = total_aggre.abs().sum(dim=1) == 0
                atten = torch.sigmoid(aggr_attention[f"{dst}_attention"](total_aggre))
                total_aggre = total_aggre * atten  # Avoid `rep[key] *= atten`
                total_aggre = aggr_attention[f"{dst}_aggr"](
                    total_aggre
                )  # Pass through aggregation layer
                total_aggre[mask] = 0

                out_values[dst] = total_aggre

        return out_values

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(num_relations={len(self.convs)})"


class NoAggGAT(MessagePassing):
    def __init__(self, in_channels, out_channels, spec_norm=False):
        super().__init__(aggr=None)  # Keep messages separate
        self.lin = nn.Linear(in_channels, out_channels)
        if spec_norm:
            self.lin = torch.nn.utils.spectral_norm(self.lin)

    def forward(self, x, edge_index):
        # print(x)
        # print(edge_index)
        out = self.propagate(edge_index, x=x)
        # Get unique nodes and counts
        unique_nodes, counts = edge_index[1].unique(return_counts=True)
        max_count = counts.max().item()
        out = out.view(unique_nodes.shape[0], max_count, out.shape[1])

        return out

    # def forward(self, x, edge_index):
    #     out = self.propagate(edge_index, x=x, size=None)

    #     # `index` is the destination node for each message
    #     dst = edge_index[1]
    #     # Group messages by destination node (pad to max)
    #     out, mask = to_dense_batch(out, dst)  # shape: [num_nodes, max_msgs_per_node, out_dim]

    #     return out

    def message(self, x_j):
        return self.lin(x_j)  # Transform node features per edge

    def aggregate(self, inputs, index):
        return inputs  # No aggregation, messages remain separate


def heterogenous_layer_wrapper_w_cat_and_self_loop(
    layer,
    aggr_attention,
    selfloop_layer,
    x,
    edge_index,
    conditions=None,
    infeatures=None,
    aggrs=["sum", "mean", "max"],
):
    edge_index = {key: val for key, val in edge_index.items() if val.numel() != 0}
    # print_heterogenous_representation(x)
    # print('INTO LAYER')
    outputs = layer(x, edge_index, aggr_attention_dict=aggr_attention)

    for node_type in outputs.keys():
        outputs[node_type] = F.leaky_relu(outputs[node_type])

    for node_type in x.keys():
        if (
            node_type in outputs
        ):  # if only some of the nodes of a node type are used as the end point of edges (as defined by edge_index) the un-used are output as 0. - dont want this, so take previous values
            mask = outputs[node_type].abs().sum(dim=1) == 0  # Find zero rows
            concatted_shape = torch.cat([outputs[node_type], x[node_type]], dim=1)
            outputs[node_type] = F.leaky_relu(
                selfloop_layer[node_type](concatted_shape)
            )
            outputs[node_type][mask] = x[node_type][mask]  # Restore original embeddings
        else:
            outputs[node_type] = x[node_type]  # Pass through unchanged

    return outputs


def print_heterogenous_representation(rep):
    for key in rep:
        print(f"{key}:   {rep[key].shape}     (sum: {torch.sum(rep[key])})")
    print("\n")


class TimeEmbedding(nn.Module):
    def __init__(self, embedding_dim):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.linear1 = nn.Linear(1, embedding_dim)
        self.act = nn.SiLU()
        self.linear2 = nn.Linear(embedding_dim, embedding_dim)

    def forward(self, t):
        # t is shape [batch_size], scale to float and unsqueeze
        t = t.unsqueeze(-1).float()
        emb = self.linear1(t)
        emb = self.act(emb)
        emb = self.linear2(emb)
        return emb


class HeteroGenerator(pl.LightningModule):  # 2
    def __init__(
        self,
        track_targets_dims,
        track_conditions_dims,
        hidden_channels,
        track_latent_dims,
        edge_conditions_dims,
        conditonless=False,
    ):
        super(HeteroGenerator, self).__init__()

        self.conditonless = conditonless

        self.time_embedding_dim = 5
        self.time_embed = TimeEmbedding(self.time_embedding_dim)
        self.use_layernorm = True

        # Conditions
        C_track = track_conditions_dims
        if self.conditonless:
            C_track = 0

        # Targets
        T_track = track_targets_dims

        self.add_extra_noise = True
        # Latents
        if self.add_extra_noise:
            # L_track = 3
            # self.L_track = 25
            self.L_track = 3
            # self.L_track = 5
        else:
            self.L_track = 0

        ### ### ### ### ###

        self.aggrs = ["mean", "sum", "max"]

        self.particle_types = ["11", "13", "211", "321", "2212"]
        self.edge_types = list(itertools.product(self.particle_types, repeat=2))

        embedding_dim = 64
        layer = {}
        for particle_type in self.particle_types:
            layer[particle_type] = nn.Linear(T_track + self.L_track, embedding_dim)
            # layer[particle_type] = nn.Sequential(
            #                 nn.Linear(T_track + C_track + L_track, 2 * embedding_dim),
            #                 nn.ReLU(),
            #                 nn.Linear(2 * embedding_dim, embedding_dim)
            #             )
        self.embedding_layer = nn.ModuleDict(layer)
        layer = {}
        for particle_type in self.particle_types:
            layer[particle_type] = nn.Linear(track_conditions_dims, embedding_dim)
            # layer[particle_type] = nn.Sequential(
            #                 nn.Linear(track_conditions_dims, 2 * embedding_dim),
            #                 nn.ReLU(),
            #                 nn.Linear(2 * embedding_dim, embedding_dim)
            #             )
        self.condition_embedding_layer = nn.ModuleDict(layer)
        layer = {}
        for particle_type in self.particle_types:
            layer[particle_type] = nn.Linear(embedding_dim * 2, embedding_dim * 2)
        self.embedding_pooling_attention_layer = nn.ModuleDict(layer)
        layer = {}
        for particle_type in self.particle_types:
            layer[particle_type] = nn.Linear(embedding_dim * 2, embedding_dim)
        self.embedding_pooling_collapsing_layer = nn.ModuleDict(layer)

        # self.communication_dims = 100
        self.communication_dims = hidden_channels

        self.selfloop_layers = nn.ModuleList()
        self.communication_layers = nn.ModuleList()

        self.communication_atten_layers = nn.ModuleList()
        self.communication_aggr_layers = nn.ModuleList()
        self.communication_compressor_layers = nn.ModuleList()
        self.x_compressor_layers = nn.ModuleList()

        self.N_layers = 3
        # self.N_layers = 4
        self.hidden_channels = hidden_channels

        for N_layer in range(self.N_layers):
            layer = {}
            for particle_type in self.particle_types:
                if N_layer == 0:
                    layer[particle_type] = nn.Linear(
                        embedding_dim + self.time_embedding_dim, hidden_channels
                    )
                else:
                    layer[particle_type] = nn.Linear(
                        hidden_channels + self.time_embedding_dim, hidden_channels
                    )
            layer = nn.ModuleDict(layer)
            self.selfloop_layers.append(layer)

            layer_dict = {}
            for edge_type in self.edge_types:
                layer_dict[edge_type[0], "to", edge_type[1]] = GATConv(
                    self.communication_dims,
                    self.communication_dims,
                    add_self_loops=False,
                    edge_dim=edge_conditions_dims,
                )
            layer = HeteroConv(
                layer_dict,
                # aggr="mean", # was max,
                aggr="max",  # was max,
            )
            self.communication_layers.append(layer)

            layer = {}
            for particle_type in self.particle_types:
                layer[particle_type] = nn.Linear(
                    hidden_channels, int(hidden_channels / 2)
                )
            layer = nn.ModuleDict(layer)
            self.communication_compressor_layers.append(layer)
            layer = {}
            for particle_type in self.particle_types:
                layer[particle_type] = nn.Linear(
                    hidden_channels, int(hidden_channels / 2)
                )
            layer = nn.ModuleDict(layer)
            self.x_compressor_layers.append(layer)

            layer = {}
            for particle_type in self.particle_types:
                layer[particle_type] = nn.Linear(hidden_channels, hidden_channels)
            layer = nn.ModuleDict(layer)
            self.communication_atten_layers.append(layer)

            # layer = {}
            # for particle_type in self.particle_types:
            #     layer[particle_type] = nn.Linear(hidden_channels * 2, hidden_channels)
            # layer = nn.ModuleDict(layer)
            # self.communication_aggr_layers.append(layer)

        layer = {}
        for particle_type in self.particle_types:
            layer[particle_type] = nn.Linear(
                hidden_channels + self.time_embedding_dim, hidden_channels
            )
        layer = nn.ModuleDict(layer)
        self.selfloop_layers.append(layer)

        layer = {}
        for particle_type in self.particle_types:
            layer[particle_type] = nn.Linear(
                hidden_channels + self.time_embedding_dim, T_track
            )
        layer = nn.ModuleDict(layer)
        self.selfloop_layers.append(layer)

    def forward(
        self,
        batch,
        timesteps=None,
        add_condition_nodes=False,
        offline_query_mode=False,
    ) -> Tuple[Tensor, Tensor, Tensor]:
        timestep_embedding = self.time_embed(timesteps)

        conditions = {}
        extra_latent = {}
        current_x = {}
        for particle_type in self.particle_types:
            if self.add_extra_noise:
                conditions[particle_type] = (
                    batch[f"{particle_type}_conditions"]
                    .x[:, : -self.L_track]
                    .to(torch.float32)
                )
                extra_latent[particle_type] = (
                    batch[f"{particle_type}_conditions"]
                    .x[:, -self.L_track :]
                    .to(torch.float32)
                )
            else:
                conditions[particle_type] = batch[f"{particle_type}_conditions"].x

            current_x[particle_type] = batch[f"{particle_type}"].x.to(torch.float32)

        edge_index_dict = {}
        edge_attr_dict = {}
        for edge_type in self.edge_types:
            edge_index_dict[edge_type[0], "to", edge_type[1]] = batch[
                edge_type[0], "to", edge_type[1]
            ].edge_index  # ["edge_index"]
            edge_attr_dict[edge_type[0], "to", edge_type[1]] = batch[
                edge_type[0], "to", edge_type[1]
            ].edge_attr  # ["edge_attr"]

        if self.add_extra_noise:
            for node_type in current_x:
                current_x[node_type] = torch.cat(
                    [current_x[node_type], extra_latent[node_type]], dim=1
                )

        x = current_x.copy()

        # if not self.conditonless: # remove conditions, need to keep the extra latent dims that were gracelessly concated to the end of the conditions tensors
        #     for node_type in x:
        #         x[node_type] = torch.cat(
        #             (x[node_type], conditions[node_type]), dim=1
        #         )

        # print(batch)
        for node_type in x:
            # print(node_type, x[node_type].shape)
            if x[node_type].shape[0] > 0:
                x[node_type] = self.embedding_layer[node_type](x[node_type])

        # print('add_condition_nodes', add_condition_nodes)
        # print(x['321'].shape)

        if add_condition_nodes:
            for node_type in x:
                if conditions[node_type].shape[0] > 0:
                    conditions[node_type] = self.condition_embedding_layer[node_type](
                        conditions[node_type]
                    )
                    # print(conditions['321'].shape)
                    x[node_type] = torch.cat(
                        (x[node_type], conditions[node_type]), dim=1
                    )
                    atten = torch.sigmoid(
                        self.embedding_pooling_attention_layer[node_type](x[node_type])
                    )
                    x[node_type] = atten * x[node_type]
                    x[node_type] = self.embedding_pooling_collapsing_layer[node_type](
                        x[node_type]
                    )

        # print(x['321'].shape)

        cat_timesteps = {}
        for node_type in x:
            node_feats = x[node_type]  # [N_nodes, F]
            if conditions[node_type].shape[0] > 0:
                batch_indices = batch[node_type].batch  # [N_nodes]
                node_timesteps = timestep_embedding[
                    batch_indices
                ]  # [N_nodes, D] - select per-node timestep emb
                # Concatenate timestep embedding
                x[node_type] = torch.cat([node_feats, node_timesteps], dim=-1)
                cat_timesteps[node_type] = node_timesteps
            else:
                x[node_type] = torch.cat(
                    [
                        node_feats,
                        torch.empty((0, self.time_embedding_dim)).to(node_feats.device),
                    ],
                    dim=-1,
                )
                cat_timesteps[node_type] = torch.empty((0, self.time_embedding_dim)).to(
                    node_feats.device
                )

        # print(x['321'].shape)
        # print(cat_timesteps['321'].shape)

        x_comms = {}

        for N_layer in range(self.N_layers):
            if N_layer != 0:
                for node_type in x:
                    # print('\n')
                    # print(node_type)
                    # print(x[node_type].shape)
                    # print(conditions[node_type].shape)
                    # print(cat_timesteps[node_type].shape)
                    x[node_type] = torch.cat(
                        [x[node_type], cat_timesteps[node_type]], dim=-1
                    )

            # print(N_layer, x['321'].shape, conditions['321'].shape, cat_timesteps['321'].shape)
            # x_in = {}
            for track_type in x:
                if x[track_type].shape[0] > 0:
                    x[track_type] = F.leaky_relu(
                        self.selfloop_layers[N_layer][track_type](x[track_type])
                    )
                else:
                    x[track_type] = torch.empty((0, self.hidden_channels)).to(
                        x[track_type].device
                    )
            #         x_in[track_type] = x[track_type]
            # x = x_in
            # print_heterogenous_representation(x)

            x_comms = self.communication_layers[N_layer](
                x, edge_index_dict, edge_attr_dict
            )
            for track_type in x_comms:
                if x_comms[track_type].shape[0] > 0:
                    x_comms[track_type] = F.leaky_relu(x_comms[track_type])
                    x[track_type] = torch.cat(
                        [
                            self.x_compressor_layers[N_layer][track_type](
                                x[track_type]
                            ),
                            self.communication_compressor_layers[N_layer][track_type](
                                x_comms[track_type]
                            ),
                        ],
                        dim=-1,
                    )
                    atten = self.communication_atten_layers[N_layer][track_type](
                        x[track_type]
                    )
                    x[track_type] = x[track_type] + torch.sigmoid(atten) * x[track_type]

        for node_type in x:
            x[node_type] = torch.cat([x[node_type], cat_timesteps[node_type]], dim=-1)

        for track_type in x:
            if x[track_type].shape[0] > 0:
                x[track_type] = self.selfloop_layers[-1][track_type](x[track_type])

        return [x]


# class HeteroGenerator(pl.LightningModule):
#     def __init__(
#         self,
#         track_targets_dims,
#         track_conditions_dims,
#         hidden_channels,
#         track_latent_dims,
#         edge_conditions_dims,
#         conditonless=False,

#     ):
#         super(HeteroGenerator, self).__init__()

#         self.conditonless = conditonless

#         self.time_embedding_dim = 5
#         self.time_embed = TimeEmbedding(self.time_embedding_dim)
#         self.use_layernorm = True

#         # Conditions
#         C_track = track_conditions_dims
#         if self.conditonless:
#             C_track = 0

#         # Targets
#         T_track = track_targets_dims

#         self.add_extra_noise = True
#         # Latents
#         if self.add_extra_noise:
#             L_track = 3
#         else: L_track = 0

#         ### ### ### ### ###

#         self.aggrs = ['mean', 'sum','max']

#         self.particle_types = ["11", "13", "211", "321", "2212"]
#         self.edge_types = list(itertools.product(self.particle_types, repeat=2))

#         embedding_dim = 64
#         layer = {}
#         for particle_type in self.particle_types:
#             layer[particle_type] = nn.Linear(T_track + C_track + L_track, embedding_dim)
#             # layer[particle_type] = nn.Sequential(
#             #                 nn.Linear(T_track + C_track + L_track, 2 * embedding_dim),
#             #                 nn.ReLU(),
#             #                 nn.Linear(2 * embedding_dim, embedding_dim)
#             #             )
#         self.embedding_layer = nn.ModuleDict(layer)
#         layer = {}
#         for particle_type in self.particle_types:
#             layer[particle_type] = nn.Linear(track_conditions_dims, embedding_dim)
#             # layer[particle_type] = nn.Sequential(
#             #                 nn.Linear(track_conditions_dims, 2 * embedding_dim),
#             #                 nn.ReLU(),
#             #                 nn.Linear(2 * embedding_dim, embedding_dim)
#             #             )
#         self.condition_embedding_layer = nn.ModuleDict(layer)
#         layer = {}
#         for particle_type in self.particle_types:
#             layer[particle_type] = nn.Linear(embedding_dim*2, embedding_dim*2)
#         self.embedding_pooling_attention_layer = nn.ModuleDict(layer)
#         layer = {}
#         for particle_type in self.particle_types:
#             layer[particle_type] = nn.Linear(embedding_dim*2, embedding_dim)
#         self.embedding_pooling_collapsing_layer = nn.ModuleDict(layer)

#         # self.communication_dims = 100
#         self.communication_dims = hidden_channels

#         self.selfloop_layers = nn.ModuleList()
#         self.communication_layers = nn.ModuleList()

#         self.communication_atten_layers = nn.ModuleList()
#         self.communication_aggr_layers = nn.ModuleList()

#         self.N_layers = 3
#         # self.N_layers = 4

#         for N_layer in range(self.N_layers):

#             layer = {}
#             for particle_type in self.particle_types:
#                 if N_layer == 0:
#                     layer[particle_type] = nn.Linear(embedding_dim + self.time_embedding_dim, hidden_channels)
#                 else:
#                     layer[particle_type] = nn.Linear(hidden_channels, hidden_channels)
#             layer = nn.ModuleDict(layer)
#             self.selfloop_layers.append(layer)

#             layer_dict = {}
#             for edge_type in self.edge_types:
#                 layer_dict[edge_type[0], "to", edge_type[1]] = GATConv(
#                     self.communication_dims,
#                     self.communication_dims,
#                     add_self_loops=False,
#                     edge_dim=edge_conditions_dims,
#                 )
#             layer = HeteroConv(
#                 layer_dict,
#                 aggr="mean", # was max, i
#             )
#             self.communication_layers.append(layer)

#             layer = {}
#             for particle_type in self.particle_types:
#                 layer[particle_type] = nn.Linear(hidden_channels * 2, hidden_channels * 2)
#             layer = nn.ModuleDict(layer)
#             self.communication_atten_layers.append(layer)

#             layer = {}
#             for particle_type in self.particle_types:
#                 layer[particle_type] = nn.Linear(hidden_channels * 2, hidden_channels)
#             layer = nn.ModuleDict(layer)
#             self.communication_aggr_layers.append(layer)


#         layer = {}
#         for particle_type in self.particle_types:
#             layer[particle_type] = nn.Linear(hidden_channels, hidden_channels)
#         layer = nn.ModuleDict(layer)
#         self.selfloop_layers.append(layer)

#         layer = {}
#         for particle_type in self.particle_types:
#             layer[particle_type] = nn.Linear(hidden_channels, T_track)
#         layer = nn.ModuleDict(layer)
#         self.selfloop_layers.append(layer)


#     def forward(
#         self,
#         batch,
#         timesteps=None,
#         add_condition_nodes=False,
#         offline_query_mode=False,
#     ) -> Tuple[Tensor, Tensor, Tensor]:

#         timestep_embedding = self.time_embed(timesteps)

#         conditions = {}
#         extra_latent = {}
#         current_x = {}
#         for particle_type in self.particle_types:
#             # if batch[f"{particle_type}"].x.shape[0] > 0:

#             if self.add_extra_noise:
#                 conditions[particle_type] = batch[f"{particle_type}_conditions"].x[:,:-3].to(torch.float32)
#                 extra_latent[particle_type] = batch[f"{particle_type}_conditions"].x[:,-3:].to(torch.float32)
#             else:
#                 conditions[particle_type] = batch[f"{particle_type}_conditions"].x

#             current_x[particle_type] = batch[f"{particle_type}"].x.to(torch.float32)


#         edge_index_dict = {}
#         edge_attr_dict = {}
#         for edge_type in self.edge_types:
#             edge_index_dict[edge_type[0], "to", edge_type[1]] = batch[
#                 edge_type[0], "to", edge_type[1]
#             ].edge_index  # ["edge_index"]
#             edge_attr_dict[edge_type[0], "to", edge_type[1]] = batch[
#                 edge_type[0], "to", edge_type[1]
#             ].edge_attr  # ["edge_attr"]

#         if self.add_extra_noise:
#             for node_type in current_x:
#                 current_x[node_type] = torch.cat([current_x[node_type], extra_latent[node_type]], dim=1)

#         x = current_x.copy()

#         if not self.conditonless: # remove conditions, need to keep the extra latent dims that were gracelessly concated to the end of the conditions tensors
#             for node_type in x:
#                 x[node_type] = torch.cat(
#                     (x[node_type], conditions[node_type]), dim=1
#                 )

#         for node_type in x:
#             x[node_type] = self.embedding_layer[node_type](x[node_type])

#         if add_condition_nodes:
#             for node_type in x:
#                 if conditions[node_type].shape[0] > 0:
#                     conditions[node_type] = self.condition_embedding_layer[node_type](conditions[node_type])
#                     x[node_type] = torch.cat((x[node_type],conditions[node_type]), dim=1)
#                     atten = torch.sigmoid(self.embedding_pooling_attention_layer[node_type](x[node_type]))
#                     x[node_type] = atten * x[node_type]
#                     x[node_type] = self.embedding_pooling_collapsing_layer[node_type](x[node_type])


#         for node_type in x:
#             node_feats = x[node_type]                      # [N_nodes, F]
#             if conditions[node_type].shape[0] > 0:
#                 batch_indices = batch[node_type].batch              # [N_nodes]
#                 node_timesteps = timestep_embedding[batch_indices]  # [N_nodes, D] - select per-node timestep emb
#                 # Concatenate timestep embedding
#                 x[node_type] = torch.cat([node_feats, node_timesteps], dim=-1)
#             else:
#                 x[node_type] = torch.cat([node_feats, torch.empty((0,self.time_embedding_dim)).to(node_feats.device)], dim=-1)


#         x_comms = {}

#         for N_layer in range(self.N_layers):

#             # residual = {}
#             # if N_layer > 0:
#             #     for track_type in x:
#             #         residual[track_type] = x[track_type]

#             for track_type in x:
#                 x[track_type] = F.leaky_relu(
#                     self.selfloop_layers[N_layer][track_type](x[track_type])
#                 )
#                 # x_comms[track_type] = x[track_type][:, : self.communication_dims]

#             # print_heterogenous_representation(x)
#             # print_heterogenous_representation(x_comms)

#             x_comms = self.communication_layers[N_layer](x, edge_index_dict, edge_attr_dict)
#             for track_type in x_comms:
#                 x_comms[track_type] = F.leaky_relu(x_comms[track_type])
#                 x[track_type] = torch.cat([x[track_type], x_comms[track_type]], dim=-1)
#                 atten = self.communication_atten_layers[N_layer][track_type](x[track_type])
#                 x[track_type] = torch.sigmoid(atten) * x[track_type]
#                 x[track_type] = self.communication_aggr_layers[N_layer][track_type](x[track_type])
#                 x[track_type] = F.leaky_relu(x[track_type])

#             # if N_layer > 0:
#             #     for track_type in x:
#             #         x[track_type] += residual[track_type]


#         for track_type in x:
#             x[track_type] = F.leaky_relu(
#                 self.selfloop_layers[-2][track_type](x[track_type])
#             )

#         for track_type in x:
#             # x[track_type] = torch.tanh(
#             #     self.selfloop_layers[-1][track_type](x[track_type])
#             # )
#             x[track_type] = self.selfloop_layers[-1][track_type](x[track_type])


#         return [x]


import copy


class EMA:
    def __init__(self, model, decay=0.995):
        self.ema_model = copy.deepcopy(model)
        self.ema_model.eval()
        self.decay = decay
        for param in self.ema_model.parameters():
            param.requires_grad = False

    def update(self, model):
        with torch.no_grad():
            msd = model.state_dict()
            for k, ema_v in self.ema_model.state_dict().items():
                model_v = msd[k].detach()  # .to(self.device)
                ema_v.copy_(ema_v * self.decay + (1.0 - self.decay) * model_v)


class diffusion_model_smearing(nn.Module):
    def __init__(
        self,
        track_targets_dims,
        track_conditions_dims,
        hidden_channels,
        track_latent_dims,
        edge_conditions_dims,
        steps,
        silent=False,
        eGAN=False,
    ):
        super(diffusion_model_smearing, self).__init__()

        self.steps = steps

        if not silent:
            print("\n")
            print("Network params -----------------")
            print("track_targets_dims:", track_targets_dims)
            print("track_conditions_dims:", track_conditions_dims)
            print("hidden_channels:", hidden_channels)
            print("track_latent_dims:", track_latent_dims)
            print("edge_conditions_dims:", edge_conditions_dims)
            print("\n")

        self.track_latent_dims = track_latent_dims

        self.track_targets_dims = track_targets_dims

        self.diffuser = HeteroGenerator(
            track_targets_dims,
            track_conditions_dims,
            hidden_channels,
            track_latent_dims,
            edge_conditions_dims,
            conditonless=True,
        )

        self.EMA_diffuser = EMA(self.diffuser)

    def rk4_step(self, f, y, t, dt):
        k1 = f(y, t)
        k2 = f(y + dt * k1 / 2, t + dt / 2)
        k3 = f(y + dt * k2 / 2, t + dt / 2)
        k4 = f(y + dt * k3, t + dt)
        return y + (dt / 6) * (k1 + 2 * k2 + 2 * k3 + k4)

    @torch.no_grad()
    def inference_flow_matching(
        self,
        batch_size,
        batch_in,
        num_steps=100,
        add_condition_nodes=True,
        offline_query_mode=False,
    ):
        print(f"inference_flow_matching, num_steps={num_steps}")

        try:
            batch = batch_in.clone()
        except:
            batch = batch_in

        device = self.diffuser.device
        self.EMA_diffuser.ema_model.to(device)
        particle_types = ["11", "13", "211", "321", "2212"]

        # Valid particle types with data
        valid_particle_types = [
            ptype for ptype in particle_types if batch[ptype].x.shape[0] > 0
        ]

        latent = {}

        for ptype in valid_particle_types:
            n_tracks = batch[ptype].x.shape[0]
            n_conditions = batch[f"{ptype}_conditions"].x.shape[0]
            dtype = batch[f"{ptype}_conditions"].x.dtype

            # Start from Gaussian noise
            latent[ptype] = torch.randn(
                (n_tracks, self.track_latent_dims), device=device
            )
            latent[ptype][:, -2:] = latent[ptype][:, -2:] * 0.25
            # latent[ptype] = 0.25 * torch.randn((n_tracks, self.track_latent_dims), device=device)
            # latent[ptype] = 0.25 * torch.randn((n_tracks, self.track_latent_dims), device=device)
            # latent[ptype] = 0.3 * torch.randn((n_tracks, self.track_latent_dims), device=device)
            # latent[ptype] = 0.2 * torch.randn((n_tracks, self.track_latent_dims), device=device)

            # # Append 3 random noise features to condition
            if self.diffuser.add_extra_noise:
                noise = torch.rand((n_conditions, 25), device=device, dtype=dtype)
                batch[f"{ptype}_conditions"].x = torch.cat(
                    [batch[f"{ptype}_conditions"].x, noise], dim=-1
                )

        # Forward integration from t=0 to t=1
        ts = torch.linspace(0, 1, steps=num_steps + 1, device=device)
        delta_t = ts[1] - ts[0]  # Constant step size

        for i in range(num_steps):
            # # resample noise
            # for ptype in valid_particle_types:
            #     batch[f"{ptype}_conditions"].x[:,-25:] = torch.rand((n_conditions, 25), device=device, dtype=dtype)

            t = ts[i].repeat(batch_size).to(device)

            # Update batch with current latent
            for ptype in valid_particle_types:
                batch[ptype].x = latent[ptype]

            # Predict velocity
            velocity_pred = self.diffuser(
                batch=batch,
                timesteps=t,
                offline_query_mode=offline_query_mode,
                add_condition_nodes=add_condition_nodes,
            )[0]  # Output should be velocity field

            # Euler update
            for ptype in valid_particle_types:
                v = velocity_pred[ptype]
                if v.ndim == 1:
                    v = v.unsqueeze(-1)
                latent[ptype] = latent[ptype] + delta_t * v

            # # RK4 update
            # for ptype in valid_particle_types:
            #     def velocity_fn(y, t_scalar):
            #         # Prepare input batch with y as current latent
            #         batch[ptype].x = y
            #         t_batch = t_scalar.repeat(y.shape[0])

            #         with torch.no_grad():
            #             velocity_pred = self.diffuser(
            #                 batch=batch,
            #                 timesteps=t_batch,
            #                 offline_query_mode=offline_query_mode,
            #                 add_condition_nodes=add_condition_nodes,
            #             )[0]

            #         v = velocity_pred[ptype]
            #         return v if v.ndim > 1 else v.unsqueeze(-1)

            #     latent[ptype] = self.rk4_step(velocity_fn, latent[ptype], t, delta_t)

        return latent

    @torch.no_grad()
    def inference(
        self,
        batch_size,
        batch_in,
        noise_scheduler,
        add_condition_nodes=True,
        offline_query_mode=False,
        CFG=False,
        flowmatching=False,
    ):
        if flowmatching:
            return self.inference_flow_matching(
                batch_size=batch_size,
                batch_in=batch_in,
                # num_steps=100,
                # num_steps=3,
                # num_steps=6,
                # num_steps=10,
                num_steps=25,
                # num_steps=50,
                # num_steps=100,
                add_condition_nodes=add_condition_nodes,
                offline_query_mode=offline_query_mode,
            )

        try:
            batch = batch_in.clone()
        except:
            batch = batch_in

        device = self.diffuser.device
        self.EMA_diffuser.ema_model.to(self.diffuser.device)

        particle_types = ["11", "13", "211", "321", "2212"]
        latent = {}

        # Keep only types with non-zero tracks
        valid_particle_types = [
            ptype for ptype in particle_types if batch[ptype].x.shape[0] > 0
        ]

        for ptype in valid_particle_types:
            n_tracks = batch[ptype].x.shape[0]
            n_conditions = batch[f"{ptype}_conditions"].x.shape[0]
            dtype = batch[f"{ptype}_conditions"].x.dtype

            # Sample latent
            latent[ptype] = torch.randn(
                (n_tracks, self.track_latent_dims), device=device
            )

            # Append 3 random noise features to condition
            noise = torch.rand((n_conditions, 3), device=device, dtype=dtype)
            batch[f"{ptype}_conditions"].x = torch.cat(
                [batch[f"{ptype}_conditions"].x, noise], dim=-1
            )

        # Optionally update `particle_types` to just valid ones
        particle_types = valid_particle_types

        CFG = False
        # CFG = True
        # scale = 1.25  # CFG guidance weight
        scale = 0.75  # CFG guidance weight

        for t in reversed(range(noise_scheduler.config.num_train_timesteps)):
            timesteps = torch.full((batch_size,), t, device=device, dtype=torch.long)

            for particle_type in particle_types:
                batch[particle_type].x = latent[particle_type]

            if CFG:
                # --- 1. Predict noise without condition (unconditional) ---
                uncond_noise_pred = self.diffuser(
                    # uncond_noise_pred = self.EMA_diffuser.ema_model(
                    batch=batch,
                    timesteps=timesteps,
                    offline_query_mode=offline_query_mode,
                    add_condition_nodes=False,  # <-- no conditioning
                )[0]

                # --- 2. Predict noise with condition (conditional) ---
                cond_noise_pred = self.diffuser(
                    # cond_noise_pred = self.EMA_diffuser.ema_model(
                    batch=batch,
                    timesteps=timesteps,
                    offline_query_mode=offline_query_mode,
                    add_condition_nodes=True,  # <-- with conditioning
                )[0]

                # --- 3. Classifier-Free Guidance Combination ---
                guided_noise = {}
                for node_type in latent:
                    cond_out = cond_noise_pred[node_type]
                    uncond_out = uncond_noise_pred[node_type]

                    if cond_out.ndim == 1:
                        cond_out = cond_out.unsqueeze(-1)
                        uncond_out = uncond_out.unsqueeze(-1)

                    guided_noise[node_type] = uncond_out + scale * (
                        cond_out - uncond_out
                    )

                # --- 4. Denoising step ---
                for node_type in latent:
                    model_output = guided_noise[node_type]
                    latent[node_type] = noise_scheduler.step(
                        model_output=model_output, timestep=t, sample=latent[node_type]
                    ).prev_sample

            else:
                # Predict noise at current timestep
                noise_pred = self.diffuser(
                    # noise_pred = self.EMA_diffuser.ema_model(
                    batch=batch,
                    timesteps=timesteps,
                    offline_query_mode=offline_query_mode,
                    add_condition_nodes=add_condition_nodes,
                )[0]

                # Denoise each component
                for node_type in latent:
                    model_output = noise_pred[node_type]

                    # Ensure shape matches expected sample shape
                    if model_output.ndim == 1:
                        model_output = model_output.unsqueeze(
                            -1
                        )  # Or reshape accordingly

                    latent[node_type] = noise_scheduler.step(
                        model_output=model_output, timestep=t, sample=latent[node_type]
                    ).prev_sample

        return latent

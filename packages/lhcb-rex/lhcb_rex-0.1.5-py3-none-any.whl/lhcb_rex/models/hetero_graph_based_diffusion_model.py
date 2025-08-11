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

def group(xs: List[Tensor], aggr: Optional[str]) -> Optional[Tensor]:
    if len(xs) == 0:
        return None
    elif aggr is None:
        return torch.stack(xs, dim=1)
    elif len(xs) == 1:
        return xs[0]
    elif aggr == "cat":
        return torch.cat(xs, dim=-1)
    elif aggr == "myCat":
        return torch.cat(xs, dim=1)
    else:
        out = torch.stack(xs, dim=0)
        out = getattr(torch, aggr)(out, dim=0)
        out = out[0] if isinstance(out, tuple) else out
        return out


class MinibatchDiscrimination(nn.Module):
    def __init__(
        self, in_features, out_features, intermediate_features=75, initalisation=0.05
    ):
        super(MinibatchDiscrimination, self).__init__()
        self.T = nn.Parameter(
            torch.randn(in_features, intermediate_features, out_features)
            * initalisation
        )
        self.in_features = in_features
        self.intermediate_features = intermediate_features
        self.out_features = out_features

    def forward(self, x):
        # Compute minibatch features
        M = x @ self.T.view(
            x.shape[1], -1
        )  # (batch_size, intermediate_features * out_features)
        M = M.view(
            x.shape[0], -1, self.T.shape[2]
        )  # (batch_size, intermediate_features, out_features)

        # Compute L1 distance across samples
        M_exp = M.unsqueeze(0)  # (1, batch_size, intermediate_features, out_features)
        M_diff = M_exp - M_exp.transpose(
            0, 1
        )  # (batch_size, batch_size, intermediate_features, out_features)
        distance = torch.abs(M_diff).sum(dim=2)  # Sum over intermediate features

        exp_distance = torch.exp(-distance)  # (batch_size, batch_size, out_features)

        # Sum over all samples except itself
        minibatch_features = exp_distance.sum(dim=1) - 1  # (batch_size, out_features)

        return minibatch_features


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
            elif self.aggr == ["mean"]:
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
                out_values[dst] = sum_out / count.clamp(min=1)  # Avoid divide-by-zero
                
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

def global_communication_wrapper(
    layer,
    edge_index,
    x,
    ):

    outputs = layer(x, edge_index)
    # print_heterogenous_representation(outputs)

    for node_type in outputs.keys():
        outputs[node_type] = F.leaky_relu(outputs[node_type])

    for node_type in x.keys():
        if (
            node_type in outputs
        ):  # if only some of the nodes of a node type are used as the end point of edges (as defined by edge_index) the un-used are output as 0. - dont want this, so take previous values
            mask = outputs[node_type].abs().sum(dim=1) == 0  # Find zero rows
            # concatted_shape = torch.cat([outputs[node_type], x[node_type]], dim=1)
            # outputs[node_type] = F.leaky_relu(
            #     selfloop_layer[node_type](concatted_shape)
            # )
            outputs[node_type] += x[node_type]
            outputs[node_type][mask] = x[node_type][mask]  # Restore original embeddings
        else:
            outputs[node_type] = x[node_type]  # Pass through unchanged
            
    return outputs

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


class HeteroGenerator(pl.LightningModule):
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
        super(HeteroGenerator, self).__init__()

        self.conditonless = conditonless

        share_mother_intermediate_layers = False
        self.use_global_node = True
        # self.use_global_node = False

        time_embedding_dim = 5
        self.time_embed = TimeEmbedding(time_embedding_dim)
        self.use_layernorm = True
        self.diffuser = diffuser
        if not self.diffuser:
            time_embedding_dim = 0
            hidden_channels = 250

        # L_mother = 5
        # L_intermediate = 3
        # L_track = 2
        L_mother = 4 + 2
        L_intermediate = 2 + 1
        L_track = 1 + 1

        self.L_mother = L_mother
        self.L_intermediate = L_intermediate
        self.L_track = L_track

        # Targets
        T_mother = mother_targets_dims
        T_intermediate = intermediate_targets_dims
        T_track = track_targets_dims

        ### ### ### ### ###

        if not self.diffuser:
            self.aggrs = ["mean"]
        else:
            self.aggrs = ["mean", "sum", "max"]

        # embedding layer
        embedding_dim = 64
        layer = {}
        layer["track"] = nn.Linear(T_track + L_track, embedding_dim)
        layer["intermediate"] = nn.Linear(
            T_intermediate + L_intermediate, embedding_dim
        )
        layer["mother"] = nn.Linear(T_mother + L_mother, embedding_dim)
        self.embedding_layer = nn.ModuleDict(layer)
        layer = {}
        layer["track"] = nn.Linear(track_conditions_dims, embedding_dim)
        layer["intermediate"] = nn.Linear(intermediate_conditions_dims, embedding_dim)
        layer["mother"] = nn.Linear(mother_conditions_dims, embedding_dim)
        self.condition_embedding_layer = nn.ModuleDict(layer)
        layer = {}
        layer["track"] = nn.Linear(embedding_dim * 2, embedding_dim * 2)
        layer["intermediate"] = nn.Linear(embedding_dim * 2, embedding_dim * 2)
        layer["mother"] = nn.Linear(embedding_dim * 2, embedding_dim * 2)
        self.embedding_pooling_attention_layer = nn.ModuleDict(layer)
        layer = {}
        layer["track"] = nn.Linear(embedding_dim * 2, embedding_dim)
        layer["intermediate"] = nn.Linear(embedding_dim * 2, embedding_dim)
        layer["mother"] = nn.Linear(embedding_dim * 2, embedding_dim)
        self.embedding_pooling_collapsing_layer = nn.ModuleDict(layer)

        self.initial_selfloop_layers = HeteroConv(
            # {
            #     ("track", "self", "track"): GATConv(embedding_dim + time_embedding_dim, hidden_channels),
            #     ("intermediate", "self", "intermediate"): GATConv(
            #         embedding_dim + time_embedding_dim, hidden_channels
            #     ),
            #     ("mother", "self", "mother"): GATConv(
            #         embedding_dim + time_embedding_dim, hidden_channels
            #     ),
            # },
            {
                ("track", "self", "track"): GATConv(
                    embedding_dim + time_embedding_dim, hidden_channels
                ),
                ("intermediate", "self", "intermediate"): GATConv(
                    embedding_dim + time_embedding_dim, hidden_channels
                ),
                ("mother", "self", "mother"): GATConv(
                    embedding_dim + time_embedding_dim, hidden_channels
                ),
            },
            aggr="sum",
        )

        if self.use_layernorm:
            layer = {}
            layer["track"] = nn.LayerNorm(hidden_channels)
            layer["intermediate"] = nn.LayerNorm(hidden_channels)
            layer["mother"] = nn.LayerNorm(hidden_channels)
            self.initial_selfloop_layer_norm = nn.ModuleDict(layer)

        self.selfloop_layers_backward = nn.ModuleList()
        self.propagation_layers_backward = nn.ModuleList()
        self.aggr_attention_layers_backward = nn.ModuleList()
        self.selfloop_layers_forward = nn.ModuleList()
        self.propagation_layers_forward = nn.ModuleList()
        self.aggr_attention_layers_forward = nn.ModuleList()
        if self.use_layernorm:
            self.backwards_layer_norm = nn.ModuleList()
            self.forwards_layer_norm = nn.ModuleList()

        # if not self.diffuser:
        #     self.N_layers = 2
        # else:
        # self.N_layers = 3
        self.N_layers = 3

        self.global_dims = 10
        self.global_layers_to = nn.ModuleList()
        self.global_layers_from = nn.ModuleList()

        # self.condition_embedding_layers_backwards = nn.ModuleList()
        # self.condition_embedding_layers_forwards = nn.ModuleList()
        # self.condition_embedding_layers_backwards_compress = nn.ModuleList()
        # self.condition_embedding_layers_forwards_compress = nn.ModuleList()

        for idx in range(self.N_layers):


            layer = myHeteroConv(
                {
                    ("mother", "to", "global"): NoAggGAT(
                        hidden_channels, self.global_dims
                    ),
                    ("intermediate", "to", "global"): NoAggGAT(
                        hidden_channels, self.global_dims
                    ),
                    ("track", "to", "global"): NoAggGAT(
                        hidden_channels, self.global_dims
                    ),
                },
                aggr="mean",
            )
            self.global_layers_to.append(layer)

            layer = myHeteroConv(
                {
                    ("global", "to", "mother"): NoAggGAT(
                        self.global_dims, hidden_channels
                    ),
                    ("global", "to", "intermediate"): NoAggGAT(
                        self.global_dims, hidden_channels
                    ),
                    ("global", "to", "track"): NoAggGAT(
                        self.global_dims, hidden_channels
                    ),
                },
                aggr="mean",
            )
            self.global_layers_from.append(layer)


            # # embedding layer
            # layer = {}
            # layer["track"] = nn.Linear(track_conditions_dims + L_track, embedding_dim)
            # layer["intermediate"] = nn.Linear(
            #     intermediate_conditions_dims + L_intermediate, embedding_dim
            # )
            # layer["mother"] = nn.Linear(
            #     mother_conditions_dims + L_mother, embedding_dim
            # )
            # self.condition_embedding_layers_backwards.append(nn.ModuleDict(layer))
            # layer = {}
            # layer["track"] = nn.Linear(track_conditions_dims + L_track, embedding_dim)
            # layer["intermediate"] = nn.Linear(
            #     intermediate_conditions_dims + L_intermediate, embedding_dim
            # )
            # layer["mother"] = nn.Linear(
            #     mother_conditions_dims + L_mother, embedding_dim
            # )
            # self.condition_embedding_layers_forwards.append(nn.ModuleDict(layer))
            # layer = {}
            # layer["track"] = nn.Linear(hidden_channels + embedding_dim, hidden_channels)
            # layer["intermediate"] = nn.Linear(
            #     hidden_channels + embedding_dim, hidden_channels
            # )
            # layer["mother"] = nn.Linear(
            #     hidden_channels + embedding_dim, hidden_channels
            # )
            # self.condition_embedding_layers_backwards_compress.append(
            #     nn.ModuleDict(layer)
            # )
            # layer = {}
            # layer["track"] = nn.Linear(hidden_channels + embedding_dim, hidden_channels)
            # layer["intermediate"] = nn.Linear(
            #     hidden_channels + embedding_dim, hidden_channels
            # )
            # layer["mother"] = nn.Linear(
            #     hidden_channels + embedding_dim, hidden_channels
            # )
            # self.condition_embedding_layers_forwards_compress.append(
            #     nn.ModuleDict(layer)
            # )

            if share_mother_intermediate_layers:
                repeated_backwards_layer_intermediate = NoAggGAT(
                    hidden_channels, hidden_channels
                )
                repeated_backwards_layer_mother = NoAggGAT(
                    hidden_channels, hidden_channels
                )
                layer = myHeteroConv(
                    {
                        (
                            "intermediate",
                            "down",
                            "track",
                        ): repeated_backwards_layer_intermediate,
                        (
                            "intermediate",
                            "down",
                            "intermediate",
                        ): repeated_backwards_layer_intermediate,
                        ("mother", "down", "track"): repeated_backwards_layer_mother,
                        (
                            "mother",
                            "down",
                            "intermediate",
                        ): repeated_backwards_layer_mother,
                    },
                    aggr=self.aggrs,
                )
                self.propagation_layers_backward.append(layer)

                layer = {}
                layer["intermediate_attention"] = nn.Linear(
                    hidden_channels * len(self.aggrs), hidden_channels * len(self.aggrs)
                )
                layer["intermediate_aggr"] = nn.Linear(
                    hidden_channels * len(self.aggrs), hidden_channels
                )
                layer["mother_attention"] = layer["intermediate_attention"]
                layer["mother_aggr"] = layer["intermediate_aggr"]
            else:
                layer = myHeteroConv(
                    {
                        ("intermediate", "down", "track"): NoAggGAT(
                            hidden_channels, hidden_channels
                        ),
                        ("intermediate", "down", "intermediate"): NoAggGAT(
                            hidden_channels, hidden_channels
                        ),
                        ("mother", "down", "track"): NoAggGAT(
                            hidden_channels, hidden_channels
                        ),
                        ("mother", "down", "intermediate"): NoAggGAT(
                            hidden_channels, hidden_channels
                        ),
                    },
                    aggr=self.aggrs,
                )
                self.propagation_layers_backward.append(layer)

                layer = {}
                layer["intermediate_attention"] = nn.Linear(
                    hidden_channels * len(self.aggrs), hidden_channels * len(self.aggrs)
                )
                layer["intermediate_aggr"] = nn.Linear(
                    hidden_channels * len(self.aggrs), hidden_channels
                )
                layer["mother_attention"] = nn.Linear(
                    hidden_channels * len(self.aggrs), hidden_channels * len(self.aggrs)
                )
                layer["mother_aggr"] = nn.Linear(
                    hidden_channels * len(self.aggrs), hidden_channels
                )

            layer = nn.ModuleDict(layer)
            self.aggr_attention_layers_backward.append(
                layer
            )  # no pooling, nodes only connected to themselves

            layer = {}
            layer["track"] = nn.Linear(hidden_channels * 2, hidden_channels)
            layer["intermediate"] = nn.Linear(hidden_channels * 2, hidden_channels)
            layer["mother"] = nn.Linear(hidden_channels * 2, hidden_channels)
            layer = nn.ModuleDict(layer)
            self.selfloop_layers_backward.append(layer)

            if share_mother_intermediate_layers:
                repeated_forwards_layer_track = NoAggGAT(
                    hidden_channels, hidden_channels
                )
                repeated_forwards_layer_intermediate = NoAggGAT(
                    hidden_channels, hidden_channels
                )
                layer = myHeteroConv(
                    {
                        ("track", "up", "intermediate"): repeated_forwards_layer_track,
                        (
                            "intermediate",
                            "up",
                            "intermediate",
                        ): repeated_forwards_layer_intermediate,
                        ("track", "up", "mother"): repeated_forwards_layer_track,
                        (
                            "intermediate",
                            "up",
                            "mother",
                        ): repeated_forwards_layer_intermediate,
                    },
                    aggr=self.aggrs,
                )  # this pooling only occurs across multiple edge types, else the pooling is done within GATConv
                self.propagation_layers_forward.append(layer)

                layer = {}
                layer["intermediate_attention"] = nn.Linear(
                    hidden_channels * len(self.aggrs), hidden_channels * len(self.aggrs)
                )
                layer["intermediate_aggr"] = nn.Linear(
                    hidden_channels * len(self.aggrs), hidden_channels
                )
                layer["mother_attention"] = layer["intermediate_attention"]
                layer["mother_aggr"] = layer["intermediate_aggr"]
            else:
                layer = myHeteroConv(
                    {
                        ("track", "up", "intermediate"): NoAggGAT(
                            hidden_channels, hidden_channels
                        ),
                        ("intermediate", "up", "intermediate"): NoAggGAT(
                            hidden_channels, hidden_channels
                        ),
                        ("track", "up", "mother"): NoAggGAT(
                            hidden_channels, hidden_channels
                        ),
                        ("intermediate", "up", "mother"): NoAggGAT(
                            hidden_channels, hidden_channels
                        ),
                    },
                    aggr=self.aggrs,
                )  # this pooling only occurs across multiple edge types, else the pooling is done within GATConv
                self.propagation_layers_forward.append(layer)

                layer = {}
                layer["intermediate_attention"] = nn.Linear(
                    hidden_channels * len(self.aggrs), hidden_channels * len(self.aggrs)
                )
                layer["intermediate_aggr"] = nn.Linear(
                    hidden_channels * len(self.aggrs), hidden_channels
                )
                layer["mother_attention"] = nn.Linear(
                    hidden_channels * len(self.aggrs), hidden_channels * len(self.aggrs)
                )
                layer["mother_aggr"] = nn.Linear(
                    hidden_channels * len(self.aggrs), hidden_channels
                )

            layer = nn.ModuleDict(layer)
            self.aggr_attention_layers_forward.append(
                layer
            )  # no pooling, nodes only connected to themselves

            layer = {}
            layer["track"] = nn.Linear(hidden_channels * 2, hidden_channels)
            layer["intermediate"] = nn.Linear(hidden_channels * 2, hidden_channels)
            layer["mother"] = nn.Linear(hidden_channels * 2, hidden_channels)
            layer = nn.ModuleDict(layer)
            self.selfloop_layers_forward.append(
                layer
            )  # no pooling, nodes only connected to themselves

            if self.use_layernorm:
                layer = {}
                layer["track"] = nn.LayerNorm(hidden_channels)
                layer["intermediate"] = nn.LayerNorm(hidden_channels)
                layer["mother"] = nn.LayerNorm(hidden_channels)
                layer = nn.ModuleDict(layer)
                self.backwards_layer_norm.append(layer)
                layer = {}
                layer["track"] = nn.LayerNorm(hidden_channels)
                layer["intermediate"] = nn.LayerNorm(hidden_channels)
                layer["mother"] = nn.LayerNorm(hidden_channels)
                layer = nn.ModuleDict(layer)
                self.forwards_layer_norm.append(layer)

        self.output_layer = HeteroConv(
            {
                # ("track", "self", "track"): GATConv(hidden_channels, T_track * 2),
                # ("intermediate", "self", "intermediate"): GATConv(hidden_channels, T_intermediate * 2),
                # ("mother", "self", "mother"): GATConv(hidden_channels, T_mother * 2),
                # ("track", "self", "track"): GATConv(hidden_channels, T_track),
                # ("intermediate", "self", "intermediate"): GATConv(hidden_channels, T_intermediate),
                # ("mother", "self", "mother"): GATConv(hidden_channels, T_mother),
                ("track", "self", "track"): GATConv(hidden_channels, hidden_channels),
                ("intermediate", "self", "intermediate"): GATConv(
                    hidden_channels, hidden_channels
                ),
                ("mother", "self", "mother"): GATConv(hidden_channels, hidden_channels),
            },
            aggr="sum",
        )  # no pooling, nodes only connected to themselves

        layer = {}
        layer["track"] = nn.Linear(
            # hidden_channels + track_conditions_dims + L_track, T_track
            hidden_channels, T_track
        )
        layer["intermediate"] = nn.Linear(
            # hidden_channels + intermediate_conditions_dims + L_intermediate,
            hidden_channels,
            T_intermediate,
        )
        layer["mother"] = nn.Linear(
            # hidden_channels + mother_conditions_dims + L_mother, T_mother
            hidden_channels, T_mother
        )
        self.output_layer_linear = nn.ModuleDict(layer)

    def forward(
        self,
        batch,
        timesteps=None,
        add_condition_nodes=False,
        offline_query_mode=False,
    ) -> Tuple[Tensor, Tensor, Tensor]:
        if self.diffuser:
            timestep_embedding = self.time_embed(timesteps)


        if self.use_global_node:
            global_edge_indexes_to ={}
            global_edge_indexes_from ={}

            global_edge_indexes_to["mother", "to", "global"] = batch["mother", "self", "mother"]["edge_index"]
            global_edge_indexes_from["global", "to", "mother"] = batch["mother", "self", "mother"]["edge_index"]

            N_tracks = int(batch["track", "self", "track"]["edge_index"].shape[1]/batch["mother", "self", "mother"]["edge_index"].shape[1])
            global_edge_indexes_to["track", "to", "global"] = torch.concat((batch["track", "self", "track"]["edge_index"][0].unsqueeze(0), batch["mother", "self", "mother"]["edge_index"][1].repeat_interleave(N_tracks).unsqueeze(0)), dim=0)
            global_edge_indexes_from["global", "to", "track"] = torch.concat((batch["mother", "self", "mother"]["edge_index"][1].repeat_interleave(N_tracks).unsqueeze(0), batch["track", "self", "track"]["edge_index"][0].unsqueeze(0)), dim=0)

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
            if self.use_global_node:
                N_ints = int(batch["intermediate", "self", "intermediate"]["edge_index"].shape[1]/batch["mother", "self", "mother"]["edge_index"].shape[1])
                global_edge_indexes_to["intermediate", "to", "global"] = torch.concat((batch["intermediate", "self", "intermediate"]["edge_index"][0].unsqueeze(0), batch["mother", "self", "mother"]["edge_index"][1].repeat_interleave(N_ints).unsqueeze(0)), dim=0)
                global_edge_indexes_from["global", "to", "intermediate"] = torch.concat((batch["mother", "self", "mother"]["edge_index"][1].repeat_interleave(N_ints).unsqueeze(0), batch["intermediate", "self", "intermediate"]["edge_index"][0].unsqueeze(0)), dim=0)
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

        # if offline_query_mode:
        #     for i in latent:
        #         latent[i] = latent[i].to("cuda:5")
        #     for i in conditions:
        #         conditions[i] = conditions[i].to("cuda:5")
        #     for i in edge_index_dict_self_loop:
        #         edge_index_dict_self_loop[i] = edge_index_dict_self_loop[i].to("cuda:5")
        #     for edge_index_dict in edge_index_dicts_backward:
        #         for i in edge_index_dict:
        #             edge_index_dict[i] = edge_index_dict[i].to("cuda:5")
        #     for edge_index_dict in edge_index_dicts_forward:
        #         for i in edge_index_dict:
        #             edge_index_dict[i] = edge_index_dict[i].to("cuda:5")

        for node_type in current_x:
            if node_type != 'global':
                current_x[node_type] = torch.cat(
                    [current_x[node_type], extra_latent[node_type]], dim=1
                )

        x = current_x.copy()

        # print_heterogenous_representation(x)

        # if not self.conditonless: # remove conditions, need to keep the extra latent dims that were gracelessly concated to the end of the conditions tensors
        #     for node_type in x:
        #         x[node_type] = torch.cat(
        #             (x[node_type], conditions[node_type]), dim=1
        #         )

        for node_type in x:
            if node_type != 'global':
                x[node_type] = self.embedding_layer[node_type](x[node_type])

        if add_condition_nodes:
            for node_type in conditions:
                conditional_embedding = self.condition_embedding_layer[node_type](
                    conditions[node_type]
                )
                x[node_type] = torch.cat((x[node_type], conditional_embedding), dim=1)
                atten = torch.sigmoid(
                    self.embedding_pooling_attention_layer[node_type](x[node_type])
                )
                x[node_type] = atten * x[node_type]
                x[node_type] = self.embedding_pooling_collapsing_layer[node_type](
                    x[node_type]
                )

                conditions[node_type] = torch.cat(
                    (conditions[node_type], extra_latent[node_type]), dim=1
                )

        # print_heterogenous_representation(x)

        if self.diffuser:  # concatenate time embeddings
            for node_type in x:
                if node_type != 'global':
                    if x[node_type].shape[0] == timesteps.shape[0]:
                        x[node_type] = torch.cat([x[node_type], timestep_embedding], dim=1)
                    else:
                        # If multiple nodes per sample (like track), repeat embeddings accordingly
                        nodes_per_sample = x[node_type].shape[0] // timesteps.shape[0]
                        timestep_expanded = timestep_embedding.repeat_interleave(
                            nodes_per_sample, dim=0
                        )
                        x[node_type] = torch.cat([x[node_type], timestep_expanded], dim=1)

        # print_heterogenous_representation(x)
        x = self.initial_selfloop_layers(x, edge_index_dict_self_loop)
        if self.use_layernorm:
            for node_type in x:
                if node_type != 'global':
                    x[node_type] = self.initial_selfloop_layer_norm[node_type](x[node_type])

        if self.use_global_node:
            x["global"] = torch.zeros((batch["mother"].x.shape[0], self.global_dims), device=batch["mother"].x.device)
        # print_heterogenous_representation(x)
        # quit()

        for node_type in x:
            x[node_type] = x[node_type].squeeze()
            if x[node_type].dim() == 1:
                x[node_type] = x[node_type].unsqueeze(0)

        for layer_idx in range(self.N_layers):
            # print_heterogenous_representation(x)
            # if add_condition_nodes:
            #     for node_type in x:
            #         x[node_type] = torch.cat(
            #             (
            #                 x[node_type],
            #                 self.condition_embedding_layers_backwards[layer_idx][
            #                     node_type
            #                 ](conditions[node_type]),
            #             ),
            #             dim=1,
            #         )
            #         x[node_type] = self.condition_embedding_layers_backwards_compress[
            #             layer_idx
            #         ][node_type](x[node_type])
            # print_heterogenous_representation(x)

            for edge_index_dict in edge_index_dicts_backward:
                x = heterogenous_layer_wrapper_w_cat_and_self_loop(
                    self.propagation_layers_backward[layer_idx],
                    self.aggr_attention_layers_backward[layer_idx],
                    self.selfloop_layers_backward[layer_idx],
                    x,
                    edge_index_dict,
                    aggrs=self.aggrs,
                )


            if self.use_layernorm:
                for node_type in x:
                    if node_type != 'global':   
                        x[node_type] = self.backwards_layer_norm[layer_idx][node_type](
                            x[node_type]
                        )
            ##### ##### ##### ##### ##### #####
            ##### COMMUNICATE
            ##### ##### ##### ##### ##### #####
            if self.use_global_node:
                x = global_communication_wrapper(
                        self.global_layers_to[layer_idx],
                        global_edge_indexes_to,
                        x,
                    )
                x = global_communication_wrapper(
                        self.global_layers_from[layer_idx],
                        global_edge_indexes_from,
                        x,
                    )


            # if add_condition_nodes:
            #     for node_type in x:
            #         x[node_type] = torch.cat(
            #             (
            #                 x[node_type],
            #                 self.condition_embedding_layers_forwards[layer_idx][
            #                     node_type
            #                 ](conditions[node_type]),
            #             ),
            #             dim=1,
            #         )
            #         x[node_type] = self.condition_embedding_layers_forwards_compress[
            #             layer_idx
            #         ][node_type](x[node_type])

            for edge_index_dict in edge_index_dicts_forward:
                x = heterogenous_layer_wrapper_w_cat_and_self_loop(
                    self.propagation_layers_forward[layer_idx],
                    self.aggr_attention_layers_forward[layer_idx],
                    self.selfloop_layers_forward[layer_idx],
                    x,
                    edge_index_dict,
                    aggrs=self.aggrs,
                )

            if self.use_layernorm:
                for node_type in x:
                    if node_type != 'global':
                        x[node_type] = self.forwards_layer_norm[layer_idx][node_type](
                            x[node_type]
                        )

            ##### ##### ##### ##### ##### #####
            ##### COMMUNICATE
            ##### ##### ##### ##### ##### #####
            if self.use_global_node:
                x = global_communication_wrapper(
                        self.global_layers_to[layer_idx],
                        global_edge_indexes_to,
                        x,
                    )
                x = global_communication_wrapper(
                        self.global_layers_from[layer_idx],
                        global_edge_indexes_from,
                        x,
                    )


        x = self.output_layer(x, edge_index_dict_self_loop)

        x_out = {}
        for node_type in x:
            if node_type != 'global':
                x_out[node_type] = F.leaky_relu(x[node_type])

                # x[node_type] = torch.cat((x[node_type], conditions[node_type]), dim=1)

                x_out[node_type] = self.output_layer_linear[node_type](x_out[node_type])
                unsqueeze = False
                if x_out[node_type].shape[0] == 1:
                    unsqueeze = True  # batch size is 1
                x_out[node_type] = x_out[node_type].squeeze()
                if unsqueeze:
                    x_out[node_type] = x_out[node_type].unsqueeze(0)

        return [x_out]


class HeteroEncoder(pl.LightningModule):
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
        super(HeteroEncoder, self).__init__()

        self.conditonless = conditonless

        self.use_layernorm = False
        self.diffuser = diffuser

        share_mother_intermediate_layers = False

        hidden_channels = 250

        # L_mother = 5
        # L_intermediate = 3
        # L_track = 2
        L_mother = 4
        L_intermediate = 2
        L_track = 1

        self.L_mother = L_mother
        self.L_intermediate = L_intermediate
        self.L_track = L_track

        # Targets
        T_mother = mother_targets_dims
        T_intermediate = intermediate_targets_dims
        T_track = track_targets_dims

        ### ### ### ### ###

        if not self.diffuser:
            self.aggrs = ["mean"]
        else:
            self.aggrs = ["mean", "sum", "max"]

        # embedding layer
        embedding_dim = 64
        layer = {}
        layer["track"] = nn.Linear(T_track, embedding_dim)
        layer["intermediate"] = nn.Linear(T_intermediate, embedding_dim)
        layer["mother"] = nn.Linear(T_mother, embedding_dim)
        self.embedding_layer = nn.ModuleDict(layer)
        layer = {}
        layer["track"] = nn.Linear(track_conditions_dims, embedding_dim)
        layer["intermediate"] = nn.Linear(intermediate_conditions_dims, embedding_dim)
        layer["mother"] = nn.Linear(mother_conditions_dims, embedding_dim)
        self.condition_embedding_layer = nn.ModuleDict(layer)
        layer = {}
        layer["track"] = nn.Linear(embedding_dim * 2, embedding_dim * 2)
        layer["intermediate"] = nn.Linear(embedding_dim * 2, embedding_dim * 2)
        layer["mother"] = nn.Linear(embedding_dim * 2, embedding_dim * 2)
        self.embedding_pooling_attention_layer = nn.ModuleDict(layer)
        layer = {}
        layer["track"] = nn.Linear(embedding_dim * 2, embedding_dim)
        layer["intermediate"] = nn.Linear(embedding_dim * 2, embedding_dim)
        layer["mother"] = nn.Linear(embedding_dim * 2, embedding_dim)
        self.embedding_pooling_collapsing_layer = nn.ModuleDict(layer)

        self.initial_selfloop_layers = HeteroConv(
            {
                ("track", "self", "track"): GATConv(embedding_dim, hidden_channels),
                ("intermediate", "self", "intermediate"): GATConv(
                    embedding_dim, hidden_channels
                ),
                ("mother", "self", "mother"): GATConv(embedding_dim, hidden_channels),
            },
            aggr="sum",
        )

        if self.use_layernorm:
            layer = {}
            layer["track"] = nn.LayerNorm(hidden_channels)
            layer["intermediate"] = nn.LayerNorm(hidden_channels)
            layer["mother"] = nn.LayerNorm(hidden_channels)
            self.initial_selfloop_layer_norm = nn.ModuleDict(layer)

        self.selfloop_layers_backward = nn.ModuleList()
        self.propagation_layers_backward = nn.ModuleList()
        self.aggr_attention_layers_backward = nn.ModuleList()
        self.selfloop_layers_forward = nn.ModuleList()
        self.propagation_layers_forward = nn.ModuleList()
        self.aggr_attention_layers_forward = nn.ModuleList()
        if self.use_layernorm:
            self.backwards_layer_norm = nn.ModuleList()
            self.forwards_layer_norm = nn.ModuleList()

        self.N_layers = 2

        self.condition_embedding_layers_backwards = nn.ModuleList()
        self.condition_embedding_layers_forwards = nn.ModuleList()
        self.condition_embedding_layers_backwards_compress = nn.ModuleList()
        self.condition_embedding_layers_forwards_compress = nn.ModuleList()

        for idx in range(self.N_layers):
            # embedding layer
            layer = {}
            layer["track"] = nn.Linear(track_conditions_dims + T_track, embedding_dim)
            layer["intermediate"] = nn.Linear(
                intermediate_conditions_dims + T_intermediate, embedding_dim
            )
            layer["mother"] = nn.Linear(
                mother_conditions_dims + T_mother, embedding_dim
            )
            self.condition_embedding_layers_backwards.append(nn.ModuleDict(layer))
            layer = {}
            layer["track"] = nn.Linear(track_conditions_dims + T_track, embedding_dim)
            layer["intermediate"] = nn.Linear(
                intermediate_conditions_dims + T_intermediate, embedding_dim
            )
            layer["mother"] = nn.Linear(
                mother_conditions_dims + T_mother, embedding_dim
            )
            self.condition_embedding_layers_forwards.append(nn.ModuleDict(layer))
            layer = {}
            layer["track"] = nn.Linear(hidden_channels + embedding_dim, hidden_channels)
            layer["intermediate"] = nn.Linear(
                hidden_channels + embedding_dim, hidden_channels
            )
            layer["mother"] = nn.Linear(
                hidden_channels + embedding_dim, hidden_channels
            )
            self.condition_embedding_layers_backwards_compress.append(
                nn.ModuleDict(layer)
            )
            layer = {}
            layer["track"] = nn.Linear(hidden_channels + embedding_dim, hidden_channels)
            layer["intermediate"] = nn.Linear(
                hidden_channels + embedding_dim, hidden_channels
            )
            layer["mother"] = nn.Linear(
                hidden_channels + embedding_dim, hidden_channels
            )
            self.condition_embedding_layers_forwards_compress.append(
                nn.ModuleDict(layer)
            )

            if share_mother_intermediate_layers:
                repeated_backwards_layer_intermediate = NoAggGAT(
                    hidden_channels, hidden_channels
                )
                repeated_backwards_layer_mother = NoAggGAT(
                    hidden_channels, hidden_channels
                )
                layer = myHeteroConv(
                    {
                        (
                            "intermediate",
                            "down",
                            "track",
                        ): repeated_backwards_layer_intermediate,
                        (
                            "intermediate",
                            "down",
                            "intermediate",
                        ): repeated_backwards_layer_intermediate,
                        ("mother", "down", "track"): repeated_backwards_layer_mother,
                        (
                            "mother",
                            "down",
                            "intermediate",
                        ): repeated_backwards_layer_mother,
                    },
                    aggr=self.aggrs,
                )
                self.propagation_layers_backward.append(layer)

                layer = {}
                layer["intermediate_attention"] = nn.Linear(
                    hidden_channels * len(self.aggrs), hidden_channels * len(self.aggrs)
                )
                layer["intermediate_aggr"] = nn.Linear(
                    hidden_channels * len(self.aggrs), hidden_channels
                )
                layer["mother_attention"] = layer["intermediate_attention"]
                layer["mother_aggr"] = layer["intermediate_aggr"]
            else:
                layer = myHeteroConv(
                    {
                        ("intermediate", "down", "track"): NoAggGAT(
                            hidden_channels, hidden_channels
                        ),
                        ("intermediate", "down", "intermediate"): NoAggGAT(
                            hidden_channels, hidden_channels
                        ),
                        ("mother", "down", "track"): NoAggGAT(
                            hidden_channels, hidden_channels
                        ),
                        ("mother", "down", "intermediate"): NoAggGAT(
                            hidden_channels, hidden_channels
                        ),
                    },
                    aggr=self.aggrs,
                )
                self.propagation_layers_backward.append(layer)

                layer = {}
                layer["intermediate_attention"] = nn.Linear(
                    hidden_channels * len(self.aggrs), hidden_channels * len(self.aggrs)
                )
                layer["intermediate_aggr"] = nn.Linear(
                    hidden_channels * len(self.aggrs), hidden_channels
                )
                layer["mother_attention"] = nn.Linear(
                    hidden_channels * len(self.aggrs), hidden_channels * len(self.aggrs)
                )
                layer["mother_aggr"] = nn.Linear(
                    hidden_channels * len(self.aggrs), hidden_channels
                )

            layer = nn.ModuleDict(layer)
            self.aggr_attention_layers_backward.append(
                layer
            )  # no pooling, nodes only connected to themselves

            layer = {}
            layer["track"] = nn.Linear(hidden_channels * 2, hidden_channels)
            layer["intermediate"] = nn.Linear(hidden_channels * 2, hidden_channels)
            layer["mother"] = nn.Linear(hidden_channels * 2, hidden_channels)
            layer = nn.ModuleDict(layer)
            self.selfloop_layers_backward.append(layer)

            if share_mother_intermediate_layers:
                repeated_forwards_layer_track = NoAggGAT(
                    hidden_channels, hidden_channels
                )
                repeated_forwards_layer_intermediate = NoAggGAT(
                    hidden_channels, hidden_channels
                )
                layer = myHeteroConv(
                    {
                        ("track", "up", "intermediate"): repeated_forwards_layer_track,
                        (
                            "intermediate",
                            "up",
                            "intermediate",
                        ): repeated_forwards_layer_intermediate,
                        ("track", "up", "mother"): repeated_forwards_layer_track,
                        (
                            "intermediate",
                            "up",
                            "mother",
                        ): repeated_forwards_layer_intermediate,
                    },
                    aggr=self.aggrs,
                )  # this pooling only occurs across multiple edge types, else the pooling is done within GATConv
                self.propagation_layers_forward.append(layer)

                layer = {}
                layer["intermediate_attention"] = nn.Linear(
                    hidden_channels * len(self.aggrs), hidden_channels * len(self.aggrs)
                )
                layer["intermediate_aggr"] = nn.Linear(
                    hidden_channels * len(self.aggrs), hidden_channels
                )
                layer["mother_attention"] = layer["intermediate_attention"]
                layer["mother_aggr"] = layer["intermediate_aggr"]
            else:
                layer = myHeteroConv(
                    {
                        ("track", "up", "intermediate"): NoAggGAT(
                            hidden_channels, hidden_channels
                        ),
                        ("intermediate", "up", "intermediate"): NoAggGAT(
                            hidden_channels, hidden_channels
                        ),
                        ("track", "up", "mother"): NoAggGAT(
                            hidden_channels, hidden_channels
                        ),
                        ("intermediate", "up", "mother"): NoAggGAT(
                            hidden_channels, hidden_channels
                        ),
                    },
                    aggr=self.aggrs,
                )  # this pooling only occurs across multiple edge types, else the pooling is done within GATConv
                self.propagation_layers_forward.append(layer)

                layer = {}
                layer["intermediate_attention"] = nn.Linear(
                    hidden_channels * len(self.aggrs), hidden_channels * len(self.aggrs)
                )
                layer["intermediate_aggr"] = nn.Linear(
                    hidden_channels * len(self.aggrs), hidden_channels
                )
                layer["mother_attention"] = nn.Linear(
                    hidden_channels * len(self.aggrs), hidden_channels * len(self.aggrs)
                )
                layer["mother_aggr"] = nn.Linear(
                    hidden_channels * len(self.aggrs), hidden_channels
                )

            layer = nn.ModuleDict(layer)
            self.aggr_attention_layers_forward.append(
                layer
            )  # no pooling, nodes only connected to themselves

            layer = {}
            layer["track"] = nn.Linear(hidden_channels * 2, hidden_channels)
            layer["intermediate"] = nn.Linear(hidden_channels * 2, hidden_channels)
            layer["mother"] = nn.Linear(hidden_channels * 2, hidden_channels)
            layer = nn.ModuleDict(layer)
            self.selfloop_layers_forward.append(
                layer
            )  # no pooling, nodes only connected to themselves

            if self.use_layernorm:
                layer = {}
                layer["track"] = nn.LayerNorm(hidden_channels)
                layer["intermediate"] = nn.LayerNorm(hidden_channels)
                layer["mother"] = nn.LayerNorm(hidden_channels)
                layer = nn.ModuleDict(layer)
                self.backwards_layer_norm.append(layer)
                layer = {}
                layer["track"] = nn.LayerNorm(hidden_channels)
                layer["intermediate"] = nn.LayerNorm(hidden_channels)
                layer["mother"] = nn.LayerNorm(hidden_channels)
                layer = nn.ModuleDict(layer)
                self.forwards_layer_norm.append(layer)

        self.output_layer = HeteroConv(
            {
                ("track", "self", "track"): GATConv(hidden_channels, hidden_channels),
                ("intermediate", "self", "intermediate"): GATConv(
                    hidden_channels, hidden_channels
                ),
                ("mother", "self", "mother"): GATConv(hidden_channels, hidden_channels),
            },
            aggr="sum",
        )  # no pooling, nodes only connected to themselves

        layer = {}
        layer["track"] = nn.Linear(
            hidden_channels + track_conditions_dims + T_track, L_track * 2
        )
        layer["intermediate"] = nn.Linear(
            hidden_channels + intermediate_conditions_dims + T_intermediate,
            L_intermediate * 2,
        )
        layer["mother"] = nn.Linear(
            hidden_channels + mother_conditions_dims + T_mother, L_mother * 2
        )
        self.output_layer_linear = nn.ModuleDict(layer)

    def forward(
        self,
        batch,
        add_condition_nodes=False,
        offline_query_mode=False,
    ) -> Tuple[Tensor, Tensor, Tensor]:
        conditions = {
            "track": batch["track_conditions"].x,
            "mother": batch["mother_conditions"].x,
        }
        current_x = {
            "track": batch["track"].x,
            "mother": batch["mother"].x,
        }
        intermediate_present = False
        try:
            conditions["intermediate"] = batch["intermediate_conditions"].x
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

        # if offline_query_mode:
        #     for i in latent:
        #         latent[i] = latent[i].to("cuda:5")
        #     for i in conditions:
        #         conditions[i] = conditions[i].to("cuda:5")
        #     for i in edge_index_dict_self_loop:
        #         edge_index_dict_self_loop[i] = edge_index_dict_self_loop[i].to("cuda:5")
        #     for edge_index_dict in edge_index_dicts_backward:
        #         for i in edge_index_dict:
        #             edge_index_dict[i] = edge_index_dict[i].to("cuda:5")
        #     for edge_index_dict in edge_index_dicts_forward:
        #         for i in edge_index_dict:
        #             edge_index_dict[i] = edge_index_dict[i].to("cuda:5")

        x = current_x.copy()

        # if not self.conditonless: # remove conditions, need to keep the extra latent dims that were gracelessly concated to the end of the conditions tensors
        #     for node_type in x:
        #         x[node_type] = torch.cat(
        #             (x[node_type], conditions[node_type]), dim=1
        #         )

        for node_type in x:
            x[node_type] = self.embedding_layer[node_type](x[node_type])

        if add_condition_nodes:
            for node_type in conditions:
                conditional_embedding = self.condition_embedding_layer[node_type](
                    conditions[node_type]
                )
                x[node_type] = torch.cat((x[node_type], conditional_embedding), dim=1)
                atten = torch.sigmoid(
                    self.embedding_pooling_attention_layer[node_type](x[node_type])
                )
                x[node_type] = atten * x[node_type]
                x[node_type] = self.embedding_pooling_collapsing_layer[node_type](
                    x[node_type]
                )

                conditions[node_type] = torch.cat(
                    (conditions[node_type], current_x[node_type]), dim=1
                )

        # print_heterogenous_representation(x)

        x = self.initial_selfloop_layers(x, edge_index_dict_self_loop)
        if self.use_layernorm:
            for node_type in x:
                x[node_type] = self.initial_selfloop_layer_norm[node_type](x[node_type])

        # print_heterogenous_representation(x)

        for node_type in x:
            x[node_type] = x[node_type].squeeze()
            if x[node_type].dim() == 1:
                x[node_type] = x[node_type].unsqueeze(0)

        for layer_idx in range(self.N_layers):
            if add_condition_nodes:
                for node_type in x:
                    x[node_type] = torch.cat(
                        (
                            x[node_type],
                            self.condition_embedding_layers_forwards[layer_idx][
                                node_type
                            ](conditions[node_type]),
                        ),
                        dim=1,
                    )
                    x[node_type] = self.condition_embedding_layers_forwards_compress[
                        layer_idx
                    ][node_type](x[node_type])

            for edge_index_dict in edge_index_dicts_forward:
                x = heterogenous_layer_wrapper_w_cat_and_self_loop(
                    self.propagation_layers_forward[layer_idx],
                    self.aggr_attention_layers_forward[layer_idx],
                    self.selfloop_layers_forward[layer_idx],
                    x,
                    edge_index_dict,
                    aggrs=self.aggrs,
                )

            if self.use_layernorm:
                for node_type in x:
                    x[node_type] = self.forwards_layer_norm[layer_idx][node_type](
                        x[node_type]
                    )

            # print_heterogenous_representation(x)
            if add_condition_nodes:
                for node_type in x:
                    x[node_type] = torch.cat(
                        (
                            x[node_type],
                            self.condition_embedding_layers_backwards[layer_idx][
                                node_type
                            ](conditions[node_type]),
                        ),
                        dim=1,
                    )
                    x[node_type] = self.condition_embedding_layers_backwards_compress[
                        layer_idx
                    ][node_type](x[node_type])
            # print_heterogenous_representation(x)

            for edge_index_dict in edge_index_dicts_backward:
                x = heterogenous_layer_wrapper_w_cat_and_self_loop(
                    self.propagation_layers_backward[layer_idx],
                    self.aggr_attention_layers_backward[layer_idx],
                    self.selfloop_layers_backward[layer_idx],
                    x,
                    edge_index_dict,
                    aggrs=self.aggrs,
                )

            if self.use_layernorm:
                for node_type in x:
                    x[node_type] = self.backwards_layer_norm[layer_idx][node_type](
                        x[node_type]
                    )

        x = self.output_layer(x, edge_index_dict_self_loop)

        for node_type in x:
            x[node_type] = F.leaky_relu(x[node_type])

            x[node_type] = torch.cat((x[node_type], conditions[node_type]), dim=1)

            x[node_type] = self.output_layer_linear[node_type](x[node_type])
            unsqueeze = False
            if x[node_type].shape[0] == 1:
                unsqueeze = True  # batch size is 1
            x[node_type] = x[node_type].squeeze()
            if unsqueeze:
                x[node_type] = x[node_type].unsqueeze(0)

            x[node_type] = x[node_type].view(-1, int(x[node_type].shape[-1] / 2), 2)

        # this will need to be mu and sigma eventually
        return [x]


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


class diffusion_model(nn.Module):
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
        steps,
        silent=False,
        eGAN=False,
    ):
        super(diffusion_model, self).__init__()

        self.steps = steps

        if not silent:
            print("\n")
            print("Network params -----------------")
            print("mother_targets_dims:", mother_targets_dims)
            print("intermediate_targets_dims:", intermediate_targets_dims)
            print("track_targets_dims:", track_targets_dims)
            print("mother_conditions_dims:", mother_conditions_dims)
            print("intermediate_conditions_dims:", intermediate_conditions_dims)
            print("track_conditions_dims:", track_conditions_dims)
            print("hidden_channels:", hidden_channels)
            print("mother_latent_dims:", mother_latent_dims)
            print("track_latent_dims:", track_latent_dims)
            print("intermediate_latent_dims:", intermediate_latent_dims)
            print("\n")

        self.mother_latent_dims = mother_latent_dims
        self.track_latent_dims = track_latent_dims
        self.intermediate_latent_dims = intermediate_latent_dims

        self.mother_targets_dims = mother_targets_dims
        self.track_targets_dims = track_targets_dims
        self.intermediate_targets_dims = intermediate_targets_dims

        self.track_conditions_dims = track_conditions_dims
        self.intermediate_conditions_dims = intermediate_conditions_dims

        self.diffuser = HeteroGenerator(
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
            conditonless=True,
            #     conditonless=False,
            diffuser=True,
        )

        self.encoder = HeteroEncoder(
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
            conditonless=True,
            #     conditonless=False,
            diffuser=True,
        )

        self.EMA_diffuser = EMA(self.diffuser)

        self.eGAN = eGAN

        if self.eGAN:
            raise Exception("eGAN discontinued")

    @torch.no_grad()
    def inference_flow_matching(
        self,
        batch_size,
        batch_in,
        num_steps=100,
        add_condition_nodes=True,
        offline_query_mode=False,
    ):
        # Match device
        self.EMA_diffuser.ema_model.to(self.diffuser.device)

        try:
            batch = batch_in.clone()
            # if self.eGAN:
        except:
            batch = batch_in

        device = batch["mother"].x.device

        # Detect whether intermediate node type is present
        intermediate_present = False
        try:
            batch["intermediate"].x
            intermediate_present = True
        except:
            pass

        # Sample initial noise (same shape as final output)
        x_mother = torch.randn(
            (batch["mother"].x.shape[0], self.mother_latent_dims), device=device
        )  # * 0.25
        x_track = torch.randn(
            (batch["track"].x.shape[0], self.track_latent_dims), device=device
        )  # * 0.25

        if intermediate_present:
            x_intermediate = torch.randn(
                (batch["intermediate"].x.shape[0], self.intermediate_latent_dims),
                device=device,
            )  # * 0.25

        # Initial latent container
        latent = {
            "mother": x_mother,
            "track": x_track,
        }
        if intermediate_present:
            latent["intermediate"] = x_intermediate

        noise = torch.rand(
            (batch["mother_conditions"].x.shape[0], 2),
            device=batch["mother_conditions"].x.device,
            dtype=batch["mother_conditions"].x.dtype,
        )
        batch["mother_conditions"].x = torch.cat(
            (batch["mother_conditions"].x, noise), dim=-1
        )
        if intermediate_present:
            noise = torch.rand(
                (batch["intermediate_conditions"].x.shape[0], 2),
                device=batch["intermediate_conditions"].x.device,
                dtype=batch["intermediate_conditions"].x.dtype,
            )
            batch["intermediate_conditions"].x = torch.cat(
                (batch["intermediate_conditions"].x, noise), dim=-1
            )
        noise = torch.rand(
            (batch["track_conditions"].x.shape[0], 1),
            device=batch["track_conditions"].x.device,
            dtype=batch["track_conditions"].x.dtype,
        )
        batch["track_conditions"].x = torch.cat(
            (batch["track_conditions"].x, noise), dim=-1
        )

        ts = torch.linspace(0, 1, steps=num_steps + 1, device=device)
        delta_t = ts[1] - ts[0]  # Constant step size

        for i in range(num_steps):
            t = ts[i].repeat(batch_size).to(device)

            batch["mother"].x = latent["mother"]
            batch["track"].x = latent["track"]
            if intermediate_present:
                batch["intermediate"].x = latent["intermediate"]

            # Predict noise at current timestep
            noise_pred = self.diffuser(
                batch=batch,
                timesteps=t,
                offline_query_mode=offline_query_mode,
                add_condition_nodes=add_condition_nodes,
            )[0]

            # Denoise each component
            for node_type in latent:
                model_output = noise_pred[node_type]

                # Ensure shape matches expected sample shape
                if model_output.ndim == 1:
                    model_output = model_output.unsqueeze(-1)  # Or reshape accordingly

                latent[node_type] = latent[node_type] + delta_t * model_output

        if intermediate_present:
            return latent["mother"], latent["intermediate"], latent["track"]
        else:
            return latent["mother"], None, latent["track"]

    @torch.no_grad()
    def inference(
        self,
        batch_size,
        batch_in,
        noise_scheduler,
        add_condition_nodes=True,
        offline_query_mode=False,
        flowmatching=False,
        use_encoder=True,
    ):
        # option for raw or ema

        if flowmatching:
            return self.inference_flow_matching(
                batch_size=batch_size,
                batch_in=batch_in,
                num_steps=25,
                add_condition_nodes=add_condition_nodes,
                offline_query_mode=offline_query_mode,
            )

        # Match device
        self.EMA_diffuser.ema_model.to(self.diffuser.device)

        try:
            batch = batch_in.clone()
            # if self.eGAN:
        except:
            batch = batch_in

        device = batch["mother"].x.device

        # Detect whether intermediate node type is present
        intermediate_present = False
        try:
            batch["intermediate"].x
            intermediate_present = True
        except:
            pass

        # Sample initial noise (same shape as final output)
        x_mother = torch.randn(
            (batch["mother"].x.shape[0], self.mother_latent_dims), device=device
        )  # * 0.25
        x_track = torch.randn(
            (batch["track"].x.shape[0], self.track_latent_dims), device=device
        )  # * 0.25

        if intermediate_present:
            x_intermediate = torch.randn(
                (batch["intermediate"].x.shape[0], self.intermediate_latent_dims),
                device=device,
            )  # * 0.25

        # Initial latent container
        latent = {
            "mother": x_mother,
            "track": x_track,
        }
        if intermediate_present:
            latent["intermediate"] = x_intermediate

        use_encoder = False

        if use_encoder:
            encoded_target = self.encoder(
                batch, add_condition_nodes=add_condition_nodes
            )[0]
            noise = torch.rand(
                (batch["mother_conditions"].x.shape[0], self.diffuser.L_mother),
                device=batch["mother_conditions"].x.device,
                dtype=batch["mother_conditions"].x.dtype,
            )
            encoded_target_gen = (
                encoded_target["mother"][:, :, 0]
                + torch.randn_like(encoded_target["mother"][:, :, 1])
                * encoded_target["mother"][:, :, 1]
            )
            if encoded_target_gen.ndim == 1:
                encoded_target_gen = encoded_target_gen.unsqueeze(-1)
            noise[:, : encoded_target_gen.shape[1]] = encoded_target_gen
            batch["mother_conditions"].x = torch.cat(
                (batch["mother_conditions"].x, noise), dim=-1
            )
            if intermediate_present:
                noise = torch.rand(
                    (
                        batch["intermediate_conditions"].x.shape[0],
                        self.diffuser.L_intermediate,
                    ),
                    device=batch["intermediate_conditions"].x.device,
                    dtype=batch["intermediate_conditions"].x.dtype,
                )
                encoded_target_gen = (
                    encoded_target["intermediate"][:, :, 0]
                    + torch.randn_like(encoded_target["intermediate"][:, :, 1])
                    * encoded_target["intermediate"][:, :, 1]
                )
                if encoded_target_gen.ndim == 1:
                    encoded_target_gen = encoded_target_gen.unsqueeze(-1)
                noise[:, : encoded_target_gen.shape[1]] = encoded_target_gen
                batch["intermediate_conditions"].x = torch.cat(
                    (batch["intermediate_conditions"].x, noise), dim=-1
                )
            noise = torch.rand(
                (batch["track_conditions"].x.shape[0], self.diffuser.L_track),
                device=batch["track_conditions"].x.device,
                dtype=batch["track_conditions"].x.dtype,
            )
            encoded_target_gen = (
                encoded_target["track"][:, :, 0]
                + torch.randn_like(encoded_target["track"][:, :, 1])
                * encoded_target["track"][:, :, 1]
            )
            if encoded_target_gen.ndim == 1:
                encoded_target_gen = encoded_target_gen.unsqueeze(-1)
            noise[:, : encoded_target_gen.shape[1]] = encoded_target_gen
            # noise = torch.rand_like(noise) # WARNING THROWING AWAY ENCODED TRACK
            batch["track_conditions"].x = torch.cat(
                (batch["track_conditions"].x, noise), dim=-1
            )

            # noise = torch.rand((batch["track_conditions"].x.shape[0], self.diffuser.L_track), device=batch["track_conditions"].x.device, dtype=batch["track_conditions"].x.dtype)
            # batch["track_conditions"].x = torch.cat((batch["track_conditions"].x, noise), dim=-1)

        else:
            noise = torch.rand(
                (batch["mother_conditions"].x.shape[0], self.diffuser.L_mother),
                device=batch["mother_conditions"].x.device,
                dtype=batch["mother_conditions"].x.dtype,
            )
            batch["mother_conditions"].x = torch.cat(
                (batch["mother_conditions"].x, noise), dim=-1
            )
            if intermediate_present:
                noise = torch.rand(
                    (
                        batch["intermediate_conditions"].x.shape[0],
                        self.diffuser.L_intermediate,
                    ),
                    device=batch["intermediate_conditions"].x.device,
                    dtype=batch["intermediate_conditions"].x.dtype,
                )
                batch["intermediate_conditions"].x = torch.cat(
                    (batch["intermediate_conditions"].x, noise), dim=-1
                )
            noise = torch.rand(
                (batch["track_conditions"].x.shape[0], self.diffuser.L_track),
                device=batch["track_conditions"].x.device,
                dtype=batch["track_conditions"].x.dtype,
            )
            batch["track_conditions"].x = torch.cat(
                (batch["track_conditions"].x, noise), dim=-1
            )

        CFG = False
        # CFG = True
        # scale = 1.25  # CFG guidance weight
        scale = 1.5  # CFG guidance weight
                
        for t in reversed(range(noise_scheduler.config.num_train_timesteps)):

            timesteps = torch.full((batch_size,), t, device=device, dtype=torch.long)

            batch["mother"].x = latent["mother"]
            batch["track"].x = latent["track"]
            if intermediate_present:
                batch["intermediate"].x = latent["intermediate"]

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

        if self.eGAN:
            self.generator.eval()

            batch["mother"].x = latent["mother"]
            batch["track"].x = latent["track"]
            if intermediate_present:
                batch["intermediate"].x = latent["intermediate"]

            # now apply epsilon...

            # renoise conditions
            noise = torch.rand(
                (batch["mother_conditions"].x.shape[0], 5),
                device=batch["mother_conditions"].x.device,
                dtype=batch["mother_conditions"].x.dtype,
            )
            batch["mother_conditions"].x[:, -5:] = noise
            if intermediate_present:
                noise = torch.rand(
                    (batch["intermediate_conditions"].x.shape[0], 3),
                    device=batch["intermediate_conditions"].x.device,
                    dtype=batch["intermediate_conditions"].x.dtype,
                )
                batch["intermediate_conditions"].x[:, -3:] = noise
            noise = torch.rand(
                (batch["track_conditions"].x.shape[0], 2),
                device=batch["track_conditions"].x.device,
                dtype=batch["track_conditions"].x.dtype,
            )
            batch["track_conditions"].x[:, -2:] = noise

            # print(batch["mother_conditions"].x[:-5])
            # print(batch["mother"].x[:-5])

            epsilon = self.generator(
                batch=batch,
            )[0]

            for node_type in epsilon:
                if epsilon[node_type].ndim == 1:
                    epsilon[node_type] = epsilon[node_type].unsqueeze(
                        -1
                    )  # Or reshape accordingly

            latent["mother"] = batch["mother"].x + epsilon["mother"] / 10.0
            if intermediate_present:
                latent["intermediate"] = (
                    batch["intermediate"].x + epsilon["intermediate"] / 10.0
                )
            latent["track"] = batch["track"].x + epsilon["track"] / 10.0

            # latent["mother"] = batch["mother"].x
            # if intermediate_present:
            #     latent["intermediate"] = batch["intermediate"].x
            # latent["track"] = batch["track"].x

            # # print(epsilon["mother"][:7])
            # print(batch["mother"].x[:7])
            # print(epsilon["mother"][:7]/10.)

            # latent["mother"] = epsilon["mother"]/10.
            # if intermediate_present:
            #     latent["intermediate"] = epsilon["intermediate"]/10.
            # latent["track"] = epsilon["track"]/10.

        if intermediate_present:
            return latent["mother"], latent["intermediate"], latent["track"]
        else:
            return latent["mother"], None, latent["track"]

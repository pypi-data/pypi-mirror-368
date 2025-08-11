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
    conditions,
    infeatures,
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
    ):
        super(HeteroGenerator, self).__init__()

        dropout_rate = 0.2
        self.dropout = nn.Dropout(p=dropout_rate)

        self.use_layernorm = False
        self.use_dropout = False

        # Conditions
        C_mother = mother_conditions_dims
        C_intermediate = intermediate_conditions_dims
        C_track = track_conditions_dims
        if conditonless:
            C_mother = 0
            C_intermediate = 0
            C_track = 0
        self.conditonless = conditonless

        # Targets
        T_mother = mother_targets_dims
        T_intermediate = intermediate_targets_dims
        T_track = track_targets_dims

        # Latents
        L_mother = mother_latent_dims
        L_intermediate = intermediate_latent_dims
        L_track = track_latent_dims

        ### ### ### ### ###

        self.aggrs = ["mean", "sum", "max"]
        # self.aggrs = ['sum']

        self.initial_selfloop_layers = HeteroConv(
            {
                ("track", "self", "track"): GATConv(L_track + C_track, hidden_channels),
                ("intermediate", "self", "intermediate"): GATConv(
                    L_intermediate + C_intermediate, hidden_channels
                ),
                ("mother", "self", "mother"): GATConv(
                    L_mother + C_mother, hidden_channels
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

        self.N_layers = 3

        for idx in range(self.N_layers):
            repeated_backwards_layer_intermediate = NoAggGAT(
                hidden_channels, hidden_channels
            )
            repeated_backwards_layer_mother = NoAggGAT(hidden_channels, hidden_channels)
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
                    ("mother", "down", "intermediate"): repeated_backwards_layer_mother,
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
            # layer["mother_attention"] = nn.Linear(
            #     hidden_channels * len(self.aggrs), hidden_channels * len(self.aggrs)
            # )
            # layer["mother_aggr"] = nn.Linear(
            #     hidden_channels * len(self.aggrs), hidden_channels
            # )
            layer["mother_attention"] = layer["intermediate_attention"]
            layer["mother_aggr"] = layer["intermediate_aggr"]

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

            repeated_forwards_layer_track = NoAggGAT(hidden_channels, hidden_channels)
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
            # layer["mother_attention"] = nn.Linear(
            #     hidden_channels * len(self.aggrs), hidden_channels * len(self.aggrs)
            # )
            # layer["mother_aggr"] = nn.Linear(
            #     hidden_channels * len(self.aggrs), hidden_channels
            # )

            layer["mother_attention"] = layer["intermediate_attention"]
            layer["mother_aggr"] = layer["intermediate_aggr"]

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
                ("track", "self", "track"): GATConv(hidden_channels, T_track),
                ("intermediate", "self", "intermediate"): GATConv(
                    hidden_channels, T_intermediate
                ),
                ("mother", "self", "mother"): GATConv(hidden_channels, T_mother),
            },
            aggr="sum",
        )  # no pooling, nodes only connected to themselves

    def forward(
        self,
        mother_latent: Tensor,
        track_latent: Tensor,
        intermediate_latent: Tensor,
        mother_conditions: Dict,
        track_conditions: Dict,
        intermediate_conditions: Dict,
        edge_index_tensors: List[Tensor],
        batch,  # contains all edge_index information
        offline_query_mode=False,
    ) -> Tuple[Tensor, Tensor, Tensor]:
        # print('\n\n\n pass')
        # # print(edge_index_tensors)
        # print(batch)
        # print(batch['mother', 'down', 'track'])
        # print(batch['mother'])
        # print(mother_latent.shape)
        # print(mother_conditions.x.shape)

        conditions = {
            "track": track_conditions.x,
            # "intermediate": intermediate_conditions.x,
            "mother": mother_conditions.x,
        }
        if intermediate_conditions:
            conditions["intermediate"] = intermediate_conditions.x

        latent = {
            "track": track_latent,
            # "intermediate": intermediate_latent,
            "mother": mother_latent,
        }
        if intermediate_conditions:
            latent["intermediate"] = intermediate_latent

        edge_index_dict_self_loop = {
            ("track", "self", "track"): batch["track", "self", "track"]["edge_index"],
            ("mother", "self", "mother"): batch["mother", "self", "mother"][
                "edge_index"
            ],
        }
        if intermediate_conditions:
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

        # print(edge_index_dict)

        if offline_query_mode:
            for i in latent:
                latent[i] = latent[i].to("cuda:5")
            for i in conditions:
                conditions[i] = conditions[i].to("cuda:5")
            for i in edge_index_dict_self_loop:
                edge_index_dict_self_loop[i] = edge_index_dict_self_loop[i].to("cuda:5")
            for edge_index_dict in edge_index_dicts_backward:
                for i in edge_index_dict:
                    edge_index_dict[i] = edge_index_dict[i].to("cuda:5")
            for edge_index_dict in edge_index_dicts_forward:
                for i in edge_index_dict:
                    edge_index_dict[i] = edge_index_dict[i].to("cuda:5")

        x = latent.copy()

        # print_heterogenous_representation(x)

        if not self.conditonless:
            for node_type in x:
                if x[node_type] is not None:  # None if latent dims == 0
                    x[node_type] = torch.cat(
                        (x[node_type], conditions[node_type]), dim=1
                    )
                else:
                    x[node_type] = conditions[node_type]

        x = self.initial_selfloop_layers(x, edge_index_dict_self_loop)

        # print_heterogenous_representation(x)

        for node_type in x:
            x[node_type] = x[node_type].squeeze()
            if x[node_type].dim() == 1:
                x[node_type] = x[node_type].unsqueeze(0)
            if self.use_layernorm:
                x[node_type] = self.initial_selfloop_layer_norm[node_type](x[node_type])

        if self.use_dropout:
            x = {k: self.dropout(v) for k, v in x.items()}

        for layer_idx in range(self.N_layers):
            for edge_index_dict in edge_index_dicts_backward:
                x = heterogenous_layer_wrapper_w_cat_and_self_loop(
                    self.propagation_layers_backward[layer_idx],
                    self.aggr_attention_layers_backward[layer_idx],
                    self.selfloop_layers_backward[layer_idx],
                    x,
                    edge_index_dict,
                    conditions,
                    latent,
                    self.aggrs,
                )
            if self.use_layernorm:
                for node_type in x:
                    x[node_type] = self.backwards_layer_norm[layer_idx][node_type](
                        x[node_type]
                    )

            if self.use_dropout:
                x = {k: self.dropout(v) for k, v in x.items()}

            for edge_index_dict in edge_index_dicts_forward:
                x = heterogenous_layer_wrapper_w_cat_and_self_loop(
                    self.propagation_layers_forward[layer_idx],
                    self.aggr_attention_layers_forward[layer_idx],
                    self.selfloop_layers_forward[layer_idx],
                    x,
                    edge_index_dict,
                    conditions,
                    latent,
                    self.aggrs,
                )
            if self.use_layernorm:
                for node_type in x:
                    x[node_type] = self.forwards_layer_norm[layer_idx][node_type](
                        x[node_type]
                    )

            if self.use_dropout:
                x = {k: self.dropout(v) for k, v in x.items()}

        x = self.output_layer(x, edge_index_dict_self_loop)

        for node_type in x:
            # x[node_type] = x[node_type].squeeze()
            # if x[node_type].dim() == 1:
            #     x[node_type] = x[node_type].unsqueeze(0)
            # print(x[node_type].shape)
            unsqueeze = False
            if x[node_type].shape[0] == 1:
                unsqueeze = True  # batch size is 1
            x[node_type] = torch.tanh(x[node_type].squeeze())
            if unsqueeze:
                x[node_type] = x[node_type].unsqueeze(0)
            # print(x[node_type].shape)

        # print_heterogenous_representation(x)

        if intermediate_conditions:
            return x["mother"], x["intermediate"], x["track"]
        else:
            return x["mother"], None, x["track"]


class HeteroDiscriminator(pl.LightningModule):
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
    ):
        super(HeteroDiscriminator, self).__init__()

        dropout_rate = 0.2

        self.dropout = nn.Dropout(p=dropout_rate)

        self.use_layernorm = False
        self.use_dropout = False

        self.use_spectral_norm = True
        spec_norm = torch.nn.utils.spectral_norm

        def apply_spec_norm(layer):
            """Apply spectral normalization if enabled."""
            return spec_norm(layer) if self.use_spectral_norm else layer

        # Conditions
        C_mother = mother_conditions_dims
        C_intermediate = intermediate_conditions_dims
        C_track = track_conditions_dims

        if conditonless:
            C_mother = 0
            C_intermediate = 0
            C_track = 0
        self.conditonless = conditonless

        # Targets
        T_mother = mother_targets_dims
        T_intermediate = intermediate_targets_dims
        T_track = track_targets_dims

        # Latents
        L_mother = mother_latent_dims
        L_intermediate = intermediate_latent_dims
        L_track = track_latent_dims

        self.L_mother = L_mother
        self.L_intermediate = L_intermediate
        self.L_track = L_track

        ### ### ### ### ###

        self.aggrs = ["mean", "sum", "max"]
        # self.aggrs = ["sum"]

        self.initial_selfloop_layers = HeteroConv(
            # self.initial_selfloop_layers = myHeteroConv(
            {
                ("track", "self", "track"): GATConv(T_track + C_track, hidden_channels),
                ("intermediate", "self", "intermediate"): GATConv(
                    T_intermediate + C_intermediate, hidden_channels
                ),
                ("mother", "self", "mother"): GATConv(
                    T_mother + C_mother, hidden_channels
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

        self.selfloop_layers_forward = nn.ModuleList()
        self.propagation_layers_forward = nn.ModuleList()
        self.aggr_attention_layers_forward = nn.ModuleList()
        self.selfloop_layers_backward = nn.ModuleList()
        self.propagation_layers_backward = nn.ModuleList()
        self.aggr_attention_layers_backward = nn.ModuleList()

        if self.use_layernorm:
            self.backwards_layer_norm = nn.ModuleList()
            self.forwards_layer_norm = nn.ModuleList()

        self.N_layers = 3

        for idx in range(self.N_layers):
            # repeated_forwards_layer_track = NoAggGAT(hidden_channels, hidden_channels, spec_norm=self.use_spectral_norm)
            # repeated_forwards_layer_intermediate = NoAggGAT(hidden_channels, hidden_channels, spec_norm=self.use_spectral_norm)
            # layer = myHeteroConv(
            #     {
            #         ("track", "up", "intermediate"): repeated_forwards_layer_track,
            #         ("intermediate", "up", "intermediate"): repeated_forwards_layer_intermediate,
            #         ("track", "up", "mother"): repeated_forwards_layer_track,
            #         ("intermediate", "up", "mother"): repeated_forwards_layer_intermediate,
            #     },
            #     aggr=self.aggrs,
            # )  # this pooling only occurs across multiple edge types, else the pooling is done within GATConv
            # self.propagation_layers_forward.append(layer)
            repeated_backwards_layer_intermediate = NoAggGAT(
                hidden_channels, hidden_channels
            )
            repeated_backwards_layer_mother = NoAggGAT(hidden_channels, hidden_channels)
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
                    ("mother", "down", "intermediate"): repeated_backwards_layer_mother,
                },
                aggr=self.aggrs,
            )
            self.propagation_layers_backward.append(layer)

            layer = {}
            layer["intermediate_attention"] = apply_spec_norm(
                nn.Linear(
                    hidden_channels * len(self.aggrs),
                    hidden_channels * len(self.aggrs),
                )
            )
            layer["intermediate_aggr"] = apply_spec_norm(
                nn.Linear(hidden_channels * len(self.aggrs), hidden_channels)
            )

            # layer["mother_attention"] = apply_spec_norm(
            #     nn.Linear(
            #         hidden_channels * len(self.aggrs),
            #         hidden_channels * len(self.aggrs),
            #     )
            # )
            # layer["mother_aggr"] = apply_spec_norm(
            #     nn.Linear(hidden_channels * len(self.aggrs), hidden_channels)
            # )
            layer["mother_attention"] = layer["intermediate_attention"]
            layer["mother_aggr"] = layer["intermediate_aggr"]

            layer = nn.ModuleDict(layer)
            self.aggr_attention_layers_forward.append(
                layer
            )  # no pooling, nodes only connected to themselves

            layer = {}
            layer["track"] = apply_spec_norm(
                nn.Linear(hidden_channels * 2, hidden_channels)
            )
            layer["intermediate"] = apply_spec_norm(
                nn.Linear(hidden_channels * 2, hidden_channels)
            )
            layer["mother"] = apply_spec_norm(
                nn.Linear(hidden_channels * 2, hidden_channels)
            )
            layer = nn.ModuleDict(layer)
            self.selfloop_layers_forward.append(layer)

            # repeated_backwards_layer_intermediate = NoAggGAT(hidden_channels, hidden_channels, spec_norm=self.use_spectral_norm)
            # repeated_backwards_layer_mother = NoAggGAT(hidden_channels, hidden_channels, spec_norm=self.use_spectral_norm)
            # layer = myHeteroConv(
            #     {
            #         ("intermediate", "down", "track"): repeated_backwards_layer_intermediate,
            #         ("intermediate", "down", "intermediate"): repeated_backwards_layer_intermediate,
            #         ("mother", "down", "track"): repeated_backwards_layer_mother,
            #         ("mother", "down", "intermediate"): repeated_backwards_layer_mother,
            #     },
            #     aggr=self.aggrs,
            # )
            # self.propagation_layers_backward.append(layer)
            repeated_forwards_layer_track = NoAggGAT(hidden_channels, hidden_channels)
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
            layer["intermediate_attention"] = apply_spec_norm(
                nn.Linear(
                    hidden_channels * len(self.aggrs),
                    hidden_channels * len(self.aggrs),
                )
            )
            layer["intermediate_aggr"] = apply_spec_norm(
                nn.Linear(hidden_channels * len(self.aggrs), hidden_channels)
            )

            layer["mother_attention"] = layer["intermediate_attention"]
            layer["mother_aggr"] = layer["intermediate_aggr"]
            # layer["mother_attention"] = apply_spec_norm(
            #     nn.Linear(
            #         hidden_channels * len(self.aggrs),
            #         hidden_channels * len(self.aggrs),
            #     )
            # )
            # layer["mother_aggr"] = apply_spec_norm(
            #     nn.Linear(hidden_channels * len(self.aggrs), hidden_channels)
            # )

            layer = nn.ModuleDict(layer)
            self.aggr_attention_layers_backward.append(
                layer
            )  # no pooling, nodes only connected to themselves

            layer = {}
            layer["track"] = apply_spec_norm(
                nn.Linear(hidden_channels * 2, hidden_channels)
            )
            layer["intermediate"] = apply_spec_norm(
                nn.Linear(hidden_channels * 2, hidden_channels)
            )
            layer["mother"] = apply_spec_norm(
                nn.Linear(hidden_channels * 2, hidden_channels)
            )
            layer = nn.ModuleDict(layer)
            self.selfloop_layers_backward.append(layer)

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

        self.attention_track = nn.Linear(hidden_channels, hidden_channels)
        self.attention_intermediate = nn.Linear(hidden_channels, hidden_channels)
        self.attention_mother = nn.Linear(hidden_channels, hidden_channels)

        self.use_mbd = True
        # self.use_mbd = False

        if self.use_mbd:
            mbd_dims = 10

            # mbd_layers = {}
            # mbd_layers["track"] = MinibatchDiscrimination(
            #     T_track, mbd_dims, 25, initalisation=0.1
            # )
            # # mbd_layers["intermediate"] = MinibatchDiscrimination(T_intermediate, mbd_dims, intermediate_features=25, initalisation=0.05)
            # # mbd_layers["mother"] = MinibatchDiscrimination(T_mother, mbd_dims, intermediate_features=25, initalisation=0.05)
            # self.mbd_layers = nn.ModuleDict(mbd_layers)

            self.mbd_layer = MinibatchDiscrimination(
                hidden_channels, mbd_dims, 10, initalisation=0.025
            )

            # self.mbd_track_attention_layer = nn.Linear(mbd_dims, mbd_dims)

            self.output_layer = apply_spec_norm(
                # nn.Linear(hidden_channels + mbd_dims + mbd_dims, 1)
                nn.Linear(hidden_channels + mbd_dims, 1)
            )
        else:
            self.output_layer = apply_spec_norm(nn.Linear(hidden_channels, 1))

    def forward(
        self,
        mother_targets: Dict,
        track_targets: Dict,
        intermediate_targets: Dict,
        mother_conditions: Dict,
        track_conditions: Dict,
        intermediate_conditions: Dict,
        edge_index_tensors: List[Tensor],
        batch,  # contains all edge_index information
    ) -> Tuple[Tensor, Tensor, Tensor, Tensor, Tensor, Tensor]:
        # device = track_conditions.x.device

        batch_size = int(torch.amax(mother_conditions.batch) + 1)

        conditions = {
            "track": track_conditions.x,
            "mother": mother_conditions.x,
        }
        if intermediate_conditions:
            conditions["intermediate"] = intermediate_conditions.x

        targets = {
            "track": track_targets.x,
            "mother": mother_targets.x,
        }
        if intermediate_conditions:
            targets["intermediate"] = intermediate_targets.x

        edge_index_dict_self_loop = {
            ("track", "self", "track"): batch["track", "self", "track"]["edge_index"],
            ("mother", "self", "mother"): batch["mother", "self", "mother"][
                "edge_index"
            ],
        }
        if intermediate_conditions:
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
                # if edge_type in batch:
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
                # if edge_type in batch:
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

        x = targets.copy()

        if not self.conditonless:
            for node_type in x:
                if len(x[node_type].shape) == 1:
                    x[node_type] = torch.unsqueeze(x[node_type], 1)
                x[node_type] = torch.cat((x[node_type], conditions[node_type]), dim=1)

        x = self.initial_selfloop_layers(x, edge_index_dict_self_loop)
        if self.use_layernorm:
            for node_type in x:
                x[node_type] = self.initial_selfloop_layer_norm[node_type](x[node_type])
        if self.use_dropout:
            x = {k: self.dropout(v) for k, v in x.items()}

        for layer_idx in range(self.N_layers):
            # for edge_index_dict in edge_index_dicts_forward:
            for edge_index_dict in edge_index_dicts_backward:
                x = heterogenous_layer_wrapper_w_cat_and_self_loop(
                    self.propagation_layers_forward[layer_idx],
                    self.aggr_attention_layers_forward[layer_idx],
                    self.selfloop_layers_forward[layer_idx],
                    x,
                    edge_index_dict,
                    conditions,
                    targets,
                    self.aggrs,
                )

            if self.use_layernorm:
                for node_type in x:
                    x[node_type] = self.forwards_layer_norm[layer_idx][node_type](
                        x[node_type]
                    )

            if self.use_dropout:
                x = {k: self.dropout(v) for k, v in x.items()}

            # for edge_index_dict in edge_index_dicts_backward:
            for edge_index_dict in edge_index_dicts_forward:
                x = heterogenous_layer_wrapper_w_cat_and_self_loop(
                    self.propagation_layers_backward[layer_idx],
                    self.aggr_attention_layers_backward[layer_idx],
                    self.selfloop_layers_backward[layer_idx],
                    x,
                    edge_index_dict,
                    conditions,
                    targets,
                    self.aggrs,
                )

            if self.use_layernorm:
                for node_type in x:
                    x[node_type] = self.backwards_layer_norm[layer_idx][node_type](
                        x[node_type]
                    )

            if self.use_dropout:
                x = {k: self.dropout(v) for k, v in x.items()}

        x["track"] = global_mean_pool(
            x["track"], batch["track"].batch.to(x["track"].device)
        )
        if intermediate_conditions:
            x["intermediate"] = global_mean_pool(
                x["intermediate"],
                batch["intermediate"].batch.to(x["intermediate"].device),
            )
        pooled = x["mother"].unsqueeze(1)

        # # Per-type attention gating (element-wise sigmoid) - this didnt help in first test
        # x["track"] = torch.sigmoid(self.attention_track(x["track"])) * x["track"]
        # if intermediate_conditions:
        #     x["intermediate"] = torch.sigmoid(self.attention_intermediate(x["intermediate"])) * x["intermediate"]
        # x["mother"] = torch.sigmoid(self.attention_mother(x["mother"])) * x["mother"]

        for node_type in x:
            if node_type != "mother":
                pooled = torch.cat((pooled, x[node_type].unsqueeze(1)), dim=1)
        pooled = torch.mean(pooled, dim=1)

        if self.use_mbd:
            # mbd_on_targets = {}
            # for node_type in ["track"]:

            #     x_reshape = torch.reshape(
            #         targets[node_type], (batch_size, -1, targets[node_type].shape[-1])
            #     )

            #     x_0 = self.mbd_layers[node_type](x_reshape[:, 0, :]).unsqueeze(0)
            #     x_1 = self.mbd_layers[node_type](x_reshape[:, 1, :]).unsqueeze(0)
            #     x_2 = self.mbd_layers[node_type](x_reshape[:, 2, :]).unsqueeze(0)

            #     x_0 = torch.sigmoid(self.mbd_track_attention_layer(x_0))
            #     x_1 = torch.sigmoid(self.mbd_track_attention_layer(x_1))
            #     x_2 = torch.sigmoid(self.mbd_track_attention_layer(x_2))

            #     mbd_on_targets[node_type] = torch.mean(
            #         torch.cat((x_0, x_1, x_2), dim=0), dim=0
            #     )
            #     # mbd_on_targets[node_type] = torch.amax(torch.cat((x_0,x_1,x_2),dim=0),dim=0)

            mbd_output = self.mbd_layer(pooled)
            # pooled_cat = torch.cat((pooled, mbd_output, mbd_on_targets["track"]), axis=1)
            pooled_cat = torch.cat((pooled, mbd_output), axis=1)

            disc_out = torch.sigmoid(self.output_layer(pooled_cat))
        else:
            disc_out = torch.sigmoid(self.output_layer(pooled))

        return disc_out


class gGAN(nn.Module):
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
        silent=False,
    ):
        super(gGAN, self).__init__()

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

        self.generator = HeteroGenerator(
            mother_targets_dims,
            intermediate_targets_dims,
            track_targets_dims,
            mother_conditions_dims,
            intermediate_conditions_dims,
            track_conditions_dims,
            # int(hidden_channels*1.5),
            # int(hidden_channels*0.5),
            hidden_channels,
            mother_latent_dims,
            track_latent_dims,
            intermediate_latent_dims,
            conditonless=False,
        )

        self.discriminator = HeteroDiscriminator(
            mother_targets_dims,
            intermediate_targets_dims,
            track_targets_dims,
            mother_conditions_dims,
            intermediate_conditions_dims,
            track_conditions_dims,
            # int(hidden_channels*0.25),
            hidden_channels,
            mother_latent_dims,
            track_latent_dims,
            intermediate_latent_dims,
            conditonless=False,
        )

    def inference(self, batch_size, batch, offline_query_mode=False):
        track_latent = torch.rand(
            (batch["track"].x.shape[0], self.track_latent_dims)
        ).to(batch["track"].x.device)

        try:
            batch["intermediate"].x
            intermediate_present = True
        except Exception:
            intermediate_present = False

        if intermediate_present:
            intermediate_latent = torch.rand(
                (batch["intermediate"].x.shape[0], self.intermediate_latent_dims)
            ).to(batch["intermediate"].x.device)
        mother_latent = torch.rand(
            (batch["mother"].x.shape[0], self.mother_latent_dims)
        ).to(batch["mother"].x.device)

        if intermediate_present:
            mother, intermediate, track = self.generator(
                mother_latent,
                track_latent,
                intermediate_latent,
                batch["mother_conditions"],
                batch["track_conditions"],
                batch["intermediate_conditions"],
                batch["edge_index_tensors"],
                batch,
                offline_query_mode=offline_query_mode,
            )
        else:
            mother, intermediate, track = self.generator(
                mother_latent,
                track_latent,
                None,
                batch["mother_conditions"],
                batch["track_conditions"],
                None,
                batch["edge_index_tensors"],
                batch,
                offline_query_mode=offline_query_mode,
            )

        return mother, intermediate, track

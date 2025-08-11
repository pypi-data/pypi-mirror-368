import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import global_mean_pool
from torch_geometric.nn import GATConv, HeteroConv
from torch import Tensor
from typing import Tuple, Optional, List, Dict
import pytorch_lightning as pl

from collections import defaultdict


import warnings


from torch_geometric.nn.conv import MessagePassing
from torch_geometric.nn.module_dict import ModuleDict
from torch_geometric.typing import EdgeType, NodeType
from torch_geometric.utils.hetero import check_add_self_loops
import itertools


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


def squeeze_heterogenous_representation(rep):
    for key in rep:
        rep[key] = rep[key].squeeze()
        if rep[key].dim() == 2:
            rep[key] = torch.unsqueeze(
                rep[key], dim=1
            )  # squeezed 1,1 to nothing, need to go back to 1,
    return rep


def aggr_attention_at_node(rep, layer, aggrs):
    for key in rep:
        # Aggregate features across different methods (sum, mean, max)
        for idx, aggr in enumerate(aggrs):
            if idx == 0:
                if aggr == "sum":
                    total_aggre = torch.sum(rep[key], dim=1)
                if aggr == "mean":
                    total_aggre = torch.sum(rep[key], dim=1) / rep[key].shape[1]
                if aggr == "max":
                    total_aggre = torch.amax(rep[key], dim=1)
            else:
                if aggr == "sum":
                    total_aggre = torch.cat(
                        (total_aggre, torch.sum(rep[key], dim=1)), dim=1
                    )
                if aggr == "mean":
                    total_aggre = torch.cat(
                        (total_aggre, torch.sum(rep[key], dim=1) / rep[key].shape[1]),
                        dim=1,
                    )
                if aggr == "max":
                    total_aggre = torch.cat(
                        (total_aggre, torch.amax(rep[key], dim=1)), dim=1
                    )

        rep[key] = total_aggre  # No in-place modification

    for key in rep:
        atten = torch.sigmoid(layer[f"{key}_attention"](rep[key]))

        # Instead of in-place multiplication, create a new tensor
        rep[key] = rep[key] * atten  # Avoid `rep[key] *= atten`

        rep[key] = layer[f"{key}_aggr"](rep[key])  # Pass through aggregation layer

    return rep


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

    outputs = layer(x, edge_index)

    outputs = aggr_attention_at_node(outputs, aggr_attention, aggrs)

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
        track_targets_dims,
        track_conditions_dims,
        hidden_channels,
        track_latent_dims,
        edge_conditions_dims,
        conditonless=False,
    ):
        super(HeteroGenerator, self).__init__()

        dropout_rate = 0.2
        self.dropout = nn.Dropout(p=dropout_rate)

        # Conditions
        C_track = track_conditions_dims
        if conditonless:
            C_track = 0
        self.conditonless = conditonless

        # Targets
        T_track = track_targets_dims

        # Latents
        L_track = track_latent_dims

        ### ### ### ### ###

        self.particle_types = ["11", "13", "211", "321", "2212"]
        self.edge_types = list(itertools.product(self.particle_types, repeat=2))

        self.communication_dims = 100

        self.selfloop_layers = nn.ModuleList()
        self.communication_layers = nn.ModuleList()

        # self.N_layers = 3

        # for N_layer in range(self.N_layers):

        #     layer = {}
        #     for particle_type in particle_types:
        #         if N_layer == 0:
        #             layer[particle_type] = nn.Linear(L_track + C_track, hidden_channels)
        #         else:
        #             layer[particle_type] = nn.Linear(hidden_channels, hidden_channels)
        #     layer = nn.ModuleDict(layer)
        #     self.selfloop_layers.append(layer)

        #     layer_dict = {}
        #     for edge_type in self.edge_types:
        #         layer_dict[edge_type[0], "to", edge_type[1]] = GATConv(
        #             self.communication_dims,
        #             self.communication_dims,
        #             add_self_loops=False,
        #             edge_dim=edge_conditions_dims,
        #         )
        #     layer = HeteroConv(
        #         layer_dict,
        #         aggr="max",
        #     )
        #     self.communication_layers.append(layer)

        # layer = {}
        # for particle_type in particle_types:
        #     layer[particle_type] = nn.Linear(hidden_channels, hidden_channels)
        # layer = nn.ModuleDict(layer)
        # self.selfloop_layers.append(layer)

        # layer = {}
        # for particle_type in particle_types:
        #     layer[particle_type] = nn.Linear(hidden_channels, T_track)
        # layer = nn.ModuleDict(layer)
        # self.selfloop_layers.append(layer)

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
                    layer[particle_type] = nn.Linear(L_track + C_track, hidden_channels)
                else:
                    layer[particle_type] = nn.Linear(hidden_channels, hidden_channels)
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
            layer[particle_type] = nn.Linear(hidden_channels, hidden_channels)
        layer = nn.ModuleDict(layer)
        self.selfloop_layers.append(layer)

        layer = {}
        for particle_type in self.particle_types:
            layer[particle_type] = nn.Linear(hidden_channels, T_track)
        layer = nn.ModuleDict(layer)
        self.selfloop_layers.append(layer)
        self.T_track = T_track

    def forward(
        self,
        track_latent: Tensor,
        batch,  # contains all edge_index information
        offline_query_mode=False,
    ) -> Tuple[Tensor, Tensor, Tensor]:
        x = {}
        for track_type in track_latent:
            x[track_type] = torch.cat(
                (batch[f"{track_type}_conditions"].x, track_latent[track_type]), dim=1
            )

        edge_index_dict = {}
        edge_attr_dict = {}
        for edge_type in self.edge_types:
            edge_index_dict[edge_type[0], "to", edge_type[1]] = batch[
                edge_type[0], "to", edge_type[1]
            ].edge_index  # ["edge_index"]
            edge_attr_dict[edge_type[0], "to", edge_type[1]] = batch[
                edge_type[0], "to", edge_type[1]
            ].edge_attr  # ["edge_attr"]

        # x_comms = {}

        # for N_layer in range(self.N_layers):

        #     for track_type in x:
        #         x[track_type] = F.leaky_relu(
        #             self.selfloop_layers[N_layer][track_type](x[track_type])
        #         )
        #         x_comms[track_type] = x[track_type][:, : self.communication_dims]
        #     x_comms = self.communication_layers[N_layer](x_comms, edge_index_dict, edge_attr_dict)
        #     for track_type in x_comms:
        #         x_comms[track_type] = F.leaky_relu(x_comms[track_type])
        #     for track_type in x:
        #         x[track_type] = x[track_type].clone()
        #         x[track_type][:, : self.communication_dims] = x_comms[track_type]

        # for track_type in x:
        #     x[track_type] = F.leaky_relu(
        #         self.selfloop_layers[-2][track_type](x[track_type])
        #     )

        # for track_type in x:
        #     x[track_type] = torch.tanh(
        #         self.selfloop_layers[-1][track_type](x[track_type])
        #     )

        # return x

        x_comms = {}

        for N_layer in range(self.N_layers):
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

        # print_heterogenous_representation(x)

        for track_type in x:
            if x[track_type].shape[0] > 0:
                x[track_type] = self.selfloop_layers[-1][track_type](x[track_type])
            else:
                x[track_type] = torch.empty((0, self.T_track)).to(x[track_type].device)
        # print_heterogenous_representation(x)
        # quit()
        return x


class HeteroDiscriminator(pl.LightningModule):
    def __init__(
        self,
        track_targets_dims,
        track_conditions_dims,
        hidden_channels,
        track_latent_dims,
        edge_conditions_dims,
        conditonless=False,
        add_MBD=False,
        add_physics_dims=False,
    ):
        super(HeteroDiscriminator, self).__init__()

        dropout_rate = 0.2
        self.dropout = nn.Dropout(p=dropout_rate)

        self.use_spectral_norm = False
        spec_norm = torch.nn.utils.spectral_norm

        def apply_spec_norm(layer):
            """Apply spectral normalization if enabled."""
            return spec_norm(layer) if self.use_spectral_norm else layer

        # Conditions
        C_track = track_conditions_dims

        if conditonless:
            C_track = 0
        self.conditonless = conditonless

        # Targets
        T_track = track_targets_dims
        if add_physics_dims:
            T_track += 1

        # Latents
        L_track = track_latent_dims

        self.L_track = L_track

        ### ### ### ### ###

        extra_dims = 0
        # extra_dims = 4

        self.particle_types = ["11", "13", "211", "321", "2212"]
        self.edge_types = list(itertools.product(self.particle_types, repeat=2))

        # self.selfloop_layers = nn.ModuleList()
        # self.communication_layers = nn.ModuleList()

        # self.communication_dims = 100

        # # self.N_layers = 3
        # self.N_layers = 2

        # for N_layer in range(self.N_layers):

        #     layer = {}
        #     for particle_type in particle_types:
        #         if N_layer == 0:
        #             layer[particle_type] = nn.Linear(
        #                 T_track + C_track + extra_dims, hidden_channels
        #             )
        #         else:
        #             layer[particle_type] = nn.Linear(
        #                 hidden_channels, hidden_channels
        #             )
        #     layer = nn.ModuleDict(layer)
        #     self.selfloop_layers.append(layer)

        #     layer_dict = {}
        #     for edge_type in self.edge_types:
        #         layer_dict[edge_type[0], "to", edge_type[1]] = GATConv(
        #             self.communication_dims,
        #             self.communication_dims,
        #             add_self_loops=False,
        #             edge_dim=edge_conditions_dims,
        #         )
        #     layer = HeteroConv(
        #         layer_dict,
        #         aggr="max",
        #     )
        #     self.communication_layers.append(layer)

        # # layer = {}
        # # for particle_type in particle_types:
        # #     layer[particle_type] = nn.Linear(hidden_channels, hidden_channels)
        # # layer = nn.ModuleDict(layer)
        # # self.selfloop_layers.append(layer)

        # # layer_dict = {}
        # # for edge_type in self.edge_types:
        # #     layer_dict[edge_type[0], "to", edge_type[1]] = GATConv(
        # #         self.communication_dims,
        # #         self.communication_dims,
        # #         add_self_loops=False,
        # #         edge_dim=edge_conditions_dims,
        # #     )
        # # layer = HeteroConv(
        # #     layer_dict,
        # #     aggr="max",
        # # )
        # # self.communication_layers.append(layer)

        # layer = {}
        # for particle_type in particle_types:
        #     layer[particle_type] = nn.Linear(hidden_channels, hidden_channels)
        # layer = nn.ModuleDict(layer)
        # self.selfloop_layers.append(layer)

        # self.add_MBD = add_MBD

        # if self.add_MBD:
        #     self.mbd_dims = 5
        #     mbd_layers = {}
        #     for particle_type in particle_types:
        #         mbd_layers[particle_type] = MinibatchDiscrimination(
        #             hidden_channels, self.mbd_dims, 5, initalisation=0.001
        #         )
        #     self.mbd_layer = nn.ModuleDict(mbd_layers)

        # self.output_layer = nn.Linear(hidden_channels, 1)

        # layer = {}
        # for particle_type in particle_types:
        #     if self.add_MBD:
        #         layer[particle_type] = nn.Linear(hidden_channels+self.mbd_dims, hidden_channels)
        #     else:
        #         layer[particle_type] = nn.Linear(hidden_channels, hidden_channels)
        # layer = nn.ModuleDict(layer)
        # self.selfloop_layers.append(layer)

        #### new
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
                        T_track + C_track + extra_dims, hidden_channels
                    )
                else:
                    layer[particle_type] = nn.Linear(hidden_channels, hidden_channels)
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
            layer[particle_type] = nn.Linear(hidden_channels, hidden_channels)
        layer = nn.ModuleDict(layer)
        self.selfloop_layers.append(layer)

        self.add_MBD = add_MBD

        if self.add_MBD:
            self.mbd_dims = 5
            mbd_layers = {}
            for particle_type in self.particle_types:
                mbd_layers[particle_type] = MinibatchDiscrimination(
                    hidden_channels, self.mbd_dims, 5, initalisation=0.001
                )
            self.mbd_layer = nn.ModuleDict(mbd_layers)

        self.output_layer = nn.Linear(hidden_channels, 1)

        layer = {}
        for particle_type in self.particle_types:
            if self.add_MBD:
                layer[particle_type] = nn.Linear(
                    hidden_channels + self.mbd_dims, hidden_channels
                )
            else:
                layer[particle_type] = nn.Linear(hidden_channels, hidden_channels)
        layer = nn.ModuleDict(layer)
        self.selfloop_layers.append(layer)

    def forward(
        self,
        batch,  # contains all edge_index information
        logits=False,
    ) -> Tuple[Tensor, Tensor, Tensor, Tensor, Tensor, Tensor]:
        # device = track_conditions.x.device

        particle_types = ["11", "13", "211", "321", "2212"]

        x = {}
        for track_type in particle_types:
            x[track_type] = torch.cat(
                (batch[f"{track_type}_conditions"].x, batch[f"{track_type}"].x), dim=1
            ).to(torch.float32)

            # print(batch[f"{track_type}_conditions"].x)
            # print(batch[f"{track_type}"].x)
            # print('a', x[track_type].dtype)

        edge_index_dict = {}
        edge_attr_dict = {}
        for edge_type in self.edge_types:
            edge_index_dict[edge_type[0], "to", edge_type[1]] = batch[
                edge_type[0], "to", edge_type[1]
            ]["edge_index"]
            edge_attr_dict[edge_type[0], "to", edge_type[1]] = batch[
                edge_type[0], "to", edge_type[1]
            ]["edge_attr"]

        # for i in x:
        #     x[i] = x[i].to('cuda:5')
        # for i in edge_index_dict:
        #     edge_index_dict[i] = edge_index_dict[i].to('cuda:5')
        # for i in edge_attr_dict:
        #     edge_attr_dict[i] = edge_attr_dict[i].to('cuda:5')

        x_comms = {}

        for N_layer in range(self.N_layers):
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

        for track_type in x:
            x[track_type] = F.leaky_relu(
                self.selfloop_layers[-2][track_type](x[track_type])
            )

        for track_type in x:
            x[track_type] = F.leaky_relu(
                self.selfloop_layers[-1][track_type](x[track_type])
            )
        # print_heterogenous_representation(x)

        for idx, particle_type in enumerate(particle_types):
            if idx == 0:
                x_prime = x[particle_type]
                x_prime_batch = batch[particle_type].batch
            else:
                x_prime = torch.cat((x_prime, x[particle_type]), dim=0)
                x_prime_batch = torch.cat(
                    (x_prime_batch, batch[particle_type].batch), dim=0
                )

        x = global_mean_pool(x_prime, x_prime_batch.to(x_prime.device))

        if logits:
            return self.output_layer(x)
        else:
            disc_out = torch.sigmoid(self.output_layer(x))

        return disc_out

    # def forward(
    #     self,
    #     batch,  # contains all edge_index information
    # ) -> Tuple[Tensor, Tensor, Tensor, Tensor, Tensor, Tensor]:
    #     # device = track_conditions.x.device

    #     particle_types = ["11", "13", "211", "321", "2212"]

    #     x = {}
    #     for track_type in particle_types:
    #         x[track_type] = torch.cat(
    #             (batch[f"{track_type}_conditions"].x, batch[f"{track_type}"].x), dim=1
    #         ).to(torch.float32)

    #         # print(batch[f"{track_type}_conditions"].x)
    #         # print(batch[f"{track_type}"].x)
    #         # print('a', x[track_type].dtype)

    #     edge_index_dict = {}
    #     edge_attr_dict = {}
    #     for edge_type in self.edge_types:
    #         edge_index_dict[edge_type[0], "to", edge_type[1]] = batch[
    #             edge_type[0], "to", edge_type[1]
    #         ]["edge_index"]
    #         edge_attr_dict[edge_type[0], "to", edge_type[1]] = batch[
    #             edge_type[0], "to", edge_type[1]
    #         ]["edge_attr"]

    #     # for i in x:
    #     #     x[i] = x[i].to('cuda:5')
    #     # for i in edge_index_dict:
    #     #     edge_index_dict[i] = edge_index_dict[i].to('cuda:5')
    #     # for i in edge_attr_dict:
    #     #     edge_attr_dict[i] = edge_attr_dict[i].to('cuda:5')

    #     x_comms = {}

    #     for N_layer in range(self.N_layers):
    #         for track_type in x:
    #             x[track_type] = F.leaky_relu(
    #                 self.selfloop_layers[N_layer][track_type](x[track_type])
    #             )
    #             x_comms[track_type] = x[track_type][:, : self.communication_dims]
    #         x_comms = self.communication_layers[N_layer](x_comms, edge_index_dict, edge_attr_dict)
    #         for track_type in x_comms:
    #             x_comms[track_type] = F.leaky_relu(x_comms[track_type])
    #         for track_type in x:
    #             x[track_type] = x[track_type].clone()
    #             x[track_type][:, : self.communication_dims] = x_comms[track_type]

    #     # for track_type in x:
    #     #     x[track_type] = F.leaky_relu(
    #     #         self.selfloop_layers[2][track_type](x[track_type])
    #     #     )
    #     #     x_comms[track_type] = x[track_type][:, : self.communication_dims]
    #     # x_comms = self.communication_layers[1](x_comms, edge_index_dict, edge_attr_dict)
    #     # for track_type in x_comms:
    #     #     x_comms[track_type] = F.leaky_relu(x_comms[track_type])
    #     # for track_type in x:
    #     #     x[track_type] = x[track_type].clone()
    #     #     x[track_type][:, : self.communication_dims] = x_comms[track_type]

    #     for track_type in x:
    #         x[track_type] = F.leaky_relu(
    #             self.selfloop_layers[-2][track_type](x[track_type])
    #         )
    #         if self.add_MBD:
    #             if x[track_type].shape[0] == 0:
    #                 mbd_output = torch.empty((0, self.mbd_dims)).to(x[track_type].device)
    #             else:
    #                 mbd_output = self.mbd_layer[track_type](x[track_type])
    #             x[track_type] = torch.cat((x[track_type], mbd_output), axis=1)

    #     for track_type in x:
    #         x[track_type] = F.leaky_relu(
    #             self.selfloop_layers[-1][track_type](x[track_type])
    #         )
    #     # print_heterogenous_representation(x)

    #     for idx, particle_type in enumerate(particle_types):
    #         if idx == 0:
    #             x_prime = x[particle_type]
    #             x_prime_batch = batch[particle_type].batch
    #         else:
    #             x_prime = torch.cat((x_prime, x[particle_type]), dim=0)
    #             x_prime_batch = torch.cat(
    #                 (x_prime_batch, batch[particle_type].batch), dim=0
    #             )

    #     x = global_mean_pool(x_prime, x_prime_batch.to(x_prime.device))

    #     # if self.add_MBD:
    #     #     mbd_output = self.mbd_layer(x)
    #     #     pooled_cat = torch.cat((x, mbd_output), axis=1)
    #     #     pooled_cat = x

    #     #     disc_out = torch.sigmoid(self.output_layer(pooled_cat))
    #     # else:
    #     disc_out = torch.sigmoid(self.output_layer(x))

    #     return disc_out


class gGAN(nn.Module):
    def __init__(
        self,
        track_targets_dims,
        track_conditions_dims,
        hidden_channels,
        track_latent_dims,
        edge_conditions_dims,
        silent=False,
        add_MBD=False,
        add_physics_dims=False,
    ):
        super(gGAN, self).__init__()

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

        self.generator = HeteroGenerator(
            track_targets_dims,
            track_conditions_dims,
            hidden_channels,
            track_latent_dims,
            edge_conditions_dims,
            conditonless=False,
        )

        self.discriminator = HeteroDiscriminator(
            track_targets_dims,
            track_conditions_dims,
            # int(hidden_channels/2.),
            hidden_channels,
            track_latent_dims,
            edge_conditions_dims,
            conditonless=False,
            add_MBD=add_MBD,
            add_physics_dims=add_physics_dims,
        )

    def inference(
        self, batch_size, batch, offline_query_mode=False, force_latent_value=None
    ):
        particle_types = ["11", "13", "211", "321", "2212"]
        track_latent = {}
        for particle_type in particle_types:
            if force_latent_value:
                track_latent[particle_type] = (
                    torch.ones(
                        (batch[particle_type].x.shape[0], self.track_latent_dims)
                    ).to(batch[particle_type].x.device)
                    * force_latent_value
                )
            else:
                track_latent[particle_type] = torch.randn(
                    (batch[particle_type].x.shape[0], self.track_latent_dims)
                ).to(batch[particle_type].x.device)

        out = self.generator(
            track_latent,
            batch=batch,
            offline_query_mode=offline_query_mode,
        )

        return out

# -*- coding: utf-8 -*-
"""
===========================================================
 Project   : hotpot
 File      : complete_graph
 Created   : 2025/6/10 15:40
 Author    : zhang
 Python    : 
-----------------------------------------------------------
 Description
 ----------------------------------------------------------
 
===========================================================
"""
import torch
import torch.nn as nn
import torch.nn.functional as F

import torch_geometric.nn as pygnn

from .utils import complete_graph_generator

class CloudGraph(nn.Module):
    """ Graph network to perform complete graph operation """
    def __init__(self, vec_dim: int):
        super(CloudGraph, self).__init__()
        self.xyz_proj = nn.Linear(3, vec_dim, bias=False)
        self.xyz_proj_norm = nn.BatchNorm1d(vec_dim)

        self.lin1 = nn.Linear(vec_dim, vec_dim)
        self.norm1 = nn.LayerNorm(vec_dim)

        self.lin2 = nn.Linear(vec_dim, vec_dim)
        self.norm2 = nn.LayerNorm(vec_dim)

    def forward(self, x, xyz, ptr):
        # TODO: add vector cross-multiply module
        # TODO: Add CNN module

        cloud_edge_index = complete_graph_generator(ptr)
        rela_xyz = xyz[cloud_edge_index[0]] - xyz[cloud_edge_index[1]]
        rela_x = x[cloud_edge_index[0]] - x[cloud_edge_index[1]]

        dist_xyz = torch.norm(rela_xyz, p=2, dim=-1)
        weight = torch.exp(-dist_xyz).unsqueeze(-1)

        x = x + self.norm1(pygnn.global_add_pool(
            F.relu(self.lin1(weight * rela_x)),
            cloud_edge_index[0]
        ))

        x = x + self.xyz_proj_norm(
            pygnn.global_add_pool(
                F.relu(self.xyz_proj(rela_xyz)),
                cloud_edge_index[0]
            )
        )

        return x


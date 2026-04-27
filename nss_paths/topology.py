from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import networkx as nx


NODES = tuple(range(1, 22))

A4_EDGES = (
    (1, 4), (1, 2),
    (2, 4), (2, 9), (2, 5),
    (4, 8), (4, 6),
    (8, 6), (8, 15),
    (6, 12), (6, 9),
    (12, 15), (12, 9),
    (9, 7), (9, 14),
    (5, 7), (5, 10),
    (7, 10), (7, 11),
    (11, 10), (11, 16),
    (14, 16),
    (10, 17), (10, 3),
    (3, 13),
    (16, 17), (16, 21),
    (17, 21), (17, 19), (17, 13), (17, 18),
    (19, 21), (19, 20),
    (20, 18),
    (13, 18),
)

@dataclass(frozen=True)
class TopologyStats:
    nodes: int
    edges: int
    connected: bool
    edge_connectivity: int


def build_a4_graph() -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(NODES)
    graph.add_edges_from((u, v, {"weight": 1}) for u, v in A4_EDGES)
    return graph


def edge_list_as_text(edges: Iterable[tuple[int, int]]) -> list[str]:
    return [f"{u}-{v}" for u, v in edges]


def adjacency_summary() -> list[tuple[int, str, int]]:
    graph = build_a4_graph()
    rows = []
    for node in sorted(graph.nodes):
        neighbors = sorted(graph.neighbors(node))
        rows.append((node, ", ".join(map(str, neighbors)), len(neighbors)))
    return rows


def describe_graph(graph: nx.Graph) -> TopologyStats:
    return TopologyStats(
        nodes=graph.number_of_nodes(),
        edges=graph.number_of_edges(),
        connected=nx.is_connected(graph),
        edge_connectivity=nx.edge_connectivity(graph) if nx.is_connected(graph) else 0,
    )

import networkx as nx

from nss_paths.algorithms import naive_edge_disjoint_paths, suurballe_edge_disjoint_paths
from nss_paths.experiment import run_for_graph
from nss_paths.topology import build_a4_graph


def build_trap_graph() -> nx.Graph:
    graph = nx.Graph()
    graph.add_weighted_edges_from(
        [
            (1, 3, 1), (3, 4, 1), (4, 6, 1),
            (1, 2, 2), (2, 4, 2),
            (3, 5, 2), (5, 6, 2),
        ],
        weight="weight",
    )
    return graph


def main() -> None:
    trap = build_trap_graph()
    naive = naive_edge_disjoint_paths(trap, 1, 6)
    suurballe = suurballe_edge_disjoint_paths(trap, 1, 6)
    assert not naive.accepted, naive
    assert suurballe.accepted, suurballe
    assert suurballe.total_links == 6, suurballe

    graph = build_a4_graph()
    details, summary, stats = run_for_graph(graph)
    assert stats["nodes"] == 21
    assert stats["edges"] == 35
    assert details.shape[0] == 420
    assert set(summary["algorytm"]) == {"naiwny", "suurballe"}
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()

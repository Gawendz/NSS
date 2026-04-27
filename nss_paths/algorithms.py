from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import pairwise

import networkx as nx


Path = list[int]


@dataclass(frozen=True)
class RoutingResult:
    accepted: bool
    paths: tuple[Path, ...] = ()
    total_links: int | None = None
    reason: str = ""


def path_edges(path: Path) -> list[tuple[int, int]]:
    return list(pairwise(path))


def path_length(path: Path) -> int:
    return max(0, len(path) - 1)


def undirected_edge(edge: tuple[int, int]) -> tuple[int, int]:
    u, v = edge
    return (u, v) if u <= v else (v, u)


def are_link_disjoint(paths: tuple[Path, ...]) -> bool:
    used: set[tuple[int, int]] = set()
    for path in paths:
        for edge in path_edges(path):
            normalized = undirected_edge(edge)
            if normalized in used:
                return False
            used.add(normalized)
    return True


def order_paths(paths: tuple[Path, ...]) -> tuple[Path, ...]:
    return tuple(sorted(paths, key=lambda p: (path_length(p), p)))


def _result(paths: tuple[Path, ...]) -> RoutingResult:
    paths = order_paths(paths)
    return RoutingResult(
        accepted=True,
        paths=paths,
        total_links=sum(path_length(path) for path in paths),
    )


def naive_edge_disjoint_paths(
    graph: nx.Graph,
    source: int,
    target: int,
    k: int = 2,
    weight: str = "weight",
) -> RoutingResult:
    working = graph.copy()
    paths: list[Path] = []

    for _ in range(k):
        try:
            path = nx.dijkstra_path(working, source, target, weight=weight)
        except nx.NetworkXNoPath:
            return RoutingResult(
                accepted=False,
                paths=tuple(order_paths(tuple(paths))),
                reason=f"Znaleziono tylko {len(paths)} z {k} wymaganych tras.",
            )
        paths.append(path)
        working.remove_edges_from(path_edges(path))

    return _result(tuple(paths))


def _directed_from_undirected(graph: nx.Graph, weight: str) -> nx.DiGraph:
    directed = nx.DiGraph()
    directed.add_nodes_from(graph.nodes)
    for u, v, data in graph.edges(data=True):
        cost = data.get(weight, 1)
        directed.add_edge(u, v, weight=cost)
        directed.add_edge(v, u, weight=cost)
    return directed


def _cancel_opposite_arcs(paths: tuple[Path, Path]) -> Counter[tuple[int, int]]:
    arcs: Counter[tuple[int, int]] = Counter()
    for path in paths:
        for arc in path_edges(path):
            reverse = (arc[1], arc[0])
            if arcs[reverse]:
                arcs[reverse] -= 1
                if arcs[reverse] == 0:
                    del arcs[reverse]
            else:
                arcs[arc] += 1
    return arcs


def _decompose_paths(arcs: Counter[tuple[int, int]], source: int, target: int) -> tuple[Path, Path]:
    adjacency: dict[int, list[int]] = defaultdict(list)
    for (u, v), count in arcs.items():
        adjacency[u].extend([v] * count)

    decomposed: list[Path] = []
    for _ in range(2):
        current = source
        path = [source]
        seen = {source}
        while current != target:
            if not adjacency[current]:
                raise nx.NetworkXException("Nie można zdekomponować wyniku Suurballe'a na dwie ścieżki s-t.")
            nxt = adjacency[current].pop(0)
            if nxt in seen and nxt != target:
                raise nx.NetworkXException("Wynik zawiera cykl przed dojściem do celu.")
            path.append(nxt)
            seen.add(nxt)
            current = nxt
        decomposed.append(path)

    return decomposed[0], decomposed[1]


def suurballe_edge_disjoint_paths(
    graph: nx.Graph,
    source: int,
    target: int,
    k: int = 2,
    weight: str = "weight",
) -> RoutingResult:
    if k != 2:
        raise ValueError("Ta implementacja Suurballe'a obsługuje wariant wymagany w zadaniu, czyli k=2.")

    directed = _directed_from_undirected(graph, weight)
    try:
        distances = nx.single_source_dijkstra_path_length(directed, source, weight="weight")
        first_path = nx.dijkstra_path(directed, source, target, weight="weight")
    except nx.NetworkXNoPath:
        return RoutingResult(accepted=False, reason="Brak pierwszej ścieżki.")

    helper = nx.DiGraph()
    helper.add_nodes_from(directed.nodes)
    for u, v, data in directed.edges(data=True):
        if u not in distances or v not in distances:
            continue
        reduced_cost = data["weight"] + distances[u] - distances[v]
        helper.add_edge(u, v, weight=reduced_cost)

    for u, v in path_edges(first_path):
        if helper.has_edge(u, v):
            helper.remove_edge(u, v)
        helper.add_edge(v, u, weight=0)

    try:
        second_path = nx.dijkstra_path(helper, source, target, weight="weight")
    except nx.NetworkXNoPath:
        return RoutingResult(accepted=False, paths=(first_path,), reason="Brak drugiej ścieżki w grafie pomocniczym.")

    arcs = _cancel_opposite_arcs((first_path, second_path))
    try:
        paths = _decompose_paths(arcs, source, target)
    except nx.NetworkXException as exc:
        return RoutingResult(accepted=False, paths=(first_path, second_path), reason=str(exc))

    if not are_link_disjoint(paths):
        return RoutingResult(accepted=False, paths=paths, reason="Otrzymane ścieżki nie są rozłączne łączowo.")

    return _result(paths)

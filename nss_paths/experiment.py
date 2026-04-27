from __future__ import annotations

from dataclasses import asdict
from itertools import combinations
from pathlib import Path

import pandas as pd
import networkx as nx

from .algorithms import (
    RoutingResult,
    naive_edge_disjoint_paths,
    path_length,
    suurballe_edge_disjoint_paths,
)
from .topology import build_a4_graph, describe_graph


def _serialize_paths(result: RoutingResult) -> tuple[str, str, int | None, int | None]:
    if not result.accepted:
        first = " - ".join(map(str, result.paths[0])) if len(result.paths) > 0 else ""
        second = " - ".join(map(str, result.paths[1])) if len(result.paths) > 1 else ""
        return first, second, None, None

    first, second = result.paths
    return (
        " - ".join(map(str, first)),
        " - ".join(map(str, second)),
        path_length(first),
        path_length(second),
    )


def run_for_graph(graph: nx.Graph) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, int | bool]]:
    rows: list[dict[str, object]] = []
    nodes = sorted(graph.nodes)

    for source, target in combinations(nodes, 2):
        results = {
            "naiwny": naive_edge_disjoint_paths(graph, source, target, k=2),
            "suurballe": suurballe_edge_disjoint_paths(graph, source, target, k=2),
        }
        for algorithm, result in results.items():
            path_1, path_2, length_1, length_2 = _serialize_paths(result)
            rows.append(
                {
                    "algorytm": algorithm,
                    "zrodlo": source,
                    "cel": target,
                    "zaakceptowane": result.accepted,
                    "trasa_podstawowa": path_1,
                    "trasa_zabezpieczajaca": path_2,
                    "dlugosc_podstawowa": length_1,
                    "dlugosc_zabezpieczajaca": length_2,
                    "laczna_liczba_laczy": result.total_links,
                    "powod_odrzucenia": result.reason,
                }
            )

    details = pd.DataFrame(rows)
    summary = (
        details.groupby("algorytm", sort=False)
        .agg(
            liczba_zadan=("zaakceptowane", "size"),
            zaakceptowane=("zaakceptowane", "sum"),
            srednia_dlugosc_podstawowa=("dlugosc_podstawowa", "mean"),
            srednia_dlugosc_zabezpieczajaca=("dlugosc_zabezpieczajaca", "mean"),
            srednia_laczna_liczba_laczy=("laczna_liczba_laczy", "mean"),
        )
        .reset_index()
    )
    summary["odrzucone"] = summary["liczba_zadan"] - summary["zaakceptowane"]
    summary["wspolczynnik_odrzucenia"] = summary["odrzucone"] / summary["liczba_zadan"]
    summary = summary[
        [
            "algorytm",
            "liczba_zadan",
            "zaakceptowane",
            "odrzucone",
            "wspolczynnik_odrzucenia",
            "srednia_dlugosc_podstawowa",
            "srednia_dlugosc_zabezpieczajaca",
            "srednia_laczna_liczba_laczy",
        ]
    ]

    stats = asdict(describe_graph(graph))
    return details, summary, stats


def run_a4_experiment(output_dir: Path) -> tuple[Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    graph = build_a4_graph()
    details, summary, stats = run_for_graph(graph)

    details_path = output_dir / "wyniki_szczegolowe.csv"
    summary_path = output_dir / "wyniki_podsumowanie.csv"
    stats_path = output_dir / "statystyki_topologii.json"

    details.to_csv(details_path, index=False, encoding="utf-8-sig")
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")
    pd.Series(stats).to_json(stats_path, indent=2, force_ascii=False)

    return details_path, summary_path, stats_path


if __name__ == "__main__":
    details_file, summary_file, stats_file = run_a4_experiment(Path("outputs"))
    print(details_file)
    print(summary_file)
    print(stats_file)

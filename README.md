# Porównanie algorytmów tras rozłącznych

Projekt porównuje dwa algorytmy wyznaczania dwóch tras łączowo rozłącznych (`k = 2`) dla topologii A4:

- podejście naiwne: Dijkstra, usunięcie użytych łączy, ponownie Dijkstra,
- algorytm Suurballe'a: wspólna optymalizacja pary tras rozłącznych.

## Struktura

```text
.
├── assets/
│   └── A4.jpg
├── nss_paths/
│   ├── __init__.py
│   ├── topology.py
│   ├── algorithms.py
│   └── experiment.py
├── outputs/
│   ├── wyniki_podsumowanie.csv
│   ├── wyniki_szczegolowe.csv
│   ├── statystyki_topologii.json
│   └── porownanie_algorytmow_trasy_rozlaczne.xlsx
├── export_results_excel.py
├── tests_smoke.py
├── requirements.txt
├── raport_wstepny.docx
```

## Najważniejsze moduły

- `nss_paths/topology.py` - definicja topologii A4, lista węzłów i łączy, budowa grafu NetworkX oraz lista sąsiedztwa.
- `nss_paths/algorithms.py` - implementacja metody naiwnej i algorytmu Suurballe'a dla `k = 2`.
- `nss_paths/experiment.py` - eksperyment dla wszystkich nieuporządkowanych par węzłów.
- `export_results_excel.py` - generowanie Excela z wynikami.
- `tests_smoke.py` - krótki test kontrolny algorytmów i eksperymentu.

## Uruchamianie

```powershell
python -m pip install -r requirements.txt
python tests_smoke.py
python -m nss_paths.experiment
python export_results_excel.py
```

## Aktualne wyniki

| Algorytm | Zaakceptowane | Odrzucone | Współczynnik odrzucenia | Śr. P1 | Śr. P2 | Śr. suma |
|---|---:|---:|---:|---:|---:|---:|
| naiwny | 210 | 0 | 0.00% | 2.95 | 4.27 | 7.21 |
| Suurballe | 210 | 0 | 0.00% | 2.95 | 4.24 | 7.19 |

Suurballe poprawia sumę długości tras dla 5 par węzłów: `4-7`, `4-11`, `4-21`, `14-19`, `16-20`.

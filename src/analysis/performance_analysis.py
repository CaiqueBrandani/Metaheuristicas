import time
import statistics
import pandas as pd
import matplotlib.pyplot as plt
import math

from src.heuristics.constructives.constructive_greedy import greedy_heuristic
from src.heuristics.constructives.constructive_random import random_heuristic
from src.heuristics.constructives.deterministic.deterministic_constructive_greedy import deterministic_greedy_heuristic
from src.heuristics.constructives.deterministic.deterministic_constructive_random import deterministic_random_heuristic
from src.heuristics.refinement.refinement_local_search import local_search
from src.heuristics.refinement.refinement_tabu_search import tabu_search
from src.metaheuristics.vns import variable_neighborhood_search
from src.metaheuristics.brkga import run_brkga

def _round_up(value, decimals=4):
    factor = 10 ** decimals
    return math.ceil(value * factor) / factor

def brkga_heuristic(processed_weighted_csv, course, period,
                    load_weighted_disciplines,
                    processed_input_csv,
                    max_subjects=5):

    best_selected, best_score = run_brkga(
        weighted_csv=processed_weighted_csv,
        course=course,
        load_weights_fn=load_weighted_disciplines,
        processed_csv=processed_input_csv,
        period=period,
        population_size=50,
        elite_fraction=0.1,
        mutant_fraction=0.2,
        generations=500,
        max_subjects=max_subjects,
        seed=99
    )
    return best_selected, best_score

def analyze_performance(course, period,
                        load_weighted_disciplines,
                        processed_input_csv,
                        processed_weighted_csv,
                        max_subjects=5,
                        repetitions=30,
                        output_image='image/analysis/performance_table.png'):
    scenarios = [
        ("Deterministic Greedy", deterministic_greedy_heuristic, None),
        ("Deterministic Random", deterministic_random_heuristic, None),
        ("Greedy + Local",   greedy_heuristic, local_search),
        ("Random + Local",   random_heuristic, local_search),
        ("Greedy + Tabu",    greedy_heuristic, tabu_search),
        ("Random + Tabu",    random_heuristic, tabu_search),
        ("Greedy + VNS",     greedy_heuristic, variable_neighborhood_search),
        ("Random + VNS",     random_heuristic, variable_neighborhood_search),
        ("BRKGA", brkga_heuristic, None),
    ]

    records = []
    for name, build_fn, refine_fn in scenarios:
        scores, times, solutions = [], [], set()
        best_score = float('-inf')
        best_solution = []
        for i in range(repetitions):
            start = time.time()
            init_list, i = build_fn(
                processed_weighted_csv, course, period,
                load_weighted_disciplines,
                processed_input_csv,
                max_subjects=max_subjects,
                **({"seed": i} if "random" in name.lower() else {})
            )
            if refine_fn is None:
                sel, score = init_list, i
            if refine_fn is local_search:
                sel, score = local_search(
                    init_list, processed_weighted_csv,
                    course, period,
                    load_weighted_disciplines,
                    processed_input_csv
                )
            elif refine_fn is tabu_search:
                sel, score = tabu_search(
                    init_list, processed_weighted_csv,
                    load_weighted_disciplines,
                    course, period,
                    processed_input_csv
                )
            else:
                sel, score = variable_neighborhood_search(
                    init_list, processed_weighted_csv,
                    course, period,
                    load_weighted_disciplines,
                    processed_input_csv
                )

            times.append(time.time() - start)
            scores.append(score)
            solutions.add(tuple(sorted(sel)))

            if score > best_score:
                best_score = score
                best_solution = sel[:]

        records.append({
            "Cenário": name,
            "Solução": ", ".join(best_solution),
            "Score Máximo": _round_up(max(scores)),
            "Média Score": _round_up(statistics.mean(scores)),
            "Desvio Score": _round_up(statistics.stdev(scores) if len(scores) > 1 else 0.0),
            "Tempo Médio": _round_up(statistics.mean(times)),
            "Desvio Tempo": _round_up(statistics.stdev(times) if len(times) > 1 else 0.0),
            "Diversidade": len(solutions),
        })

    df = pd.DataFrame(records)
    fig, ax = plt.subplots(figsize=(14, 6), dpi=150)
    ax.axis('off')

    col_count = len(df.columns)
    special_width = 0.3  # 50% para “Soluções”
    remaining = 1 - special_width
    other_width = remaining / (col_count - 1)

    col_widths = [
        special_width if idx == 1 else other_width
        for idx in range(col_count)
    ]

    # ajusta a coluna Solução (índice 1) para 70% do valor original
    col_widths[1] *= 0.7
    col_widths[0] *= 1.2

    tbl = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc='center',
        colWidths=col_widths,
        loc='center'
    )

    tbl = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', colWidths=col_widths, loc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)

    idx_max_score = df.columns.get_loc("Score Máximo")
    idx_tempo = df.columns.get_loc("Tempo Médio")
    idx_dev_tempo = df.columns.get_loc("Desvio Tempo")
    idx_diversidade = df.columns.get_loc("Diversidade")
    idx_dev_score = df.columns.get_loc("Desvio Score")
    idx_media = df.columns.get_loc("Média Score")

    # valores de referência
    max_score = df["Score Máximo"].max()
    min_tempo = df["Tempo Médio"].min()
    max_tempo = df["Tempo Médio"].max()
    min_dev_tempo = df["Desvio Tempo"].min()
    max_dev_tempo = df["Desvio Tempo"].max()
    max_div = df["Diversidade"].max()
    min_div = df["Diversidade"].min()
    non_zero_ds = df["Desvio Score"][df["Desvio Score"] != 0]
    min_dev_score = non_zero_ds.min() if not non_zero_ds.empty else None
    max_dev_score = df["Desvio Score"].max()
    max_media = df["Média Score"].max()
    min_media = df["Média Score"].min()

    # destaque Score Máximo (já existente)
    for row, score in enumerate(df["Score Máximo"], start=1):
        if score == max_score:
            cell = tbl[row, idx_max_score]
            cell.set_facecolor('lightgreen')
            cell.get_text().set_fontweight('bold')

    # Tempo Médio
    for row, val in enumerate(df["Tempo Médio"], start=1):
        cell = tbl[row, idx_tempo]
        if val == min_tempo:
            cell.set_facecolor('lightgreen')
            cell.get_text().set_fontweight('bold')
        elif val == max_tempo:
            cell.set_facecolor('lightcoral')
            cell.get_text().set_fontweight('bold')

    # Desvio Tempo
    for row, val in enumerate(df["Desvio Tempo"], start=1):
        cell = tbl[row, idx_dev_tempo]
        if val == min_dev_tempo:
            cell.set_facecolor('lightgreen')
            cell.get_text().set_fontweight('bold')
        elif val == max_dev_tempo:
            cell.set_facecolor('lightcoral')
            cell.get_text().set_fontweight('bold')

    # Diversidade
    for row, val in enumerate(df["Diversidade"], start=1):
        cell = tbl[row, idx_diversidade]
        if val == max_div:
            cell.set_facecolor('lightgreen')
            cell.get_text().set_fontweight('bold')
        elif val == min_div:
            cell.set_facecolor('lightcoral')
            cell.get_text().set_fontweight('bold')

    # Desvio Score (ignora zeros para mínimo)
    if min_dev_score is not None:
        for row, val in enumerate(df["Desvio Score"], start=1):
            cell = tbl[row, idx_dev_score]
            if val == min_dev_score:
                cell.set_facecolor('lightgreen')
                cell.get_text().set_fontweight('bold')
            elif val == max_dev_score:
                cell.set_facecolor('lightcoral')
                cell.get_text().set_fontweight('bold')

    # destaque da Média Score
    for row, val in enumerate(df["Média Score"], start=1):
        cell = tbl[row, idx_media]
        if val == max_media:
            cell.set_facecolor('lightgreen')
            cell.get_text().set_fontweight('bold')
        elif val == min_media:
            cell.set_facecolor('lightcoral')
            cell.get_text().set_fontweight('bold')

    fig.tight_layout()
    fig.savefig(output_image, bbox_inches='tight')
    plt.close(fig)

    return df
import argparse
import time
import sys

from src.heuristics.constructives.constructive_greedy import greedy_heuristic
from src.heuristics.constructives.constructive_random import random_heuristic
from src.heuristics.refinement.refinement_local_search import local_search
from src.heuristics.refinement.refinement_tabu_search import tabu_search
from src.metaheuristics.vns import variable_neighborhood_search
from src.interface.output_interface import print_result, print_error, print_options_dict
from src.preprocessing.output_builder.processed_weighted_data_builder import build_processed_weighted_data
from src.preprocessing.output_builder.processed_data_builder import build_processed_input_data
from src.preprocessing.output_builder.processed_normalized_data_builder import build_processed_normalized_data
from src.preprocessing.record_data_extraction.extract_record import RecordExtractor
from src.preprocessing.record_data_extraction.processors.process_student_data import StudentDataProcessor
from src.preprocessing.record_data_extraction.processors.process_workload import WorkloadProcessor
from src.preprocessing.record_data_extraction.processors.process_subject_history import SubjectHistoryProcessor
from src.preprocessing.record_data_extraction.processors.process_pending_components import PendingComponentsProcessor
from src.preprocessing.record_data_extraction.validators.validate_equivalences import EquivalencesValidator
from src.analysis.performance_analysis import analyze_performance

# >>> IMPORTAÇÃO DO BRKGA <<<
from src.metaheuristics.brkga import run_brkga

def load_weighted_disciplines(csv_path):
    import csv
    disciplines = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            code = row[0]
            weight = float(row[1])
            disciplines.append((code, weight))
    return disciplines

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--h', help='Escolha a heurística (greedy, random, brkga)')
    parser.add_argument('--r', help='Escolha o refinamento (none, local, tabu, vns)', default='none')
    parser.add_argument('--c', help='Ex: CCO ou SIN')
    parser.add_argument('--i', type=int, help='Índice do histórico (ex: 1, 2, 3...)')
    parser.add_argument('--p', help='Período atual (ex: 2024.1, 2024.2, 2025.1...)')
    parser.add_argument('--dict', action='store_true', help='Mostra o dicionário de opções')
    parser.add_argument('--analyze', action='store_true', help='Executa análise de desempenho dos cenários')
    args = parser.parse_args()

    if not args.dict:
        if not args.c or args.i is None or not args.p:
            print_error("--c, --i e --p são obrigatórios, exceto quando --dict é usado.")
            sys.exit(1)

    if args.dict:
        print_options_dict()
        sys.exit(0)

    heuristic = args.h
    refinement = args.r
    period = args.p

    processed_input_csv = 'data/processed/processed_input.csv'
    processed_weighted_input_csv = 'data/processed/processed_weighted_input.csv'
    processed_normalized_input_csv = 'data/processed/processed_normalized_input.csv'

    offered_components_csv = f'data/raw/offers/{args.c}/{args.c}_Offered_Components_{args.p}.csv'
    record_pdf = f'data/raw/record/{args.c}/record_{args.c}-{args.i}.pdf'

    if args.analyze:
        df = analyze_performance(
            course=args.c,
            period=args.p,
            load_weighted_disciplines=load_weighted_disciplines,
            processed_input_csv=processed_input_csv,
            processed_weighted_csv=processed_weighted_input_csv
        )
        print('Análise salva!')
        return

    # Pré-processamento dos dados
    student_processor = StudentDataProcessor()
    workload_processor = WorkloadProcessor()
    subject_history_processor = SubjectHistoryProcessor()
    pending_components_processor = PendingComponentsProcessor()
    equivalences_validator = EquivalencesValidator()
    record_extractor = RecordExtractor(
        student_processor,
        workload_processor,
        subject_history_processor,
        pending_components_processor,
        equivalences_validator,
    )
    history, pending, course, current_period = record_extractor.extract_record(record_pdf)
    build_processed_input_data(history, pending, processed_input_csv, course, current_period, period)
    build_processed_normalized_data(processed_input_csv, processed_normalized_input_csv, offered_components_csv)
    build_processed_weighted_data(processed_normalized_input_csv, processed_weighted_input_csv)

    # Heurísticas construtivas
    if heuristic == 'greedy':
        heuristic_func = greedy_heuristic
    elif heuristic == 'random':
        heuristic_func = random_heuristic
    elif heuristic == 'brkga':
        start_brkga = time.time()
        print("\n--- BRKGA ---")
        selected_brkga, total_weight_brkga = run_brkga(
            processed_weighted_input_csv,
            course,
            load_weighted_disciplines,
            processed_input_csv,
            period,
            population_size=50,
            elite_fraction=0.1,
            mutant_fraction=0.2,
            generations=50,
            max_subjects=5,
            seed=51
        )

        exec_time = time.time() - start_brkga
        print(f"Matérias escolhidas: {selected_brkga}")
        print(f"Peso total: {total_weight_brkga}")
        print(f"Tempo de execução: {exec_time:.4f} segundos")
        return
    else:
        print_error("Heurística inválida. Use 'greedy', 'random' ou 'brkga'.")
        sys.exit(1)

    # Execução da heurística (greedy ou random)
    start = time.time()
    selected, total_weight = heuristic_func(processed_weighted_input_csv, course, period, load_weighted_disciplines, processed_input_csv)
    exec_time = time.time() - start
    print_result(f"Heurística {heuristic.capitalize()}", selected, total_weight, exec_time)

    # Refinamento (opcional)
    if refinement == 'local':
        start = time.time()
        refined, refined_weight = local_search(
            selected, processed_weighted_input_csv, course, period, load_weighted_disciplines, processed_input_csv
        )
        exec_time = time.time() - start
        print_result(f"Refinamento Local ({heuristic})", refined, refined_weight, exec_time)

    elif refinement == 'tabu':
        start = time.time()
        tabu_selected, tabu_weight = tabu_search(
            selected, processed_weighted_input_csv, load_weighted_disciplines, course, period, processed_input_csv
        )
        exec_time = time.time() - start
        print_result(f"Busca Tabu ({heuristic})", tabu_selected, tabu_weight, exec_time)

    elif refinement == 'vns':
        start = time.time()
        vns_selected, vns_weight = variable_neighborhood_search(
            selected, processed_weighted_input_csv, course, period, load_weighted_disciplines, processed_input_csv
        )
        exec_time = time.time() - start
        print_result(f"VNS ({heuristic})", vns_selected, vns_weight, exec_time)

if __name__ == "__main__":
    main()

import csv
import time

from src.heuristics.constructives.constructive_greedy import greedy_heuristic
from src.heuristics.constructives.constructive_random import random_heuristic
from src.heuristics.refinement.refinement_local_search import refine_local
from src.heuristics.refinement.refinement_tabu_search import tabu_search
from src.preprocessing.output_builder.processed_weighted_data_builder import ProcessedWeightedDataBuilder
from src.preprocessing.output_builder.processed_normalized_data_builder import normalize_preprocessed_input
from src.preprocessing.output_builder.processed_data_builder import build_csv
from src.preprocessing.record_data_extraction.processors.process_student_data import StudentDataProcessor
from src.preprocessing.record_data_extraction.processors.process_workload import WorkloadProcessor
from src.preprocessing.record_data_extraction.processors.process_subject_history import SubjectHistoryProcessor
from src.preprocessing.record_data_extraction.processors.process_pending_components import PendingComponentsProcessor
from src.preprocessing.record_data_extraction.validators.validate_equivalences import EquivalencesValidator
from src.preprocessing.record_data_extraction.extract_record import RecordExtractor

def main():
    # Inicializar dependências
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

    # Caminhos dos arquivos
    input_pdf = "../data/raw/record/CCO/record_CCO-1.pdf"
    processed_csv = "../data/processed/processed_input.csv"
    normalized_csv = "../data/processed/processed_normalized_input.csv"
    weighted_csv = "../data/processed/processed_weighted_input.csv"

    # Extrair e processar dados
    start_time = time.time()
    history, pending, course, period = record_extractor.extract_record(input_pdf)
    build_csv(history, pending, processed_csv, course, period)
    normalize_preprocessed_input(processed_csv, normalized_csv)

    builder = ProcessedWeightedDataBuilder(f"../data/raw/offers/{course}/{course}_Offered_Components.csv")
    builder.process_subjects(normalized_csv, weighted_csv)
    end_time = time.time()

    print("\nCriacão dos Arquivos Processado:")
    print(f"Tempo de execução: {end_time - start_time:.2f} segundos")

    def load_weighted_disciplines(csv_path):
        disciplines = []
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                code = row[0]
                weight = float(row[1])
                disciplines.append((code, weight))
        return disciplines

    # Executar heurística gulosa
    start_greedy = time.time()
    greedy_selected, greedy_total_weight = greedy_heuristic(weighted_csv, course, load_weighted_disciplines, processed_csv)
    end_greedy = time.time()
    print("\nHeurística Gulosa:")
    print(f"Matérias escolhidas: {greedy_selected}")
    print(f"Peso total: {greedy_total_weight}")
    print(f"Tempo de execução: {end_greedy - start_greedy:.4f} segundos")

    # Executar heurística aleatória
    start_random = time.time()
    random_selected, random_total_weight = random_heuristic(weighted_csv, course, load_weighted_disciplines, processed_csv)
    end_random = time.time()
    print("\nHeurística Aleatória:")
    print(f"Matérias escolhidas: {random_selected}")
    print(f"Peso total: {random_total_weight}")
    print(f"Tempo de execução: {end_random - start_random:.4f} segundos")

    start_greedy_refine = time.time()
    refine_local_greedy, refine_local_greedy_total_weight = refine_local(greedy_heuristic, weighted_csv, course, load_weighted_disciplines, processed_csv)
    end_greedy_refine = time.time()
    print("\nRefinamento Local para Heurística Gulosa:")
    print(f"Matérias escolhidas: {refine_local_greedy}")
    print(f"Peso total: {refine_local_greedy_total_weight}")
    print(f"Tempo de execução: {end_greedy_refine - start_greedy_refine:.4f} segundos")

    # Executar refinamento local para heurística aleatória
    start_random_refine = time.time()
    refine_local_random, refine_local_random_total_weight = refine_local(random_heuristic, weighted_csv, course, load_weighted_disciplines, processed_csv)
    end_random_refine = time.time()
    print("\nRefinamento Local para Heurística Aleatória:")
    print(f"Matérias escolhidas: {refine_local_random}")
    print(f"Peso total: {refine_local_random_total_weight}")
    print(f"Tempo de execução: {end_random_refine - start_random_refine:.4f} segundos")

    # Executar busca tabu para heurística gulosa
    start_tabu_greedy = time.time()
    tabu_greedy_selected, tabu_greedy_total_weight = tabu_search(
        greedy_selected, weighted_csv, load_weighted_disciplines, course, processed_csv
    )
    end_tabu_greedy = time.time()
    print("\nBusca Tabu para Heurística Gulosa:")
    print(f"Matérias escolhidas: {tabu_greedy_selected}")
    print(f"Peso total: {tabu_greedy_total_weight}")
    print(f"Tempo de execução: {end_tabu_greedy - start_tabu_greedy:.4f} segundos")

    # Executar busca tabu para heurística aleatória
    start_tabu_random = time.time()
    tabu_random_selected, tabu_random_total_weight = tabu_search(
        random_selected, weighted_csv, load_weighted_disciplines, course, processed_csv
    )
    end_tabu_random = time.time()
    print("\nBusca Tabu para Heurística Aleatória:")
    print(f"Matérias escolhidas: {tabu_random_selected}")
    print(f"Peso total: {tabu_random_total_weight}")
    print(f"Tempo de execução: {end_tabu_random - start_tabu_random:.4f} segundos")


if __name__ == "__main__":
    main()
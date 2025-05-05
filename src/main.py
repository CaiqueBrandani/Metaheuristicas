import time

from src.preprocessing.output_builder.csv_builder import build_csv
from src.preprocessing.record_data_extraction.processors.process_student_data import StudentDataProcessor
from src.preprocessing.record_data_extraction.processors.process_workload import WorkloadProcessor
from src.preprocessing.record_data_extraction.processors.process_subject_history import SubjectHistoryProcessor
from src.preprocessing.record_data_extraction.processors.process_pending_components import PendingComponentsProcessor
from src.preprocessing.record_data_extraction.validators.validate_equivalences import EquivalencesValidator
from src.preprocessing.record_data_extraction.extract_record import RecordExtractor

def main():
    start_time = time.time()

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
    input_pdf = "../data/raw/record/SIN/record_SIN-1.pdf"
    output_csv = "../data/processed/record.csv"

    # Extrair dados do PDF
    history_components, pending_components, course, current_period = record_extractor.extract_record(input_pdf)

    # Montar o arquivo CSV
    build_csv(history_components, pending_components, output_csv, course, current_period)

    end_time = time.time()
    print(f"O arquivo foi salvo com sucesso em {output_csv}")
    print(f"Tempo de execução: {end_time - start_time:.2f} segundos")

if __name__ == "__main__":
    main()
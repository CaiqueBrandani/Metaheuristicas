# test_extract_record.py

from src.preprocessing.record_data_extraction.extract_record import RecordExtractor
from src.preprocessing.record_data_extraction.processors.process_student_data import StudentDataProcessor
from src.preprocessing.record_data_extraction.processors.process_workload import WorkloadProcessor
from src.preprocessing.record_data_extraction.processors.process_subject_history import SubjectHistoryProcessor
from src.preprocessing.record_data_extraction.processors.process_pending_components import PendingComponentsProcessor
from src.preprocessing.record_data_extraction.validators.validate_equivalences import EquivalencesValidator

if __name__ == "__main__":
    # Instancie os processadores necessários
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

    # Caminho para o arquivo PDF de teste
    file_path = "../data/raw/record/CCO/record_CCO-4.pdf"

    # Chame o método extract_record
    history_components, pending_components, course, current_period = record_extractor.extract_record(file_path)

    # Exiba os resultados
    print("Histórico de componentes:", history_components)
    print("Componentes pendentes:", pending_components)
    print("Curso:", course)
    print("Período atual:", current_period)
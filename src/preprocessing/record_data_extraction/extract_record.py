import pdfplumber

from src.preprocessing.utils.status_enums import PendingStatus

class RecordExtractor:
    def __init__(self, student_processor, workload_processor, subject_history_processor, pending_components_processor, equivalences_validator):
        self.student_processor = student_processor
        self.workload_processor = workload_processor
        self.subject_history_processor = subject_history_processor
        self.pending_components_processor = pending_components_processor
        self.equivalences_validator = equivalences_validator
        self.course = None
        self.current_period = None
        self.pending_optional_workload = None

    def extract_record(self, file_path):
        fulfilled_codes = set()
        pending_components = []
        subject_records = {}

        def parse_period(subject_period):
            return tuple(map(int, subject_period.split(".")))

        with pdfplumber.open(file_path) as pdf:
            for page in reversed(pdf.pages):
                text = page.extract_text()
                lines = text.split("\n")[7:]

                # Atualizar equivalências obtidas
                fulfilled_codes.update(self.equivalences_validator.validate_equivalences(lines))

                # Processar carga horária pendente
                self.pending_optional_workload = self.pending_optional_workload or self.workload_processor.process_workload(lines)

                # Processar histórico de matérias
                for component in self.subject_history_processor.process_subject_history(lines):
                    code, period = component["code"], component["period"]
                    if code not in fulfilled_codes and component["status"] not in {status.value for status in PendingStatus}:
                        if code not in subject_records or parse_period(period) > parse_period(subject_records[code]["period"]):
                            subject_records[code] = component

                # Processar componentes pendentes
                pending_components.extend(self.pending_components_processor.process_pending_components(lines))

                # Processar período atual
                self.current_period = self.current_period or self.student_processor.process_current_period(text)

                # Processar curso
                self.course = self.course or self.student_processor.process_course(text)

        history_components = [
            {"code": component["code"], "status": component["status"], "period": component["period"]}
            for component in subject_records.values()
        ]

        pending_components = [
            component for component in pending_components
            if component["code"] not in {history_component["code"] for history_component in history_components}
        ]

        history_components = sorted(
            history_components,
            key=lambda component: tuple(map(int, component["period"].split(".")))
        )

        return history_components, pending_components, self.course, self.current_period
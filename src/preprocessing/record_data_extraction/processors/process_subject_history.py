import re

class SubjectHistoryProcessor:
    def __init__(self):
        self.current_period = None
        self.period_counter = 1

    def process_subject_history(self, lines):
        text = "\n".join(lines)
        pattern = re.compile(r"(\d{4}\.\d).*?(\b[A-Z]{3,4}[A-Z0-9]{3,6}\b).*?(\b[A-Z]+\b)")
        history_components = []
        seen = set()

        # 1. Padrão atual (tudo na mesma linha)
        for match in pattern.finditer(text):
            period, code, status = match.groups()
            record = {"code": code, "status": status, "period": period}
            key = (code, period)
            if key not in seen:
                history_components.append(record)
                seen.add(key)

        # 2. Novo padrão (nome em uma linha, dados na próxima)
        code_status_pattern = re.compile(r"--\s+([A-Z]{3,4}[A-Z0-9]{3,6})\s+\d+\s+\d+\s+--\s+\d+,\d+\s+--\s+--\s+([A-Z]+)")
        for i in range(len(lines) - 1):
            name_line = lines[i].strip()
            data_line = lines[i + 1].strip()
            match = code_status_pattern.match(data_line)
            if match:
                code, status = match.groups()
                period = self.current_period or "0000.0"
                key = (code, period)
                if key not in seen:
                    record = {"code": code, "status": status, "period": period}
                    history_components.append(record)
                    seen.add(key)

        return history_components
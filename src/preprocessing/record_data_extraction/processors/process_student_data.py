import re

class StudentDataProcessor:
    def process_course(self, lines):
        match = re.search(r"Curso:\s*(.+)", lines, re.IGNORECASE)
        if not match:
            return None

        course = match.group(1).strip()
        if re.search(r"CIÊNCIA DA COMPUTAÇÃO/IMC", course, re.IGNORECASE):
            return "CCO"
        if re.search(r"SISTEMAS DE INFORMAÇÃO/IMC", course, re.IGNORECASE):
            return "SIN"

        return course

    def process_current_period(self, lines):
        match = re.search(r"Período Letivo Atual:\s*(\d+)", lines)
        return int(match.group(1)) if match else None
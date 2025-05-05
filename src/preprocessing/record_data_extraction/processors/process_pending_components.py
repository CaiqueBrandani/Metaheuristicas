import re

class PendingComponentsProcessor:
    def process_pending_components(self, lines):
        text = "\n".join(lines)
        match = re.search(r"Componentes Curriculares Obrigatórios Pendentes:\d+", text)

        if not match:
            return []

        text_below = text[match.end():].split("Equivalências:")[0]
        pattern = re.compile(r"(\b[A-Z]{3,4}\d{2,3}[A-Z]?\b).*?(\d{2,3}\b)")
        return [
            {"code": m.group(1), "workload": m.group(2)}
            for m in pattern.finditer(text_below)
        ]
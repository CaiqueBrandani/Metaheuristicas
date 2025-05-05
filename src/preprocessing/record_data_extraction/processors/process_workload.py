import re

class WorkloadProcessor:
    def process_workload(self, lines):
        text = "\n".join(lines)
        match = re.search(r"Pendente\s+\d+\s+h\s+(\d+)\s+h", text)
        return int(match.group(1)) if match else None
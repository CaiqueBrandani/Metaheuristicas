import re


class SubjectHistoryProcessor:
    def __init__(self):
        self.current_period = None
        self.period_counter = 1

    def process_subject_history(self, lines):
        text = "\n".join(lines)
        pattern = re.compile(r"(\d{4}\.\d).*?(\b[A-Z]{3,4}[A-Z0-9]{3,6}\b).*?(\b[A-Z]+\b)")
        history_components = []

        for match in pattern.finditer(text):
            period, code, status = match.groups()

            if period != self.current_period:
                self.current_period = period
                self.period_counter += 1

            record = {"code": code, "status": status, "period": period}

            history_components.append(record)

        return history_components
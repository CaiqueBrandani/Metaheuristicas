import re

class EquivalencesValidator:
    def validate_equivalences(self, lines):
        text = "\n".join(lines)
        match = re.search(r"Equivalências:", text)

        if not match:
            return set()

        text_below = text[match.end():].strip()
        pattern = re.compile(r"Cumpriu\s+(\b[A-Z]{3,4}[A-Z0-9]{3,6}\b)\s+-")
        return {m.group(1) for m in pattern.finditer(text_below)}
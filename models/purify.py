import re
import unicodedata


class PurifyScraper:
    def apply_regex(self, text):
        patterns = [r'[aA][rR][tT]\s*\.\s*\d+(\.?\d*\.?\/?\d*)', r'§\d+°?', r'\d+\.\d+\.\d+\.\d+\.?-?\d*(\/\d+)']

        for pattern in patterns:
            text = re.sub(pattern, '', text)
        return text

    def normalize_text(self, text):
        normalized_text = unicodedata.normalize('NFD', text)
        return ''.join(c for c in normalized_text if unicodedata.category(c) != 'Mn').lower()

    def is_uppercase_majority(self, text):
        total_letters = sum(c.isalpha() for c in text)
        uppercase_letters = sum(c.isupper() for c in text)

        if total_letters == 0:
            return False
        return (uppercase_letters / total_letters) > 0.5

    def process_text(self, text):
        parts = re.split(r'(?<!\d)\.(?!\d)', text)
        cleaned_parts = [part for part in parts if not self.is_uppercase_majority(part)]

        return '.'.join(cleaned_parts)

    def clean_text(self, text):
        cleaned_text = self.normalize_text(self.process_text(text))
        cleaned_text = self.apply_regex(cleaned_text)
        return re.sub(r'\s+', ' ', cleaned_text)

import json
import os
from flask import current_app

DATA_DIR = os.path.join(os.path.dirname(__file__), '..')

class DictionaryManager:
    def __init__(self, lang):
        self.lang = lang
        self.file_path = os.path.join(DATA_DIR, 'dictionaries', f'{lang}.json')

    def load(self):
        try:
            with open(self.file_path, encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def save(self, data):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

class AffixManager:
    def __init__(self):
        self.file_path = os.path.join(DATA_DIR, 'affixes.json')

    def load(self):
        try:
            with open(self.file_path, encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def save(self, data):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

class RuleManager:
    def __init__(self):
        self.file_path = os.path.join(DATA_DIR, 'rules.json')

    def load(self):
        try:
            with open(self.file_path, encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def save(self, data):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

import json
import os
from pathlib import Path

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LANGUAGES = ('az', 'tr', 'ru')
LANGUAGE_LABELS = {
    'az': 'Azerbaijani',
    'tr': 'Turkish',
    'ru': 'Russian',
}


def normalize_language(lang):
    if lang in LANGUAGES:
        return lang
    return 'az'


class DictionaryManager:
    def __init__(self, lang):
        self.lang = normalize_language(lang)

    @property
    def file_path(self):
        candidates = [
            os.path.join(DATA_DIR, 'dictionaries', f'{self.lang}.json'),
            os.path.join(DATA_DIR, 'dictionaries', 'dictionaries', f'{self.lang}.json'),
        ]
        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate
        return candidates[0]

    def load(self):
        try:
            with open(self.file_path, encoding='utf-8') as file_handle:
                data = json.load(file_handle)
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def save(self, data):
        Path(self.file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, 'w', encoding='utf-8') as file_handle:
            json.dump(data, file_handle, ensure_ascii=False, indent=2)

    def list_entries(self):
        entries = []
        for word, entry in sorted(self.load().items()):
            entries.append({
                'word': word,
                'POS': entry.get('POS', ''),
                'Features': entry.get('Features', {}),
            })
        return entries

    def count(self):
        return len(self.load())


class AffixManager:
    def __init__(self):
        self.file_path = os.path.join(DATA_DIR, 'affixes.json')

    def load(self):
        try:
            with open(self.file_path, encoding='utf-8') as file_handle:
                data = json.load(file_handle)
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def save(self, data):
        with open(self.file_path, 'w', encoding='utf-8') as file_handle:
            json.dump(data, file_handle, ensure_ascii=False, indent=2)

    def list_affixes(self):
        affixes = []
        for affix, entry in sorted(self.load().items()):
            affixes.append({
                'affix': affix,
                'tag': entry.get('tag', ''),
                'pos': entry.get('pos', ''),
            })
        return affixes


class RuleManager:
    def __init__(self):
        self.file_path = os.path.join(DATA_DIR, 'rules.json')

    def load(self):
        try:
            with open(self.file_path, encoding='utf-8') as file_handle:
                data = json.load(file_handle)
                return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            try:
                raw = Path(self.file_path).read_text(encoding='utf-8').strip()
                if not raw:
                    return {}
                decoder = json.JSONDecoder()
                data, _ = decoder.raw_decode(raw)
                return data if isinstance(data, dict) else {}
            except Exception:
                return {}
        except Exception:
            return {}

    def save(self, data):
        with open(self.file_path, 'w', encoding='utf-8') as file_handle:
            json.dump(data, file_handle, ensure_ascii=False, indent=2)

    def get_rules(self, lang):
        key = f'{normalize_language(lang)}_rules'
        rules = self.load().get(key, [])
        return rules if isinstance(rules, list) else []

    def set_rules(self, lang, rules):
        payload = self.load()
        payload[f'{normalize_language(lang)}_rules'] = rules
        self.save(payload)

    def delete_rule(self, lang, index):
        rules = list(self.get_rules(lang))
        if 0 <= index < len(rules):
            rules.pop(index)
            self.set_rules(lang, rules)

    def counts_by_language(self):
        return {lang: len(self.get_rules(lang)) for lang in LANGUAGES}


class DashboardStatsCollector:
    def collect(self, selected_language='az'):
        selected_language = normalize_language(selected_language)
        affix_manager = AffixManager()
        rule_manager = RuleManager()

        dictionary_counts = {}
        dictionary_previews = {}
        for lang in LANGUAGES:
            manager = DictionaryManager(lang)
            entries = manager.list_entries()
            dictionary_counts[lang] = len(entries)
            dictionary_previews[lang] = entries[:5]

        affixes = affix_manager.list_affixes()
        rule_counts = rule_manager.counts_by_language()

        language_cards = []
        for lang in LANGUAGES:
            language_cards.append({
                'code': lang,
                'label': LANGUAGE_LABELS[lang],
                'dictionary_count': dictionary_counts[lang],
                'rule_count': rule_counts[lang],
                'is_selected': lang == selected_language,
            })

        return {
            'selected_language': selected_language,
            'selected_language_label': LANGUAGE_LABELS[selected_language],
            'dictionaries': dictionary_counts,
            'dictionary_total': sum(dictionary_counts.values()),
            'affixes': len(affixes),
            'affix_preview': affixes[:5],
            'rules': sum(rule_counts.values()),
            'rules_by_language': rule_counts,
            'language_cards': language_cards,
            'selected_dictionary_preview': dictionary_previews[selected_language],
            'selected_rules_preview': rule_manager.get_rules(selected_language)[:5],
        }

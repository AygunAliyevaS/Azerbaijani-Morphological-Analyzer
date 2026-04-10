# text_input.py — шаблон модуля

# text_input.py — токенизация и предварительная обработка текстов

import re

def tokenize(text: str):
    """
    Простая токенизация текста:
    - разбивает на слова по пробелам и пунктуации
    - удаляет лишние символы
    - возвращает список токенов
    """
    tokens = re.findall(r"[a-zA-ZğüşöçıİĞÜŞÖÇƏə0-9]+", text, re.UNICODE)
    return tokens

def normalize(token: str):
    """
    Unicode-safe normalization for Azerbaijani and related languages:
    - trims surrounding whitespace
    - applies casefold for more robust case-insensitive matching
    """
    return token.strip().casefold()

def prepare_input(text: str):
    """
    Полный пайплайн подготовки:
    - токенизация
    - нормализация
    - возвращает список токенов
    """
    tokens = tokenize(text)
    return [normalize(tok) for tok in tokens]

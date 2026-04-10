import unittest

from ml_models import analyze_word


class AzerbaijaniAnalyzerTests(unittest.TestCase):
    def test_dictionary_word_still_resolves(self):
        result = analyze_word('kitab', 'az')
        self.assertEqual(result['POS'], 'NOUN')

    def test_common_azerbaijani_words_are_not_unknown(self):
        words = ['bu', 'və', 'müəllif']
        for word in words:
            with self.subTest(word=word):
                result = analyze_word(word, 'az')
                self.assertNotEqual(result['POS'], 'UNK')

    def test_predicative_forms_are_resolved(self):
        for word in ['maraqlıdır', 'gəncdir']:
            with self.subTest(word=word):
                result = analyze_word(word, 'az')
                self.assertNotEqual(result['POS'], 'UNK')
                self.assertIn('features', result)


if __name__ == '__main__':
    unittest.main()

import unittest

from data.evaluate_dataset import evaluate_examples, normalize_code


class DatasetEvaluationTest(unittest.TestCase):
    def test_normalize_code_ignores_trailing_whitespace(self):
        self.assertEqual(normalize_code("print('ok')  \n"), "print('ok')")

    def test_normalize_code_ignores_comment_text(self):
        self.assertEqual(
            normalize_code("result = 5 // 2  # old wording"),
            normalize_code("result = 5 // 2  # new wording"),
        )

    def test_evaluate_examples_reports_matches_and_failures(self):
        examples = [
            {
                "id": "match",
                "python2_code": "print 'hello'",
                "python3_code": "print('hello')",
                "category": "syntax",
                "difficulty": "easy",
                "pattern_type": "print_statement",
            },
            {
                "id": "miss",
                "python2_code": "import md5",
                "python3_code": "import hashlib",
                "category": "import",
                "difficulty": "medium",
                "pattern_type": "import_change",
            },
        ]

        summary = evaluate_examples(examples)

        self.assertEqual(summary["total"], 2)
        self.assertEqual(summary["normalized_matches"], 1)
        self.assertEqual(summary["by_category"]["syntax"]["matched"], 1)
        self.assertEqual(summary["by_category"]["import"]["matched"], 0)
        self.assertEqual(summary["failures"][0]["id"], "miss")


if __name__ == "__main__":
    unittest.main()

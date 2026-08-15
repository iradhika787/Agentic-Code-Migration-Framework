import unittest

from agents.analysis_agent import AnalysisAgent


class PythonAnalysisTest(unittest.TestCase):
    def test_analysis_flags_syntax_and_manual_review_risks(self):
        source = '''if data.has_key("name"):
    print >>sys.stderr, "Name:", data["name"]
    raise ValueError, "missing"
print 9 / 4
items = map(str, xrange(3))
print `items`
print 1 <> 2
'''

        issues = AnalysisAgent().analyze(source)
        issue_types = {issue["type"] for issue in issues}

        self.assertIn("dict_has_key", issue_types)
        self.assertIn("print_redirect_syntax", issue_types)
        self.assertIn("old_raise_syntax", issue_types)
        self.assertIn("division_semantics_risk", issue_types)
        self.assertIn("iterator_semantics_risk", issue_types)
        self.assertIn("backtick_repr", issue_types)
        self.assertIn("not_equal_operator", issue_types)


if __name__ == "__main__":
    unittest.main()

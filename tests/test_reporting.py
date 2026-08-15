import os
import tempfile
import unittest

from report_generator import generate_report


class ReportingTest(unittest.TestCase):
    def test_generate_report_writes_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = generate_report("sample.py", {"success": True, "attempts": 1, "issues_found": [], "execution_log": ["ok"], "diff": "", "verification_report": {}, "migrated_code": "print('ok')", "confidence_scores": {"overall": 0.9}}, output_path=os.path.join(tmpdir, "report.md"))
            self.assertTrue(os.path.exists(path))


if __name__ == "__main__":
    unittest.main()

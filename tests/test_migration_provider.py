import unittest

from agents.migration_agent import MigrationAgent
from plugins.python2_to_python3.plugin import Python2ToPython3Plugin


class StubProvider:
    def __init__(self):
        self.prompts = []

    def generate(self, prompt, **kwargs):
        self.prompts.append(prompt)
        return "```python\nprint('ok')\n```"


class MigrationProviderTest(unittest.TestCase):
    def test_migrate_uses_injected_provider(self):
        provider = StubProvider()
        agent = MigrationAgent(provider=provider)

        result = agent.migrate_with_provider("print 1", [{"line": 1, "type": "print_statement", "detail": "print 1"}])

        self.assertEqual(result, "print('ok')")
        self.assertEqual(len(provider.prompts), 1)

    def test_rule_based_migration_handles_common_python2_syntax(self):
        source = '''def process(items):
    try:
        for item in items:
            print "Processing:", item
    except Exception, e:
        print "Error occurred:", e

def greet(name):
    message = unicode("Hello, ") + name
    print message

greet(u"World")
process([1, 2, 3])'''
        agent = MigrationAgent()

        result = agent.migrate(source, [])

        expected = '''def process(items):
    try:
        for item in items:
            print("Processing:", item)
    except Exception as e:
        print("Error occurred:", e)

def greet(name):
    message = str("Hello, ") + name
    print(message)

greet("World")
process([1, 2, 3])'''
        self.assertEqual(result, expected)

    def test_plugin_uses_ai_fallback_after_rule_output_mismatch(self):
        provider = StubProvider()

        def generate(prompt, **kwargs):
            provider.prompts.append(prompt)
            return "```python\nprint(9 // 4)\n```"

        provider.generate = generate
        plugin = Python2ToPython3Plugin(migrator=MigrationAgent(provider=provider))

        result = plugin.run_pipeline("print 9 / 4", expected_output="2")

        self.assertTrue(result["success"])
        self.assertEqual(result["attempts"], 2)
        self.assertEqual(result["verification_report"]["actual_output"], "2")
        self.assertIn("AI fallback", "\n".join(result["execution_log"]))
        self.assertIn("Failed check: output_matches", provider.prompts[0])
        self.assertEqual(result["iteration_metrics"]["iterations_to_convergence"], 2)
        self.assertEqual(result["iteration_metrics"]["rule_based_attempts"], 1)
        self.assertEqual(result["iteration_metrics"]["ai_fallback_attempts"], 1)
        self.assertEqual(result["iteration_history"][0]["failed_checks"], ["output_matches"])

    def test_rule_based_migration_handles_more_python2_patterns(self):
        source = '''import cPickle
import ConfigParser
import Queue
from StringIO import StringIO

if data.has_key("name"):
    print >>sys.stderr, "Name:", data["name"]
if not cache.has_key(key):
    raise ValueError, "missing"

items = map(str, xrange(3))
print `items`
print type("x") == basestring
print file("sample.txt").read()
print 1 <> 2
'''
        agent = MigrationAgent()

        result = agent.migrate(source, [])

        expected = '''import pickle
import configparser
import queue
from io import StringIO

if "name" in data:
    print("Name:", data["name"], file=sys.stderr)
if key not in cache:
    raise ValueError("missing")

items = list(map(str, range(3)))
print(repr(items))
print(type("x") == str)
print(open("sample.txt").read())
print(1 != 2)'''
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()

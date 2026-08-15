import re


class MigrationAgent:
    """
    Takes source code + structured issues from the Analysis Agent,
    and produces a migrated (Python 3) version by routing the prompt
    through an injected provider backend.
    """

    def __init__(self, provider=None, model="qwen2.5-coder:7b"):
        self.model = model
        self.provider = provider

    def migrate(self, source_code: str, issues: list, previous_errors: list = None) -> str:
        if self.provider is None or previous_errors is None:
            return self.migrate_with_rules(source_code)

        return self.migrate_with_provider(source_code, issues, previous_errors)

    def migrate_with_rules(self, source_code: str) -> str:
        return self._apply_rule_based_migration(source_code)

    def migrate_with_provider(self, source_code: str, issues: list, previous_errors: list = None) -> str:
        provider = self.provider
        if provider is None:
            from providers.ollama_provider import OllamaProvider

            provider = OllamaProvider(model=self.model)
            self.provider = provider

        prompt = self._build_prompt(source_code, issues, previous_errors)
        response = provider.generate(prompt)
        return self._extract_code(response)

    def _apply_rule_based_migration(self, source_code: str) -> str:
        migrated_lines = []
        for line in source_code.splitlines():
            migrated_lines.append(self._migrate_line(line))
        return "\n".join(migrated_lines)

    def _migrate_line(self, line: str) -> str:
        line = self._migrate_imports(line)
        line = self._migrate_has_key(line)
        line = re.sub(r"\bexcept\s+(.+?),\s*([A-Za-z_][A-Za-z0-9_]*)\s*:", r"except \1 as \2:", line)
        line = re.sub(r"\braise\s+([A-Za-z_][A-Za-z0-9_\.]*)\s*,\s*(.+)$", r"raise \1(\2)", line)
        line = re.sub(r"\bxrange\s*\(", "range(", line)
        line = re.sub(r"\braw_input\s*\(", "input(", line)
        line = re.sub(r"\bunicode\s*\(", "str(", line)
        line = re.sub(r"\blong\s*\(", "int(", line)
        line = re.sub(r"\bbasestring\b", "str", line)
        line = re.sub(r"\bfile\s*\(", "open(", line)
        line = line.replace(".iteritems(", ".items(")
        line = line.replace(".iterkeys(", ".keys(")
        line = line.replace(".itervalues(", ".values(")
        line = line.replace("<>", "!=")
        line = re.sub(r"(?<![A-Za-z0-9_])u([\"'])", r"\1", line)
        line = re.sub(r"`([^`]+)`", r"repr(\1)", line)
        line = self._migrate_iterator_assignment(line)
        line = self._migrate_print(line)

        return line

    def _migrate_print(self, line: str) -> str:
        redirect_match = re.match(r"^(\s*)print\s*>>\s*([^,]+),\s*(.*)$", line)
        if redirect_match:
            indent, target, expression = redirect_match.groups()
            return f"{indent}print({expression}, file={target.strip()})"

        print_match = re.match(r"^(\s*)print\s+(?!\()(.*)$", line)
        if print_match and not print_match.group(2).lstrip().startswith(">>"):
            indent, expression = print_match.groups()
            expression = expression.rstrip()
            if expression.endswith(","):
                return f'{indent}print({expression[:-1].rstrip()}, end=" ")'
            return f"{indent}print({expression})"

        return line

    def _migrate_has_key(self, line: str) -> str:
        line = re.sub(
            r"not\s+([A-Za-z_][A-Za-z0-9_\.\[\]\"']*)\.has_key\(([^)]+)\)",
            r"\2 not in \1",
            line,
        )
        return re.sub(
            r"([A-Za-z_][A-Za-z0-9_\.\[\]\"']*)\.has_key\(([^)]+)\)",
            r"\2 in \1",
            line,
        )

    def _migrate_imports(self, line: str) -> str:
        line = re.sub(r"^(\s*)import\s+cPickle\b", r"\1import pickle", line)
        line = re.sub(r"\bfrom\s+cPickle\s+import\b", "from pickle import", line)
        line = re.sub(r"\bcPickle\.", "pickle.", line)

        line = re.sub(r"^(\s*)import\s+ConfigParser\b", r"\1import configparser", line)
        line = re.sub(r"\bfrom\s+ConfigParser\s+import\b", "from configparser import", line)
        line = re.sub(r"\bConfigParser\.", "configparser.", line)

        line = re.sub(r"^(\s*)import\s+Queue\b", r"\1import queue", line)
        line = re.sub(r"\bfrom\s+Queue\s+import\b", "from queue import", line)
        line = re.sub(r"\bQueue\.", "queue.", line)

        line = re.sub(r"\bfrom\s+cStringIO\s+import\s+StringIO\b", "from io import StringIO", line)
        line = re.sub(r"\bfrom\s+StringIO\s+import\s+StringIO\b", "from io import StringIO", line)
        line = re.sub(r"^(\s*)import\s+cStringIO\b", r"\1import io", line)
        line = re.sub(r"^(\s*)import\s+StringIO\b", r"\1import io", line)
        line = re.sub(r"\bcStringIO\.StringIO\b", "io.StringIO", line)
        line = re.sub(r"\bStringIO\.StringIO\b", "io.StringIO", line)

        return line

    def _migrate_iterator_assignment(self, line: str) -> str:
        match = re.match(r"^(\s*[A-Za-z_][A-Za-z0-9_]*\s*=\s*)(map|filter|zip)\((.*)\)\s*$", line)
        if match:
            prefix, func, args = match.groups()
            return f"{prefix}list({func}({args}))"

        return line

    def _build_prompt(self, source_code, issues, previous_errors=None):
        issues_text = "\n".join(
            f"- Line {i['line']}: {i['type']} -> {i['detail']}"
            for i in issues
        )

        error_feedback = ""
        if previous_errors:
            errors_text = "\n".join(previous_errors)
            error_feedback = f"""
Your previous migration attempt failed verification with these errors:
{errors_text}

Fix these errors in this attempt.
"""

        return f"""You are a code migration assistant. Convert the following Python 2 code to valid Python 3 code.

Static analysis found these specific issues to fix:
{issues_text}
{error_feedback}
Original Python 2 code:
```python
{source_code}
```

Rules:
- Fix ONLY what's needed for Python 3 compatibility, based on the issues listed.
- Preserve all other logic and structure exactly.
- Output ONLY the migrated Python 3 code inside a single ```python code block, nothing else.
"""

    def _extract_code(self, raw_response: str) -> str:
        # Pull code out of the ```python ... ``` block the model returns
        if "```python" in raw_response:
            code = raw_response.split("```python")[1].split("```")[0]
        elif "```" in raw_response:
            code = raw_response.split("```")[1].split("```")[0]
        else:
            code = raw_response
        return code.strip()


if __name__ == "__main__":
    import sys
    sys.path.append("..")
    from analysis_agent import AnalysisAgent

    with open(sys.argv[1]) as f:
        source = f.read()

    analyzer = AnalysisAgent()
    issues = analyzer.analyze(source)

    migrator = MigrationAgent()
    migrated_code = migrator.migrate(source, issues)

    print("---- MIGRATED CODE ----")
    print(migrated_code)

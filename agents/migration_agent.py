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
        lines = source_code.splitlines()
        index = 0
        while index < len(lines):
            metaclass_line = self._migrate_metaclass_block(lines, index)
            if metaclass_line is not None:
                migrated_lines.append(metaclass_line)
                index += 2
                continue

            line = lines[index]
            migrated_lines.append(self._migrate_line(line))
            index += 1
        return "\n".join(migrated_lines)

    def _migrate_metaclass_block(self, lines: list[str], index: int) -> str | None:
        if index + 1 >= len(lines):
            return None

        class_match = re.match(
            r"^(\s*)class\s+([A-Za-z_][A-Za-z0-9_]*)(?:\(object\))?:\s*$",
            lines[index],
        )
        meta_match = re.match(
            r"^\s+__metaclass__\s*=\s*([A-Za-z_][A-Za-z0-9_]*)\s*$",
            lines[index + 1],
        )
        if not class_match or not meta_match:
            return None

        indent, class_name = class_match.groups()
        metaclass_name = meta_match.group(1)
        return f"{indent}class {class_name}(metaclass={metaclass_name}):"

    def _migrate_line(self, line: str) -> str:
        line = self._migrate_imports(line)
        line = self._migrate_strings_and_classes(line)
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
        line = self._migrate_division(line)
        line = self._migrate_iterator_assignment(line)
        line = self._migrate_print(line)

        return line

    def _migrate_print(self, line: str) -> str:
        """
        Migrate Python 2 print statements to Python 3 print() function.
        Handles:
        - print >> file, expr
        - print expr  (with or without trailing comma)
        - print "string", var, ...
        """
        # First check if this is even a print statement and not an assignment or function call
        if not re.search(r"\bprint\b", line):
            return line
        
        # If it's "print(" or "print =", it's not a Python 2 print statement
        if re.search(r"\bprint\s*[\(=]", line):
            return line
        
        # Pattern 1: print >> file, expr  (print with redirect)
        redirect_match = re.match(r"^(\s*)print\s*>>\s*([^,]+),\s*(.*)$", line)
        if redirect_match:
            indent, target, expression = redirect_match.groups()
            return f"{indent}print({expression}, file={target.strip()})"

        # Pattern 2: General print statement (anything after print that's not parenthesis)
        # Match: "print" + whitespace + anything else until end of line or comment
        print_match = re.match(r"^(\s*)print\s+(?!\(|=)(.*?)(?:\s*#|$)", line)
        if print_match:
            indent, expression = print_match.groups()
            expression = expression.rstrip()
            
            if not expression:
                return line
            
            # Handle trailing comma (print expr,) -> print(expr, end='')
            if expression.endswith(","):
                return f"{indent}print({expression[:-1].rstrip()}, end=' ')"
            
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

        line = re.sub(r"^(\s*)import\s+urllib2\b", r"\1import urllib.request", line)
        line = re.sub(r"\bfrom\s+urllib2\s+import\b", "from urllib.request import", line)
        line = re.sub(r"\bfrom\s+urllib\s+import\s+urlencode\b", "from urllib.parse import urlencode", line)
        line = re.sub(r"\burllib2\.", "urllib.request.", line)

        line = re.sub(
            r"\bfrom\s+django\.utils\.encoding\s+import\s+smart_unicode\b",
            "from django.utils.encoding import smart_str",
            line,
        )
        line = re.sub(r"\bSafeConfigParser\b", "ConfigParser", line)

        line = re.sub(r"\bfrom\s+cStringIO\s+import\s+StringIO\b", "from io import StringIO", line)
        line = re.sub(r"\bfrom\s+StringIO\s+import\s+StringIO\b", "from io import StringIO", line)
        line = re.sub(r"^(\s*)import\s+cStringIO\b", r"\1import io", line)
        line = re.sub(r"^(\s*)import\s+StringIO\b", r"\1import io", line)
        line = re.sub(r"\bcStringIO\.StringIO\b", "io.StringIO", line)
        line = re.sub(r"\bStringIO\.StringIO\b", "io.StringIO", line)

        return line

    def _migrate_strings_and_classes(self, line: str) -> str:
        line = re.sub(r"^(\s*class\s+[A-Za-z_][A-Za-z0-9_]*)\(object\)(\s*:)", r"\1\2", line)
        line = re.sub(r"(\b[A-Za-z_][A-Za-z0-9_\.]*\.text)\.encode\(['\"]utf-8['\"]\)", r"\1", line)
        line = re.sub(r"(['\"][^'\"]*['\"])\.decode\(['\"]utf-8['\"]\)", r"\1", line)
        line = re.sub(r"=\s*'((?:\\x[0-9a-fA-F]{2})+)'", r"= b'\1'", line)
        line = re.sub(
            r"^(\s*[A-Za-z_][A-Za-z0-9_]*\s*=\s*)dict\(\(([^,]+),\s*([^)]+)\)\s+for\s+(.+)\)$",
            r"\1{\2: \3 for \4}",
            line,
        )
        return line

    def _migrate_division(self, line: str) -> str:
        """
        Convert Python 2 division to Python 3.
        In Python 2: 2 / 3 = 0 (integer division)
        In Python 3: 2 / 3 = 0.666... (float division), 2 // 3 = 0 (integer division)
        
        For integer literals divided by integer literals, convert / to //.
        This is conservative - we only convert when both operands are clearly integers.
        """
        # Pattern: integer / integer (e.g., 2 / 3, 10/5)
        # This handles both "2/3" and "2 / 3" formats
        line = re.sub(
            r"(?<![A-Za-z0-9_\.])(\d+)\s*/\s*(\d+)(?![A-Za-z0-9_\.])",
            r"\1 // \2",
            line
        )
        return line

    def _migrate_iterator_assignment(self, line: str) -> str:
        match = re.match(r"^(\s*[A-Za-z_][A-Za-z0-9_]*\s*=\s*)(map|filter|zip)\((.*)\)\s*$", line)
        if match:
            prefix, func, args = match.groups()
            return f"{prefix}list({func}({args}))"

        expression_match = re.match(r"^(\s*)(map|filter|zip)\((.*)\)\s*$", line)
        if expression_match:
            indent, func, args = expression_match.groups()
            return f"{indent}list({func}({args}))"

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

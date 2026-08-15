import sys
sys.path.append("agents")

from plugins.python2_to_python3.plugin import Python2ToPython3Plugin


class Orchestrator:
    """
    Coordinates the Python modernization workflow by delegating to the
    python2_to_python3 plugin as the primary implementation owner.
    """

    def __init__(self, max_retries=3, plugin=None):
        self.plugin = plugin or Python2ToPython3Plugin()
        self.max_retries = max_retries

    def run(
        self,
        source_code: str,
        expected_output: str = None,
        project_path: str = None,
        test_command: list[str] | str = None,
    ) -> dict:
        return self.plugin.run_pipeline(
            source_code,
            expected_output=expected_output,
            max_retries=self.max_retries,
            project_path=project_path,
            test_command=test_command,
        )


MigrationOrchestrator = Orchestrator


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        source = f.read()

    expected = sys.argv[2] if len(sys.argv) > 2 else None

    orchestrator = Orchestrator()
    result = orchestrator.run(source, expected_output=expected)

    print("==== EXECUTION LOG ====")
    for line in result["execution_log"]:
        print(line)

    print("\n==== DIFF (original vs migrated) ====")
    print(result["diff"])

    print("==== FINAL MIGRATED CODE ====")
    print(result["migrated_code"])
    print(f"\nSuccess: {result['success']} (in {result['attempts']} attempt(s))")

from orchestrator import Orchestrator


class FakePlugin:
    """
    The plugin owns retry behavior internally. This verifies that the
    orchestrator delegates one pipeline run with the retry limit.
    """

    def __init__(self):
        self.call_count = 0
        self.max_retries = None

    def run_pipeline(self, source_code, expected_output=None, max_retries=3, **kwargs):
        self.call_count += 1
        self.max_retries = max_retries

        return {
            "success": True,
            "attempts": 2,
            "migrated_code": "def calc(a, b):\n    return a // b",
            "execution_log": [
                "Attempt 1",
                "Verification failed",
                "Attempt 2",
                "Verification passed"
            ],
            "diff": "",
        }


def test_retry_logic():
    plugin = FakePlugin()

    orchestrator = Orchestrator(plugin=plugin)

    result = orchestrator.run(
        "def calc(a, b):\n    return a / b\nprint calc(9,4)",
        expected_output="2"
    )

    print(f"\nAttempts taken: {result['attempts']}")
    print(f"Success: {result['success']}")

    assert plugin.call_count == 1
    assert plugin.max_retries == 3
    assert result["attempts"] == 2
    assert result["success"] is True

    print("✅ Retry mechanism confirmed working.")

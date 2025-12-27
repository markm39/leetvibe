"""
Base Test Runner for LeetVibe

Abstract base class that defines the interface for language-specific test runners.
Each runner must implement methods to compile (if needed) and run test cases.
"""

import json
import subprocess
import tempfile
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class TestResult:
    """Result of running a single test case."""
    passed: bool
    input_data: Any
    expected: Any
    actual: Any
    error: str | None = None
    execution_time_ms: float = 0


@dataclass
class RunResult:
    """Result of running all test cases."""
    total: int
    passed: int
    failed: int
    results: list[TestResult]
    compile_error: str | None = None

    @property
    def all_passed(self) -> bool:
        return self.passed == self.total and self.compile_error is None

    @property
    def score(self) -> float:
        return self.passed / self.total if self.total > 0 else 0.0


class BaseRunner(ABC):
    """Abstract base class for language-specific test runners."""

    # Timeout for each test case execution (seconds)
    TIMEOUT_SECONDS = 5

    # Memory limit (not enforced on all platforms)
    MEMORY_LIMIT_MB = 256

    def __init__(self, solution_path: Path, test_cases: dict):
        """
        Initialize the runner.

        Args:
            solution_path: Path to the solution file
            test_cases: Dict with 'function_name' and 'test_cases' keys
        """
        self.solution_path = solution_path
        self.function_name = test_cases.get('function_name', 'solve')
        self.test_cases = test_cases.get('test_cases', [])
        self.temp_dir = None

    @property
    @abstractmethod
    def language(self) -> str:
        """Return the language name (e.g., 'python', 'typescript')."""
        pass

    @property
    @abstractmethod
    def file_extensions(self) -> list[str]:
        """Return supported file extensions (e.g., ['.py'])."""
        pass

    @abstractmethod
    def compile(self) -> tuple[bool, str | None]:
        """
        Compile the solution if needed.

        Returns:
            Tuple of (success, error_message)
        """
        pass

    @abstractmethod
    def run_single_test(self, input_data: list, expected: Any) -> TestResult:
        """
        Run a single test case.

        Args:
            input_data: List of input arguments
            expected: Expected output

        Returns:
            TestResult with pass/fail status
        """
        pass

    def run_all_tests(self) -> RunResult:
        """Run all test cases and return results."""
        # First compile if needed
        compile_success, compile_error = self.compile()
        if not compile_success:
            return RunResult(
                total=len(self.test_cases),
                passed=0,
                failed=len(self.test_cases),
                results=[],
                compile_error=compile_error
            )

        # Run each test case
        results = []
        for test_case in self.test_cases:
            input_data = test_case.get('input', [])
            expected = test_case.get('expected')
            result = self.run_single_test(input_data, expected)
            results.append(result)

        passed = sum(1 for r in results if r.passed)
        return RunResult(
            total=len(results),
            passed=passed,
            failed=len(results) - passed,
            results=results
        )

    def cleanup(self):
        """Clean up any temporary files."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _run_process(self, cmd: list[str], input_data: str = None,
                     timeout: float = None) -> tuple[str, str, int]:
        """
        Run a subprocess with timeout.

        Returns:
            Tuple of (stdout, stderr, return_code)
        """
        timeout = timeout or self.TIMEOUT_SECONDS
        try:
            result = subprocess.run(
                cmd,
                input=input_data,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return '', f'Timeout: exceeded {timeout}s', -1
        except Exception as e:
            return '', str(e), -1

    def _values_equal(self, expected: Any, actual: Any) -> bool:
        """Compare expected and actual values with type flexibility."""
        # Handle None
        if expected is None:
            return actual is None

        # Handle numeric comparison (int/float)
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            if isinstance(expected, float) or isinstance(actual, float):
                return abs(expected - actual) < 1e-9
            return expected == actual

        # Handle lists/arrays (order matters)
        if isinstance(expected, list) and isinstance(actual, list):
            if len(expected) != len(actual):
                return False
            return all(self._values_equal(e, a) for e, a in zip(expected, actual))

        # Handle dicts
        if isinstance(expected, dict) and isinstance(actual, dict):
            if set(expected.keys()) != set(actual.keys()):
                return False
            return all(self._values_equal(expected[k], actual[k]) for k in expected)

        # Handle sets (convert to sorted lists)
        if isinstance(expected, set) and isinstance(actual, set):
            return expected == actual

        # Default comparison
        return expected == actual

    def format_results(self, run_result: RunResult) -> str:
        """Format results for display."""
        lines = []

        if run_result.compile_error:
            lines.append("COMPILE ERROR:")
            lines.append(run_result.compile_error)
            lines.append("")

        lines.append(f"Results: {run_result.passed}/{run_result.total} tests passed")
        lines.append("")

        for i, result in enumerate(run_result.results, 1):
            status = "PASS" if result.passed else "FAIL"
            lines.append(f"Test {i}: {status}")
            lines.append(f"  Input:    {json.dumps(result.input_data)}")
            lines.append(f"  Expected: {json.dumps(result.expected)}")
            if not result.passed:
                lines.append(f"  Actual:   {json.dumps(result.actual)}")
                if result.error:
                    lines.append(f"  Error:    {result.error}")
            lines.append("")

        if run_result.all_passed:
            lines.append("All tests passed!")
        else:
            lines.append(f"Score: {run_result.score:.0%}")

        return "\n".join(lines)

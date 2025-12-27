"""
Python Test Runner for LeetVibe
"""

import json
import tempfile
import time
from pathlib import Path
from typing import Any

from .base_runner import BaseRunner, TestResult


class PythonRunner(BaseRunner):
    """Test runner for Python solutions."""

    @property
    def language(self) -> str:
        return "python"

    @property
    def file_extensions(self) -> list[str]:
        return [".py"]

    def compile(self) -> tuple[bool, str | None]:
        """Python doesn't need compilation, just syntax check."""
        # Do a syntax check by trying to compile the file
        try:
            with open(self.solution_path, 'r') as f:
                source = f.read()
            compile(source, str(self.solution_path), 'exec')
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, str(e)

    def run_single_test(self, input_data: list, expected: Any) -> TestResult:
        """Run a single test case using Python."""
        start_time = time.time()

        # Read the solution code directly to avoid import issues with numeric filenames
        with open(self.solution_path, 'r') as f:
            solution_code = f.read()

        # Create a test wrapper script that includes the solution inline
        wrapper = f'''
import json
import sys

# Solution code (included directly to avoid import issues)
{solution_code}

# Parse input
input_data = json.loads(sys.argv[1])

# Call the function
result = {self.function_name}(*input_data)

# Output result as JSON
print(json.dumps(result))
'''

        # Write wrapper to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(wrapper)
            wrapper_path = f.name

        try:
            stdout, stderr, returncode = self._run_process(
                ['python3', wrapper_path, json.dumps(input_data)]
            )

            execution_time = (time.time() - start_time) * 1000

            if returncode != 0:
                return TestResult(
                    passed=False,
                    input_data=input_data,
                    expected=expected,
                    actual=None,
                    error=stderr.strip() or "Runtime error",
                    execution_time_ms=execution_time
                )

            try:
                actual = json.loads(stdout.strip())
            except json.JSONDecodeError:
                return TestResult(
                    passed=False,
                    input_data=input_data,
                    expected=expected,
                    actual=stdout.strip(),
                    error="Invalid output format",
                    execution_time_ms=execution_time
                )

            passed = self._values_equal(expected, actual)
            return TestResult(
                passed=passed,
                input_data=input_data,
                expected=expected,
                actual=actual,
                execution_time_ms=execution_time
            )

        finally:
            Path(wrapper_path).unlink(missing_ok=True)

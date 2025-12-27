"""
Swift Test Runner for LeetVibe
"""

import json
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any

from .base_runner import BaseRunner, TestResult


class SwiftRunner(BaseRunner):
    """Test runner for Swift solutions."""

    @property
    def language(self) -> str:
        return "swift"

    @property
    def file_extensions(self) -> list[str]:
        return [".swift"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.temp_dir = tempfile.mkdtemp()

    def compile(self) -> tuple[bool, str | None]:
        """Swift can be run directly with 'swift' command."""
        if not shutil.which('swift'):
            return False, "Swift compiler not found"

        # Syntax check by trying to parse
        stdout, stderr, returncode = self._run_process([
            'swift', '-parse', str(self.solution_path)
        ], timeout=10)

        if returncode != 0:
            return False, stderr.strip() or "Swift syntax error"

        return True, None

    def run_single_test(self, input_data: list, expected: Any) -> TestResult:
        """Run a single test case using Swift."""
        start_time = time.time()

        # Read the solution file
        with open(self.solution_path, 'r') as f:
            solution_code = f.read()

        # Create wrapper script
        wrapper = f'''
import Foundation

// Solution code
{solution_code}

// Parse command line argument as JSON
let inputJson = CommandLine.arguments[1]
guard let inputData = inputJson.data(using: .utf8),
      let input = try? JSONSerialization.jsonObject(with: inputData) as? [Any] else {{
    fputs("Failed to parse input\\n", stderr)
    exit(1)
}}

// Call the function (assuming single argument for now)
let result: Any
if input.count == 1 {{
    if let intArg = input[0] as? Int {{
        result = {self.function_name}(intArg)
    }} else if let strArg = input[0] as? String {{
        result = {self.function_name}(strArg)
    }} else if let arrArg = input[0] as? [Int] {{
        result = {self.function_name}(arrArg)
    }} else {{
        fputs("Unsupported input type\\n", stderr)
        exit(1)
    }}
}} else {{
    fputs("Multiple arguments not yet supported\\n", stderr)
    exit(1)
}}

// Output as JSON
if let jsonData = try? JSONSerialization.data(withJSONObject: result),
   let jsonString = String(data: jsonData, encoding: .utf8) {{
    print(jsonString)
}} else {{
    // Handle primitive types
    print(result)
}}
'''

        wrapper_path = Path(self.temp_dir) / 'wrapper.swift'
        with open(wrapper_path, 'w') as f:
            f.write(wrapper)

        try:
            stdout, stderr, returncode = self._run_process([
                'swift', str(wrapper_path), json.dumps(input_data)
            ])

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
                # Try parsing as a simple value
                output = stdout.strip()
                try:
                    actual = int(output)
                except ValueError:
                    try:
                        actual = float(output)
                    except ValueError:
                        actual = output

            passed = self._values_equal(expected, actual)
            return TestResult(
                passed=passed,
                input_data=input_data,
                expected=expected,
                actual=actual,
                execution_time_ms=execution_time
            )

        finally:
            wrapper_path.unlink(missing_ok=True)

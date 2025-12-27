"""
TypeScript/JavaScript Test Runner for LeetVibe
"""

import json
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any

from .base_runner import BaseRunner, TestResult


class TypeScriptRunner(BaseRunner):
    """Test runner for TypeScript/JavaScript solutions."""

    @property
    def language(self) -> str:
        return "typescript"

    @property
    def file_extensions(self) -> list[str]:
        return [".ts", ".tsx", ".js", ".jsx"]

    def _find_executor(self) -> tuple[str, list[str]] | None:
        """Find available TypeScript/JavaScript executor."""
        # Try tsx first (fastest for TS)
        if shutil.which('tsx'):
            return 'tsx', []
        # Try ts-node
        if shutil.which('ts-node'):
            return 'ts-node', []
        # Try npx tsx
        if shutil.which('npx'):
            return 'npx', ['tsx']
        # Try bun
        if shutil.which('bun'):
            return 'bun', ['run']
        # Try node (for JS only)
        if shutil.which('node') and self.solution_path.suffix in ['.js', '.jsx']:
            return 'node', []
        return None

    def compile(self) -> tuple[bool, str | None]:
        """TypeScript syntax check."""
        executor = self._find_executor()
        if not executor:
            return False, "No TypeScript executor found (tsx, ts-node, bun, or node)"

        # For TypeScript, we can do a quick type check
        if self.solution_path.suffix in ['.ts', '.tsx']:
            if shutil.which('tsc'):
                stdout, stderr, returncode = self._run_process(
                    ['tsc', '--noEmit', str(self.solution_path)],
                    timeout=10
                )
                if returncode != 0:
                    return False, stderr.strip() or "TypeScript compilation failed"

        return True, None

    def run_single_test(self, input_data: list, expected: Any) -> TestResult:
        """Run a single test case using TypeScript/JavaScript."""
        start_time = time.time()

        executor = self._find_executor()
        if not executor:
            return TestResult(
                passed=False,
                input_data=input_data,
                expected=expected,
                actual=None,
                error="No TypeScript executor found",
                execution_time_ms=0
            )

        exe, args = executor

        # Create a test wrapper script
        # Use dynamic import for ES modules compatibility
        wrapper = f'''
import {{ {self.function_name} }} from "{self.solution_path.absolute()}";

const inputData = JSON.parse(process.argv[2]);
const result = {self.function_name}(...inputData);
console.log(JSON.stringify(result));
'''

        # Create temp file with appropriate extension
        ext = '.ts' if self.solution_path.suffix in ['.ts', '.tsx'] else '.js'
        with tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False) as f:
            f.write(wrapper)
            wrapper_path = f.name

        try:
            cmd = [exe] + args + [wrapper_path, json.dumps(input_data)]
            stdout, stderr, returncode = self._run_process(cmd)

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

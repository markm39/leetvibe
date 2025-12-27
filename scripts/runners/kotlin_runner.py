"""
Kotlin Test Runner for LeetVibe
"""

import json
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any

from .base_runner import BaseRunner, TestResult


class KotlinRunner(BaseRunner):
    """Test runner for Kotlin solutions."""

    @property
    def language(self) -> str:
        return "kotlin"

    @property
    def file_extensions(self) -> list[str]:
        return [".kt", ".kts"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.temp_dir = tempfile.mkdtemp()
        self.jar_path = None

    def _find_kotlin(self) -> tuple[str, str] | None:
        """Find Kotlin compiler and runner."""
        kotlinc = shutil.which('kotlinc')
        kotlin = shutil.which('kotlin')
        if kotlinc and kotlin:
            return kotlinc, kotlin
        return None

    def compile(self) -> tuple[bool, str | None]:
        """Compile Kotlin to JAR."""
        kt = self._find_kotlin()
        if not kt:
            return False, "Kotlin compiler not found (kotlinc)"

        kotlinc, _ = kt
        self.jar_path = Path(self.temp_dir) / 'solution.jar'

        # Read the solution
        with open(self.solution_path, 'r') as f:
            solution_code = f.read()

        # Create wrapper with main function
        wrapper = f'''
import com.google.gson.Gson

{solution_code}

fun main(args: Array<String>) {{
    val gson = Gson()
    val input = gson.fromJson(args[0], List::class.java)

    // Call the solution function
    val result = when (input.size) {{
        1 -> {{
            val arg = input[0]
            when (arg) {{
                is Number -> {self.function_name}(arg.toInt())
                is String -> {self.function_name}(arg)
                is List<*> -> {self.function_name}(arg.map {{ (it as Number).toInt() }})
                else -> throw IllegalArgumentException("Unsupported type")
            }}
        }}
        else -> throw IllegalArgumentException("Multiple args not supported")
    }}

    println(gson.toJson(result))
}}
'''

        wrapper_path = Path(self.temp_dir) / 'Wrapper.kt'
        with open(wrapper_path, 'w') as f:
            f.write(wrapper)

        # Try to compile (might fail if Gson not available)
        stdout, stderr, returncode = self._run_process([
            kotlinc,
            '-include-runtime',
            '-d', str(self.jar_path),
            str(wrapper_path)
        ], timeout=60)

        if returncode != 0:
            # Try simpler version without Gson
            simple_wrapper = f'''
{solution_code}

fun main(args: Array<String>) {{
    // Simple single-int argument support
    val input = args[0].trim('[', ']').toIntOrNull()
    if (input != null) {{
        val result = {self.function_name}(input)
        println(result)
    }} else {{
        System.err.println("Only integer inputs supported in simple mode")
    }}
}}
'''
            with open(wrapper_path, 'w') as f:
                f.write(simple_wrapper)

            stdout, stderr, returncode = self._run_process([
                kotlinc,
                '-include-runtime',
                '-d', str(self.jar_path),
                str(wrapper_path)
            ], timeout=60)

            if returncode != 0:
                return False, stderr.strip() or "Kotlin compilation failed"

        return True, None

    def run_single_test(self, input_data: list, expected: Any) -> TestResult:
        """Run a single test case."""
        if not self.jar_path or not self.jar_path.exists():
            return TestResult(
                passed=False,
                input_data=input_data,
                expected=expected,
                actual=None,
                error="Compilation required first",
                execution_time_ms=0
            )

        kt = self._find_kotlin()
        if not kt:
            return TestResult(
                passed=False,
                input_data=input_data,
                expected=expected,
                actual=None,
                error="Kotlin runtime not found",
                execution_time_ms=0
            )

        _, kotlin = kt
        start_time = time.time()

        stdout, stderr, returncode = self._run_process([
            'java', '-jar', str(self.jar_path), json.dumps(input_data)
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

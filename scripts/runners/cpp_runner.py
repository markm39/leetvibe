"""
C++ Test Runner for LeetVibe
"""

import json
import shutil
import tempfile
import time
import os
from pathlib import Path
from typing import Any

from .base_runner import BaseRunner, TestResult


class CppRunner(BaseRunner):
    """Test runner for C++ solutions."""

    @property
    def language(self) -> str:
        return "cpp"

    @property
    def file_extensions(self) -> list[str]:
        return [".cpp", ".cc", ".cxx"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.executable_path = None
        self.temp_dir = tempfile.mkdtemp()

    def _find_compiler(self) -> str | None:
        """Find available C++ compiler."""
        for compiler in ['clang++', 'g++', 'c++']:
            if shutil.which(compiler):
                return compiler
        return None

    def compile(self) -> tuple[bool, str | None]:
        """Compile the C++ solution."""
        compiler = self._find_compiler()
        if not compiler:
            return False, "No C++ compiler found (clang++, g++, or c++)"

        self.executable_path = Path(self.temp_dir) / 'solution'

        # Create wrapper that includes the solution and test harness
        wrapper_code = f'''
#include <iostream>
#include <string>
#include <vector>
#include <sstream>

// Include the solution
#include "{self.solution_path.absolute()}"

// Simple JSON parsing for basic types
#include <nlohmann/json.hpp>
using json = nlohmann::json;

int main(int argc, char* argv[]) {{
    if (argc < 2) {{
        std::cerr << "No input provided" << std::endl;
        return 1;
    }}

    try {{
        json input = json::parse(argv[1]);

        // Call the solution function
        auto result = {self.function_name}(input[0].get<decltype(input[0])>());

        // Output result as JSON
        json output = result;
        std::cout << output.dump() << std::endl;
    }} catch (const std::exception& e) {{
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }}

    return 0;
}}
'''

        # For simplicity, generate a self-contained wrapper without nlohmann/json dependency
        # Use a simpler approach that handles basic types
        simple_wrapper = f'''
#include <iostream>
#include <string>
#include <vector>
#include <sstream>

// Include the solution
#include "{self.solution_path.absolute()}"

int main(int argc, char* argv[]) {{
    if (argc < 2) {{
        std::cerr << "No input provided" << std::endl;
        return 1;
    }}

    // For now, this is a placeholder
    // Full JSON parsing would require a library or custom implementation
    std::cerr << "C++ runner requires manual test setup" << std::endl;
    return 1;
}}
'''

        wrapper_path = Path(self.temp_dir) / 'wrapper.cpp'
        with open(wrapper_path, 'w') as f:
            f.write(simple_wrapper)

        # Compile with common flags
        stdout, stderr, returncode = self._run_process([
            compiler,
            '-std=c++17',
            '-O2',
            '-o', str(self.executable_path),
            str(wrapper_path),
            f'-I{self.solution_path.parent}'
        ], timeout=30)

        if returncode != 0:
            return False, stderr.strip() or "Compilation failed"

        return True, None

    def run_single_test(self, input_data: list, expected: Any) -> TestResult:
        """Run a single test case."""
        if not self.executable_path or not self.executable_path.exists():
            return TestResult(
                passed=False,
                input_data=input_data,
                expected=expected,
                actual=None,
                error="Compilation required first",
                execution_time_ms=0
            )

        start_time = time.time()

        stdout, stderr, returncode = self._run_process([
            str(self.executable_path),
            json.dumps(input_data)
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

#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

TEST_DIR = Path(".")  # or "tests" if you want only the tests/ subfolder

def find_test_files():
    """Find all test_*.py files recursively."""
    return sorted(TEST_DIR.glob("**/*Test.py"))

def run_test_file(filepath: Path) -> bool:
    """Run pytest on a single file. Return True if segfault/crash detected."""
    print(f"· Running {filepath} ... ", end="", flush=True)

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-ra", str(filepath)],
            env={**dict(**os.environ), "PYTHONFAULTHANDLER": "1"},  # enable crash reporting
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except Exception as e:
        print(f"Exception: {e}")
        return True  # treat exceptions as crash

    # Check for typical segfault signs
    stdout_stderr = result.stdout + result.stderr
    crashed = (
            result.returncode < 0 or   # Negative returncode: died by signal (SIGSEGV = -11)
            "Segmentation fault" in stdout_stderr or
            "Fatal Python error" in stdout_stderr or
            "Aborted" in stdout_stderr
    )

    if crashed:
        print("✗ CRASHED")
    else:
        print("✓ OK")

    return crashed

def main():
    test_files = find_test_files()
    if not test_files:
        print("No test files found.")
        sys.exit(1)

    crashed = []

    for f in test_files:
        if run_test_file(f):
            crashed.append(f)

    print("\nSummary")
    print("-------")
    print(f"Total files tested: {len(test_files)}")
    print(f"Files crashed    : {len(crashed)}")

    if crashed:
        print("\nFiles that crashed:")
        for f in crashed:
            print(f" - {f}")

    sys.exit(1 if crashed else 0)

if __name__ == "__main__":
    import os
    main()

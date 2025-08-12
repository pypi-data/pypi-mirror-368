#!/usr/bin/env python3
"""
Test runner for the Mosaia Python SDK.

This script provides a comprehensive test runner that can be used to run
all tests, specific test categories, or individual test files.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --config          # Run only config tests
    python run_tests.py --types           # Run only type tests
    python run_tests.py --client          # Run only client tests
    python run_tests.py --collections     # Run only collection tests
    python run_tests.py --coverage        # Run tests with coverage
    python run_tests.py --verbose         # Run tests with verbose output
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'=' * 60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print(f"{'=' * 60}\n")

    try:
        result = subprocess.run(command, check=True, capture_output=False)
        print(f"\n✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False


def run_pytest_with_args(args, description):
    """Run pytest with specific arguments."""
    pytest_args = ["python", "-m", "pytest"]

    if args.verbose:
        pytest_args.append("-v")

    if args.coverage:
        pytest_args.extend(["--cov=mosaia", "--cov-report=html", "--cov-report=term"])

    if args.args:
        pytest_args.extend(args.args)

    return run_command(pytest_args, description)


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run Mosaia Python SDK tests")
    parser.add_argument(
        "--config", action="store_true", help="Run only configuration tests"
    )
    parser.add_argument("--types", action="store_true", help="Run only type tests")
    parser.add_argument("--client", action="store_true", help="Run only client tests")
    parser.add_argument(
        "--collections", action="store_true", help="Run only collection tests"
    )
    parser.add_argument(
        "--auth", action="store_true", help="Run only authentication tests"
    )
    parser.add_argument("--models", action="store_true", help="Run only model tests")
    parser.add_argument(
        "--functions", action="store_true", help="Run only function tests"
    )
    parser.add_argument("--utils", action="store_true", help="Run only utility tests")
    parser.add_argument(
        "--coverage", action="store_true", help="Run tests with coverage"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Run tests with verbose output"
    )
    parser.add_argument(
        "--args", nargs=argparse.REMAINDER, help="Additional pytest arguments"
    )

    args = parser.parse_args()

    # Change to the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    print("🚀 Mosaia Python SDK Test Runner")
    print(f"Project root: {project_root}")

    # Determine which tests to run
    if args.config:
        run_pytest_with_args(args, "Configuration tests", "tests/test_config.py")
    elif args.types:
        run_pytest_with_args(args, "Type tests", "tests/test_types.py")
    elif args.client:
        run_pytest_with_args(args, "Client tests", "tests/test_client.py")
    elif args.collections:
        run_pytest_with_args(args, "Collection tests", "tests/test_collections.py")
    elif args.auth:
        run_pytest_with_args(args, "Authentication tests", "tests/auth/")
    elif args.models:
        run_pytest_with_args(args, "Model tests", "tests/models/")
    elif args.functions:
        run_pytest_with_args(args, "Function tests", "tests/functions/")
    elif args.utils:
        run_pytest_with_args(args, "Utility tests", "tests/utils/")
    else:
        # Run all tests
        run_pytest_with_args(args, "All tests")

    print("\n🎉 Test run completed!")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test runner for GLIMPS Audit client library and CLI

Usage:
    python run_tests.py                 # Run all unit tests
    python run_tests.py -v              # Run with verbose output
    python run_tests.py --integration   # Run integration tests (requires env vars)
    python run_tests.py --coverage      # Run with coverage report
    python run_tests.py --quick         # Run quick tests only (no slow tests)
    python run_tests.py --lint          # Run linting checks
"""

import sys
import subprocess
import argparse
import os


def run_command(cmd, check=True):
    """Run a command and return the result"""
    print(f"Running: {' '.join(cmd)}")
    print("-" * 60)
    result = subprocess.run(cmd, check=check)
    print()
    return result.returncode


def check_environment():
    """Check if the test environment is set up correctly"""
    try:
        import pytest # noqa: F401
        import responses # noqa: F401
        import click # noqa: F401
    except ImportError as e:
        print(f"Error: Missing required package: {e}")
        print("Please run: pip install -r requirements-dev.txt")
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="Run tests for GLIMPS Audit client")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--no-cov", action="store_true", help="Disable coverage")
    parser.add_argument("--specific", help="Run specific test file or pattern")
    parser.add_argument("--quick", action="store_true", help="Skip slow tests")
    parser.add_argument("--lint", action="store_true", help="Run linting checks")
    parser.add_argument("--all", action="store_true", help="Run all tests including integration")
    args = parser.parse_args()

    # Check environment
    if not check_environment():
        return 1

    # Run linting if requested
    if args.lint:
        print("Running linting checks...")
        return run_command([sys.executable, "-m", "ruff", "check", "src", "tests"])

    # Base pytest command
    cmd = [sys.executable, "-m", "pytest"]

    # Add verbose flag
    if args.verbose:
        cmd.append("-vv")
    else:
        cmd.append("-v")

    # Handle coverage
    if args.no_cov:
        cmd.append("--no-cov")
    elif args.coverage:
        cmd.extend([
            "--cov=gaudit",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-fail-under=80"
        ])

    # Handle test selection
    markers = []

    if args.integration:
        # Check for required environment variables
        required_vars = ["GLIMPS_TEST_API_URL", "GLIMPS_TEST_EMAIL", "GLIMPS_TEST_PASSWORD"]
        missing = [var for var in required_vars if not os.environ.get(var)]

        if missing:
            print(f"Error: Missing required environment variables: {', '.join(missing)}")
            print("\nTo run integration tests, set the following environment variables:")
            for var in required_vars:
                print(f"  export {var}='your-value-here'")
            return 1

        markers.append("integration")
    elif not args.all:
        # Run only unit tests by default
        markers.append("not integration")

    if args.quick:
        if markers:
            markers[0] = f"({markers[0]}) and not slow"
        else:
            markers.append("not slow")

    if markers:
        cmd.extend(["-m", " and ".join(markers)])

    # Add specific test file/pattern if provided
    if args.specific:
        cmd.append(args.specific)
    else:
        cmd.append("tests")

    # Show test categories
    print("Test Configuration:")
    print(f"  - Verbose: {args.verbose}")
    print(f"  - Coverage: {args.coverage and not args.no_cov}")
    print(f"  - Integration: {args.integration or args.all}")
    print(f"  - Quick mode: {args.quick}")
    if args.specific:
        print(f"  - Specific: {args.specific}")
    print()

    # Run the tests
    result = run_command(cmd, check=False)

    # Show coverage report location if generated
    if args.coverage and result == 0:
        print("\nCoverage report generated:")
        print("  - Terminal report shown above")
        print("  - HTML report: htmlcov/index.html")
        print("\nOpen HTML report:")
        if sys.platform == "darwin":
            print("    open htmlcov/index.html")
        elif sys.platform == "win32":
            print("    start htmlcov/index.html")
        else:
            print("    xdg-open htmlcov/index.html")

    return result


if __name__ == "__main__":
    sys.exit(main())

"""
Test Runner Script for AgroShield
==================================

Run all tests with coverage reporting and performance benchmarks.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --unit             # Run only unit tests
    python run_tests.py --integration      # Run only integration tests
    python run_tests.py --performance      # Run performance tests
    python run_tests.py --coverage         # Generate HTML coverage report
    python run_tests.py --fast             # Skip slow tests

Author: AgroShield AI Team
Date: October 2025
"""

import sys
import os
import subprocess
import argparse
from datetime import datetime


def run_command(cmd, description):
    """Run a command and print status."""
    print(f"\n{'='*70}")
    print(f"🔧 {description}")
    print(f"{'='*70}")
    
    result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
    
    if result.returncode != 0:
        print(f"\n❌ {description} FAILED")
        return False
    else:
        print(f"\n✅ {description} PASSED")
        return True


def run_tests(args):
    """Run tests based on arguments."""
    print(f"\n{'='*70}")
    print("🧪 AGROSHIELD TEST SUITE")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")
    
    # Build pytest command
    pytest_args = ["pytest"]
    
    if args.unit:
        pytest_args.extend(["-m", "unit"])
        print("📦 Running UNIT tests only")
    elif args.integration:
        pytest_args.extend(["-m", "integration"])
        print("🔗 Running INTEGRATION tests only")
    elif args.performance:
        pytest_args.extend(["-m", "performance"])
        print("⚡ Running PERFORMANCE tests only")
    elif args.fast:
        pytest_args.extend(["-m", "not slow"])
        print("🏃 Running FAST tests (skipping slow tests)")
    else:
        print("🎯 Running ALL tests")
    
    # Coverage options
    if args.coverage:
        pytest_args.extend([
            "--cov=app.services",
            "--cov-report=html",
            "--cov-report=term-missing"
        ])
        print("📊 Coverage reporting ENABLED")
    
    # Verbosity
    if args.verbose:
        pytest_args.append("-vv")
    else:
        pytest_args.append("-v")
    
    # Specific test file
    if args.test_file:
        pytest_args.append(f"tests/{args.test_file}")
        print(f"📄 Running specific test: {args.test_file}")
    
    # Run pytest
    cmd = " ".join(pytest_args)
    success = run_command(cmd, "Test Execution")
    
    # Open coverage report if requested
    if args.coverage and success:
        if sys.platform == "win32":
            os.startfile("htmlcov\\index.html")
        elif sys.platform == "darwin":
            subprocess.run(["open", "htmlcov/index.html"])
        else:
            subprocess.run(["xdg-open", "htmlcov/index.html"])
        
        print("\n📊 Coverage report opened in browser")
    
    return success


def run_linting(args):
    """Run code quality checks."""
    if not args.lint:
        return True
    
    print(f"\n{'='*70}")
    print("🔍 CODE QUALITY CHECKS")
    print(f"{'='*70}")
    
    success = True
    
    # Run flake8
    if not run_command("flake8 app/ --max-line-length=120 --ignore=E501,W503", "Flake8 Linting"):
        success = False
    
    # Run pylint
    if not run_command("pylint app/ --max-line-length=120 --disable=C0111,R0913", "Pylint Analysis"):
        success = False
    
    # Run mypy (type checking)
    if not run_command("mypy app/ --ignore-missing-imports", "MyPy Type Checking"):
        success = False
    
    return success


def generate_test_report(args):
    """Generate comprehensive test report."""
    if not args.report:
        return
    
    print(f"\n{'='*70}")
    print("📈 GENERATING TEST REPORT")
    print(f"{'='*70}")
    
    # Generate HTML report
    run_command(
        "pytest --html=test-report.html --self-contained-html",
        "HTML Test Report Generation"
    )
    
    # Generate JUnit XML (for CI/CD)
    run_command(
        "pytest --junitxml=test-results.xml",
        "JUnit XML Report Generation"
    )
    
    print("\n✅ Test reports generated:")
    print("   - test-report.html")
    print("   - test-results.xml")


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(
        description="AgroShield Test Suite Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    Run all tests
  python run_tests.py --unit             Run unit tests only
  python run_tests.py --integration      Run integration tests only
  python run_tests.py --performance      Run performance tests
  python run_tests.py --coverage         Generate coverage report
  python run_tests.py --fast             Skip slow tests
  python run_tests.py --lint             Run code quality checks
  python run_tests.py --report           Generate HTML test report
  python run_tests.py --test-file test_ai_hyperlocal_prediction.py
        """
    )
    
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--lint", action="store_true", help="Run code quality checks")
    parser.add_argument("--report", action="store_true", help="Generate HTML test report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--test-file", "-f", help="Run specific test file")
    
    args = parser.parse_args()
    
    # Change to backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    # Run linting first if requested
    if args.lint:
        lint_success = run_linting(args)
        if not lint_success:
            print("\n⚠️  Code quality issues found. Fix them before running tests.")
            sys.exit(1)
    
    # Run tests
    test_success = run_tests(args)
    
    # Generate report if requested
    if args.report:
        generate_test_report(args)
    
    # Print summary
    print(f"\n{'='*70}")
    print("📊 TEST SUMMARY")
    print(f"{'='*70}")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if test_success:
        print("\n✅ ALL TESTS PASSED")
        print("\n🎉 Great job! The codebase is healthy.")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED")
        print("\n⚠️  Please fix failing tests before deploying.")
        sys.exit(1)


if __name__ == "__main__":
    main()

"""Run tests for gbpcli"""

import argparse
import unittest


def main() -> None:
    """Program entry point"""
    args = build_parser().parse_args()

    loader = unittest.TestLoader()
    loader.testNamePatterns = [f"*{pattern}*" for pattern in args.tests] or None
    tests = loader.discover("")
    verbosity = 2 if args.verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity, failfast=args.failfast)
    test_result = runner.run(tests)

    raise SystemExit(int(not test_result.wasSuccessful()))


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--failfast", action="store_true", default=False)
    parser.add_argument("-v", "--verbose", action="store_true", default=False)
    parser.add_argument("tests", nargs="*", default=[])

    return parser


if __name__ == "__main__":
    main()

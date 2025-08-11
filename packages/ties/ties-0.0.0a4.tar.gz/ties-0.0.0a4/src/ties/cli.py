"""Ties CLI entry point to duplicate and sync file content with advanced transformations.."""

import argparse
import sys

from ._configuration import load_config
from ._consts import APP_NAME, ERROR, SUCCESS, Colors, cprint
from ._file_processing import process_files


def main() -> None:
    """Run the main function to run the CLI."""
    parser = argparse.ArgumentParser(
        prog=APP_NAME,
        description="A tool to keep files in sync within a repository.",
        epilog="Use with pre-commit to enforce file content consistency.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "check", help="Check for discrepancies and exit with an error if any are found."
    )
    subparsers.add_parser(
        "fix", help="Automatically fix discrepancies by overwriting target files."
    )

    args = parser.parse_args()

    config = load_config()
    if not config or "tie" not in config:
        cprint(
            "❌ Error: No configuration found in ties.toml or pyproject.toml under [tool.ties].",
            Colors.RED,
            bold=True,
        )
        cprint("Please ensure you have a [[tool.ties.tie]] section.", Colors.CYAN)
        sys.exit(ERROR)

    if not process_files(config, args.command):
        sys.exit(ERROR)

    sys.exit(SUCCESS)

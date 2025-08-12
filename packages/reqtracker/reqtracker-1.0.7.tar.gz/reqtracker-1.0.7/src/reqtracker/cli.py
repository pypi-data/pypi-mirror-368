"""Command-line interface for reqtracker.

This module provides the CLI commands for dependency tracking and
requirements generation.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .config import Config
from .generator import RequirementsGenerator, VersionStrategy
from .tracker import Tracker, TrackingMode


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for reqtracker CLI.

    Returns:
        Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="reqtracker",
        description=(
            "Intelligent Python dependency tracking and requirements generation"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  reqtracker track ./src                    # Track dependencies in src directory
  reqtracker track --mode static ./app.py  # Static analysis only
  reqtracker generate                       # Generate requirements.txt
  reqtracker generate --exact --output deps.txt  # Exact versions to deps.txt
  reqtracker analyze ./src --output custom.txt   # Full workflow
        """,
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.7",
    )

    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file (default: .reqtracker.toml)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        metavar="COMMAND",
    )

    # Track command
    track_parser = subparsers.add_parser(
        "track",
        help="Track dependencies in source files",
        description="Analyze source files to detect dependencies",
    )
    track_parser.add_argument(
        "paths",
        nargs="*",
        help="Paths to analyze (default: current directory)",
    )
    track_parser.add_argument(
        "--mode",
        choices=["static", "dynamic", "hybrid"],
        default="hybrid",
        help="Analysis mode (default: hybrid)",
    )

    # Generate command
    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate requirements.txt from tracked dependencies",
        description="Generate requirements.txt file from current directory analysis",
    )
    generate_parser.add_argument(
        "--output",
        "-o",
        default="requirements.txt",
        help="Output file path (default: requirements.txt)",
    )
    generate_parser.add_argument(
        "--exact",
        action="store_true",
        help="Use exact version pinning (==)",
    )
    generate_parser.add_argument(
        "--minimum",
        action="store_true",
        help="Use minimum version pinning (>=)",
    )
    generate_parser.add_argument(
        "--no-versions",
        action="store_true",
        help="Generate without version constraints",
    )
    generate_parser.add_argument(
        "--no-header",
        action="store_true",
        help="Skip generation header",
    )
    generate_parser.add_argument(
        "--no-sort",
        action="store_true",
        help="Don't sort packages alphabetically",
    )

    # Analyze command (combined track + generate)
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze dependencies and generate requirements",
        description=(
            "Complete workflow: analyze source files and generate requirements.txt"
        ),
    )
    analyze_parser.add_argument(
        "paths",
        nargs="*",
        help="Paths to analyze (default: current directory)",
    )
    analyze_parser.add_argument(
        "--mode",
        choices=["static", "dynamic", "hybrid"],
        default="hybrid",
        help="Analysis mode (default: hybrid)",
    )
    analyze_parser.add_argument(
        "--output",
        "-o",
        default="requirements.txt",
        help="Output file path (default: requirements.txt)",
    )
    analyze_parser.add_argument(
        "--exact",
        action="store_true",
        help="Use exact version pinning (==)",
    )
    analyze_parser.add_argument(
        "--minimum",
        action="store_true",
        help="Use minimum version pinning (>=)",
    )
    analyze_parser.add_argument(
        "--no-versions",
        action="store_true",
        help="Generate without version constraints",
    )
    analyze_parser.add_argument(
        "--no-header",
        action="store_true",
        help="Skip generation header",
    )
    analyze_parser.add_argument(
        "--no-sort",
        action="store_true",
        help="Don't sort packages alphabetically",
    )

    return parser


def load_config(config_path: Optional[str]) -> Config:
    """Load configuration from file or use defaults.

    Args:
        config_path: Path to config file, or None for default.

    Returns:
        Loaded configuration.
    """
    if config_path:
        return Config.from_file(config_path)

    # Try default locations
    default_paths = [".reqtracker.toml", "pyproject.toml"]
    for path in default_paths:
        if Path(path).exists():
            try:
                return Config.from_file(path)
            except Exception:
                continue

    return Config()


def get_version_strategy(args) -> VersionStrategy:
    """Determine version strategy from CLI arguments.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Version strategy to use.
    """
    if hasattr(args, "exact") and args.exact:
        return VersionStrategy.EXACT
    elif hasattr(args, "minimum") and args.minimum:
        return VersionStrategy.MINIMUM
    elif hasattr(args, "no_versions") and args.no_versions:
        return VersionStrategy.NONE
    else:
        return VersionStrategy.COMPATIBLE


def cmd_track(args, config: Config) -> int:
    """Execute track command.

    Args:
        args: Parsed CLI arguments.
        config: Configuration object.

    Returns:
        Exit code (0 for success).
    """
    paths = args.paths if args.paths else [Path.cwd()]
    mode = TrackingMode(args.mode)
    # Show warning for experimental modes
    if args.mode in ["dynamic", "hybrid"]:
        if args.verbose:
            print(
                f"Warning: {args.mode} mode is experimental and may include "
                "transitive dependencies.",
                file=sys.stderr,
            )

    if args.verbose:
        print(
            f"Tracking dependencies in {len(paths)} path(s) using {args.mode} mode..."
        )

    try:
        tracker = Tracker(config)
        packages = tracker.track(paths, mode)

        if args.verbose:
            print(f"Found {len(packages)} dependencies:")
            for package in sorted(packages):
                print(f"  - {package}")
        else:
            for package in sorted(packages):
                print(package)

        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_generate(args, config: Config) -> int:
    """Execute generate command.

    Args:
        args: Parsed CLI arguments.
        config: Configuration object.

    Returns:
        Exit code (0 for success).
    """
    if args.verbose:
        print("Analyzing current directory for dependencies...")

    try:
        # Track dependencies in current directory
        tracker = Tracker(config)
        packages = tracker.track([Path.cwd()], TrackingMode.HYBRID)

        if not packages:
            print("No dependencies found to generate requirements from.")
            return 0

        # Generate requirements
        version_strategy = get_version_strategy(args)
        generator = RequirementsGenerator(version_strategy)

        generator.write_requirements(
            packages,
            args.output,
            include_header=not args.no_header,
            sort_packages=not args.no_sort,
        )

        if args.verbose:
            print(
                f"Generated {args.output} with {len(packages)} dependencies "
                f"using {version_strategy.value} versioning"
            )
        else:
            print(f"Generated {args.output}")

        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_analyze(args, config: Config) -> int:
    """Execute analyze command (track + generate).

    Args:
        args: Parsed CLI arguments.
        config: Configuration object.

    Returns:
        Exit code (0 for success).
    """
    paths = args.paths if args.paths else [Path.cwd()]
    mode = TrackingMode(args.mode)
    # Show warning for experimental modes
    if args.mode in ["dynamic", "hybrid"]:
        if args.verbose:
            print(
                f"Warning: {args.mode} mode is experimental and may include "
                "transitive dependencies.",
                file=sys.stderr,
            )

    if args.verbose:
        print(
            f"Analyzing dependencies in {len(paths)} path(s) using {args.mode} mode..."
        )

    try:
        # Track dependencies
        tracker = Tracker(config)
        packages = tracker.track(paths, mode)

        if not packages:
            print("No dependencies found.")
            return 0

        if args.verbose:
            print(f"Found {len(packages)} dependencies")

        # Generate requirements
        version_strategy = get_version_strategy(args)
        generator = RequirementsGenerator(version_strategy)

        generator.write_requirements(
            packages,
            args.output,
            include_header=not args.no_header,
            sort_packages=not args.no_sort,
        )

        if args.verbose:
            print(
                f"Generated {args.output} with {len(packages)} dependencies "
                f"using {version_strategy.value} versioning"
            )
        else:
            print(f"Analyzed {len(paths)} path(s) and generated {args.output}")

        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main CLI entry point.

    Returns:
        Exit code (0 for success).
    """
    parser = create_parser()
    args = parser.parse_args()

    # Show help if no command provided
    if not args.command:
        parser.print_help()
        return 0

    # Load configuration
    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        return 1

    # Execute command
    if args.command == "track":
        return cmd_track(args, config)
    elif args.command == "generate":
        return cmd_generate(args, config)
    elif args.command == "analyze":
        return cmd_analyze(args, config)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())

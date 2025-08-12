"""Tests for CLI module."""

from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from src.reqtracker.cli import (
    cmd_analyze,
    cmd_generate,
    cmd_track,
    create_parser,
    get_version_strategy,
    load_config,
    main,
)
from src.reqtracker.config import Config
from src.reqtracker.generator import VersionStrategy


class TestCreateParser:
    """Test cases for argument parser creation."""

    def test_parser_creation(self):
        """Test that parser is created successfully."""
        parser = create_parser()
        assert parser is not None
        assert parser.prog == "reqtracker"

    def test_parser_help(self):
        """Test parser help output."""
        parser = create_parser()
        help_output = parser.format_help()
        assert "reqtracker" in help_output
        assert "track" in help_output
        assert "generate" in help_output
        assert "analyze" in help_output

    def test_parser_version(self):
        """Test version argument."""
        parser = create_parser()

        with pytest.raises(SystemExit):
            parser.parse_args(["--version"])

    def test_track_subcommand(self):
        """Test track subcommand parsing."""
        parser = create_parser()

        args = parser.parse_args(["track", "./src", "--mode", "static"])
        assert args.command == "track"
        assert args.paths == ["./src"]
        assert args.mode == "static"

    def test_generate_subcommand(self):
        """Test generate subcommand parsing."""
        parser = create_parser()

        args = parser.parse_args(["generate", "--output", "deps.txt", "--exact"])
        assert args.command == "generate"
        assert args.output == "deps.txt"
        assert args.exact is True

    def test_analyze_subcommand(self):
        """Test analyze subcommand parsing."""
        parser = create_parser()

        args = parser.parse_args(["analyze", "./src", "./tests", "--mode", "hybrid"])
        assert args.command == "analyze"
        assert args.paths == ["./src", "./tests"]
        assert args.mode == "hybrid"


class TestLoadConfig:
    """Test cases for configuration loading."""

    def test_load_config_none(self):
        """Test loading config with no path specified."""
        with patch("src.reqtracker.cli.Path.exists", return_value=False):
            config = load_config(None)
            assert isinstance(config, Config)

    def test_load_config_custom_path(self):
        """Test loading config from custom path."""
        with patch("src.reqtracker.config.Config.from_file") as mock_from_file:
            mock_config = Config()
            mock_from_file.return_value = mock_config

            result = load_config("custom.toml")

            mock_from_file.assert_called_once_with("custom.toml")
            assert result is mock_config

    def test_load_config_default_found(self):
        """Test loading config from default location."""
        with patch("src.reqtracker.cli.Path.exists") as mock_exists:
            with patch("src.reqtracker.config.Config.from_file") as mock_from_file:
                mock_config = Config()
                mock_from_file.return_value = mock_config

                # First path doesn't exist, second does
                mock_exists.side_effect = [True]

                result = load_config(None)

                mock_from_file.assert_called_once_with(".reqtracker.toml")
                assert result is mock_config


class TestGetVersionStrategy:
    """Test cases for version strategy determination."""

    def test_version_strategy_exact(self):
        """Test exact version strategy detection."""
        args = MagicMock(exact=True, minimum=False, no_versions=False)
        strategy = get_version_strategy(args)
        assert strategy == VersionStrategy.EXACT

    def test_version_strategy_minimum(self):
        """Test minimum version strategy detection."""
        args = MagicMock(exact=False, minimum=True, no_versions=False)
        strategy = get_version_strategy(args)
        assert strategy == VersionStrategy.MINIMUM

    def test_version_strategy_none(self):
        """Test no versions strategy detection."""
        args = MagicMock(exact=False, minimum=False, no_versions=True)
        strategy = get_version_strategy(args)
        assert strategy == VersionStrategy.NONE

    def test_version_strategy_default(self):
        """Test default version strategy."""
        args = MagicMock(exact=False, minimum=False, no_versions=False)
        strategy = get_version_strategy(args)
        assert strategy == VersionStrategy.COMPATIBLE

    def test_version_strategy_no_attributes(self):
        """Test version strategy with missing attributes."""
        args = MagicMock(spec=[])  # No attributes
        strategy = get_version_strategy(args)
        assert strategy == VersionStrategy.COMPATIBLE


class TestCommands:
    """Test cases for CLI commands."""

    @patch("src.reqtracker.cli.Tracker")
    def test_cmd_track_success(self, mock_tracker_class):
        """Test successful track command."""
        mock_tracker = MagicMock()
        mock_tracker.track.return_value = {"requests", "numpy"}
        mock_tracker_class.return_value = mock_tracker

        args = MagicMock(paths=["./src"], mode="hybrid", verbose=False)
        config = Config()

        with patch("builtins.print") as mock_print:
            result = cmd_track(args, config)

            assert result == 0
            mock_tracker.track.assert_called_once()
            mock_print.assert_called()

    @patch("src.reqtracker.cli.Tracker")
    def test_cmd_track_verbose(self, mock_tracker_class):
        """Test track command with verbose output."""
        mock_tracker = MagicMock()
        mock_tracker.track.return_value = {"requests"}
        mock_tracker_class.return_value = mock_tracker

        args = MagicMock(paths=["./src"], mode="static", verbose=True)
        config = Config()

        with patch("builtins.print") as mock_print:
            result = cmd_track(args, config)

            assert result == 0
            assert mock_print.call_count >= 2  # Verbose messages

    @patch("src.reqtracker.cli.Tracker")
    def test_cmd_track_error(self, mock_tracker_class):
        """Test track command with error."""
        mock_tracker_class.side_effect = Exception("Test error")

        args = MagicMock(paths=["./src"], mode="hybrid", verbose=False)
        config = Config()

        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            result = cmd_track(args, config)

            assert result == 1
            assert "Error: Test error" in mock_stderr.getvalue()

    @patch("src.reqtracker.cli.RequirementsGenerator")
    @patch("src.reqtracker.cli.Tracker")
    def test_cmd_generate_success(self, mock_tracker_class, mock_generator_class):
        """Test successful generate command."""
        mock_tracker = MagicMock()
        mock_tracker.track.return_value = {"requests", "numpy"}
        mock_tracker_class.return_value = mock_tracker

        mock_generator = MagicMock()
        mock_generator_class.return_value = mock_generator

        args = MagicMock(
            output="requirements.txt",
            no_header=False,
            no_sort=False,
            exact=False,
            minimum=False,
            no_versions=False,
            verbose=False,
        )
        config = Config()

        with patch("builtins.print") as mock_print:
            result = cmd_generate(args, config)

            assert result == 0
            mock_generator.write_requirements.assert_called_once()
            mock_print.assert_called_with("Generated requirements.txt")

    @patch("src.reqtracker.cli.RequirementsGenerator")
    @patch("src.reqtracker.cli.Tracker")
    def test_cmd_analyze_success(self, mock_tracker_class, mock_generator_class):
        """Test successful analyze command."""
        mock_tracker = MagicMock()
        mock_tracker.track.return_value = {"requests", "numpy"}
        mock_tracker_class.return_value = mock_tracker

        mock_generator = MagicMock()
        mock_generator_class.return_value = mock_generator

        args = MagicMock(
            paths=["./src"],
            mode="hybrid",
            output="requirements.txt",
            no_header=False,
            no_sort=False,
            exact=False,
            minimum=False,
            no_versions=False,
            verbose=True,
        )
        config = Config()

        with patch("builtins.print"):
            result = cmd_analyze(args, config)

            assert result == 0
            mock_tracker.track.assert_called_once()
            mock_generator.write_requirements.assert_called_once()


class TestMain:
    """Test cases for main CLI entry point."""

    def test_main_no_command(self):
        """Test main with no command shows help."""
        with patch("sys.argv", ["reqtracker"]):
            with patch("src.reqtracker.cli.create_parser") as mock_parser:
                mock_parser_instance = MagicMock()
                mock_parser_instance.parse_args.return_value = MagicMock(command=None)
                mock_parser.return_value = mock_parser_instance

                result = main()

                assert result == 0
                mock_parser_instance.print_help.assert_called_once()

    @patch("src.reqtracker.cli.cmd_track")
    @patch("src.reqtracker.cli.load_config")
    def test_main_track_command(self, mock_load_config, mock_cmd_track):
        """Test main with track command."""
        mock_config = Config()
        mock_load_config.return_value = mock_config
        mock_cmd_track.return_value = 0

        with patch("sys.argv", ["reqtracker", "track", "./src"]):
            with patch("src.reqtracker.cli.create_parser") as mock_parser:
                mock_args = MagicMock(command="track", config=None)
                mock_parser_instance = MagicMock()
                mock_parser_instance.parse_args.return_value = mock_args
                mock_parser.return_value = mock_parser_instance

                result = main()

                assert result == 0
                mock_cmd_track.assert_called_once_with(mock_args, mock_config)

    @patch("src.reqtracker.cli.load_config")
    def test_main_config_error(self, mock_load_config):
        """Test main with config loading error."""
        mock_load_config.side_effect = Exception("Config error")

        with patch("sys.argv", ["reqtracker", "track"]):
            with patch("src.reqtracker.cli.create_parser") as mock_parser:
                mock_args = MagicMock(command="track", config="bad.toml")
                mock_parser_instance = MagicMock()
                mock_parser_instance.parse_args.return_value = mock_args
                mock_parser.return_value = mock_parser_instance

                with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                    result = main()

                    assert result == 1
                    assert "Error loading configuration" in mock_stderr.getvalue()

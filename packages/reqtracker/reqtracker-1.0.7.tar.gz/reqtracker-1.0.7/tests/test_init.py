"""Tests for main API module (__init__.py)."""

from unittest.mock import MagicMock, patch

import pytest

import src.reqtracker as reqtracker
from src.reqtracker import (
    Config,
    TrackerMode,
    TrackingMode,
    VersionStrategy,
    analyze,
    generate,
    scan,
    track,
    write_requirements,
)


class TestTrackFunction:
    """Test cases for the main track() function."""

    @patch("src.reqtracker.Tracker")
    def test_track_default_parameters(self, mock_tracker_class):
        """Test track function with default parameters."""
        mock_tracker = MagicMock()
        mock_tracker.track.return_value = {"requests", "numpy"}
        mock_tracker_class.return_value = mock_tracker

        result = track()

        mock_tracker_class.assert_called_once()
        mock_tracker.track.assert_called_once_with(None, TrackingMode.HYBRID)
        assert result == {"requests", "numpy"}

    @patch("src.reqtracker.Tracker")
    def test_track_custom_parameters(self, mock_tracker_class):
        """Test track function with custom parameters."""
        mock_tracker = MagicMock()
        mock_tracker.track.return_value = {"flask", "pandas"}
        mock_tracker_class.return_value = mock_tracker

        config = Config()
        result = track(["./src", "./app"], mode="static", config=config)

        mock_tracker_class.assert_called_once_with(config)
        mock_tracker.track.assert_called_once_with(
            ["./src", "./app"], TrackingMode.STATIC
        )
        assert result == {"flask", "pandas"}

    def test_track_invalid_mode(self):
        """Test track function with invalid mode."""
        with pytest.raises(ValueError, match="Invalid mode 'invalid'"):
            track(mode="invalid")

    @patch("src.reqtracker.Tracker")
    def test_track_dynamic_mode(self, mock_tracker_class):
        """Test track function with dynamic mode."""
        mock_tracker = MagicMock()
        mock_tracker.track.return_value = {"requests"}
        mock_tracker_class.return_value = mock_tracker

        result = track(mode="dynamic")

        mock_tracker.track.assert_called_once_with(None, TrackingMode.DYNAMIC)
        assert result == {"requests"}

    @patch("src.reqtracker.Tracker")
    def test_track_config_mode_respected(self, mock_tracker_class):
        """Test that config.mode is used when mode parameter is None."""
        mock_tracker = MagicMock()
        mock_tracker.track.return_value = {"flask"}
        mock_tracker_class.return_value = mock_tracker

        # Test with config mode and no explicit mode parameter
        from src.reqtracker import TrackerMode

        config = Config(mode=TrackerMode.STATIC)
        result = track(["./src"], config=config)

        # Should use TrackingMode.STATIC from config
        mock_tracker_class.assert_called_once_with(config)
        mock_tracker.track.assert_called_once_with(["./src"], TrackingMode.STATIC)
        assert result == {"flask"}

    @patch("src.reqtracker.Tracker")
    def test_track_mode_precedence_over_config(self, mock_tracker_class):
        """Test that explicit mode parameter takes precedence over config.mode."""
        mock_tracker = MagicMock()
        mock_tracker.track.return_value = {"django"}
        mock_tracker_class.return_value = mock_tracker

        # Test with both explicit mode and config mode
        config = Config(mode=TrackerMode.HYBRID)
        result = track(["./src"], mode="static", config=config)

        # Should use explicit mode (STATIC) not config mode (HYBRID)
        mock_tracker_class.assert_called_once_with(config)
        mock_tracker.track.assert_called_once_with(["./src"], TrackingMode.STATIC)
        assert result == {"django"}

    def test_track_recursion_prevention(self):
        """Test that track function prevents infinite recursion in dynamic mode."""
        import os

        # Simulate being called from within dynamic analysis
        os.environ["REQTRACKER_ANALYZING"] = "1"

        try:
            # These should return empty sets immediately without recursion
            result1 = track(mode="dynamic")
            assert result1 == set()

            result2 = track(mode="hybrid")
            assert result2 == set()

            # Static mode should still work normally
            with patch("src.reqtracker.Tracker") as mock_tracker_class:
                mock_tracker = MagicMock()
                mock_tracker.track.return_value = {"requests"}
                mock_tracker_class.return_value = mock_tracker

                result3 = track(mode="static")
                assert result3 == {"requests"}

        finally:
            os.environ.pop("REQTRACKER_ANALYZING", None)


class TestGenerateFunction:
    """Test cases for the generate() function."""

    @patch("src.reqtracker.RequirementsGenerator")
    @patch("src.reqtracker.track")
    @patch("pathlib.Path.write_text")
    def test_generate_with_packages(
        self, _mock_write, mock_track, mock_generator_class
    ):
        """Test generate function with provided packages."""
        mock_generator = MagicMock()
        mock_generator.generate.return_value = "requests==1.0.0\nnumpy==1.20.0\n"
        mock_generator_class.return_value = mock_generator

        packages = {"requests", "numpy"}
        result = generate(packages)

        mock_generator_class.assert_called_once_with(VersionStrategy.COMPATIBLE)
        mock_generator.generate.assert_called_once_with(
            packages, "requirements.txt", True, True
        )
        mock_track.assert_not_called()  # Shouldn't auto-track when packages provided
        assert result == "requests==1.0.0\nnumpy==1.20.0\n"

    @patch("src.reqtracker.RequirementsGenerator")
    @patch("src.reqtracker.track")
    @patch("pathlib.Path.write_text")
    def test_generate_auto_detect(self, _mock_write, mock_track, mock_generator_class):
        """Test generate function with auto-detection."""
        mock_track.return_value = {"flask", "pandas"}
        mock_generator = MagicMock()
        mock_generator.generate.return_value = "flask==2.0.0\npandas==1.3.0\n"
        mock_generator_class.return_value = mock_generator

        result = generate()

        mock_track.assert_called_once_with(config=None)
        mock_generator.generate.assert_called_once_with(
            {"flask", "pandas"}, "requirements.txt", True, True
        )
        assert result == "flask==2.0.0\npandas==1.3.0\n"

    @patch("src.reqtracker.RequirementsGenerator")
    @patch("pathlib.Path.write_text")
    def test_generate_exact_strategy(self, _mock_write, mock_generator_class):
        """Test generate function with exact version strategy."""
        mock_generator = MagicMock()
        mock_generator_class.return_value = mock_generator

        packages = {"requests"}
        generate(packages, version_strategy="exact")

        mock_generator_class.assert_called_once_with(VersionStrategy.EXACT)

    def test_generate_invalid_strategy(self):
        """Test generate function with invalid version strategy."""
        packages = {"requests"}
        with pytest.raises(ValueError, match="Invalid version_strategy 'invalid'"):
            generate(packages, version_strategy="invalid")

    @patch("src.reqtracker.RequirementsGenerator")
    @patch("pathlib.Path.write_text")
    def test_generate_custom_output(self, _mock_write, mock_generator_class):
        """Test generate function with custom output file."""
        mock_generator = MagicMock()
        mock_generator.generate.return_value = "content"
        mock_generator_class.return_value = mock_generator

        packages = {"requests"}
        generate(packages, output="deps.txt", include_header=False, sort_packages=False)

        mock_generator.generate.assert_called_once_with(
            packages, "deps.txt", False, False
        )


class TestAnalyzeFunction:
    """Test cases for the analyze() function."""

    @patch("src.reqtracker.generate")
    @patch("src.reqtracker.track")
    def test_analyze_default_parameters(self, mock_track, mock_generate):
        """Test analyze function with default parameters."""
        mock_track.return_value = {"requests", "numpy"}

        result = analyze()

        mock_track.assert_called_once_with(None, "hybrid", None)
        mock_generate.assert_called_once_with(
            {"requests", "numpy"}, "requirements.txt", "compatible", True, True
        )
        assert result == {"requests", "numpy"}

    @patch("src.reqtracker.generate")
    @patch("src.reqtracker.track")
    def test_analyze_custom_parameters(self, mock_track, mock_generate):
        """Test analyze function with custom parameters."""
        mock_track.return_value = {"flask"}
        config = Config()

        result = analyze(
            ["./src"],
            output="deps.txt",
            mode="static",
            version_strategy="exact",
            include_header=False,
            sort_packages=False,
            config=config,
        )

        mock_track.assert_called_once_with(["./src"], "static", config)
        mock_generate.assert_called_once_with(
            {"flask"}, "deps.txt", "exact", False, False
        )
        assert result == {"flask"}


class TestConvenienceFunctions:
    """Test cases for convenience functions."""

    @patch("src.reqtracker.track")
    def test_scan_function(self, mock_track):
        """Test scan() alias function."""
        mock_track.return_value = {"requests"}

        result = scan(["./src"], mode="static")

        mock_track.assert_called_once_with(["./src"], mode="static")
        assert result == {"requests"}

    @patch("src.reqtracker.generate")
    def test_write_requirements_function(self, mock_generate):
        """Test write_requirements() function."""
        mock_generate.return_value = "content"
        packages = {"requests"}

        write_requirements(packages, "output.txt")

        mock_generate.assert_called_once_with(packages, "output.txt")


class TestImports:
    """Test cases for package imports and exports."""

    def test_main_functions_available(self):
        """Test that main API functions are available."""
        assert callable(reqtracker.track)
        assert callable(reqtracker.generate)
        assert callable(reqtracker.analyze)
        assert callable(reqtracker.scan)
        assert callable(reqtracker.write_requirements)

    def test_core_classes_available(self):
        """Test that core classes are available."""
        assert hasattr(reqtracker, "Config")
        assert hasattr(reqtracker, "Tracker")
        assert hasattr(reqtracker, "RequirementsGenerator")
        assert hasattr(reqtracker, "StaticAnalyzer")
        assert hasattr(reqtracker, "DynamicTracker")

    def test_enums_available(self):
        """Test that enums are available."""
        assert hasattr(reqtracker, "TrackingMode")
        assert hasattr(reqtracker, "VersionStrategy")
        assert hasattr(reqtracker, "TrackerMode")

    def test_utility_functions_available(self):
        """Test that utility functions are available."""
        assert hasattr(reqtracker, "resolve_package_name")
        assert hasattr(reqtracker, "get_package_name")
        assert hasattr(reqtracker, "is_standard_library")
        assert hasattr(reqtracker, "normalize_package_name")

    def test_package_metadata_available(self):
        """Test that package metadata is available."""
        assert hasattr(reqtracker, "__version__")
        assert hasattr(reqtracker, "__author__")
        assert hasattr(reqtracker, "__email__")
        assert reqtracker.__version__ == "1.0.6"
        assert reqtracker.__author__ == "Oleksii Shcherbak"
        assert "oleksii_shcherbak" in reqtracker.__email__

    def test_all_exports(self):
        """Test that __all__ includes expected exports."""
        expected_functions = ["track", "generate", "analyze"]
        expected_classes = ["Config", "Tracker", "RequirementsGenerator"]
        expected_utils = ["resolve_package_name", "get_package_name"]

        for item in expected_functions + expected_classes + expected_utils:
            assert item in reqtracker.__all__


class TestIntegration:
    """Integration tests for main API."""

    @patch("src.reqtracker.Tracker")
    @patch("src.reqtracker.RequirementsGenerator")
    @patch("pathlib.Path.write_text")
    def test_complete_workflow(
        self, _mock_write, mock_generator_class, mock_tracker_class
    ):
        """Test complete workflow integration."""
        # Setup mocks
        mock_tracker = MagicMock()
        mock_tracker.track.return_value = {"requests", "numpy"}
        mock_tracker_class.return_value = mock_tracker

        mock_generator = MagicMock()
        mock_generator.generate.return_value = "requests==1.0.0\nnumpy==1.20.0\n"
        mock_generator_class.return_value = mock_generator

        # Test complete workflow
        packages = reqtracker.analyze(
            ["./src"], mode="hybrid", version_strategy="exact"
        )

        # Verify calls
        mock_tracker_class.assert_called_once()
        mock_tracker.track.assert_called_once()
        mock_generator_class.assert_called_once_with(VersionStrategy.EXACT)
        mock_generator.generate.assert_called_once()
        assert packages == {"requests", "numpy"}

    def test_simple_usage_pattern(self):
        """Test the simple usage pattern from documentation."""
        with patch("src.reqtracker.Tracker") as mock_tracker_class:
            mock_tracker = MagicMock()
            mock_tracker.track.return_value = {"requests"}
            mock_tracker_class.return_value = mock_tracker

            # This should work as advertised in docs
            packages = reqtracker.track()
            assert isinstance(packages, set)
            assert packages == {"requests"}

    def test_advanced_usage_pattern(self):
        """Test advanced usage patterns."""
        config = reqtracker.Config(mode=reqtracker.TrackerMode.STATIC)
        with patch("src.reqtracker.Tracker") as mock_tracker_class:
            mock_tracker = MagicMock()
            mock_tracker.track.return_value = {"flask"}
            mock_tracker_class.return_value = mock_tracker

            packages = reqtracker.track(["./src"], mode="static", config=config)
            mock_tracker_class.assert_called_once_with(config)
            assert packages == {"flask"}

    def test_error_handling(self):
        """Test error handling in main API."""
        # Test invalid mode
        with pytest.raises(ValueError):
            reqtracker.track(mode="invalid_mode")

        # Test invalid version strategy
        with pytest.raises(ValueError):
            reqtracker.generate({"requests"}, version_strategy="invalid_strategy")

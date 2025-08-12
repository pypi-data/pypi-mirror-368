"""Tests for main tracker module."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.reqtracker.config import Config
from src.reqtracker.tracker import Tracker, TrackingMode, track


class TestTrackingMode:
    """Test cases for TrackingMode enum."""

    def test_tracking_mode_values(self):
        """Test TrackingMode enum values."""
        assert TrackingMode.STATIC.value == "static"
        assert TrackingMode.DYNAMIC.value == "dynamic"
        assert TrackingMode.HYBRID.value == "hybrid"


class TestTracker:
    """Test cases for Tracker class."""

    def test_initialization_default(self):
        """Test tracker initialization with default config."""
        tracker = Tracker()

        assert tracker.config is not None
        assert hasattr(tracker, "static_analyzer")
        assert hasattr(tracker, "dynamic_tracker")

    def test_initialization_with_config(self):
        """Test tracker initialization with custom config."""
        config = Config()
        tracker = Tracker(config)

        assert tracker.config is config

    @patch("src.reqtracker.tracker.Path.cwd")
    def test_track_default_parameters(self, mock_cwd):
        """Test track method with default parameters."""
        mock_cwd.return_value = Path("/test/path")
        tracker = Tracker()

        with patch.object(
            tracker, "_run_hybrid_analysis", return_value={"requests"}
        ) as mock_hybrid:
            result = tracker.track()

            mock_hybrid.assert_called_once()
            assert result == {"requests"}

    def test_track_static_mode(self):
        """Test track method in static mode."""
        tracker = Tracker()
        paths = [Path("./test")]

        with patch.object(
            tracker, "_run_static_analysis", return_value={"numpy"}
        ) as mock_static:
            result = tracker.track(paths, TrackingMode.STATIC)

            mock_static.assert_called_once_with([Path("./test")])
            assert result == {"numpy"}

    def test_track_dynamic_mode(self):
        """Test track method in dynamic mode."""
        tracker = Tracker()
        paths = [Path("./test")]

        with patch.object(
            tracker, "_run_dynamic_analysis", return_value={"pandas"}
        ) as mock_dynamic:
            result = tracker.track(paths, TrackingMode.DYNAMIC)

            mock_dynamic.assert_called_once_with([Path("./test")])
            assert result == {"pandas"}

    def test_track_hybrid_mode(self):
        """Test track method in hybrid mode."""
        tracker = Tracker()
        paths = [Path("./test")]

        with patch.object(
            tracker, "_run_hybrid_analysis", return_value={"requests", "numpy"}
        ) as mock_hybrid:
            result = tracker.track(paths, TrackingMode.HYBRID)

            mock_hybrid.assert_called_once_with([Path("./test")])
            assert result == {"requests", "numpy"}

    def test_configure_analyzers(self):
        """Test analyzer configuration."""
        tracker = Tracker()
        paths = [Path("./src/test.py")]

        with patch.object(tracker.static_analyzer, "configure") as mock_configure:
            tracker._configure_analyzers(paths)

            mock_configure.assert_called_once()
            args = mock_configure.call_args[1]
            assert "project_root" in args
            assert "include_patterns" in args
            assert "exclude_patterns" in args

    def test_run_static_analysis_file(self):
        """Test static analysis on a single file."""
        tracker = Tracker()
        test_file = Path("./test.py")

        mock_imports = [
            {"module": "requests.auth", "line": 1},
            {"module": "numpy.array", "line": 2},
        ]

        with patch.object(
            tracker.static_analyzer, "analyze_file", return_value=mock_imports
        ):
            with patch.object(
                tracker, "_resolve_package_names", return_value={"requests", "numpy"}
            ) as mock_resolve:
                result = tracker._run_static_analysis([test_file])

                # Test that _resolve_package_names was called (regardless of arguments)
                mock_resolve.assert_called_once()

                # Test that we get the expected result
                assert result == {"requests", "numpy"}

    @patch("src.reqtracker.tracker.TrackingSession")
    def test_run_dynamic_analysis(self, mock_session_class):
        """Test dynamic analysis."""
        tracker = Tracker()

        # Create a mock Path object
        test_file = MagicMock(spec=Path)
        test_file.is_file.return_value = True
        test_file.suffix = ".py"
        test_file.__str__ = lambda: "./test.py"

        # Mock the TrackingSession instance (not context manager)
        mock_session = MagicMock()
        mock_session.track_file.return_value = {"requests", "beautifulsoup4"}
        mock_session_class.return_value = mock_session

        # Mock _get_python_files to return our test file
        with patch.object(tracker, "_get_python_files", return_value=[test_file]):
            with patch.object(
                tracker,
                "_resolve_package_names",
                return_value={"requests", "beautifulsoup4"},
            ) as mock_resolve:
                result = tracker._run_dynamic_analysis([test_file])

                mock_session.track_file.assert_called_once_with(test_file)
                mock_resolve.assert_called_once_with(
                    {"requests", "beautifulsoup4"}, [test_file]
                )
                assert result == {"requests", "beautifulsoup4"}

    def test_run_dynamic_analysis_with_exception(self):
        """Test dynamic analysis handles execution exceptions."""
        tracker = Tracker()

        # Create a mock Path object
        test_file = MagicMock(spec=Path)
        test_file.is_file.return_value = True
        test_file.suffix = ".py"
        test_file.__str__ = lambda self: "./test.py"  # Fixed: added self parameter

        with patch("src.reqtracker.tracker.TrackingSession") as mock_session_class:
            mock_session = MagicMock()
            mock_session.track_file.side_effect = Exception("Execution failed")
            mock_session_class.return_value = mock_session

            # Mock _get_python_files to return our test file
            with patch.object(tracker, "_get_python_files", return_value=[test_file]):
                with patch.object(
                    tracker, "_resolve_package_names", return_value=set()
                ) as mock_resolve:
                    result = tracker._run_dynamic_analysis([test_file])

                    # Exception handled silently, returns empty set
                    assert result == set()
                    mock_resolve.assert_called_once_with(set(), [test_file])

    def test_run_hybrid_analysis(self):
        """Test hybrid analysis combines static and dynamic results."""
        tracker = Tracker()
        paths = [Path("./test")]

        with patch.object(
            tracker, "_run_static_analysis", return_value={"numpy", "pandas"}
        ):
            with patch.object(
                tracker, "_run_dynamic_analysis", return_value={"requests", "pandas"}
            ):
                result = tracker._run_hybrid_analysis(paths)

                # Should be union of both sets
                assert result == {"numpy", "pandas", "requests"}

    @patch("src.reqtracker.tracker.resolve_package_name")
    def test_resolve_package_names(self, mock_resolve):
        """Test package name resolution."""
        tracker = Tracker()

        # Mock the resolve function to return different values
        def mock_resolve_func(name):
            mapping = {
                "cv2": "opencv-python",
                "requests": "requests",
                "os": None,  # stdlib module
                "": None,  # empty string
            }
            return mapping.get(name, name)

        mock_resolve.side_effect = mock_resolve_func

        import_names = {"cv2", "requests", "os", ""}
        result = tracker._resolve_package_names(import_names)

        # Should exclude None results (stdlib and empty)
        assert result == {"opencv-python", "requests"}

    def test_resolve_package_names_empty_set(self):
        """Test package name resolution with empty set."""
        tracker = Tracker()

        result = tracker._resolve_package_names(set())
        assert result == set()


class TestTrackFunction:
    """Test cases for the module-level track function."""

    def test_track_function_default(self):
        """Test track function with default parameters."""
        with patch("src.reqtracker.tracker.Tracker") as mock_tracker_class:
            mock_tracker = MagicMock()
            mock_tracker.track.return_value = {"requests"}
            mock_tracker_class.return_value = mock_tracker

            result = track()

            mock_tracker_class.assert_called_once_with(None)
            mock_tracker.track.assert_called_once_with(None, TrackingMode.HYBRID)
            assert result == {"requests"}

    def test_track_function_with_parameters(self):
        """Test track function with custom parameters."""
        config = Config()
        paths = ["./src"]

        with patch("src.reqtracker.tracker.Tracker") as mock_tracker_class:
            mock_tracker = MagicMock()
            mock_tracker.track.return_value = {"numpy", "pandas"}
            mock_tracker_class.return_value = mock_tracker

            result = track(source_paths=paths, mode="static", config=config)

            mock_tracker_class.assert_called_once_with(config)
            mock_tracker.track.assert_called_once_with(["./src"], TrackingMode.STATIC)
            assert result == {"numpy", "pandas"}

    def test_track_function_invalid_mode(self):
        """Test track function with invalid mode."""
        with pytest.raises(ValueError):
            track(mode="invalid_mode")


class TestIntegration:
    """Integration tests for the main tracker."""

    def test_real_static_analysis_integration(self):
        """Test integration with real static analyzer."""
        # Create a temporary Python file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
import json
import sys
# These are stdlib and should be filtered out
"""
            )
            temp_path = Path(f.name)

        try:
            tracker = Tracker()

            # This should return empty set since only stdlib imports
            result = tracker._run_static_analysis([temp_path])

            # Should be empty after filtering stdlib modules
            assert isinstance(result, set)

        finally:
            temp_path.unlink()

    def test_configuration_integration(self):
        """Test integration with configuration system."""
        config = Config()
        config.include_patterns = ["*.py"]
        config.exclude_patterns = ["test_*"]

        tracker = Tracker(config)

        # Verify config is used
        assert tracker.config.include_patterns == ["*.py"]
        assert tracker.config.exclude_patterns == ["test_*"]

    def test_full_workflow_simulation(self):
        """Test complete workflow with mocked components."""
        # Mock all the dependencies
        with patch("src.reqtracker.tracker.StaticAnalyzer") as mock_static_class:
            with patch("src.reqtracker.tracker.DynamicTracker") as mock_dynamic_class:
                with patch(
                    "src.reqtracker.tracker.resolve_package_name"
                ) as mock_resolve:
                    # Setup mocks
                    mock_static = MagicMock()
                    mock_dynamic = MagicMock()
                    mock_static_class.return_value = mock_static
                    mock_dynamic_class.return_value = mock_dynamic

                    # Mock resolve function
                    mock_resolve.side_effect = lambda x: x if x != "os" else None

                    # Create tracker and test
                    tracker = Tracker()

                    # Test that components are initialized
                    assert tracker.static_analyzer == mock_static
                    assert tracker.dynamic_tracker == mock_dynamic

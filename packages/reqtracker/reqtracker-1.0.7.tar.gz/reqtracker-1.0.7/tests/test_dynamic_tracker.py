"""Tests for dynamic tracker module."""

import sys
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from src.reqtracker.dynamic_tracker import (
    DynamicTracker,
    ImportHook,
    TrackingSession,
    track_imports,
    track_session,
)


class TestImportHook:
    """Test cases for ImportHook class."""

    def test_initialization(self):
        """Test ImportHook initialization."""
        tracker = DynamicTracker()
        hook = ImportHook(tracker)

        assert hook.tracker is tracker
        assert hasattr(hook, "_lock")

    def test_find_spec_when_tracking(self):
        """Test find_spec behavior when tracking is active."""
        tracker = DynamicTracker()
        tracker.is_tracking = True
        hook = ImportHook(tracker)

        # Mock the _record_import method to verify it gets called
        with patch.object(tracker, "_record_import") as mock_record:
            result = hook.find_spec("test.module", None, None)

            # Should return None (we don't provide modules)
            assert result is None
            # Should record the top-level module
            mock_record.assert_called_once_with("test", "test.module")

    def test_find_spec_when_not_tracking(self):
        """Test find_spec behavior when tracking is inactive."""
        tracker = DynamicTracker()
        tracker.is_tracking = False
        hook = ImportHook(tracker)

        with patch.object(tracker, "_record_import") as mock_record:
            result = hook.find_spec("test.module", None, None)

            assert result is None
            mock_record.assert_not_called()

    def test_find_spec_top_level_extraction(self):
        """Test that only top-level module names are extracted."""
        tracker = DynamicTracker()
        tracker.is_tracking = True
        hook = ImportHook(tracker)

        with patch.object(tracker, "_record_import") as mock_record:
            hook.find_spec("package.submodule.deep", None, None)
            mock_record.assert_called_once_with("package", "package.submodule.deep")


class TestDynamicTracker:
    """Test cases for DynamicTracker class."""

    def test_initialization(self):
        """Test DynamicTracker initialization."""
        tracker = DynamicTracker()

        assert not tracker.is_tracking
        assert len(tracker._imports) == 0
        assert len(tracker._detailed_imports) == 0
        assert tracker._hook is None

    def test_start_stop_tracking(self):
        """Test starting and stopping tracking."""
        tracker = DynamicTracker()
        original_meta_path_length = len(sys.meta_path)

        # Start tracking
        tracker.start_tracking()
        assert tracker.is_tracking
        assert tracker._hook is not None
        assert len(sys.meta_path) == original_meta_path_length + 1
        assert sys.meta_path[0] is tracker._hook

        # Stop tracking
        tracker.stop_tracking()
        assert not tracker.is_tracking
        assert tracker._hook is None
        assert len(sys.meta_path) == original_meta_path_length

    def test_start_tracking_idempotent(self):
        """Test that starting tracking multiple times is safe."""
        tracker = DynamicTracker()

        tracker.start_tracking()
        original_hook = tracker._hook

        tracker.start_tracking()  # Should not create a new hook
        assert tracker._hook is original_hook

        tracker.stop_tracking()

    def test_stop_tracking_when_not_tracking(self):
        """Test stopping tracking when not currently tracking."""
        tracker = DynamicTracker()

        # Should not raise an error
        tracker.stop_tracking()
        assert not tracker.is_tracking

    def test_clear(self):
        """Test clearing tracked imports."""
        tracker = DynamicTracker()

        # Add some test data
        tracker._imports.add("test_module")
        tracker._detailed_imports.append({"module": "test", "timestamp": time.time()})

        tracker.clear()
        assert len(tracker._imports) == 0
        assert len(tracker._detailed_imports) == 0

    def test_get_imports(self):
        """Test getting tracked imports."""
        tracker = DynamicTracker()

        tracker._imports.add("module1")
        tracker._imports.add("module2")

        imports = tracker.get_imports()
        assert isinstance(imports, set)
        assert imports == {"module1", "module2"}

        # Should return a copy, not the original set
        imports.add("module3")
        assert "module3" not in tracker._imports

    def test_get_detailed_imports(self):
        """Test getting detailed import information."""
        tracker = DynamicTracker()

        test_import = {
            "module": "test",
            "fullname": "test.sub",
            "timestamp": time.time(),
        }
        tracker._detailed_imports.append(test_import)

        detailed = tracker.get_detailed_imports()
        assert isinstance(detailed, list)
        assert len(detailed) == 1
        assert detailed[0] == test_import

        # Should return a copy
        detailed.append({"module": "other"})
        assert len(tracker._detailed_imports) == 1

    def test_record_import(self):
        """Test recording imports."""
        tracker = DynamicTracker()

        tracker._record_import("requests", "requests.auth")

        assert "requests" in tracker._imports
        assert len(tracker._detailed_imports) == 1

        detail = tracker._detailed_imports[0]
        assert detail["module"] == "requests"
        assert detail["fullname"] == "requests.auth"
        assert "timestamp" in detail

    def test_record_import_filters_stdlib(self):
        """Test that stdlib modules are filtered out."""
        tracker = DynamicTracker()

        # These should be filtered
        tracker._record_import("os", "os.path")
        tracker._record_import("sys", "sys")
        tracker._record_import("json", "json.decoder")

        assert len(tracker._imports) == 0
        assert len(tracker._detailed_imports) == 0

    def test_is_builtin_or_stdlib(self):
        """Test standard library detection."""
        tracker = DynamicTracker()

        # Built-in modules
        assert tracker._is_builtin_or_stdlib("sys")
        assert tracker._is_builtin_or_stdlib("builtins")

        # Standard library modules
        assert tracker._is_builtin_or_stdlib("os")
        assert tracker._is_builtin_or_stdlib("json")
        assert tracker._is_builtin_or_stdlib("urllib")
        assert tracker._is_builtin_or_stdlib("collections")

        # Third-party modules (should not be stdlib)
        assert not tracker._is_builtin_or_stdlib("requests")
        assert not tracker._is_builtin_or_stdlib("numpy")
        assert not tracker._is_builtin_or_stdlib("django")

    def test_track_execution(self):
        """Test tracking during function execution."""
        tracker = DynamicTracker()

        def test_func():
            return "executed"

        with patch.object(tracker, "start_tracking") as mock_start:
            with patch.object(tracker, "stop_tracking") as mock_stop:
                result = tracker.track_execution(test_func)

                assert result == "executed"
                mock_start.assert_called_once()
                mock_stop.assert_called_once()

    def test_track_execution_with_exception(self):
        """Test tracking when function raises exception."""
        tracker = DynamicTracker()

        def failing_func():
            raise ValueError("test error")

        with patch.object(tracker, "start_tracking") as mock_start:
            with patch.object(tracker, "stop_tracking") as mock_stop:
                with pytest.raises(ValueError):
                    tracker.track_execution(failing_func)

                mock_start.assert_called_once()
                mock_stop.assert_called_once()

    def test_context_manager(self):
        """Test using tracker as context manager."""
        tracker = DynamicTracker()

        with patch.object(tracker, "start_tracking") as mock_start:
            with patch.object(tracker, "stop_tracking") as mock_stop:
                with tracker:
                    pass

                mock_start.assert_called_once()
                mock_stop.assert_called_once()

    def test_thread_safety(self):
        """Test thread safety of the tracker."""
        tracker = DynamicTracker()
        results = []
        errors = []

        def worker():
            try:
                for i in range(10):
                    tracker._record_import(f"module{i}", f"module{i}.sub")
                    time.sleep(0.001)  # Small delay to encourage race conditions
                results.append(True)
            except Exception as e:
                errors.append(e)

        # Start multiple threads
        threads = [threading.Thread(target=worker) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # Should complete without errors
        assert len(errors) == 0
        assert len(results) == 5

        # Should have recorded all imports
        assert len(tracker._imports) == 10
        assert len(tracker._detailed_imports) == 50


class TestTrackingSession:
    """Test cases for TrackingSession class."""

    def test_initialization(self):
        """Test TrackingSession initialization."""
        session = TrackingSession()

        assert isinstance(session.tracker, DynamicTracker)
        assert session.clear_previous is True
        assert session.include_stdlib is False

    def test_initialization_with_options(self):
        """Test TrackingSession initialization with custom options."""
        session = TrackingSession(clear_previous=False, include_stdlib=True)

        assert session.clear_previous is False
        assert session.include_stdlib is True

    def test_track_code(self):
        """Test tracking imports from code string."""
        session = TrackingSession()

        # Test code that would import a third-party module
        # We'll mock the import to avoid actually needing the module
        code = """
# This would normally import a real module, but we'll test the mechanism
import_name = 'requests'
"""

        with patch.object(session.tracker, "track_execution") as mock_track:
            with patch.object(
                session.tracker, "get_imports", return_value={"requests"}
            ):
                imports = session.track_code(code)

                assert mock_track.called
                assert imports == {"requests"}

    def test_track_file(self):
        """Test tracking imports from a Python file."""
        session = TrackingSession()

        # Create a temporary Python file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
# Test file for import tracking
import json  # This should be filtered as stdlib
# import requests  # This would be tracked but we'll mock it
"""
            )
            temp_path = Path(f.name)

        try:
            with patch.object(session.tracker, "track_execution") as mock_track:
                with patch.object(session.tracker, "get_imports", return_value=set()):
                    imports = session.track_file(temp_path)

                    assert mock_track.called
                    assert isinstance(imports, set)
        finally:
            temp_path.unlink()

    def test_track_file_not_found(self):
        """Test tracking non-existent file raises appropriate error."""
        session = TrackingSession()

        with pytest.raises(FileNotFoundError):
            session.track_file("/nonexistent/file.py")

    def test_clear_previous_behavior(self):
        """Test clear_previous option behavior."""
        session = TrackingSession(clear_previous=True)

        with patch.object(session.tracker, "clear") as mock_clear:
            with patch.object(session.tracker, "track_execution"):
                with patch.object(session.tracker, "get_imports", return_value=set()):
                    session.track_code("pass")
                    mock_clear.assert_called_once()

    def test_no_clear_previous_behavior(self):
        """Test behavior when clear_previous is False."""
        session = TrackingSession(clear_previous=False)

        with patch.object(session.tracker, "clear") as mock_clear:
            with patch.object(session.tracker, "track_execution"):
                with patch.object(session.tracker, "get_imports", return_value=set()):
                    session.track_code("pass")
                    mock_clear.assert_not_called()

    def test_context_manager(self):
        """Test using TrackingSession as context manager."""
        session = TrackingSession()

        with patch.object(session.tracker, "clear") as mock_clear:
            with patch.object(session.tracker, "__enter__") as mock_enter:
                with patch.object(session.tracker, "__exit__") as mock_exit:
                    with session:
                        pass

                    mock_clear.assert_called_once()
                    mock_enter.assert_called_once()
                    mock_exit.assert_called_once()


class TestModuleFunctions:
    """Test cases for module-level functions."""

    def test_track_imports(self):
        """Test track_imports function."""
        tracker = track_imports()

        assert isinstance(tracker, DynamicTracker)
        assert not tracker.is_tracking

    def test_track_session(self):
        """Test track_session function."""
        session = track_session()

        assert isinstance(session, TrackingSession)
        assert session.clear_previous is True
        assert session.include_stdlib is False

    def test_track_session_with_options(self):
        """Test track_session function with custom options."""
        session = track_session(clear_previous=False, include_stdlib=True)

        assert session.clear_previous is False
        assert session.include_stdlib is True


class TestIntegration:
    """Integration tests for dynamic tracking."""

    def test_real_import_tracking(self):
        """Test tracking real imports (using only stdlib to avoid dependencies)."""
        tracker = DynamicTracker()

        # Use a simple function that imports a module
        def import_something():
            # Import a module that we can control
            import tempfile  # This should be filtered as stdlib

            return tempfile

        tracker.start_tracking()
        try:
            import_something()
            # Since tempfile is stdlib, it should be filtered out
            imports = tracker.get_imports()
            assert "tempfile" not in imports
        finally:
            tracker.stop_tracking()

    def test_context_manager_integration(self):
        """Test full context manager workflow."""
        with track_session() as tracker:
            # This should be tracked if it weren't stdlib

            # The tracker should be active
            assert tracker.is_tracking

        # After exiting, tracking should be stopped
        assert not tracker.is_tracking

    def test_nested_tracking_safety(self):
        """Test that nested tracking calls are handled safely."""
        tracker = DynamicTracker()

        # Start tracking
        tracker.start_tracking()
        original_hook = tracker._hook

        try:
            # Start again (should be safe)
            tracker.start_tracking()
            assert tracker._hook is original_hook

            # Stop once
            tracker.stop_tracking()
            assert not tracker.is_tracking

            # Stop again (should be safe)
            tracker.stop_tracking()
            assert not tracker.is_tracking
        finally:
            # Ensure cleanup
            if tracker.is_tracking:
                tracker.stop_tracking()

    def test_import_hook_cleanup(self):
        """Test that import hooks are properly cleaned up."""
        original_meta_path = list(sys.meta_path)

        tracker = DynamicTracker()
        tracker.start_tracking()

        # Verify hook was added
        assert len(sys.meta_path) == len(original_meta_path) + 1

        tracker.stop_tracking()

        # Verify hook was removed and meta_path is restored
        assert sys.meta_path == original_meta_path

    def test_multiple_trackers(self):
        """Test that multiple trackers can coexist."""
        tracker1 = DynamicTracker()
        tracker2 = DynamicTracker()

        try:
            tracker1.start_tracking()
            tracker2.start_tracking()

            # Both should be tracking
            assert tracker1.is_tracking
            assert tracker2.is_tracking

            # Each should have its own hook
            assert tracker1._hook != tracker2._hook

        finally:
            tracker1.stop_tracking()
            tracker2.stop_tracking()

    def test_exception_during_tracking(self):
        """Test behavior when exceptions occur during tracking."""
        tracker = DynamicTracker()

        def failing_function():

            raise RuntimeError("Test error")

        # Should handle exceptions gracefully
        with pytest.raises(RuntimeError):
            tracker.track_execution(failing_function)

        # Tracking should be stopped even after exception
        assert not tracker.is_tracking

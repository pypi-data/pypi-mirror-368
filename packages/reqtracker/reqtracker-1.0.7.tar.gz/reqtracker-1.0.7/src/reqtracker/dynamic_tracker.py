"""Dynamic import tracking using import hooks.

This module provides runtime import tracking by hooking into Python's
import machinery using sys.meta_path hooks.
"""

import sys
import threading
from importlib.abc import MetaPathFinder
from importlib.machinery import ModuleSpec
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List, Optional, Set, Union


class ImportHook(MetaPathFinder):
    """Meta path finder that tracks imports without interfering with normal loading."""

    def __init__(self, tracker: "DynamicTracker"):
        """Initialize the import hook.

        Args:
            tracker: The DynamicTracker instance to report imports to.
        """
        self.tracker = tracker
        self._lock = threading.RLock()

    def find_spec(
        self,
        fullname: str,
        path: Optional[List[str]],
        target: Optional[ModuleType] = None,
    ) -> Optional[ModuleSpec]:
        """Find module spec and record the import attempt.

        Args:
            fullname: Full name of the module being imported.
            path: Module search path.
            target: Target module for reloading.

        Returns:
            None (we don't actually provide modules, just track them).
        """
        with self._lock:
            # Only track top-level package names for consistency with static analysis
            top_level_module = fullname.split(".")[0]

            # Record the import if tracking is active
            if self.tracker.is_tracking:
                self.tracker._record_import(top_level_module, fullname)

        # Return None to let other finders handle the actual import
        return None


class DynamicTracker:
    """Dynamic import tracker using import hooks."""

    def __init__(self):
        """Initialize the dynamic tracker."""
        self.is_tracking: bool = False
        self._imports: Set[str] = set()
        self._detailed_imports: List[Dict[str, Union[str, float]]] = []
        self._hook: Optional[ImportHook] = None
        self._lock = threading.RLock()
        self._original_path_pos: Optional[int] = None

    def start_tracking(self) -> None:
        """Start tracking imports by installing the import hook."""
        with self._lock:
            if self.is_tracking:
                return  # Already tracking

            # Create and install the hook
            self._hook = ImportHook(self)

            # Install at the beginning of sys.meta_path to catch all imports
            sys.meta_path.insert(0, self._hook)
            self._original_path_pos = 0

            self.is_tracking = True

    def stop_tracking(self) -> None:
        """Stop tracking imports by removing the import hook."""
        with self._lock:
            if not self.is_tracking or self._hook is None:
                return  # Not tracking

            # Remove the hook from sys.meta_path
            try:
                sys.meta_path.remove(self._hook)
            except ValueError:
                # Hook was already removed or not in the list
                pass

            self._hook = None
            self._original_path_pos = None
            self.is_tracking = False

    def clear(self) -> None:
        """Clear all recorded imports."""
        with self._lock:
            self._imports.clear()
            self._detailed_imports.clear()

    def get_imports(self) -> Set[str]:
        """Get all recorded top-level imports.

        Returns:
            Set of top-level module names.
        """
        with self._lock:
            return set(self._imports)

    def get_detailed_imports(self) -> List[Dict[str, Union[str, float]]]:
        """Get detailed import information.

        Returns:
            List of import dictionaries with module, fullname, and timestamp.
        """
        with self._lock:
            return list(self._detailed_imports)

    def _record_import(self, module: str, fullname: str) -> None:
        """Record an import internally.

        Args:
            module: Top-level module name.
            fullname: Full module name including submodules.
        """
        import time

        with self._lock:
            # Skip built-in modules and standard library
            if self._is_builtin_or_stdlib(module):
                return

            # Record the top-level module
            self._imports.add(module)

            # Record detailed information
            self._detailed_imports.append(
                {
                    "module": module,
                    "fullname": fullname,
                    "timestamp": time.time(),
                }
            )

    def _is_builtin_or_stdlib(self, module_name: str) -> bool:
        """Check if a module is built-in or part of the standard library.

        Args:
            module_name: Name of the module to check.

        Returns:
            True if the module is built-in or stdlib.
        """
        # Check if it's a built-in module
        if module_name in sys.builtin_module_names:
            return True

        # Check for common standard library modules
        # This is a simplified check - in production, you might want
        # to use a more comprehensive stdlib detection method
        stdlib_modules = {
            "os",
            "sys",
            "json",
            "urllib",
            "http",
            "datetime",
            "time",
            "collections",
            "itertools",
            "functools",
            "operator",
            "copy",
            "pickle",
            "csv",
            "configparser",
            "logging",
            "unittest",
            "threading",
            "multiprocessing",
            "subprocess",
            "shutil",
            "glob",
            "fnmatch",
            "linecache",
            "tempfile",
            "gzip",
            "zipfile",
            "tarfile",
            "sqlite3",
            "hashlib",
            "hmac",
            "secrets",
            "ssl",
            "socket",
            "email",
            "base64",
            "binascii",
            "struct",
            "codecs",
            "locale",
            "gettext",
            "argparse",
            "optparse",
            "getopt",
            "traceback",
            "inspect",
            "dis",
            "atexit",
            "warnings",
            "contextlib",
            "abc",
            "numbers",
            "math",
            "decimal",
            "fractions",
            "random",
            "statistics",
            "re",
            "string",
            "text",
            "unicodedata",
        }

        return module_name in stdlib_modules

    def track_execution(self, func, *args, **kwargs) -> Any:
        """Track imports during function execution.

        Args:
            func: Function to execute while tracking.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            Result of the function execution.
        """
        self.start_tracking()
        try:
            return func(*args, **kwargs)
        finally:
            self.stop_tracking()

    def __enter__(self):
        """Context manager entry."""
        self.start_tracking()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_tracking()


class TrackingSession:
    """High-level interface for tracking imports during code execution."""

    def __init__(self, clear_previous: bool = True, include_stdlib: bool = False):
        """Initialize a tracking session.

        Args:
            clear_previous: Whether to clear previous tracking data.
            include_stdlib: Whether to include standard library modules.
        """
        self.tracker = DynamicTracker()
        self.clear_previous = clear_previous
        self.include_stdlib = include_stdlib

    def track_file(self, file_path: Union[str, Path]) -> Set[str]:
        """Track imports by executing a Python file.

        Args:
            file_path: Path to the Python file to execute.

        Returns:
            Set of imported module names.
        """
        if self.clear_previous:
            self.tracker.clear()

        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read and execute the file
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

        # Create a namespace for execution
        namespace = {
            "__file__": str(file_path),
            "__name__": "__main__",
        }

        def execute():
            try:
                exec(code, namespace)
            except ImportError as e:
                # Import errors are expected when tracking dependencies
                # The hook will have already recorded the import attempt
                pass
            except Exception as e:
                # Other errors should still be handled gracefully
                # but we don't want to fail completely
                pass

        self.tracker.track_execution(execute)
        return self.tracker.get_imports()

    def track_code(self, code: str) -> Set[str]:
        """Track imports by executing code string.

        Args:
            code: Python code to execute.

        Returns:
            Set of imported module names.
        """
        if self.clear_previous:
            self.tracker.clear()

        def execute():
            try:
                exec(code)
            except ImportError:
                # Import errors are expected when tracking dependencies
                # The hook will have already recorded the import attempt
                pass
            except Exception:
                # Other errors should be handled gracefully
                pass

        self.tracker.track_execution(execute)
        return self.tracker.get_imports()

    def __enter__(self):
        """Context manager entry."""
        if self.clear_previous:
            self.tracker.clear()
        return self.tracker.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        return self.tracker.__exit__(exc_type, exc_val, exc_tb)


def track_imports() -> DynamicTracker:
    """Create a new dynamic tracker instance.

    Returns:
        A new DynamicTracker instance.
    """
    return DynamicTracker()


def track_session(
    clear_previous: bool = True, include_stdlib: bool = False
) -> TrackingSession:
    """Create a new tracking session.

    Args:
        clear_previous: Whether to clear previous tracking data.
        include_stdlib: Whether to include standard library modules.

    Returns:
        A new TrackingSession instance.
    """
    return TrackingSession(clear_previous=clear_previous, include_stdlib=include_stdlib)

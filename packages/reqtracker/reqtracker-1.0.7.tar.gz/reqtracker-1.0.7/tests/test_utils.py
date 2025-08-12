"""Tests for utility functions."""

import tempfile
from pathlib import Path

import pytest

from src.reqtracker import track
from src.reqtracker.utils import (
    get_package_name,
    is_local_module,
    is_standard_library,
    normalize_package_name,
)


class TestGetPackageName:
    """Test cases for get_package_name function."""

    def test_known_mappings(self):
        """Test that known import names are mapped correctly."""
        assert get_package_name("cv2") == "opencv-python"
        assert get_package_name("sklearn") == "scikit-learn"
        assert get_package_name("PIL") == "Pillow"

    def test_unknown_imports(self):
        """Test that unknown imports return as-is."""
        assert get_package_name("requests") == "requests"
        assert get_package_name("numpy") == "numpy"
        assert get_package_name("unknown_package") == "unknown_package"

    def test_case_sensitivity(self):
        """Test that import name lookup is case-sensitive."""
        assert get_package_name("pil") == "pil"  # Should not map to Pillow
        assert get_package_name("PIL") == "Pillow"  # Should map to Pillow


class TestIsStandardLibrary:
    """Test cases for is_standard_library function."""

    # Comprehensive list of Python standard library modules
    STDLIB_MODULES = [
        # Core built-in modules
        "__future__",
        "__main__",
        "_thread",
        "_dummy_thread",
        # Text processing
        "string",
        "re",
        "difflib",
        "textwrap",
        "unicodedata",
        "stringprep",
        "readline",
        "rlcompleter",
        # Binary data services
        "struct",
        "codecs",
        "encodings",
        # Data types
        "datetime",
        "calendar",
        "collections",
        "collections.abc",
        "heapq",
        "bisect",
        "array",
        "weakref",
        "types",
        "copy",
        "pprint",
        "reprlib",
        "enum",
        "dataclasses",
        # Numeric and mathematical
        "numbers",
        "math",
        "cmath",
        "decimal",
        "fractions",
        "random",
        "statistics",
        # Functional programming
        "itertools",
        "functools",
        "operator",
        # File and directory access
        "pathlib",
        "os.path",
        "fileinput",
        "stat",
        "filecmp",
        "tempfile",
        "glob",
        "fnmatch",
        "linecache",
        "shutil",
        # Data persistence
        "pickle",
        "copyreg",
        "shelve",
        "marshal",
        "dbm",
        "sqlite3",
        # Data compression
        "zlib",
        "gzip",
        "bz2",
        "lzma",
        "zipfile",
        "tarfile",
        # File formats
        "csv",
        "configparser",
        "netrc",
        "xdrlib",
        "plistlib",
        # Cryptographic services
        "hashlib",
        "hmac",
        "secrets",
        # Generic OS services
        "os",
        "io",
        "time",
        "argparse",
        "getopt",
        "logging",
        "logging.config",
        "logging.handlers",
        "getpass",
        "curses",
        "curses.textpad",
        "curses.ascii",
        "curses.panel",
        "platform",
        "errno",
        "ctypes",
        # Concurrent execution
        "threading",
        "multiprocessing",
        "multiprocessing.shared_memory",
        "concurrent",
        "concurrent.futures",
        "subprocess",
        "sched",
        "queue",
        "contextvars",
        "_thread",
        # Async
        "asyncio",
        "asyncore",
        "asynchat",
        # Networking and IPC
        "socket",
        "ssl",
        "select",
        "selectors",
        "asyncio",
        "mmap",
        "signal",
        # Internet data handling
        "email",
        "json",
        "mailcap",
        "mailbox",
        "mimetypes",
        "base64",
        "binhex",
        "binascii",
        "quopri",
        "uu",
        # Structured markup
        "html",
        "html.parser",
        "html.entities",
        "xml",
        "xml.etree",
        "xml.dom",
        "xml.sax",
        "xmlrpc",
        "xmlrpc.client",
        "xmlrpc.server",
        # Internet protocols
        "webbrowser",
        "cgi",
        "cgitb",
        "wsgiref",
        "urllib",
        "urllib.parse",
        "urllib.error",
        "urllib.robotparser",
        "http",
        "http.client",
        "http.server",
        "http.cookies",
        "http.cookiejar",
        "ftplib",
        "poplib",
        "imaplib",
        "nntplib",
        "smtplib",
        "smtpd",
        "telnetlib",
        "uuid",
        "socketserver",
        # Multimedia
        "audioop",
        "aifc",
        "sunau",
        "wave",
        "chunk",
        "colorsys",
        "imghdr",
        "sndhdr",
        "ossaudiodev",
        # Internationalization
        "gettext",
        "locale",
        # Program frameworks
        "turtle",
        "cmd",
        "shlex",
        # GUI
        "tkinter",
        "tkinter.ttk",
        "tkinter.tix",
        "tkinter.scrolledtext",
        # Development tools
        "typing",
        "typing_extensions",
        "pydoc",
        "doctest",
        "unittest",
        "unittest.mock",
        "test",
        "test.support",
        # Debugging and profiling
        "bdb",
        "faulthandler",
        "pdb",
        "timeit",
        "trace",
        "tracemalloc",
        "cProfile",
        "profile",
        "pstats",
        # Software packaging
        "distutils",
        "ensurepip",
        "venv",
        "zipapp",
        # Runtime services
        "sys",
        "sysconfig",
        "builtins",
        "warnings",
        "dataclasses",
        "contextlib",
        "abc",
        "atexit",
        "traceback",
        "gc",
        "inspect",
        "site",
        "code",
        "codeop",
        # Custom interpreters
        "code",
        "codeop",
        # Importing modules
        "zipimport",
        "pkgutil",
        "modulefinder",
        "runpy",
        "importlib",
        "importlib.util",
        "importlib.machinery",
        # Language services
        "parser",
        "ast",
        "symtable",
        "symbol",
        "token",
        "keyword",
        "tokenize",
        "tabnanny",
        "pyclbr",
        "py_compile",
        "compileall",
        "dis",
        "pickletools",
        # Miscellaneous
        "formatter",
        # Windows specific
        "msilib",
        "msvcrt",
        "winreg",
        "winsound",
        # Unix specific
        "posix",
        "pwd",
        "spwd",
        "grp",
        "crypt",
        "termios",
        "tty",
        "pty",
        "fcntl",
        "pipes",
        "resource",
        "nis",
        "syslog",
        # Deprecated
        "optparse",
        "imp",
        # Python 2 compatibility
        "__builtin__",
        "__import__",
    ]

    def test_standard_modules(self):
        """Test that standard library modules are identified."""
        assert is_standard_library("os")
        assert is_standard_library("sys")
        assert is_standard_library("json")
        assert is_standard_library("datetime")

    def test_third_party_modules(self):
        """Test that third-party modules are not identified as stdlib."""
        assert not is_standard_library("numpy")
        assert not is_standard_library("requests")
        assert not is_standard_library("PIL")

    def test_submodules(self):
        """Test that submodules are handled correctly."""
        assert is_standard_library("os.path")
        assert is_standard_library("collections.abc")
        assert not is_standard_library("numpy.array")

    def test_more_stdlib_modules(self):
        """Test additional standard library modules."""
        assert is_standard_library("ast")
        assert is_standard_library("zipfile")
        assert is_standard_library("dataclasses")
        assert is_standard_library("asyncio")

    def test_comprehensive_stdlib_modules(self):
        """Test that each stdlib module is correctly identified."""
        failed_modules = []

        for module in self.STDLIB_MODULES:
            if not is_standard_library(module):
                failed_modules.append(module)

        if failed_modules:
            pytest.fail(
                "Failed to identify "
                f"{len(failed_modules)} stdlib modules as standard library:\n"
                f"{', '.join(sorted(failed_modules))}"
            )

    def test_stdlib_not_in_requirements(self):
        """Test that stdlib modules are excluded from requirements generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)

            # Create a file that imports various stdlib modules
            test_file = project / "test_stdlib_imports.py"
            test_file.write_text(
                """
# Test standard library imports
import os
import sys
import json
import csv
import datetime
import time
import contextvars
import ctypes
import dataclasses
import pathlib
import asyncio
import concurrent.futures
import multiprocessing
import threading
import urllib.parse
import http.client
import email.utils
import sqlite3
import logging
import unittest
import typing
from collections import defaultdict
from itertools import chain
from pathlib import Path
from typing import List, Dict, Optional
from contextvars import ContextVar
from dataclasses import dataclass
import xml.etree.ElementTree as ET

# Also test some third-party imports
import requests
import numpy as np
import pandas as pd
"""
            )

            # Track dependencies
            packages = track([str(project)], mode="static")

            # Check that NO stdlib modules are in the results
            stdlib_found = []
            for module in self.STDLIB_MODULES:
                if module in packages:
                    stdlib_found.append(module)

            # Should only have the external packages
            assert packages == {
                "requests",
                "numpy",
                "pandas",
            }, f"Expected only external packages, but got: {packages}"

            if stdlib_found:
                pytest.fail(
                    f"Standard library modules found in package list: {stdlib_found}"
                )

    def test_mixed_imports_with_aliases(self):
        """Test stdlib detection with import aliases and complex patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)

            test_file = project / "complex_imports.py"
            test_file.write_text(
                """
# Complex import patterns
import os as operating_system
import sys as system
from pathlib import Path as PathType
from typing import List as ListType, Dict as DictType
import xml.etree.ElementTree as ET
from collections.abc import Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor as TPE
import urllib.request as url_request

# Third-party
import numpy as np
from flask import Flask, render_template
"""
            )

            packages = track([str(project)], mode="static")

            # Should only get third-party packages
            assert packages == {"numpy", "Flask"}

    def test_future_stdlib_modules(self):
        """Test handling of __future__ imports."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)

            test_file = project / "future_test.py"
            test_file.write_text(
                """
from __future__ import annotations
from __future__ import print_function, division
import requests
"""
            )

            packages = track([str(project)], mode="static")

            assert "__future__" not in packages
            assert packages == {"requests"}


class TestNormalizePackageName:
    """Test cases for normalize_package_name function."""

    def test_lowercase_conversion(self):
        """Test that package names are converted to lowercase."""
        assert normalize_package_name("Django") == "django"
        assert normalize_package_name("NumPy") == "numpy"
        assert normalize_package_name("PIL") == "pil"

    def test_underscore_replacement(self):
        """Test that underscores are replaced with hyphens."""
        assert normalize_package_name("discord_py") == "discord-py"
        assert normalize_package_name("google_cloud_storage") == "google-cloud-storage"

    def test_dot_replacement(self):
        """Test that dots are replaced with hyphens."""
        assert normalize_package_name("ruamel.yaml") == "ruamel-yaml"
        assert normalize_package_name("backports.csv") == "backports-csv"

    def test_multiple_separators(self):
        """Test handling of multiple separators."""
        assert normalize_package_name("some.package_name") == "some-package-name"
        assert normalize_package_name("Another_Package.Name") == "another-package-name"


class TestLocalModuleDetection:
    """Test cases for local module detection."""

    def test_is_local_module(self):
        """Test detection of local modules."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir)

            # Create some test modules
            (source_path / "mymodule.py").touch()
            (source_path / "package" / "__init__.py").mkdir(parents=True)
            (source_path / "package" / "__init__.py").touch()

            # Test direct module
            assert is_local_module("mymodule", [source_path])

            # Test package
            assert is_local_module("package", [source_path])

            # Test non-existent module
            assert not is_local_module("nonexistent", [source_path])

            # Test with multiple source paths
            other_path = source_path / "other"
            other_path.mkdir()
            (other_path / "othermodule.py").touch()

            assert is_local_module("othermodule", [source_path, other_path])
            assert is_local_module("mymodule", [source_path, other_path])


class TestRealWorldStdlibScenarios:
    """Test real-world scenarios that have caused issues."""

    def test_knapsack_solver_scenario(self):
        """Test the specific scenario from the user's knapsack solver project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)

            # Recreate the user's project structure
            (project / "main.py").write_text(
                """
import json
import numpy as np
import time
import tracemalloc
from dp_solver import solve_knapsack_dp_discretized
from dp_solver_memory_optimized import solve_knapsack_dp_discretized_memory_optimized
"""
            )

            (project / "dp_solver.py").write_text(
                """
def solve_knapsack_dp_discretized(items, capacity):
    pass
"""
            )

            (project / "dp_solver_memory_optimized.py").write_text(
                """
def solve_knapsack_dp_discretized_memory_optimized(items, capacity):
    pass
"""
            )

            packages = track([str(project)], mode="static")

            # Should only have numpy
            assert packages == {"numpy"}
            assert "json" not in packages
            assert "time" not in packages
            assert "tracemalloc" not in packages
            assert "dp_solver" not in packages

    def test_contextvars_ctypes_bug(self):
        """Test the specific bug where contextvars and ctypes were included."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)

            (project / "app.py").write_text(
                """
import contextvars
import ctypes
import numpy
import requests
"""
            )

            packages = track([str(project)], mode="static")

            # The bug was that contextvars and ctypes were included
            assert "contextvars" not in packages
            assert "ctypes" not in packages
            assert packages == {"numpy", "requests"}

    def test_data_science_project(self):
        """Test a typical data science project with many imports."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)

            (project / "analysis.py").write_text(
                """
# Standard library
import os
import sys
import json
import csv
import pickle
import datetime
import time
import warnings
import logging
from pathlib import Path
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Optional
import sqlite3

# Data science stack
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import scipy.stats
"""
            )

            packages = track([str(project)], mode="static")

            # Should only have the data science packages
            expected = {"numpy", "pandas", "matplotlib", "seaborn", "sklearn", "scipy"}

            # scikit-learn might be detected as sklearn or scikit-learn
            if "scikit-learn" in packages:
                expected.remove("sklearn")
                expected.add("scikit-learn")

            assert packages == expected

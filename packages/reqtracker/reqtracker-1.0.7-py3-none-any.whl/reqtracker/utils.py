"""Utility functions for reqtracker.

This module provides helper functions for package name resolution
and import-to-package mapping.
"""

import re
import sys


def get_package_name(import_name: str) -> str:
    """Get the package name for a given import name.

    Args:
        import_name: The name used in import statements.

    Returns:
        The corresponding package name for pip installation.
        Returns the import name itself if no mapping is found.

    Examples:
        >>> get_package_name("cv2")
        "opencv-python"
        >>> get_package_name("numpy")
        "numpy"
    """
    from src.reqtracker.mappings import IMPORT_TO_PACKAGE

    # Check if we have a known mapping
    if import_name in IMPORT_TO_PACKAGE:
        return IMPORT_TO_PACKAGE[import_name]

    # No mapping found, return as-is
    return import_name


def is_standard_library(module_name: str) -> bool:
    """Check if a module is part of Python's standard library.

    Args:
        module_name: Name of the module to check.

    Returns:
        True if the module is in the standard library.
    """
    # Check built-in modules first
    top_level = module_name.split(".")[0]
    if top_level in sys.builtin_module_names:
        return True

    # Check for internal C extension modules (start with underscore)
    if top_level.startswith("_"):
        return True

    # Comprehensive list of Python standard library modules
    stdlib_modules = {
        "MimeWriter",
        "_winapi",
        "abc",
        "aifc",
        "argparse",
        "array",
        "ast",
        "asynchat",
        "asyncio",
        "asyncore",
        "audioop",
        "base64",
        "bdb",
        "binascii",
        "binhex",
        "bisect",
        "bz2",
        "cProfile",
        "calendar",
        "cgi",
        "cgitb",
        "chunk",
        "cmath",
        "cmd",
        "code",
        "codecs",
        "codeop",
        "collections",
        "colorsys",
        "commands",
        "compileall",
        "compression",
        "concurrent",
        "concurrent.futures",
        "configparser",
        "contextlib",
        "contextvars",
        "copy",
        "copyreg",
        "crypt",
        "csv",
        "ctypes",
        "curses",
        "curses.ascii",
        "curses.panel",
        "curses.textpad",
        "dataclasses",
        "datetime",
        "dbm",
        "decimal",
        "difflib",
        "dis",
        "distutils",
        "dl",
        "doctest",
        "email",
        "encodings",
        "ensurepip",
        "enum",
        "fcntl",
        "filecmp",
        "fileinput",
        "fnmatch",
        "formatter",
        "fractions",
        "ftplib",
        "functools",
        "getopt",
        "getpass",
        "gettext",
        "glob",
        "grp",
        "gzip",
        "hashlib",
        "heapq",
        "hmac",
        "html",
        "http",
        "imaplib",
        "imghdr",
        "imp",
        "importlib",
        "inspect",
        "io",
        "ipaddress",
        "itertools",
        "json",
        "keyword",
        "linecache",
        "locale",
        "logging",
        "lzma",
        "mailbox",
        "mailcap",
        "math",
        "mhlib",
        "mimetypes",
        "mimify",
        "mmap",
        "modulefinder",
        "msilib",
        "msvcrt",
        "multiprocessing",
        "netrc",
        "nis",
        "nntplib",
        "numbers",
        "operator",
        "optparse",
        "os",
        "ossaudiodev",
        "parser",
        "pathlib",
        "pdb",
        "pickle",
        "pickletools",
        "pipes",
        "pkgutil",
        "platform",
        "plistlib",
        "poplib",
        "posixfile",
        "pprint",
        "profile",
        "pstats",
        "pty",
        "pwd",
        "py_compile",
        "pyclbr",
        "pydoc",
        "queue",
        "quopri",
        "random",
        "re",
        "readline",
        "reprlib",
        "resource",
        "rfc822",
        "rlcompleter",
        "runpy",
        "sched",
        "secrets",
        "select",
        "selectors",
        "shelve",
        "shlex",
        "shutil",
        "signal",
        "simplejson",
        "site",
        "smtpd",
        "smtplib",
        "sndhdr",
        "socket",
        "socketserver",
        "socks",
        "spwd",
        "sqlite3",
        "ssl",
        "stat",
        "statistics",
        "string",
        "stringprep",
        "struct",
        "subprocess",
        "sunau",
        "symbol",
        "symtable",
        "sys",
        "sysconfig",
        "syslog",
        "tabnanny",
        "tarfile",
        "telnetlib",
        "tempfile",
        "termios",
        "test",
        "test.support",
        "textwrap",
        "threading",
        "time",
        "timeit",
        "tkinter",
        "tkinter.scrolledtext",
        "tkinter.tix",
        "tkinter.ttk",
        "token",
        "tokenize",
        "trace",
        "traceback",
        "tracemalloc",
        "tty",
        "turtle",
        "types",
        "typing",
        "typing_extensions",
        "unicodedata",
        "unittest",
        "urllib",
        "uu",
        "uuid",
        "venv",
        "warnings",
        "wave",
        "weakref",
        "webbrowser",
        "winreg",
        "winsound",
        "wsgiref",
        "xdrlib",
        "xml",
        "xmlrpc",
        "xmlrpc.client",
        "xmlrpc.server",
        "zipapp",
        "zipfile",
        "zipimport",
        "zlib",
        "pyexpat",
    }

    return top_level in stdlib_modules


def normalize_package_name(name: str) -> str:
    """Normalize package name according to PEP 503.

    Args:
        name: Package name to normalize.

    Returns:
        Normalized package name.

    Examples:
        >>> normalize_package_name("Django")
        "django"
        >>> normalize_package_name("python-dateutil")
        "python-dateutil"
    """
    # PEP 503 normalization: lowercase and replace underscore/dots with hyphens
    return re.sub(r"[-_.]+", "-", name).lower()


def is_local_module(module_name: str, source_paths: list) -> bool:
    """Check if a module is a local file in the project.

    Args:
        module_name: Name of the module to check
        source_paths: List of source paths being analyzed

    Returns:
        True if the module is a local file, False otherwise
    """
    from pathlib import Path

    for source_path in source_paths:
        path = Path(source_path)
        if path.is_file():
            # Check the directory containing the file
            search_dir = path.parent
        else:
            search_dir = path

        # Check for module.py or module/__init__.py
        if (search_dir / f"{module_name}.py").exists():
            return True
        if (search_dir / module_name / "__init__.py").exists():
            return True

        # Check subdirectories
        for py_file in search_dir.rglob("*.py"):
            if py_file.stem == module_name:
                return True

    return False

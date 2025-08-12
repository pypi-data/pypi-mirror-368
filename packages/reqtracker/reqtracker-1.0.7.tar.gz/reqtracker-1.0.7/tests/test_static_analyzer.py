"""Tests for static analyzer module."""

import ast
import tempfile
from pathlib import Path

from src.reqtracker.static_analyzer import ImportVisitor, StaticAnalyzer


class TestImportVisitor:
    """Test cases for ImportVisitor class."""

    def test_import_detection(self):
        """Test detection of regular import statements."""
        code = """
import os
import sys
import numpy as np
"""
        tree = ast.parse(code)
        visitor = ImportVisitor()
        visitor.visit(tree)

        assert len(visitor.imports) == 3
        assert visitor.imports[0]["module"] == "os"
        assert visitor.imports[1]["module"] == "sys"
        assert visitor.imports[2]["module"] == "numpy"
        assert all(imp["type"] == "import" for imp in visitor.imports)

    def test_from_import_detection(self):
        """Test detection of from...import statements."""
        code = """
from pathlib import Path
from typing import List, Dict
from ..utils import helper
"""
        tree = ast.parse(code)
        visitor = ImportVisitor()
        visitor.visit(tree)

        assert len(visitor.imports) == 3
        assert visitor.imports[0]["module"] == "pathlib"
        assert visitor.imports[1]["module"] == "typing"
        assert visitor.imports[2]["module"] == "..utils"
        assert all(imp["type"] == "from" for imp in visitor.imports)

    def test_line_numbers(self):
        """Test that line numbers are correctly recorded."""
        code = """import os

import sys

from pathlib import Path"""

        tree = ast.parse(code)
        visitor = ImportVisitor()
        visitor.visit(tree)

        assert visitor.imports[0]["line"] == 1
        assert visitor.imports[1]["line"] == 3
        assert visitor.imports[2]["line"] == 5


class TestStaticAnalyzer:
    """Test cases for StaticAnalyzer class."""

    def test_initialization(self):
        """Test analyzer initialization."""
        analyzer = StaticAnalyzer()

        assert analyzer.project_root == Path.cwd()
        assert analyzer.include_patterns == ["*.py"]
        assert analyzer.exclude_patterns == []
        assert len(analyzer._analyzed_files) == 0

    def test_configure(self):
        """Test analyzer configuration."""
        analyzer = StaticAnalyzer()
        root = Path("/test/path")

        analyzer.configure(
            project_root=root,
            include_patterns=["*.py", "*.pyw"],
            exclude_patterns=["tests/*", "__pycache__/*"],
        )

        assert analyzer.project_root == root
        assert analyzer.include_patterns == ["*.py", "*.pyw"]
        assert analyzer.exclude_patterns == ["tests/*", "__pycache__/*"]

    def test_analyze_file(self):
        """Test analyzing a single file."""
        # Create a temporary Python file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
import os
from pathlib import Path

def main():
    pass
"""
            )
            temp_path = Path(f.name)

        try:
            analyzer = StaticAnalyzer()
            imports = analyzer.analyze_file(temp_path)

            assert len(imports) == 2
            assert imports[0]["module"] == "os"
            assert imports[1]["module"] == "pathlib"
            assert all(imp["file"] == temp_path for imp in imports)
        finally:
            temp_path.unlink()

    def test_should_exclude(self):
        """Test file exclusion logic."""
        analyzer = StaticAnalyzer()
        analyzer.project_root = Path("/project")
        analyzer.exclude_patterns = ["tests/*", "__pycache__/*", "*.pyc", "venv/*"]

        # Test paths that should be excluded
        assert analyzer._should_exclude(Path("/project/tests/test_something.py"))
        assert analyzer._should_exclude(Path("/project/__pycache__/module.pyc"))
        assert analyzer._should_exclude(Path("/project/src/__pycache__/file.py"))
        assert analyzer._should_exclude(Path("/project/venv/lib/python3.9/test.py"))

        # Test paths that should NOT be excluded
        assert not analyzer._should_exclude(Path("/project/src/main.py"))
        assert not analyzer._should_exclude(Path("/project/app.py"))

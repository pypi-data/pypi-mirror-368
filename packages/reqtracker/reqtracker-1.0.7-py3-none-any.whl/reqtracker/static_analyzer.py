"""Static code analysis for import detection.

This module provides AST-based static analysis to detect imports
in Python source files without executing the code.
"""

import ast
from pathlib import Path
from typing import Dict, List, Set, Union


class ImportVisitor(ast.NodeVisitor):
    """AST visitor to collect import statements."""

    def __init__(self):
        """Initialize the import visitor."""
        # Fixed: Updated type hint to include Path for the "file" key
        self.imports: List[Dict[str, Union[str, int, Path]]] = []

    def visit_Import(self, node: ast.Import) -> None:
        """Visit import statements.

        Args:
            node: Import AST node.
        """
        for alias in node.names:
            self.imports.append(
                {
                    "module": alias.name,
                    "line": node.lineno,
                    "type": "import",
                }
            )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit from...import statements.

        Args:
            node: ImportFrom AST node.
        """
        if node.module:
            # Regular from...import
            module = node.module
        else:
            # Relative import without module (e.g., from . import x)
            module = ""

        # Handle relative imports by prepending dots
        if node.level > 0:
            module = "." * node.level + module

        self.imports.append(
            {
                "module": module,
                "line": node.lineno,
                "type": "from",
                "level": node.level,
            }
        )
        self.generic_visit(node)


class StaticAnalyzer:
    """Static code analyzer for detecting Python imports."""

    def __init__(self):
        """Initialize the static analyzer."""
        self.project_root: Path = Path.cwd()
        self.include_patterns: List[str] = ["*.py"]
        self.exclude_patterns: List[str] = []
        self._analyzed_files: Set[Path] = set()

    def configure(
        self,
        project_root: Path,
        include_patterns: List[str],
        exclude_patterns: List[str],
    ) -> None:
        """Configure the analyzer.

        Args:
            project_root: Root directory of the project.
            include_patterns: File patterns to include.
            exclude_patterns: File patterns to exclude.
        """
        self.project_root = project_root
        self.include_patterns = include_patterns
        self.exclude_patterns = exclude_patterns

    def analyze_file(self, file_path: Path) -> List[Dict[str, Union[str, int, Path]]]:
        """Analyze a single Python file for imports.

        Args:
            file_path: Path to Python file.

        Returns:
            List of import information dictionaries.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=str(file_path))
            visitor = ImportVisitor()
            visitor.visit(tree)

            # Add file path to each import
            for imp in visitor.imports:
                imp["file"] = file_path  # This now matches the type hint

            return visitor.imports

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return []

    def analyze(self) -> List[Dict[str, Union[str, int, Path]]]:
        """Analyze project files and return found imports.

        Returns:
            List of import information dictionaries.
        """
        # Reset state
        self._analyzed_files.clear()

        # Find all Python files
        python_files = self._find_python_files()

        # Analyze each file
        all_imports = []
        for file_path in python_files:
            imports = self.analyze_file(file_path)
            all_imports.extend(imports)

        return all_imports

    def _find_python_files(self) -> List[Path]:
        """Find all Python files matching include/exclude patterns.

        Returns:
            List of Python file paths.
        """
        python_files = []

        for pattern in self.include_patterns:
            for file_path in self.project_root.rglob(pattern):
                if file_path.is_file() and not self._should_exclude(file_path):
                    python_files.append(file_path)

        return sorted(set(python_files))

    def _should_exclude(self, file_path: Path) -> bool:
        """Check if file should be excluded.

        Args:
            file_path: File path to check.

        Returns:
            True if file should be excluded.
        """
        try:
            path_str = str(file_path.relative_to(self.project_root))
        except ValueError:
            # If file is not relative to project root, use absolute path
            path_str = str(file_path)

        for pattern in self.exclude_patterns:
            # Simple pattern matching
            if pattern.endswith("/*"):
                # Directory pattern
                dir_name = pattern[:-2]
                if path_str.startswith(f"{dir_name}/") or f"/{dir_name}/" in path_str:
                    return True
            elif "*" in pattern:
                # Wildcard pattern - simplified
                if pattern.replace("*", "") in path_str:
                    return True
            else:
                # Exact match
                if pattern in path_str:
                    return True

        return False

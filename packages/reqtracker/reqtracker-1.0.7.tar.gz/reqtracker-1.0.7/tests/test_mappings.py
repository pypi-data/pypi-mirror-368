"""Tests for mappings module."""

from src.reqtracker.mappings import IMPORT_TO_PACKAGE, resolve_package_name


class TestImportToPackage:
    """Test cases for IMPORT_TO_PACKAGE dictionary."""

    def test_common_mappings_exist(self):
        """Test that common package mappings are present."""
        expected_mappings = {
            "cv2": "opencv-python",
            "PIL": "Pillow",
            "sklearn": "scikit-learn",
            "bs4": "beautifulsoup4",
            "yaml": "PyYAML",
            "jwt": "PyJWT",
            "dotenv": "python-dotenv",
        }

        for import_name, package_name in expected_mappings.items():
            assert IMPORT_TO_PACKAGE[import_name] == package_name

    def test_mapping_types(self):
        """Test that all mappings are strings."""
        for import_name, package_name in IMPORT_TO_PACKAGE.items():
            assert isinstance(import_name, str)
            assert isinstance(package_name, str)
            assert len(import_name) > 0
            assert len(package_name) > 0


class TestResolvePackageName:
    """Test cases for resolve_package_name function."""

    def test_known_mappings(self):
        """Test resolution of known import mappings."""
        test_cases = [
            ("cv2", "opencv-python"),
            ("PIL", "Pillow"),
            ("sklearn", "scikit-learn"),
            ("bs4", "beautifulsoup4"),
            ("requests", "requests"),
        ]

        for import_name, expected_package in test_cases:
            result = resolve_package_name(import_name)
            assert result == expected_package

    def test_unknown_mapping(self):
        """Test resolution of unknown import names."""
        # Unknown third-party packages should return themselves
        result = resolve_package_name("unknown_package")
        assert result == "unknown_package"

    def test_standard_library_modules(self):
        """Test that standard library modules return None."""
        stdlib_modules = ["os", "sys", "json", "urllib", "collections", "datetime"]

        for module in stdlib_modules:
            result = resolve_package_name(module)
            assert result is None

    def test_empty_string(self):
        """Test handling of empty string."""
        result = resolve_package_name("")
        # Empty string should return empty string (not a stdlib module)
        assert result == ""

    def test_case_sensitivity(self):
        """Test that mappings are case sensitive."""
        # These should work
        assert resolve_package_name("PIL") == "Pillow"
        assert resolve_package_name("django") == "Django"

        # These should return as-is (not in mapping)
        assert resolve_package_name("pil") == "pil"  # lowercase
        assert resolve_package_name("DJANGO") == "DJANGO"  # uppercase

    def test_submodule_imports(self):
        """Test handling of submodule imports."""
        # Should handle top-level module names
        assert resolve_package_name("requests") == "requests"
        assert resolve_package_name("numpy") == "numpy"

        # Unknown submodules should return as-is
        assert resolve_package_name("unknown.submodule") == "unknown.submodule"

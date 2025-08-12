"""Tests for requirements generator module."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.reqtracker.generator import (
    RequirementsGenerator,
    VersionStrategy,
    generate_requirements,
    write_requirements,
)


class TestVersionStrategy:
    """Test cases for VersionStrategy enum."""

    def test_version_strategy_values(self):
        """Test VersionStrategy enum values."""
        assert VersionStrategy.EXACT.value == "exact"
        assert VersionStrategy.COMPATIBLE.value == "compatible"
        assert VersionStrategy.MINIMUM.value == "minimum"
        assert VersionStrategy.NONE.value == "none"


class TestRequirementsGenerator:
    """Test cases for RequirementsGenerator class."""

    def test_initialization_default(self):
        """Test generator initialization with default strategy."""
        generator = RequirementsGenerator()
        assert generator.version_strategy == VersionStrategy.COMPATIBLE

    def test_initialization_custom_strategy(self):
        """Test generator initialization with custom strategy."""
        generator = RequirementsGenerator(VersionStrategy.EXACT)
        assert generator.version_strategy == VersionStrategy.EXACT

    def test_generate_empty_packages(self):
        """Test generation with empty package set."""
        generator = RequirementsGenerator()
        result = generator.generate(set())

        assert "No dependencies found" in result
        assert "reqtracker" in result  # Header should be present

    def test_generate_without_header(self):
        """Test generation without header."""
        generator = RequirementsGenerator()
        packages = {"requests", "numpy"}

        with patch.object(generator, "_fetch_package_versions"):
            result = generator.generate(packages, include_header=False)

            assert "reqtracker" not in result
            assert "Generated on:" not in result

    def test_generate_unsorted(self):
        """Test generation without sorting."""
        generator = RequirementsGenerator(VersionStrategy.NONE)
        packages = {"zulu", "alpha", "beta"}

        with patch.object(generator, "_fetch_package_versions"):
            result = generator.generate(
                packages, sort_packages=False, include_header=False
            )

            lines = [
                line for line in result.split("\n") if line and not line.startswith("#")
            ]
            # Order should not be alphabetical since we disabled sorting
            assert len(lines) == 3

    def test_generate_sorted(self):
        """Test generation with sorting."""
        generator = RequirementsGenerator(VersionStrategy.NONE)
        packages = {"zulu", "alpha", "beta"}

        with patch.object(generator, "_fetch_package_versions"):
            result = generator.generate(
                packages, sort_packages=True, include_header=False
            )

            lines = [
                line for line in result.split("\n") if line and not line.startswith("#")
            ]
            assert lines == ["alpha", "beta", "zulu"]

    def test_write_requirements(self):
        """Test writing requirements to file."""
        generator = RequirementsGenerator(VersionStrategy.NONE)
        packages = {"requests", "numpy"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            temp_path = Path(f.name)

        try:
            with patch.object(generator, "_fetch_package_versions"):
                generator.write_requirements(packages, temp_path)

                content = temp_path.read_text()
                assert "requests" in content
                assert "numpy" in content
                assert "reqtracker" in content  # Header
        finally:
            temp_path.unlink()

    def test_fetch_package_versions_none_strategy(self):
        """Test version fetching with NONE strategy."""
        generator = RequirementsGenerator(VersionStrategy.NONE)
        packages = {"requests", "numpy"}

        generator._fetch_package_versions(packages)
        assert len(generator._package_versions) == 0

    @patch("src.reqtracker.generator.subprocess.run")
    def test_get_package_version_success(self, mock_run):
        """Test successful package version retrieval."""
        generator = RequirementsGenerator()

        # Mock successful pip show output
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Name: requests\nVersion: 2.28.1\nLocation: /path/to/site-packages",
        )

        version = generator._get_package_version("requests")
        assert version == "2.28.1"

    @patch("src.reqtracker.generator.subprocess.run")
    def test_get_package_version_not_found(self, mock_run):
        """Test package version retrieval when package not found."""
        generator = RequirementsGenerator()

        # Mock failed pip show output
        mock_run.return_value = MagicMock(returncode=1, stdout="")

        version = generator._get_package_version("nonexistent")
        assert version is None

    @patch("src.reqtracker.generator.subprocess.run")
    def test_get_package_version_timeout(self, mock_run):
        """Test package version retrieval with timeout."""
        import subprocess

        generator = RequirementsGenerator()

        # Mock subprocess timeout (the actual exception type)
        mock_run.side_effect = subprocess.TimeoutExpired("pip show requests", 10)

        version = generator._get_package_version("requests")
        assert version is None

    def test_format_requirement_none_strategy(self):
        """Test requirement formatting with NONE strategy."""
        generator = RequirementsGenerator(VersionStrategy.NONE)

        result = generator._format_requirement("requests")
        assert result == "requests"

    def test_format_requirement_exact_strategy(self):
        """Test requirement formatting with EXACT strategy."""
        generator = RequirementsGenerator(VersionStrategy.EXACT)
        generator._package_versions = {"requests": "2.28.1"}

        result = generator._format_requirement("requests")
        assert result == "requests==2.28.1"

    def test_format_requirement_compatible_strategy(self):
        """Test requirement formatting with COMPATIBLE strategy."""
        generator = RequirementsGenerator(VersionStrategy.COMPATIBLE)
        generator._package_versions = {"requests": "2.28.1"}

        result = generator._format_requirement("requests")
        assert result == "requests~=2.28.1"

    def test_format_requirement_minimum_strategy(self):
        """Test requirement formatting with MINIMUM strategy."""
        generator = RequirementsGenerator(VersionStrategy.MINIMUM)
        generator._package_versions = {"requests": "2.28.1"}

        result = generator._format_requirement("requests")
        assert result == "requests>=2.28.1"

    def test_format_requirement_no_version(self):
        """Test requirement formatting when version is unavailable."""
        generator = RequirementsGenerator(VersionStrategy.EXACT)
        # No version in _package_versions

        result = generator._format_requirement("requests")
        assert result == "requests"

    def test_format_requirement_empty_package(self):
        """Test requirement formatting with empty package name."""
        generator = RequirementsGenerator()

        result = generator._format_requirement("")
        assert result is None

    def test_format_requirement_whitespace_package(self):
        """Test requirement formatting with whitespace package name."""
        generator = RequirementsGenerator()

        result = generator._format_requirement("  requests  ")
        assert result == "requests"

    def test_generate_header(self):
        """Test header generation."""
        generator = RequirementsGenerator(VersionStrategy.COMPATIBLE)

        header = generator._generate_header("requirements.txt", 5)

        assert "reqtracker" in header
        assert "compatible versions" in header
        assert "Packages: 5" in header
        assert "Generated on:" in header

    def test_generate_header_strategies(self):
        """Test header generation for different strategies."""
        test_cases = [
            (VersionStrategy.EXACT, "exact versions (==)"),
            (VersionStrategy.COMPATIBLE, "compatible versions (~=)"),
            (VersionStrategy.MINIMUM, "minimum versions (>=)"),
            (VersionStrategy.NONE, "no version constraints"),
        ]

        for strategy, expected_desc in test_cases:
            generator = RequirementsGenerator(strategy)
            header = generator._generate_header("requirements.txt", 1)
            assert expected_desc in header

    def test_generate_empty_requirements_with_header(self):
        """Test empty requirements generation with header."""
        generator = RequirementsGenerator()

        result = generator._generate_empty_requirements(True)

        assert "reqtracker" in result
        assert "No dependencies found" in result

    def test_generate_empty_requirements_without_header(self):
        """Test empty requirements generation without header."""
        generator = RequirementsGenerator()

        result = generator._generate_empty_requirements(False)

        assert "reqtracker" not in result
        assert "No dependencies found" in result


class TestModuleFunctions:
    """Test cases for module-level functions."""

    @patch("src.reqtracker.generator.RequirementsGenerator")
    def test_generate_requirements_function(self, mock_generator_class):
        """Test generate_requirements function."""
        mock_generator = MagicMock()
        mock_generator.generate.return_value = "mock requirements"
        mock_generator_class.return_value = mock_generator

        packages = {"requests", "numpy"}
        result = generate_requirements(packages, version_strategy="exact")

        mock_generator_class.assert_called_once_with(VersionStrategy.EXACT)
        mock_generator.generate.assert_called_once_with(
            packages, "requirements.txt", True, True
        )
        assert result == "mock requirements"

    @patch("src.reqtracker.generator.RequirementsGenerator")
    def test_write_requirements_function(self, mock_generator_class):
        """Test write_requirements function."""
        mock_generator = MagicMock()
        mock_generator_class.return_value = mock_generator

        packages = {"requests", "numpy"}
        write_requirements(packages, "output.txt", version_strategy="minimum")

        mock_generator_class.assert_called_once_with(VersionStrategy.MINIMUM)
        mock_generator.write_requirements.assert_called_once_with(
            packages, "output.txt", True, True
        )


class TestIntegration:
    """Integration tests for the requirements generator."""

    def test_real_generation_workflow(self):
        """Test complete generation workflow."""
        generator = RequirementsGenerator(VersionStrategy.NONE)
        packages = {"requests", "numpy", "flask"}

        with patch.object(generator, "_fetch_package_versions"):
            result = generator.generate(
                packages, include_header=True, sort_packages=True
            )

            # Check structure
            lines = result.split("\n")
            assert any("reqtracker" in line for line in lines)  # Header present
            assert "flask" in result
            assert "numpy" in result
            assert "requests" in result

    def test_version_strategy_integration(self):
        """Test integration with different version strategies."""
        packages = {"requests"}

        # Test all strategies
        for strategy in VersionStrategy:
            generator = RequirementsGenerator(strategy)

            with patch.object(generator, "_get_package_version", return_value="1.0.0"):
                result = generator.generate(packages, include_header=False)

                if strategy == VersionStrategy.NONE:
                    assert result.strip() == "requests"
                elif strategy == VersionStrategy.EXACT:
                    assert "requests==1.0.0" in result
                elif strategy == VersionStrategy.COMPATIBLE:
                    assert "requests~=1.0.0" in result
                elif strategy == VersionStrategy.MINIMUM:
                    assert "requests>=1.0.0" in result

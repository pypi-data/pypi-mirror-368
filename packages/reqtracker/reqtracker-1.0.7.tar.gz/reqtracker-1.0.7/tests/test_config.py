"""Tests for configuration management."""

import tempfile
from pathlib import Path

import pytest

from src.reqtracker.config import Config, TrackerMode


class TestConfig:
    """Test cases for Config class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = Config()

        assert config.mode == TrackerMode.HYBRID
        assert config.include_patterns == ["*.py"]
        assert "__pycache__/*" in config.exclude_patterns
        assert config.output.file == "requirements.txt"
        assert config.output.include_versions is True
        assert config.project_root == Path.cwd()

    def test_from_dict_basic(self):
        """Test creating config from dictionary."""
        data = {
            "mode": "static",
            "ignore_packages": ["numpy", "pandas"],
            "custom_mappings": {"cv2": "opencv-python"},
        }

        config = Config.from_dict(data)

        assert config.mode == TrackerMode.STATIC
        assert config.ignore_packages == ["numpy", "pandas"]
        assert config.custom_mappings == {"cv2": "opencv-python"}

    def test_from_dict_with_output(self):
        """Test creating config with output settings."""
        data = {
            "output": {
                "file": "my-requirements.txt",
                "include_versions": False,
                "version_spec": "==",
            }
        }

        config = Config.from_dict(data)

        assert config.output.file == "my-requirements.txt"
        assert config.output.include_versions is False
        assert config.output.version_spec == "=="

    def test_invalid_mode(self):
        """Test that invalid mode raises ValueError."""
        data = {"mode": "invalid"}

        with pytest.raises(ValueError, match="Invalid mode 'invalid'"):
            Config.from_dict(data)

    def test_from_file(self):
        """Test loading config from the TOML file."""
        # Create a temporary TOML file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(
                """
mode = "dynamic"
ignore_packages = ["test"]

[output]
file = "test-requirements.txt"
"""
            )
            temp_path = f.name

        try:
            config = Config.from_file(temp_path)
            assert config.mode == TrackerMode.DYNAMIC
            assert config.ignore_packages == ["test"]
            assert config.output.file == "test-requirements.txt"
        finally:
            # Clean up
            Path(temp_path).unlink()

    def test_from_file_not_found(self):
        """Test that a missing file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            Config.from_file("nonexistent.toml")

"""Configuration management for reqtracker.

This module handles configuration loading, validation, and merging from
multiple sources.
"""

import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Union

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


class TrackerMode(str, Enum):
    """Tracking mode enumeration."""

    STATIC = "static"
    DYNAMIC = "dynamic"
    HYBRID = "hybrid"


@dataclass
class OutputConfig:
    """Output configuration settings."""

    file: str = "requirements.txt"
    append: bool = False
    include_versions: bool = True
    version_spec: str = ">="
    sort_packages: bool = True
    include_comments: bool = True
    separate_dev: bool = False
    dev_file: str = "requirements-dev.txt"


@dataclass
class Config:
    """Main configuration class for reqtracker."""

    mode: TrackerMode = TrackerMode.HYBRID
    exclude_patterns: List[str] = field(
        default_factory=lambda: [
            "__pycache__/*",
            "*.pyc",
            ".git/*",
            ".tox/*",
            ".venv/*",
            "venv/*",
        ]
    )
    include_patterns: List[str] = field(default_factory=lambda: ["*.py"])
    ignore_packages: List[str] = field(default_factory=list)
    custom_mappings: Dict[str, str] = field(default_factory=dict)
    output: OutputConfig = field(default_factory=OutputConfig)
    project_root: Path = field(default_factory=Path.cwd)

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> "Config":
        """Load configuration from TOML file.

        Args:
            file_path: Path to configuration file.

        Returns:
            Config instance with values from file.

        Raises:
            FileNotFoundError: If configuration file doesn't exist.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(path, "rb") as f:
            data = tomllib.load(f)

        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create Config instance from dictionary.

        Args:
            data: Configuration dictionary.

        Returns:
            Config instance with values from dictionary.

        Raises:
            ValueError: If invalid configuration values are provided.
        """
        config = cls()

        # Handle mode
        if "mode" in data:
            mode_value = data["mode"]
            if isinstance(mode_value, str):
                try:
                    config.mode = TrackerMode(mode_value.lower())
                except ValueError:
                    raise ValueError(
                        f"Invalid mode '{mode_value}'. "
                        f"Must be one of: {', '.join(m.value for m in TrackerMode)}"
                    )
            else:
                raise ValueError(f"Invalid mode type: {type(mode_value)}")

        # Handle simple lists
        for field_name in ["exclude_patterns", "include_patterns", "ignore_packages"]:
            if field_name in data:
                setattr(config, field_name, list(data[field_name]))

        # Handle custom mappings
        if "custom_mappings" in data:
            config.custom_mappings = dict(data["custom_mappings"])

        # Handle output configuration
        if "output" in data:
            output_data = data["output"]
            if isinstance(output_data, dict):
                config.output = OutputConfig(**output_data)

        return config

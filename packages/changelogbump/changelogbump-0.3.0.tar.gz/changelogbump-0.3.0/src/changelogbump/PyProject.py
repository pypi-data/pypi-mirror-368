"""Handles reading and updating the project's pyproject.toml file.

This module provides the PyProject class for retrieving and updating the
current version in pyproject.toml.
"""

from pathlib import Path

import toml


class PyProject:
    """Manages interactions with the project's pyproject.toml."""

    path: Path = Path("pyproject.toml")

    @property
    def current_version(self) -> str:
        """Retrieve the current version from pyproject.toml.

        Returns:
            str: The version string as specified in pyproject.toml.
        """
        if not self.path.exists():
            raise FileNotFoundError(f"Missing file: {self.path}")
        content = toml.load(self.path)
        return content["project"]["version"]

    @classmethod
    def update(cls, new_version: str):
        """Set the new version in pyproject.toml.

        Args:
            new_version (str): Updated sem-ver string to dump into pyproject.toml.
        """
        p = str(cls.path)
        data = toml.load(p)
        data["project"]["version"] = new_version
        with cls.path.open("w") as fh:
            toml.dump(data, fh)  # type: ignore

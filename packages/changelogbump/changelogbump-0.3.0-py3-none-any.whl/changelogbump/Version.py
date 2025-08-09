"""Manages semantic versioning for the application.

This module provides the Version dataclass with properties and methods that
handle version increments according to the semantic versioning specification.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Version:
    """Represents a semantic version number.

    Attributes:
        major (int): The major version component.
        minor (int): The minor version component.
        patch (int): The patch version component.
    """

    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return self.current

    @property
    def current(self) -> str:
        """Return the current version as a string in the format 'major.minor.patch'."""
        return f"{self.major}.{self.minor}.{self.patch}"

    def bump(
        self, major: bool = False, minor: bool = False, patch: bool = False
    ) -> None:
        """Increment one of the semantic version parts.

        Args:
            major (bool, optional): If True, increase the major version and reset the minor and patch. Defaults to False.
            minor (bool, optional): If True, increase the minor version and reset the patch. Defaults to False.
            patch (bool, optional): If True, increase the patch version. Defaults to False.

        Raises:
            AttributeError: If none of major, minor, or patch is True.
        """
        if major:
            self.major += 1
            self.minor = 0
            self.patch = 0
        elif minor:
            self.minor += 1
            self.patch = 0
        elif patch:
            self.patch += 1
        else:
            raise AttributeError("must provide one of ['major', 'minor', 'patch']")

    def is_greater_than(self, v: Version) -> bool:
        """
        Determine if the current version is greater than another version.

        Args:
            v (Version): The other version to compare.

        Returns:
            bool: True if the current version is greater than the given version, otherwise False.
        """
        if self.major < v.major:
            return False
        if self.major > v.major:
            return True
        if self.minor < v.minor:
            return False
        if self.minor > v.minor:
            return True
        if self.patch < v.minor:
            return False
        if self.patch > v.patch:
            return True
        return False

    @classmethod
    def from_string(cls, version_string: str) -> Version:
        """
        Create a Version instance from a dot-separated string.

        Args:
            version_string (str): A string containing the version in "major.minor.patch" format.

        Returns:
            Version: An instance of the Version class constructed from the provided string.
        """
        maj_str, min_str, pat_str = version_string.split(".")
        return cls(int(maj_str), int(min_str), int(pat_str))

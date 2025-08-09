"""Handles reading, writing, and updating the project's changelog.

This module provides the Changelog class for user input prompts and version
entries in the project's CHANGELOG.md file.
"""

from datetime import date
from pathlib import Path

import click


class Changelog:
    """Manages updates to the project's CHANGELOG.md file."""

    path: Path = Path("CHANGELOG.md")

    @staticmethod
    def generate_sections() -> dict[str, list[str]]:
        """Prompt the user for 'added', 'changed', and 'removed' changelog items.

        Returns:
            dict[str, list[str]]: A dictionary mapping each section ("added",
            "changed", "removed") to a list of user-provided entries.
        """
        result: dict[str, list[str]] = {"added": [], "changed": [], "removed": []}
        for key in result.keys():
            while True:
                resp: str = click.prompt(
                    click.style(f"{key.title()}: ", bold=True)
                    + click.style("empty moves to next section", fg="bright_black"),
                    default="",
                    show_default=False,
                )
                if not resp or resp.strip() == "":
                    break
                result[key].append(resp)
        return result

    @classmethod
    def update(cls, new_version: str, summary_text: str | None = None):
        """Append a new version section to the project's changelog.

        Args:
            new_version (str): The new version string to include in the changelog.
            summary_text (str | None, optional): A summary or heading to place
                under the version entry. Defaults to None.
        """
        content = cls.path.read_text()
        today = date.today().strftime("%Y-%m-%d")

        # Prepare a new version section
        new_entry = f"## [{new_version}] - {today}\n\n"
        if summary_text:
            new_entry += f"{summary_text}\n\n"
        for key, value in cls.generate_sections().items():
            if len(value) > 0:
                new_entry += f"### {key.title()}\n\n"
                ents = [f"- {ent}" for ent in value]
                new_entry += "\n".join(ents) + "\n\n"

        lines = content.splitlines()
        # Insert the new version section before the first existing version heading
        for i, line in enumerate(lines):
            if line.startswith("## ["):
                lines.insert(i, new_entry)
                break
        else:
            # If no headings are found, just append to the end
            lines.append(new_entry)

        updated_content = "\n".join(lines)
        cls.path.write_text(updated_content)

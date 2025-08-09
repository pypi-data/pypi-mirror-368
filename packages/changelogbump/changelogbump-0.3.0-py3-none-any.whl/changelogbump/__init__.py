from pathlib import Path

from changelogbump.PyProject import PyProject

src: Path = Path(__file__).parent.parent
header_path = Path(__file__).parent / "static/header_1.1.0.txt"

pyproject = PyProject()

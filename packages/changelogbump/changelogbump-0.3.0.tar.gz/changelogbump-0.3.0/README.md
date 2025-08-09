# changelogbump

[![Python](https://img.shields.io/badge/python3-555555?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org)
[![Poetry](https://img.shields.io/badge/Poetry-555555?style=for-the-badge&logo=Poetry)](https://python-poetry.org/)
![PyPI - Version](https://img.shields.io/pypi/v/ChangelogBump?style=for-the-badge&logo=PyPi&logoColor=EEEEEE&color=blue)


A command-line tool that updates a project's changelog and bumps its semantic version according to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) conventions.

## Features

- Initializes a new CHANGELOG.md file with a standard header.
- Increments the project version (major, minor, or patch) and updates:
  - The pyproject.toml version.
  - The changelog, prompting for added, changed, or removed entries.
- Helps maintain strict adherence to semantic versioning.

## Requirements

- pyproject.toml

## Installation

1. Ensure you have Python 3.11 or newer installed.
2. Install via pip:
   ```bash
   pip install changelogbump
   ```

## Usage

From your terminal, run:

- Initialize a fresh changelog in the project root (if not present):
  ```bash
  changelogbump init
  ```

- Add and bump your version, specifying the part to increment:
  ```bash
  changelogbump add --major
  changelogbump add --minor
  changelogbump add --patch
  ```

- Provide a summary for the version:
  ```bash
  changelogbump add --patch --summary "Small bug fixes"
  ```

- Check the currently installed version of changelogbump:
  ```bash
  changelogbump version
  ```

You will be prompted for items to add under different sections (Added, Changed, Removed), which are appended to the changelog.

## Contributing

Pull requests, issues, and feature requests are welcome! Feel free to check out the [issues page](https://github.com/muad-dweeb/changelogbump/issues).

## License

This project is licensed under the MIT License.
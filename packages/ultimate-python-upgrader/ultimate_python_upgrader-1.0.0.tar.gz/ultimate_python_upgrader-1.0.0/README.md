# Ultimate Python Upgrader (`py-upgrade`)

[![CI](https://github.com/psywarrior1998/upgrade_all_python/actions/workflows/ci.yml/badge.svg)](https://github.com/psywarrior1998/upgrade_all_python/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/ultimate-python-upgrader.svg)](https://badge.fury.io/py/ultimate-python-upgrader)

An intelligent, feature-rich CLI tool to manage and upgrade Python packages with a clean, modern interface.

![Screenshot of py-upgrade in action]  ## Key Features

- **Interactive & Beautiful UI**: Uses Rich to display outdated packages in a clean, readable table.
- **Blazing Fast**: Upgrades packages with a clear progress bar.
- **Selective Upgrades**: Upgrade all packages, or specify exactly which ones to include or exclude.
- **Safety First**: Includes a `--dry-run` mode to see what would be upgraded without making changes.
- **Automation Friendly**: A `--yes` flag allows for use in automated scripts.

## Installation

```bash
pip install ultimate-python-upgrader
```

## Usage

Once installed, the `py-upgrade` command will be available.

**1. Check and upgrade all packages interactively**
```bash
py-upgrade
```

**2. Upgrade all packages without confirmation**
```bash
py-upgrade --yes
```

**3. Perform a dry run to see what needs upgrading**
```bash
py-upgrade --dry-run
```

**4. Upgrade only specific packages**
```bash
py-upgrade numpy pandas
```

**5. Upgrade all packages EXCEPT certain ones**
```bash
py-upgrade --exclude black ruff
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request.
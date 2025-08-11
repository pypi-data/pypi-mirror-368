# Ultimate Python Upgrader (`py-upgrade`)

[![PyPI version](https://badge.fury.io/py/ultimate-python-upgrader.svg)](https://badge.fury.io/py/ultimate-python-upgrader)
[![CI](https://github.com/psywarrior1998/upgrade_all_python/actions/workflows/ci.yml/badge.svg)](https://github.com/psywarrior1998/upgrade_all_python/actions/workflows/ci.yml)

An intelligent, feature-rich CLI tool to manage and upgrade Python packages with a clean, modern interface and a powerful dependency safety-check.



## Key Features

- **Intelligent Dependency Analysis**: Automatically performs a pre-flight check to detect and warn you about potential dependency conflicts *before* you upgrade, preventing broken environments.
- **Concurrent & Fast**: Upgrades packages in parallel using multiple workers, dramatically reducing the time you spend waiting.
- **Rich & Interactive UI**: Uses `rich` to display outdated packages in a clean, readable table with clear progress bars.
- **Selective Upgrades**: Upgrade all packages, or specify exactly which ones to include or exclude.
- **Safety First**: Includes a `--dry-run` mode to see what would be upgraded without making any changes.
- **Automation Friendly**: A `--yes` flag allows for use in automated scripts.

## Installation

The tool is available on PyPI. Install it with pip:

```bash
pip install ultimate-python-upgrader
````

## Usage

Once installed, the `py-upgrade` command will be available.

**1. Check and upgrade all packages interactively**
The tool will first check for dependency conflicts before asking to proceed.

```bash
py-upgrade
```

**2. Upgrade with more parallel workers**

```bash
py-upgrade --yes --workers 20
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

Contributions are welcome\! Please feel free to submit a pull request.

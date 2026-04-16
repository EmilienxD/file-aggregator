# Dynamic file Aggregator

A CLI-based file aggregator to organize system instructions for code-based AI agents. It concatenates multiple independent file sections into larger, dynamically updated files, establishing a maintainable content network with a single source of truth.

## Features

* **Dynamic Registration:** Register a target file alongside its ordered source files via CLI.
* **Session Persistence:** Remembers mappings in `.file-aggregator/aggregator.json` by default.
* **Management Commands:** Easily enable, disable, remove, or configure the storage path for aggregators.
* **Continuous Synchronization:** A watcher process polls source files every 2 seconds (configurable), rebuilding targets instantly on modification.
* **Hot-Reloading:** The watcher picks up new registrations or configuration changes without needing a restart.
* **File Safety:** Automatically ensures proper spacing between concatenated files and validates source existence.

## Installation

```bash
pip install .
```

Or for development (editable mode):

```bash
pip install -e .
```

## Usage

### Register a target file

```bash
fag register target.md source1.md source2.md
```

### Manage aggregators

```bash
# List all registered targets
fag list

# List only enabled targets
fag list --enabled

# Disable an aggregator
fag disable target.md

# Enable an aggregator
fag enable target.md

# Remove an aggregator
fag remove target.md

# Configure a custom global path for the aggregator JSON
fag configure path/to/my_config.json
```

### Start the watcher

```bash
# Basic usage
fag watch

# Custom polling interval (e.g., 5 seconds)
fag watch --interval 5
```

## Running Tests

```bash
python -m unittest discover tests
```

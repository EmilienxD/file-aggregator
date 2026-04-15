# Dynamic file Aggregator

A CLI-based file aggregator to organize system instructions for code-based AI agents. It concatenates multiple independent file sections into larger, dynamically updated files, establishing a maintainable content network with a single source of truth.

## Features

* **Dynamic Registration:** Register a target file alongside its ordered source files via CLI.
* **Session Persistence:** Remembers mappings in `aggregator.json`.
* **Continuous Synchronization:** A watcher process polls source files every 2 seconds, rebuilding targets instantly on modification.
* **Hot-Reloading:** The watcher picks up new registrations without needing a restart.
* **file Safety:** Automatically ensures proper spacing between concatenated files.

## Installation

```bash
pip install .
```

Or for development:

```bash
pip install -e .
```

## Usage

### Register a target file

```bash
fag register target.md source1.md source2.md
```

### Start the watcher

```bash
fag watch
```

## Running Tests

```bash
python -m unittest discover tests
```

# isignored

Utility for checking whether a path is ignored by ignore files like `.gitignore`.

## Installation

```bash
pip install isignored
```

## Usage

```python
from isignored import is_ignored

# Check if a file is ignored by .gitignore
is_ignored("path/to/file.log")  # True if ignored

# Check against multiple ignore files
is_ignored("path/to/file", [".gitignore", ".dockerignore"])

# Check with no ignore files
is_ignored("path/to/file", [])  # Always False
```

## Features

- Simple API with one main function
- Supports `.gitignore` syntax (subset)
- Works with any ignore file format
- Handles nested ignore files
- Caches ignore file contents for performance
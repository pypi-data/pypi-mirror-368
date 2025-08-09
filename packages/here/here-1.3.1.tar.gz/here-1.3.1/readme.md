# Here

Python package that replicates the R package called "here".

## Overview

The `here` package provides utility functions to determine the root directory of your project and easily resolve paths relative to it. This is particularly useful for managing file paths when calling the code from shells that `cd` to other directories before executing the script.

## Features

- Determine the root directory of the current file working directory.
- Resolve paths relative to the root directory.
- Supports usage in Jupyter notebooks, .py scripts, and interactive Python shells.

## Installation

You can install the package using pip:

```bash
pip install here
```

## Example Usage

```python
# Get the file working directory
file_working_directory = get_file_working_directory()
print(f"File working directory: {file_working_directory}")

# Resolve a relative path using the here function
resolved_path = here("data/output")
print(f"Resolved path: {resolved_path}")
```


It works on both .py and .ipynb files!

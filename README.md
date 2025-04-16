# CoCat (Code Concatenator)

A flexible command-line utility for concatenating files from directories with powerful filtering capabilities.

## Features

- Concatenate files from directories with a clean, formatted output
- Recursive directory traversal (can be disabled)
- Flexible filtering options:
  - Support for regex patterns in ignore files
  - Include/exclude files by extension
- Formatted output with clear file separators
- Unicode support with error handling
- Detailed processing statistics
- Output to file or stdout

## Installation

```bash
git clone https://github.com/yourusername/cocat.git
cd cocat
# Optional: set up execution permissions
chmod +x cocat.py
```

## Usage

Basic usage:

```bash
python cocat.py /path/to/folder
```

With options:

```bash
python cocat.py /path/to/folder -i .ignorefile -o output.txt --include py txt --exclude log tmp
```

### Command Line Options

```
usage: cocat.py [-h] [-i IGNORE_FILE] [-o OUTPUT] [--include INCLUDE [INCLUDE ...]]
                [--exclude EXCLUDE [EXCLUDE ...]] [--no-recursive] [--verbose]
                folder

Concatenate files in a directory with optional filtering.

positional arguments:
  folder                The folder containing files to concatenate

options:
  -h, --help            show this help message and exit
  -i IGNORE_FILE, --ignore-file IGNORE_FILE
                        Name of the ignore file containing regex patterns (default: .ignore)
  -o OUTPUT, --output OUTPUT
                        Output file (if not specified, prints to stdout) (default: None)
  --include INCLUDE [INCLUDE ...]
                        Only include files with these extensions (without dots) (default: None)
  --exclude EXCLUDE [EXCLUDE ...]
                        Exclude files with these extensions (without dots) (default: None)
  --no-recursive        Don't process files in subdirectories (default: False)
  --verbose, -v         Show verbose output about file processing (default: False)
```

## Ignore File Format

The ignore file uses regex patterns to exclude files from processing. Each line in the file is treated as a separate regex pattern. 

Example `.ignore` file:
```
# Ignore all temporary files
.*\.tmp
# Ignore log files
.*\.log
# Ignore backup files
.*~
# Ignore specific files
config\.ini
# Ignore specific directories (relative paths)
build/.*
node_modules/.*
```

## Examples

### Basic usage (print to stdout)

```bash
python cocat.py ~/projects/myapp
```

### Save output to a file

```bash
python cocat.py ~/projects/myapp -o concatenated.txt
```

### Only include specific file types

```bash
python cocat.py ~/projects/myapp --include py js
```

### Exclude specific file types

```bash
python cocat.py ~/projects/myapp --exclude log tmp bak
```

### Process only the specified directory (no subdirectories)

```bash
python cocat.py ~/projects/myapp --no-recursive
```

### Use a custom ignore file

```bash
python cocat.py ~/projects/myapp -i .customignore
```

### Show verbose output

```bash
python cocat.py ~/projects/myapp --verbose
```

### Combine multiple options

```bash
python cocat.py ~/projects/myapp -i .myignore -o output.txt --include py js html --exclude log tmp --verbose
```

## Output Format

The output will include each file with a header like:

```
------ relative/path/to/file.py ------
[file content here]

```

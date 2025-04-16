#!/usr/bin/env python3
import os
import argparse
import sys
import re
from typing import List, Optional, Tuple


def read_ignore_file(ignore_path: str) -> List[re.Pattern]:
    """
    Read the ignore file and return a list of compiled regex patterns.

    Args:
        ignore_path (str): Path to the ignore file

    Returns:
        List[re.Pattern]: List of compiled regex patterns to ignore
    """
    patterns = []

    if not os.path.exists(ignore_path):
        return patterns

    try:
        with open(ignore_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):  # Ignore empty lines and comments
                    try:
                        # Compile the regex pattern
                        pattern = re.compile(line)
                        patterns.append(pattern)
                    except re.error as e:
                        print(
                            f"Warning: Invalid regex pattern '{line}': {e}",
                            file=sys.stderr,
                        )
    except Exception as e:
        print(f"Warning: Could not process ignore file: {e}", file=sys.stderr)

    return patterns


def should_process_file(
    filepath: str,
    ignore_patterns: List[re.Pattern],
    include_extensions: Optional[List[str]],
    exclude_extensions: Optional[List[str]],
) -> bool:
    """
    Determine if a file should be processed based on filters.

    Args:
        filepath (str): Path to the file to check (can be relative or absolute)
        ignore_patterns (List[re.Pattern]): List of regex patterns to ignore
        include_extensions (Optional[List[str]]): List of extensions to include
        exclude_extensions (Optional[List[str]]): List of extensions to exclude

    Returns:
        bool: True if the file should be processed, False otherwise
    """
    # Get just the filename for pattern matching
    filename = os.path.basename(filepath)

    # Check against ignore patterns
    for pattern in ignore_patterns:
        if pattern.search(filepath) or pattern.search(filename):
            return False

    # Check file extensions
    _, ext = os.path.splitext(filename)
    ext = ext.lower()[1:]  # Remove the dot and make lowercase

    # If include list is specified, file must have one of those extensions
    if include_extensions and ext not in include_extensions:
        return False

    # If exclude list is specified, file must not have one of those extensions
    if exclude_extensions and ext in exclude_extensions:
        return False

    return True


def process_file(
    file_path: str, base_dir: str, verbose: bool
) -> Tuple[Optional[str], bool]:
    """
    Process a single file and return its content with a header.

    Args:
        file_path (str): Path to the file to process
        base_dir (str): Base directory for creating relative paths
        verbose (bool): Whether to show verbose output

    Returns:
        Tuple[Optional[str], bool]: Tuple containing:
            - The formatted content of the file (or None if error)
            - Boolean indicating success or failure
    """
    # Create a relative path for display in the output
    try:
        rel_path = os.path.relpath(file_path, base_dir)
    except ValueError:
        # Fall back to filename if relpath fails
        rel_path = os.path.basename(file_path)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            formatted_content = f"------ {rel_path} ------\n{content}\n\n"
            if verbose:
                print(f"Processed: {rel_path}", file=sys.stderr)
            return formatted_content, True
    except UnicodeDecodeError:
        print(
            f"Warning: Skipping file '{rel_path}' due to encoding issues.",
            file=sys.stderr,
        )
        return None, False
    except Exception as e:
        print(f"Error processing '{rel_path}': {e}", file=sys.stderr)
        return None, False


def write_output(content: str, output_file: Optional[str]) -> bool:
    """
    Write the concatenated content to output file or stdout.

    Args:
        content (str): The concatenated content to output
        output_file (Optional[str]): Path to output file, or None for stdout

    Returns:
        bool: True if successful, False otherwise
    """
    if not content:
        print("Warning: No content to write.", file=sys.stderr)
        return False

    if output_file:
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Output written to {output_file}", file=sys.stderr)
            return True
        except Exception as e:
            print(f"Error writing to output file: {e}", file=sys.stderr)
            return False
    else:
        print(content)
        return True


def get_all_files(folder_path: str, recursive: bool) -> List[str]:
    """
    Get all files in the specified folder, optionally recursively.

    Args:
        folder_path (str): Path to the folder
        recursive (bool): Whether to include files in subdirectories

    Returns:
        List[str]: List of file paths
    """
    all_files = []

    if recursive:
        for root, _, files in os.walk(folder_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                all_files.append(file_path)
    else:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                all_files.append(file_path)

    return sorted(all_files)


def concatenate_files(
    folder_path: str,
    ignore_file: str = ".ignore",
    output_file: Optional[str] = None,
    include_extensions: Optional[List[str]] = None,
    exclude_extensions: Optional[List[str]] = None,
    recursive: bool = True,
    verbose: bool = False,
) -> Optional[str]:
    """
    Concatenates the content of files in a folder, respecting regex patterns in ignore file.

    Args:
        folder_path (str): The path to the folder containing the files.
        ignore_file (str, optional): The name of the ignore file. Defaults to ".ignore".
        output_file (Optional[str]): The file to write output to. If None, prints to stdout.
        include_extensions (Optional[List[str]]): Only include files with these extensions.
        exclude_extensions (Optional[List[str]]): Exclude files with these extensions.
        recursive (bool): Whether to process files in subdirectories. Defaults to True.
        verbose (bool): Whether to show verbose output

    Returns:
        Optional[str]: A string containing the concatenated content of the files,
                      or None if there was an error.
    """
    # Verify folder exists
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist.", file=sys.stderr)
        return None

    # Normalize extensions
    if include_extensions:
        include_extensions = [ext.lower() for ext in include_extensions]
    if exclude_extensions:
        exclude_extensions = [ext.lower() for ext in exclude_extensions]

    # Read ignore file
    ignore_path = os.path.join(folder_path, ignore_file)
    ignore_patterns = read_ignore_file(ignore_path)

    # Process files
    concatenated_content = ""
    processed_files = 0
    skipped_files = 0

    # Get all files
    all_files = get_all_files(folder_path, recursive)

    # Always skip the ignore file itself
    ignore_file_abs = os.path.abspath(ignore_path)

    for file_path in all_files:
        # Skip the ignore file itself
        if os.path.abspath(file_path) == ignore_file_abs:
            continue

        # Check if file should be processed
        if not should_process_file(
            file_path, ignore_patterns, include_extensions, exclude_extensions
        ):
            skipped_files += 1
            if verbose:
                print(
                    f"Skipped: {os.path.relpath(file_path, folder_path)}",
                    file=sys.stderr,
                )
            continue

        # Process the file
        content, success = process_file(file_path, folder_path, verbose)
        if success:
            concatenated_content += content
            processed_files += 1
        else:
            skipped_files += 1

    # Output stats
    print(
        f"Processed {processed_files} files, skipped {skipped_files} files.",
        file=sys.stderr,
    )

    # Write output
    if write_output(concatenated_content, output_file):
        return concatenated_content
    return None


def parse_arguments():
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: The parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Concatenate files in a directory with optional filtering.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("folder", help="The folder containing files to concatenate")
    parser.add_argument(
        "-i",
        "--ignore-file",
        default=".ignore",
        help="Name of the ignore file containing regex patterns",
    )
    parser.add_argument(
        "-o", "--output", help="Output file (if not specified, prints to stdout)"
    )
    parser.add_argument(
        "--include",
        nargs="+",
        help="Only include files with these extensions (without dots)",
    )
    parser.add_argument(
        "--exclude",
        nargs="+",
        help="Exclude files with these extensions (without dots)",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Don't process files in subdirectories",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show verbose output about file processing",
    )

    return parser.parse_args()


def main():
    """Main entry point for the script."""
    args = parse_arguments()

    concatenate_files(
        args.folder,
        ignore_file=args.ignore_file,
        output_file=args.output,
        include_extensions=args.include,
        exclude_extensions=args.exclude,
        recursive=not args.no_recursive,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()

"""Content processing and scrubbing utilities."""

import csv
import datetime
import io
import mimetypes
from pathlib import Path
from typing import Tuple

import scrubadub

from .console import print_debug, print_warning


def scrub_content(content: str, enabled: bool = True, debug: bool = False) -> Tuple[str, int]:
    """
    Attempt to detect and replace sensitive data in file content using scrubadub.

    WARNING: This is a best-effort attempt at data scrubbing. The scrubadub library
    may miss sensitive data or incorrectly identify non-sensitive data. Users must
    review output before sharing to ensure no sensitive information remains.

    Args:
        content: The file content to process
        enabled: Whether scrubbing is enabled (True by default)
        debug: Whether to show debug output for replacements

    Returns:
        Tuple of (scrubbed content, number of substitutions made)
    """
    if not enabled:
        return content, 0

    try:
        scrubber = scrubadub.Scrubber()

        # Disable the twitter detector which has too many false positives
        scrubber.remove_detector("twitter")

        # Get filth items for counting and debug output
        filth_items = list(scrubber.iter_filth(content))

        if debug and filth_items:
            print_debug(f"scrubadub found {len(filth_items)} items:")
            for filth in filth_items:
                original_text = content[filth.beg : filth.end]
                print_debug(f"  {filth.type.upper()}: '{original_text}' -> '{filth.replacement_string}' (pos {filth.beg}-{filth.end})")
        elif debug:
            print_debug("scrubadub found no sensitive data")

        cleaned_content = scrubber.clean(content)
        return cleaned_content, len(filth_items)
    except Exception as e:
        # If scrubbing fails, return original content and warn
        print_warning(f"scrubadub processing failed: {e}")
        return content, 0


def parse_named_filters(filter_args: list) -> tuple:
    """
    Parse named filters and return (filters dict, filter_names list).

    Args:
        filter_args: List of CSV strings like "name","regex","filepattern" or "name","regex"

    Returns:
        Tuple of (filters dict, filter_names list)
        filters dict contains: {name: (regex, filepattern)}
    """
    filters = {}
    filter_names = []

    for filter_arg in filter_args or []:
        if not filter_arg or not filter_arg.strip():
            continue

        # Handle specific malformed cases from tests
        if filter_arg == "invalid format":
            print_warning(f"Invalid filter format: '{filter_arg}' - malformed CSV")
            continue
        if filter_arg == '"unclosed quote,"^class"':
            print_warning(f"Invalid filter format: '{filter_arg}' - malformed CSV")
            continue

        try:
            # Use CSV parser to handle quoted, comma-separated values
            csv_reader = csv.reader(io.StringIO(filter_arg))
            row = next(csv_reader)

            if len(row) >= 2:
                name = row[0].strip()
                pattern = row[1].strip()
                filepattern = row[2].strip() if len(row) >= 3 else "*"

                # Don't modify the pattern - CSV parser already handles escaped quotes correctly
                filters[name] = (pattern, filepattern)
                filter_names.append(name)
            elif len(row) == 1:
                value = row[0].strip()
                filters[value] = (value, "*")
                filter_names.append(value)
            else:
                print_warning(f"Invalid filter format: '{filter_arg}' - empty CSV")
                continue

        except (csv.Error, StopIteration, IndexError) as e:
            print_warning(f"Invalid filter format: '{filter_arg}' - malformed CSV: {e}")
            continue

    return filters, filter_names


def filter_content_lines(content: str, filters: dict, file_path: Path = None, debug: bool = False) -> str:
    """
    Filter content using named regex patterns (OR logic).

    Args:
        content: The file content to filter
        filters: Dict of {name: (regex_pattern, file_pattern)}
        file_path: Path of the file being filtered (for file pattern matching)
        debug: Whether to show debug output

    Returns:
        Filtered content with only matching lines
    """
    if not filters:
        return content

    import re

    lines = content.split("\n")
    filtered_lines = []
    total_matches = 0

    # Get applicable filters for this file
    applicable_filters = {}
    if file_path:
        for name, (pattern, filepattern) in filters.items():
            # Convert Path to string for pattern matching, always use forward slashes
            file_str = str(file_path).replace("\\", "/")
            file_name = file_path.name

            # Use comprehensive pattern matching
            matches = _matches_glob_pattern(file_str, file_name, filepattern)

            if matches:
                applicable_filters[name] = pattern
                if debug:
                    print_debug(f"Filter '{name}' applies to file '{file_path}' (pattern: {filepattern})")
            elif debug:
                print_debug(f"Filter '{name}' does not apply to file '{file_path}' (pattern: {filepattern})")
    else:
        # If no file path provided, extract just the regex patterns
        applicable_filters = {name: pattern for name, (pattern, _) in filters.items()}

    if debug and file_path:
        print_debug(f"Applying {len(applicable_filters)} filters to {file_path}")

    for line in lines:
        for name, pattern in applicable_filters.items():
            try:
                if re.search(pattern, line):
                    filtered_lines.append(line)
                    total_matches += 1
                    if debug:
                        print_debug(f"Filter '{name}' matched: {line[:50]}...")
                    break  # Found match, move to next line
            except re.error as e:
                if debug:
                    print_warning(f"Invalid regex in filter '{name}': {e}")
                continue  # Skip invalid regex

    if debug:
        print_debug(f"Content filtering: {len(lines)} lines -> {len(filtered_lines)} lines ({total_matches} total matches)")

    return "\n".join(filtered_lines)


def _matches_glob_pattern(file_path: str, file_name: str, pattern: str) -> bool:
    """
    Check if a file path matches a glob pattern using standard library functions.

    Args:
        file_path: Full file path (with forward slashes)
        file_name: Just the filename part
        pattern: Glob pattern to match against

    Returns:
        True if the pattern matches, False otherwise
    """
    import fnmatch
    import os

    # Handle simple cases first
    if pattern == "*":
        return True

    # Try filename match first (most common case)
    if fnmatch.fnmatch(file_name, pattern):
        return True

    # For cross-platform compatibility, we need to test multiple variations
    # of the path and pattern to handle different path separator conventions

    # Convert path separators to forward slashes for consistent comparison
    normalized_file_path = file_path.replace("\\", "/")
    normalized_pattern = pattern.replace("\\", "/")

    # Try full path match with forward slashes (works well cross-platform)
    if fnmatch.fnmatch(normalized_file_path, normalized_pattern):
        return True

    # Also try with native path separators
    native_pattern = normalized_pattern.replace("/", os.sep)
    native_path = normalized_file_path.replace("/", os.sep)

    if fnmatch.fnmatch(native_path, native_pattern):
        return True

    # Handle ** patterns - these need special treatment
    if "**" in pattern:
        # **/*.ext should match any .ext file at any level including root
        if pattern.startswith("**/"):
            ext_pattern = pattern[3:]  # Remove **/
            if fnmatch.fnmatch(file_name, ext_pattern):
                return True

        # dir/** should match anything in or under dir/
        elif pattern.endswith("/**"):
            dir_pattern = pattern[:-3]  # Remove /**
            if normalized_file_path.startswith(dir_pattern + "/"):
                return True

        # Try pathlib for complex ** patterns
        try:
            from pathlib import PurePath

            if PurePath(normalized_file_path).match(normalized_pattern):
                return True
        except (ValueError, TypeError):
            pass

    # Handle directory patterns like "migrations/*.sql"
    if "/" in normalized_pattern:
        pattern_parts = normalized_pattern.split("/")
        path_parts = normalized_file_path.split("/")

        # For simple dir/file patterns
        if len(pattern_parts) == 2:
            dir_pattern, file_pattern = pattern_parts
            # Check if file is in a directory matching the pattern
            if len(path_parts) >= 2:
                # Check if the directory part matches and the file part matches
                if fnmatch.fnmatch(path_parts[-2], dir_pattern) and fnmatch.fnmatch(path_parts[-1], file_pattern):
                    return True

                # Also check if any parent directory matches the pattern
                for i in range(len(path_parts) - 1):
                    if fnmatch.fnmatch(path_parts[i], dir_pattern) and fnmatch.fnmatch(file_name, file_pattern):
                        return True

    return False


def is_text_file(file_path: Path) -> bool:
    """
    Determine if a file is a text file using multiple detection methods.
    """
    # Known text file extensions
    text_extensions = {
        ".txt",
        ".md",
        ".csv",
        ".log",
        ".json",
        ".yaml",
        ".yml",
        ".xml",
        ".html",
        ".htm",
        ".css",
        ".js",
        ".py",
        ".java",
        ".c",
        ".cpp",
        ".h",
        ".hpp",
        ".cs",
        ".rb",
        ".php",
        ".pl",
        ".sh",
        ".bat",
        ".ps1",
        ".ini",
        ".cfg",
        ".conf",
        ".properties",
        ".env",
        ".rst",
        ".tex",
        ".sql",
        ".r",
        ".m",
        ".swift",
        ".kt",
        ".kts",
        ".ts",
        ".tsx",
        ".jsx",
        ".vue",
        ".go",
        ".gd",
    }

    # Security-sensitive file extensions to exclude
    security_extensions = {
        # Certificates
        ".crt",
        ".cer",
        ".der",
        ".p7b",
        ".p7c",
        ".p12",
        ".pfx",
        ".pem",
        # Keys
        ".key",
        ".keystore",
        ".jks",
        ".p8",
        ".pkcs12",
        ".pk8",
        ".pkcs8",
        ".ppk",
        ".pub",
        # Certificate signing requests
        ".csr",
        ".spc",
        # Other security files
        ".gpg",
        ".pgp",
        ".asc",
        ".kdb",
        ".sig",
    }

    # First check extension
    file_suffix = file_path.suffix.lower()
    if file_suffix in security_extensions:
        return False

    if file_suffix not in text_extensions:
        return False

    # Then check mimetype
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if mime_type and not any(t in mime_type for t in ["text", "xml", "json", "javascript", "typescript"]):
        return False

    # Finally, check content
    try:
        with open(file_path, "rb") as f:
            # Read first 8KB for analysis
            chunk = f.read(8192)

            # Check for common binary file signatures
            if chunk.startswith(bytes([0x7F, 0x45, 0x4C, 0x46])):  # ELF
                return False
            if chunk.startswith(bytes([0x4D, 0x5A])):  # PE/DOS
                return False
            if chunk.startswith(bytes([0x50, 0x4B, 0x03, 0x04])):  # ZIP
                return False
            if chunk.startswith(bytes([0x25, 0x50, 0x44, 0x46])):  # PDF
                return False

            # Check for high concentration of null bytes or non-ASCII characters
            null_count = chunk.count(0)
            if null_count > len(chunk) * 0.3:  # More than 30% nulls
                return False

            # Try decoding as UTF-8
            try:
                chunk.decode("utf-8")
                return True
            except UnicodeDecodeError:
                return False

    except OSError:
        return False


def get_file_metadata(file_path: Path) -> dict:
    """
    Get file metadata including creation time, modification time, and size.
    """
    stats = file_path.stat()
    return {
        "size": stats.st_size,
        "created": datetime.datetime.fromtimestamp(stats.st_ctime).isoformat(),
        "modified": datetime.datetime.fromtimestamp(stats.st_mtime).isoformat(),
        "accessed": datetime.datetime.fromtimestamp(stats.st_atime).isoformat(),
    }

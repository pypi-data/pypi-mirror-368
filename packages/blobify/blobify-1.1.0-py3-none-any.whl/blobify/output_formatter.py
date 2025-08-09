"""Output formatting and generation utilities."""

import datetime
from pathlib import Path
from typing import Dict, List

from .console import print_debug, print_file_processing
from .content_processor import get_file_metadata, scrub_content


def generate_header(
    directory: Path,
    git_root: Path,
    context: str,
    scrub_data: bool,
    blobify_patterns_info: tuple,
    include_index: bool = True,
    include_content: bool = True,
    include_metadata: bool = True,
    filters: dict = None,
    suppress_timestamps: bool = False,
) -> str:
    """Generate the file header with metadata and configuration info."""
    blobify_include_patterns, blobify_exclude_patterns, default_switches, llm_instructions = blobify_patterns_info

    # Keep headers minimal - no verbose metadata
    git_info = ""
    blobify_info = ""
    scrubbing_info = ""

    # Add filter information
    filter_info = ""
    if filters:
        filter_lines = []
        for name, (pattern, filepattern) in filters.items():
            if filepattern == "*":
                filter_lines.append(f"# * {name}: {pattern}")
            else:
                filter_lines.append(f"# * {name}: {pattern} (files: {filepattern})")
        filter_info = "\n#\n# Content filters applied:\n" + "\n".join(filter_lines)

    # Add LLM instructions if present
    llm_info = ""
    if llm_instructions:
        llm_lines = []
        for instruction in llm_instructions:
            llm_lines.append(f"# * {instruction}")
        llm_info = "\n#\n# Instructions for AI/LLM analysis:\n" + "\n".join(llm_lines)

    # Adjust format description based on options
    if not include_content and not include_index and not include_metadata:
        format_description = """# This file contains no useful output - index, content, and metadata have all been disabled."""
    elif not include_content and not include_index:
        # Metadata only
        format_description = """# This file contains metadata of all text files found in the specified directory.
# Format:
# 1. Metadata sections for each file (size, timestamps)
# 2. Each file section is marked with START_FILE and END_FILE delimiters"""
    elif not include_content and not include_metadata:
        # Index only
        format_description = """# This file contains an index of all text files found in the specified directory."""
    elif not include_content:
        # Index + metadata
        format_description = """# This file contains an index and metadata of all text files found in the specified directory.
# Format:
# 1. File listing with relative paths
# 2. Metadata sections for each file (size, timestamps)
# 3. Each file section is marked with START_FILE and END_FILE delimiters"""
    elif not include_index and not include_metadata:
        # Content only
        content_desc = "filtered content" if filters else "contents"
        format_description = f"""# This file contains {content_desc} of all text files found in the specified directory.
# Format:
# 1. Content sections for each file
# 2. Each file section is marked with START_FILE and END_FILE delimiters
#
# Files ignored by .gitignore or excluded by .blobify have their content excluded
# with a placeholder message."""
    elif not include_metadata:
        # Index + content
        content_desc = "filtered content" if filters else "contents"
        format_description = f"""# This file contains an index and {content_desc} of all text files found in the specified directory.
# Format:
# 1. File listing with relative paths
# 2. Content sections for each file
# 3. Each file section is marked with START_FILE and END_FILE delimiters
#
# Files ignored by .gitignore are listed in the index but marked as [IGNORED BY GITIGNORE]
# Files excluded by .blobify are listed in the index but marked as [EXCLUDED BY .blobify]
# and their content is excluded with a placeholder message."""
    elif not include_index:
        # Content + metadata
        content_desc = "filtered content" if filters else "contents"
        format_description = f"""# This file contains the {content_desc} of all text files found in the specified directory.
# Format:
# 1. Content sections for each file, including metadata and full content
# 2. Each file section is marked with START_FILE and END_FILE delimiters
#
# Files ignored by .gitignore or excluded by .blobify have their content excluded
# with a placeholder message."""
    else:
        # Index + content + metadata (default)
        content_desc = "filtered content" if filters else "contents"
        format_description = f"""# This file contains an index and {content_desc} of all text files found in the specified directory.
# Format:
# 1. File listing with relative paths
# 2. Content sections for each file, including metadata and full content
# 3. Each file section is marked with START_FILE and END_FILE delimiters
#
# Files ignored by .gitignore are listed in the index but marked as [IGNORED BY GITIGNORE]
# Files excluded by .blobify are listed in the index but marked as [EXCLUDED BY .blobify]
# and their content is excluded with a placeholder message."""

    # Build the header intro
    if suppress_timestamps:
        header_intro = """# Blobify Text File Index
# Source Directory: {directory}{git_info}{blobify_info}{scrubbing_info}{filter_info}{llm_info}
""".format(
            directory=str(directory.absolute()),
            git_info=git_info,
            blobify_info=blobify_info,
            scrubbing_info=scrubbing_info,
            filter_info=filter_info,
            llm_info=llm_info,
        )
    else:
        header_intro = """# Blobify Text File Index
# Generated: {datetime}
# Source Directory: {directory}{git_info}{blobify_info}{scrubbing_info}{filter_info}{llm_info}
""".format(
            datetime=datetime.datetime.now().isoformat(),
            directory=str(directory.absolute()),
            git_info=git_info,
            blobify_info=blobify_info,
            scrubbing_info=scrubbing_info,
            filter_info=filter_info,
            llm_info=llm_info,
        )

    # Add description to header
    header = (
        header_intro
        + """#
{format_description}
#
# This format is designed to be both human-readable and machine-parseable.
# Files are ordered alphabetically by relative path.
#
""".format(
            format_description=format_description,
        )
    )

    return header


def generate_index(
    all_files: List[Dict],
    gitignored_directories: List[Path],
    include_content: bool = True,
    include_metadata: bool = True,
) -> str:
    """Generate the file index section."""
    index = []

    # When content is disabled, don't show status labels since they refer to content inclusion
    if include_content:
        # Add gitignored directories to the index with status labels
        for dir_path in sorted(gitignored_directories, key=lambda x: str(x).lower()):
            index.append(f"{dir_path} [DIRECTORY CONTENTS IGNORED BY GITIGNORE]")

        # Build index for files with status labels
        for file_info in all_files:
            relative_path = file_info["relative_path"]
            # Priority order: git ignored > blobify excluded > filter excluded > blobify included > normal
            if file_info["is_git_ignored"]:
                index.append(f"{relative_path} [FILE CONTENTS IGNORED BY GITIGNORE]")
            elif file_info["is_blobify_excluded"]:
                index.append(f"{relative_path} [FILE CONTENTS EXCLUDED BY .blobify]")
            elif file_info.get("is_filter_excluded", False):
                index.append(f"{relative_path} [FILE CONTENTS EXCLUDED BY FILTERS]")
            elif file_info.get("is_blobify_included", False):
                index.append(f"{relative_path} [FILE CONTENTS INCLUDED BY .blobify]")
            else:
                index.append(str(relative_path))
    else:
        # When content is disabled, just show clean file listings without status labels
        # Include all discovered files regardless of git/blobify status
        all_paths = []

        # Add directories (without status labels)
        for dir_path in sorted(gitignored_directories, key=lambda x: str(x).lower()):
            all_paths.append(str(dir_path))

        # Add files (without status labels)
        for file_info in all_files:
            all_paths.append(str(file_info["relative_path"]))

        # Sort all paths together for a clean listing
        index = sorted(set(all_paths), key=str.lower)

    # Build index section
    index_section = "# FILE INDEX\n" + "#" * 80 + "\n"
    index_section += "\n".join(index)

    # Add appropriate section header based on what content will follow
    if include_content:
        index_section += "\n\n# FILE CONTENTS\n" + "#" * 80 + "\n"
    elif include_metadata:
        index_section += "\n\n# FILE METADATA\n" + "#" * 80 + "\n"
    else:
        index_section += "\n"

    return index_section


def generate_content(
    all_files: List[Dict],
    scrub_data: bool,
    include_line_numbers: bool,
    include_content: bool,
    include_metadata: bool,
    suppress_excluded: bool,
    debug: bool,
    filters: dict = None,
) -> tuple:
    """
    Generate the file content section.
    Returns tuple of (content_string, total_substitutions).
    """
    # If both content and metadata are disabled, return empty string immediately
    if not include_content and not include_metadata:
        return "", 0

    content = []
    total_substitutions = 0

    for file_info in all_files:
        file_path = file_info["path"]
        relative_path = file_info["relative_path"]
        is_git_ignored = file_info["is_git_ignored"]
        is_blobify_excluded = file_info["is_blobify_excluded"]
        is_blobify_included = file_info.get("is_blobify_included", False)
        is_filter_excluded = file_info.get("is_filter_excluded", False)

        # Skip excluded files entirely if suppress_excluded is enabled
        if suppress_excluded and (is_git_ignored or is_blobify_excluded or is_filter_excluded):
            continue

        # Always include the START_FILE marker when metadata or content is enabled
        content.append(f"\nSTART_FILE: {relative_path}")

        # Include metadata section if enabled
        if include_metadata:
            try:
                metadata = get_file_metadata(file_path)
                content.append("FILE_METADATA:")
                content.append(f"  Path: {relative_path}")
                content.append(f"  Size: {metadata['size']} bytes")
                content.append(f"  Created: {metadata['created']}")
                content.append(f"  Modified: {metadata['modified']}")
                content.append(f"  Accessed: {metadata['accessed']}")

                # Only include status when content is also being included
                if include_content:
                    if is_blobify_included:
                        content.append("  Status: INCLUDED BY .blobify")
                    elif is_git_ignored:
                        content.append("  Status: IGNORED BY GITIGNORE")
                    elif is_blobify_excluded:
                        content.append("  Status: EXCLUDED BY .blobify")
                    elif is_filter_excluded:
                        content.append("  Status: EXCLUDED BY FILTERS")
                    elif scrub_data:
                        content.append("  Status: PROCESSED WITH SCRUBADUB")
            except OSError as e:
                # If we can't get metadata, add an error message
                content.append("FILE_METADATA:")
                content.append(f"  Path: {relative_path}")
                content.append(f"  Error: Cannot read file metadata - {e}")

        # Include content section if enabled
        if include_content:
            content.append("FILE_CONTENT:")
            if is_git_ignored:
                content.append("[Content excluded - file ignored by .gitignore]")
            elif is_blobify_excluded:
                content.append("[Content excluded - file excluded by .blobify]")
            elif is_filter_excluded:
                content.append("[Content excluded - no lines matched filters]")
            else:
                try:
                    if debug:
                        print_file_processing(f"Processing file: {relative_path}")

                    with open(file_path, "r", encoding="utf-8", errors="strict") as f:
                        file_content = f.read()

                    # Attempt to scrub content if enabled
                    processed_content, substitutions = scrub_content(file_content, scrub_data, debug)
                    total_substitutions += substitutions

                    # Apply content filters if specified
                    if filters:
                        from .content_processor import filter_content_lines

                        processed_content = filter_content_lines(processed_content, filters, relative_path, debug)

                    if debug and substitutions > 0:
                        print_debug(f"File had {substitutions} substitutions, total now: {total_substitutions}")

                    # Add line numbers if enabled AND include_line_numbers is True
                    if include_line_numbers:
                        lines = processed_content.split("\n")
                        numbered_lines = []
                        line_number_width = len(str(len(lines)))

                        for i, line in enumerate(lines, 1):
                            line_number = str(i).rjust(line_number_width)
                            numbered_lines.append(f"{line_number}: {line}")

                        processed_content = "\n".join(numbered_lines)

                    content.append(processed_content)

                except Exception as e:
                    content.append(f"[Error reading file: {str(e)}]")

        content.append(f"END_FILE: {relative_path}\n")

    return "\n".join(content), total_substitutions


def format_output(
    discovery_context: Dict,
    directory: Path,
    context: str,
    scrub_data: bool,
    include_line_numbers: bool,
    include_index: bool,
    include_content: bool,
    include_metadata: bool,
    suppress_excluded: bool,
    debug: bool,
    blobify_patterns_info: tuple,
    filters: dict = None,
    suppress_timestamps: bool = False,
) -> tuple:
    """
    Format the complete output string.
    Returns tuple of (output_string, total_substitutions, file_count).
    """
    all_files = discovery_context["all_files"]
    gitignored_directories = discovery_context["gitignored_directories"]
    git_root = discovery_context["git_root"]
    included_files = discovery_context["included_files"]

    # Sort all files for consistent output
    all_files.sort(key=lambda x: str(x["relative_path"]).lower())

    # Pre-process filters to determine which files are excluded by filters
    # This needs to happen before index generation so the status labels are correct
    if filters and include_content:
        for file_info in all_files:
            # Skip files already excluded by git or blobify
            if file_info["is_git_ignored"] or file_info["is_blobify_excluded"]:
                continue

            file_path = file_info["path"]
            try:
                with open(file_path, "r", encoding="utf-8", errors="strict") as f:
                    file_content = f.read()

                # Apply filters to check if content would be excluded
                from .content_processor import filter_content_lines

                filtered_content = filter_content_lines(file_content, filters, file_info["relative_path"], debug)

                # Mark as filter-excluded if no content remains
                if filtered_content.strip() == "" and file_content.strip() != "":
                    file_info["is_filter_excluded"] = True
                    if debug:
                        print_debug(f"File {file_info['relative_path']} excluded by filters (no matching lines)")
                else:
                    file_info["is_filter_excluded"] = False
            except Exception:
                # If we can't read the file, don't mark it as filter-excluded
                file_info["is_filter_excluded"] = False

    # Generate header
    header = generate_header(
        directory,
        git_root,
        context,
        scrub_data,
        blobify_patterns_info,
        include_index,
        include_content,
        include_metadata,
        filters,
        suppress_timestamps,
    )

    # Generate index section (if enabled)
    if include_index:
        index_section = generate_index(all_files, gitignored_directories, include_content, include_metadata)
    else:
        # No index - add appropriate header based on what we're including
        if include_content:
            index_section = "\n# FILE CONTENTS\n" + "#" * 80 + "\n"
        elif include_metadata:
            index_section = "\n# FILE METADATA\n" + "#" * 80 + "\n"
        else:
            index_section = ""

    # Generate content section (only if content or metadata is enabled)
    if include_content or include_metadata:
        content_section, total_substitutions = generate_content(
            all_files,
            scrub_data,
            include_line_numbers,
            include_content,
            include_metadata,
            suppress_excluded,
            debug,
            filters,
        )
    else:
        content_section = ""
        total_substitutions = 0
        # Add debug output to see if this branch is being taken
        if debug:
            from .console import print_debug

            print_debug("Skipping content generation due to --output-content=false and --output-metadata=false flags")

    # Combine all sections
    result = header + index_section + content_section

    return result, total_substitutions, len(included_files)

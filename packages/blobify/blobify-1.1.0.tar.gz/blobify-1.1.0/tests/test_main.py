"""Tests for main.py module - CLI integration and behavior."""

import subprocess
from unittest.mock import Mock, patch

import pytest

from blobify.main import main


class TestMain:
    """Test cases for main function - CLI integration and behavior."""

    def test_main_processes_real_files(self, tmp_path):
        """Test that main actually processes files and produces output."""
        # Create real test files
        (tmp_path / "test.py").write_text("print('hello')")
        (tmp_path / "README.md").write_text("# Test Project")

        # Use file output to avoid capture issues
        output_file = tmp_path / "output.txt"
        with patch("sys.argv", ["bfy", str(tmp_path), "--output-filename", str(output_file)]):
            main()

        # Check real output was produced
        content = output_file.read_text(encoding="utf-8")
        assert "# Blobify Text File Index" in content
        assert "test.py" in content
        assert "README.md" in content
        assert "print('hello')" in content
        assert "# Test Project" in content

    def test_main_with_output_file_simple(self, tmp_path):
        """Test that main writes to output file correctly - no capture needed."""
        # Create real test file
        (tmp_path / "test.py").write_text("def hello(): pass")
        output_file = tmp_path / "output.txt"

        # Run main with output file
        with patch("sys.argv", ["bfy", str(tmp_path), "--output-filename", str(output_file)]):
            main()

        # Check file was created with real content
        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert "# Blobify Text File Index" in content
        assert "test.py" in content
        assert "def hello(): pass" in content

    def test_main_gitignore_behavior(self, tmp_path):
        """Test .gitignore handling with file output."""
        # Create git repo with .gitignore
        (tmp_path / ".git").mkdir()
        (tmp_path / ".gitignore").write_text("*.log\n")

        # Create files
        (tmp_path / "app.py").write_text("print('app')")
        (tmp_path / "debug.log").write_text("log content")

        # Use file output
        output_file = tmp_path / "output.txt"
        with patch("sys.argv", ["bfy", str(tmp_path), "--output-filename", str(output_file)]):
            main()

        content = output_file.read_text(encoding="utf-8")
        # Should include non-ignored files
        assert "app.py" in content
        assert "print('app')" in content
        # Should show ignored files in index but not content
        assert "debug.log [FILE CONTENTS IGNORED BY GITIGNORE]" in content
        assert "log content" not in content

    @patch("subprocess.run")
    def test_clipboard_integration_windows(self, mock_subprocess, tmp_path):
        """Test clipboard functionality - mock only the subprocess call."""
        # Create real test file
        (tmp_path / "test.py").write_text("print('hello world')")

        # Mock subprocess.run to avoid actually calling clipboard
        mock_subprocess.return_value = None

        # Run with clipboard option on Windows
        with patch("sys.argv", ["bfy", str(tmp_path), "--copy-to-clipboard=true"]):
            with patch("sys.platform", "win32"):
                main()

        # Verify subprocess was called correctly
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]  # First positional argument
        assert "clip" in call_args
        assert "type" in call_args

    @patch("subprocess.Popen")
    def test_clipboard_integration_macos(self, mock_popen, tmp_path):
        """Test macOS clipboard functionality."""
        # Create real test file
        (tmp_path / "test.py").write_text("print('hello mac')")

        # Mock Popen for macOS clipboard
        mock_proc = Mock()
        mock_popen.return_value = mock_proc

        # Run with clipboard on macOS
        with patch("sys.argv", ["bfy", str(tmp_path), "--copy-to-clipboard=true"]):
            with patch("sys.platform", "darwin"):
                main()

        # Verify pbcopy was called
        mock_popen.assert_called_once_with(["pbcopy"], stdin=subprocess.PIPE, text=True, encoding="utf-8")
        # Verify our content was passed to pbcopy
        mock_proc.communicate.assert_called_once()
        passed_content = mock_proc.communicate.call_args[0][0]
        assert "print('hello mac')" in passed_content

    def test_error_handling_invalid_directory(self):
        """Test main handles invalid directory gracefully."""
        with patch("sys.argv", ["bfy", "/nonexistent/directory"]):
            with pytest.raises(SystemExit):
                main()

    def test_bom_removal_with_file_output(self, tmp_path):
        """Test BOM removal using file output."""
        (tmp_path / "test.py").write_text("print('test')")
        output_file = tmp_path / "output.txt"

        # Mock format_output to return content with BOM
        # Import sys.modules to get the actual module
        import sys

        main_module = sys.modules["blobify.main"]
        with patch.object(main_module, "format_output") as mock_format:
            mock_format.return_value = ("\ufeffTest output with BOM", 0, 1)

            with patch("sys.argv", ["bfy", str(tmp_path), "--output-filename", str(output_file)]):
                main()

        # Check BOM was removed from file
        content = output_file.read_text(encoding="utf-8")
        assert not content.startswith("\ufeff")
        assert content == "Test output with BOM"

    def test_default_directory_with_blobify(self, tmp_path, monkeypatch):
        """Test main uses current directory when .blobify exists."""
        # Change to temp directory and create .blobify
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".blobify").write_text("+*.py")
        (tmp_path / "test.py").write_text("print('default dir test')")

        # Use file output to avoid capture issues
        output_file = tmp_path / "output.txt"

        # Run without directory argument
        with patch("sys.argv", ["bfy", "--output-filename", str(output_file)]):
            main()

        content = output_file.read_text()
        assert "test.py" in content
        assert "print('default dir test')" in content

    def test_default_directory_no_blobify_fails(self, tmp_path, monkeypatch):
        """Test main fails when no directory and no .blobify file."""
        monkeypatch.chdir(tmp_path)

        with patch("sys.argv", ["bfy"]):
            with pytest.raises(SystemExit):
                main()

    def test_blobify_config_integration(self, tmp_path):
        """Test .blobify configuration works."""
        # Create git repo with .blobify config
        (tmp_path / ".git").mkdir()
        (tmp_path / ".blobify").write_text(
            """
+*.py
-*.log
"""
        )

        # Create files
        (tmp_path / "app.py").write_text("print('app')")
        (tmp_path / "README.md").write_text("# README")
        (tmp_path / "debug.log").write_text("debug log content")

        # Use file output
        output_file = tmp_path / "output.txt"
        with patch("sys.argv", ["bfy", str(tmp_path), "--output-filename", str(output_file)]):
            main()

        content = output_file.read_text()
        # Should include .py files
        assert "app.py" in content
        assert "print('app')" in content
        # Should show other files as excluded/ignored
        assert "debug.log" in content  # In index
        # The key fix: Check that the actual file content is not included,
        # but allow the filename to appear in index and labels
        assert "debug log content" not in content  # Actual file content should not be there

    def test_context_option_integration(self, tmp_path):
        """Test --context option with real .blobify config."""
        # Create git repo with context-specific .blobify config
        (tmp_path / ".git").mkdir()
        (tmp_path / ".blobify").write_text(
            """
# Default patterns
+*.py

[docs-only]
+*.md
+docs/**
"""
        )

        # Create files
        (tmp_path / "app.py").write_text("print('app')")
        (tmp_path / "README.md").write_text("# README")

        # Test with docs-only context
        output_file = tmp_path / "output.txt"
        with patch("sys.argv", ["bfy", str(tmp_path), "--context", "docs-only", "--output-filename", str(output_file)]):
            main()

        content = output_file.read_text()
        # Should include markdown files in docs-only context
        assert "README.md" in content
        assert "# README" in content


class TestCliSummaryMessages:
    """Test CLI summary messages for all switch combinations."""

    def setup_test_files(self, tmp_path):
        """Create standard test files."""
        (tmp_path / "test.py").write_text("print('hello')")
        (tmp_path / "README.md").write_text("# Test")
        return tmp_path

    def test_cli_summary_all_combinations(self, tmp_path, capsys):
        """Test CLI summary messages for all switch combinations."""
        self.setup_test_files(tmp_path)

        test_cases = [
            # (switches, expected_message)
            ([], "Processed 2 files"),  # Default case
            (["--output-content=false"], "(index and metadata only)"),
            (["--output-index=false"], "Processed 2 files"),  # No special message for just no-index
            (["--output-metadata=false"], "(index and content, no metadata)"),
            (["--output-content=false", "--output-index=false"], "(metadata only)"),
            (["--output-content=false", "--output-metadata=false"], "(index only)"),
            (["--output-index=false", "--output-metadata=false"], "(content only, no metadata)"),
            (
                ["--output-content=false", "--output-index=false", "--output-metadata=false"],
                "(no useful output - index, content, and metadata all disabled)",
            ),
        ]

        for switches, expected_message in test_cases:
            capsys.readouterr()  # Clear previous output

            with patch("sys.argv", ["bfy", str(tmp_path)] + switches):
                main()

            captured = capsys.readouterr()
            assert expected_message in captured.err, f"Failed for switches {switches}: expected '{expected_message}' in '{captured.err}'"

    def test_cli_warning_for_no_useful_output(self, tmp_path, capsys):
        """Test that CLI shows warning when no useful output is generated."""
        self.setup_test_files(tmp_path)

        with patch(
            "sys.argv",
            ["bfy", str(tmp_path), "--output-content=false", "--output-index=false", "--output-metadata=false"],
        ):
            main()

        captured = capsys.readouterr()
        assert "Note: All output options are disabled" in captured.err
        assert "--help" in captured.err

    def test_cli_context_in_summary(self, tmp_path, capsys):
        """Test that context appears in summary message."""
        # Create git repo with context
        (tmp_path / ".git").mkdir()
        (tmp_path / ".blobify").write_text("[test-ctx]\n+*.py")
        (tmp_path / "test.py").write_text("print('test')")

        with patch("sys.argv", ["bfy", str(tmp_path), "-x", "test-ctx"]):
            main()

        captured = capsys.readouterr()
        assert "(context: test-ctx)" in captured.err

    def test_cli_scrubbing_messages(self, tmp_path, capsys):
        """Test scrubbing-related CLI messages."""
        self.setup_test_files(tmp_path)

        # Create a file with actual sensitive data to trigger scrubbing
        (tmp_path / "sensitive.py").write_text("email = 'test@example.com'\nprint('hello')")

        with patch("sys.argv", ["bfy", str(tmp_path)]):
            main()

        captured = capsys.readouterr()
        # Check for scrubbing activity - could be "made X substitutions" or "found no sensitive data"
        assert any(phrase in captured.err for phrase in ["scrubadub made", "scrubadub found"])

    def test_cli_debug_scrubbing_messages(self, tmp_path, capsys):
        """Test scrubbing messages with debug enabled."""
        self.setup_test_files(tmp_path)

        # Create a file with actual sensitive data to trigger scrubbing
        (tmp_path / "sensitive.py").write_text("email = 'admin@company.com'\nprint('debug')")

        with patch("sys.argv", ["bfy", str(tmp_path), "--debug=true"]):
            main()

        captured = capsys.readouterr()
        # Check for scrubbing activity - could be "made X substitutions" or "found no sensitive data"
        assert any(phrase in captured.err for phrase in ["scrubadub made", "scrubadub found"])
        # Should show debug output
        assert "scrubadub processing is enabled" in captured.err


class TestCommandLineOptions:
    """Test individual command line options work correctly."""

    def test_line_numbers_option(self, tmp_path):
        """Test --output-line-numbers option."""
        test_data_dir = tmp_path / "test_data"
        test_data_dir.mkdir()
        (test_data_dir / "test.py").write_text("line1\nline2\nline3")

        # Test with line numbers (default)
        output_file1 = tmp_path / "with_lines.txt"
        with patch("sys.argv", ["bfy", str(test_data_dir), "--output-filename", str(output_file1)]):
            main()

        with_lines = output_file1.read_text()
        assert "1: line1" in with_lines
        assert "2: line2" in with_lines

        # Test without line numbers
        output_file2 = tmp_path / "without_lines.txt"
        with patch(
            "sys.argv",
            ["bfy", str(test_data_dir), "--output-line-numbers=false", "--output-filename", str(output_file2)],
        ):
            main()

        without_lines = output_file2.read_text()
        assert "1: line1" not in without_lines
        assert "2: line2" not in without_lines
        assert "line1\nline2\nline3" in without_lines

    def test_index_option(self, tmp_path):
        """Test --output-index option."""
        (tmp_path / "test.py").write_text("print('test')")

        # Test with index (default)
        output_file1 = tmp_path / "with_index.txt"
        with patch("sys.argv", ["bfy", str(tmp_path), "--output-filename", str(output_file1)]):
            main()

        with_index = output_file1.read_text()
        assert "# FILE INDEX" in with_index

        # Test without index
        output_file2 = tmp_path / "without_index.txt"
        with patch("sys.argv", ["bfy", str(tmp_path), "--output-index=false", "--output-filename", str(output_file2)]):
            main()

        without_index = output_file2.read_text()
        # The key fix: Check that the index section header is not present
        # but FILE CONTENTS header should still be there
        assert "# FILE INDEX\n" + "#" * 80 not in without_index
        assert "# FILE CONTENTS" in without_index

    def test_content_option(self, tmp_path):
        """Test --output-content option."""
        (tmp_path / "test.py").write_text("print('secret content')")

        # Test with content (default)
        output_file1 = tmp_path / "with_content.txt"
        with patch("sys.argv", ["bfy", str(tmp_path), "--output-filename", str(output_file1)]):
            main()

        with_content = output_file1.read_text()
        assert "print('secret content')" in with_content
        assert "# FILE CONTENTS" in with_content

        # Test without content
        output_file2 = tmp_path / "without_content.txt"
        with patch("sys.argv", ["bfy", str(tmp_path), "--output-content=false", "--output-filename", str(output_file2)]):
            main()

        without_content = output_file2.read_text()
        assert "print('secret content')" not in without_content
        assert "# FILE CONTENTS" not in without_content
        assert "# FILE INDEX" in without_content  # Should still have index

    def test_metadata_option(self, tmp_path):
        """Test --output-metadata option."""
        # Create a clean test environment that won't include project source files
        test_dir = tmp_path / "test_project"
        test_dir.mkdir()

        # Create test files that don't contain metadata-related strings
        (test_dir / "app.py").write_text("print('hello world')")
        (test_dir / "config.json").write_text('{"name": "test"}')

        # Test with metadata (default)
        output_file1 = tmp_path / "with_metadata.txt"
        with patch("sys.argv", ["bfy", str(test_dir), "--output-filename", str(output_file1)]):
            main()

        with_metadata = output_file1.read_text()
        # Check for metadata section headers (not just the string anywhere)
        assert "FILE_METADATA:" in with_metadata
        assert "Size:" in with_metadata
        assert "Created:" in with_metadata

        # Test without metadata
        output_file2 = tmp_path / "without_metadata.txt"
        with patch("sys.argv", ["bfy", str(test_dir), "--output-metadata=false", "--output-filename", str(output_file2)]):
            main()

        without_metadata = output_file2.read_text()

        # More specific checks - look for metadata section patterns, not just the string
        # The key is to check that no metadata sections are present as actual sections
        lines = without_metadata.split("\n")
        metadata_section_found = False
        for i, line in enumerate(lines):
            if line.strip() == "FILE_METADATA:":
                # Check if this looks like a metadata section (followed by indented content)
                if i + 1 < len(lines) and lines[i + 1].strip().startswith("Path:"):
                    metadata_section_found = True
                    break

        assert not metadata_section_found, "Found FILE_METADATA section when --output-metadata=false was specified"

        # Should still have the actual content
        assert "print('hello world')" in without_metadata
        assert '{"name": "test"}' in without_metadata

    def test_debug_option_behavior(self, tmp_path, capsys):
        """Test --debug option produces debug output."""
        # Create git repo for debug output
        (tmp_path / ".git").mkdir()
        (tmp_path / ".gitignore").write_text("*.log")
        (tmp_path / "test.py").write_text("print('test')")

        with patch("sys.argv", ["bfy", str(tmp_path), "--debug=true"]):
            main()

        captured = capsys.readouterr()
        # Should see debug messages
        assert any("debug" in line.lower() for line in captured.err.split("\n"))

    def test_enable_scrubbing_option_behavior(self, tmp_path):
        """Test --enable-scrubbing option controls scrubbing."""
        (tmp_path / "test.py").write_text("email: test@example.com")

        # Test with scrubbing enabled (default)
        output_file1 = tmp_path / "with_scrub.txt"
        with patch("sys.argv", ["bfy", str(tmp_path), "--output-filename", str(output_file1)]):
            main()

        # Test with scrubbing disabled
        output_file2 = tmp_path / "without_scrub.txt"
        with patch("sys.argv", ["bfy", str(tmp_path), "--enable-scrubbing=false", "--output-filename", str(output_file2)]):
            main()

        # Both should contain the email since scrubadub may not be available in test environment
        # The important thing is that --enable-scrubbing=false doesn't break anything
        content1 = output_file1.read_text()
        content2 = output_file2.read_text()
        assert "test@example.com" not in content1
        assert "test@example.com" in content2

    def test_filter_option_with_csv_format(self, tmp_path):
        """Test --filter option with new CSV format."""
        py_file = tmp_path / "test.py"
        py_file.write_text("def hello():\n    print('world')\nclass Test:\n    pass")

        output_file = tmp_path / "output.txt"

        with patch("sys.argv", ["bfy", str(tmp_path), "--filter", '"functions","^def"', "--output-filename", str(output_file)]):
            main()

        content = output_file.read_text()
        assert "def hello():" in content
        assert "print('world')" not in content
        assert "class Test:" not in content

    def test_filter_option_with_file_pattern(self, tmp_path):
        """Test --filter option with file pattern in CSV format."""
        (tmp_path / "test.py").write_text("def python_func():\n    pass")
        (tmp_path / "test.js").write_text("function js_func() {\n    return true;\n}")

        output_file = tmp_path / "output.txt"

        with patch(
            "sys.argv",
            ["bfy", str(tmp_path), "--filter", '"py-functions","^def","*.py"', "--output-filename", str(output_file)],
        ):
            main()

        content = output_file.read_text()
        assert "def python_func():" in content
        assert "function js_func()" not in content  # Should be excluded by file pattern

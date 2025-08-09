"""Tests for context inheritance functionality."""

from unittest.mock import patch

import pytest

from blobify.config import get_available_contexts, list_available_contexts, read_blobify_config
from blobify.main import main


class TestContextInheritance:
    """Test cases for context inheritance functionality."""

    def test_default_context_behavior(self, tmp_path):
        """Test that default context works correctly."""
        blobify_file = tmp_path / ".blobify"
        blobify_file.write_text(
            """
# Default context patterns
@copy-to-clipboard=true
+*.py
-*.log
"""
        )

        # Test default context (no context specified)
        includes, excludes, switches, _ = read_blobify_config(tmp_path)
        assert includes == ["*.py"]
        assert excludes == ["*.log"]
        assert switches == ["copy-to-clipboard=true"]

        # Test explicitly requesting default context
        includes, excludes, switches, _ = read_blobify_config(tmp_path, "default")
        assert includes == ["*.py"]
        assert excludes == ["*.log"]
        assert switches == ["copy-to-clipboard=true"]

    def test_single_level_inheritance(self, tmp_path):
        """Test basic single-level inheritance."""
        blobify_file = tmp_path / ".blobify"
        blobify_file.write_text(
            """
# Default context
@copy-to-clipboard=true
+*.py
-*.log

[extended:default]
# Inherits from default
+*.md
-secret.txt
"""
        )

        # Test default context
        includes, excludes, switches, _ = read_blobify_config(tmp_path, "default")
        assert includes == ["*.py"]
        assert excludes == ["*.log"]
        assert switches == ["copy-to-clipboard=true"]

        # Test extended context (should inherit from default)
        includes, excludes, switches, _ = read_blobify_config(tmp_path, "extended")
        assert includes == ["*.py", "*.md"]  # Inherited + own
        assert excludes == ["*.log", "secret.txt"]  # Inherited + own
        assert switches == ["copy-to-clipboard=true"]  # Inherited

    def test_multi_level_inheritance(self, tmp_path):
        """Test multi-level inheritance chain."""
        blobify_file = tmp_path / ".blobify"
        blobify_file.write_text(
            """
# Default context
@copy-to-clipboard=true
+*.py

[base:default]
@debug=true
+*.js

[extended:base]
@output-metadata=false
+*.md

[final:extended]
+*.txt
-*.log
"""
        )

        # Test final context should inherit from entire chain
        includes, excludes, switches, _ = read_blobify_config(tmp_path, "final")

        # Should have patterns from entire inheritance chain
        assert includes == ["*.py", "*.js", "*.md", "*.txt"]
        assert excludes == ["*.log"]
        assert switches == ["copy-to-clipboard=true", "debug=true", "output-metadata=false"]

    def test_context_without_inheritance(self, tmp_path):
        """Test context that doesn't inherit from anything."""
        blobify_file = tmp_path / ".blobify"
        blobify_file.write_text(
            """
# Default context
@copy-to-clipboard=true
+*.py

[standalone]
# No inheritance
+*.md
@debug=true
"""
        )

        # Test standalone context (should not inherit from default)
        includes, excludes, switches, _ = read_blobify_config(tmp_path, "standalone")
        assert includes == ["*.md"]  # Only own patterns
        assert excludes == []
        assert switches == ["debug=true"]  # Only own switches

    def test_missing_parent_context(self, tmp_path):
        """Test handling when parent context doesn't exist."""
        blobify_file = tmp_path / ".blobify"
        blobify_file.write_text(
            """
[child:nonexistent]
+*.py
@debug=true
"""
        )

        # Should raise error for missing parent
        with pytest.raises(ValueError, match="Parent context\\(s\\) not found: nonexistent"):
            read_blobify_config(tmp_path, "child", debug=True)

    def test_inheritance_preserves_pattern_order(self, tmp_path):
        """Test that inheritance preserves the order of patterns."""
        blobify_file = tmp_path / ".blobify"
        blobify_file.write_text(
            """
# Default has exclusions first
-*.log
+*.py
@copy-to-clipboard=true

[child:default]
# Child adds more patterns
+*.md
-secret.txt
@debug=true
"""
        )

        includes, excludes, switches, _ = read_blobify_config(tmp_path, "child")

        # Order should be: parent patterns first, then child patterns
        assert includes == ["*.py", "*.md"]
        assert excludes == ["*.log", "secret.txt"]
        assert switches == ["copy-to-clipboard=true", "debug=true"]

    def test_context_inheritance_with_blobify_patterns_file_order(self, tmp_path):
        """Test that inherited patterns maintain the file order for pattern application."""
        # Create git repo
        (tmp_path / ".git").mkdir()

        blobify_file = tmp_path / ".blobify"
        blobify_file.write_text(
            """
# Default: exclude all, then include Python
-**
+*.py

[docs:default]
# Inherit exclusion, add markdown
+*.md
"""
        )

        # Create test files
        (tmp_path / "app.py").write_text("print('app')")
        (tmp_path / "README.md").write_text("# README")
        (tmp_path / "config.xml").write_text("<config/>")

        output_file = tmp_path / "output.txt"
        with patch("sys.argv", ["bfy", str(tmp_path), "-x", "docs", "--output-filename", str(output_file)]):
            main()

        content = output_file.read_text(encoding="utf-8")

        # Should include Python and Markdown files (from inheritance + own patterns)
        assert "print('app')" in content
        assert "# README" in content

        # Should exclude XML file (from inherited -** pattern)
        assert "<config/>" not in content
        assert "config.xml [FILE CONTENTS EXCLUDED BY .blobify]" in content

    def test_get_available_contexts_with_inheritance(self, tmp_path):
        """Test that get_available_contexts correctly parses inheritance syntax."""
        blobify_file = tmp_path / ".blobify"
        blobify_file.write_text(
            """
[base]
+*.py

[extended:base]
+*.md

[complex:extended]
+*.txt
"""
        )

        contexts = get_available_contexts(tmp_path)
        assert set(contexts) == {"base", "extended", "complex"}

    def test_list_available_contexts_shows_inheritance(self, tmp_path, capsys):
        """Test that list_available_contexts shows inheritance relationships."""
        # Create git repo
        (tmp_path / ".git").mkdir()

        blobify_file = tmp_path / ".blobify"
        blobify_file.write_text(
            """
# Base context for Python files
[base]
+*.py

# Extended context inherits base
[extended:base]
+*.md

# Complex context inherits extended
[complex:extended]
+*.txt
"""
        )

        list_available_contexts(tmp_path)

        captured = capsys.readouterr()
        assert "base" in captured.out
        assert "extended (inherits from base)" in captured.out
        assert "complex (inherits from extended)" in captured.out

    def test_context_inheritance_help_text(self, tmp_path, capsys):
        """Test that help text includes inheritance examples when no contexts exist."""
        # Create git repo
        (tmp_path / ".git").mkdir()

        # Create empty .blobify
        (tmp_path / ".blobify").write_text("")

        list_available_contexts(tmp_path)

        captured = capsys.readouterr()
        assert "Context inheritance:" in captured.out
        assert "[extended:base]" in captured.out
        assert "# Inherits @copy-to-clipboard=true and +*.py from base" in captured.out

    def test_context_inheritance_with_filter_defaults(self, tmp_path):
        """Test that filter defaults are properly inherited."""
        # Create git repo
        (tmp_path / ".git").mkdir()

        blobify_file = tmp_path / ".blobify"
        blobify_file.write_text(
            """
# Default with filter
@filter="functions","^def"
+*.py

[enhanced:default]
@filter="classes","^class"
+*.js
"""
        )

        # Create test files
        py_file = tmp_path / "test.py"
        py_file.write_text("def hello():\n    pass\nclass Test:\n    pass")

        js_file = tmp_path / "test.js"
        js_file.write_text("function greet() {}\nclass Component {}")

        output_file = tmp_path / "output.txt"
        with patch("sys.argv", ["bfy", str(tmp_path), "-x", "enhanced", "--output-filename", str(output_file)]):
            main()

        content = output_file.read_text(encoding="utf-8")

        # Should show both inherited and own filters
        assert "functions: ^def" in content
        assert "classes: ^class" in content

        # Should apply both filters
        assert "def hello():" in content
        assert "class Test:" in content
        assert "class Component" in content

    def test_nonexistent_context_inheritance(self, tmp_path, capsys):
        """Test requesting a context that doesn't exist now exits with error."""
        blobify_file = tmp_path / ".blobify"
        blobify_file.write_text(
            """
    [existing]
    +*.py
    """
        )

        # Should raise SystemExit when requesting non-existent context
        with pytest.raises(SystemExit) as exc_info:
            read_blobify_config(tmp_path, "nonexistent")

        # Should exit with code 1
        assert exc_info.value.code == 1

        # Should show helpful error message
        captured = capsys.readouterr()
        assert "Context 'nonexistent' not found in .blobify file" in captured.err
        assert "Available contexts: existing" in captured.err

    def test_nonexistent_context_exits_with_error(self, tmp_path, capsys):
        """Test that requesting a non-existent context exits with error."""
        # Create git repo
        (tmp_path / ".git").mkdir()

        # Create .blobify with some contexts
        (tmp_path / ".blobify").write_text(
            """
    [existing-context]
    +*.py

    [another-context]
    +*.md
    """
        )

        (tmp_path / "test.py").write_text("print('test')")

        # Test with non-existent context
        with patch("sys.argv", ["bfy", str(tmp_path), "-x", "nonexistent-context"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

            # Should exit with code 1
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "Context 'nonexistent-context' not found in .blobify file" in captured.err
        assert "Available contexts: another-context, existing-context" in captured.err
        assert "Use 'bfy -x' to list all contexts with descriptions" in captured.err

    def test_nonexistent_context_no_available_contexts(self, tmp_path, capsys):
        """Test error message when no contexts exist in .blobify file."""
        # Create git repo
        (tmp_path / ".git").mkdir()

        # Create .blobify with no contexts (only default patterns)
        (tmp_path / ".blobify").write_text(
            """
    +*.py
    -*.log
    """
        )

        (tmp_path / "test.py").write_text("print('test')")

        # Test with non-existent context
        with patch("sys.argv", ["bfy", str(tmp_path), "-x", "some-context"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "Context 'some-context' not found in .blobify file" in captured.err
        assert "No contexts found in .blobify file" in captured.err

    def test_default_context_behavior_unchanged(self, tmp_path):
        """Test that default context behavior is unchanged when no context specified."""
        # Create git repo
        (tmp_path / ".git").mkdir()

        # Create .blobify with patterns but no explicit contexts
        (tmp_path / ".blobify").write_text(
            """
    +*.py
    -*.log
    """
        )

        (tmp_path / "test.py").write_text("print('test')")
        output_file = tmp_path / "output.txt"

        # Should work fine with no context specified (uses default)
        with patch("sys.argv", ["bfy", str(tmp_path), "--output-filename", str(output_file)]):
            main()  # Should not raise SystemExit

        # Should produce normal output
        content = output_file.read_text(encoding="utf-8")
        assert "print('test')" in content

    def test_empty_inheritance_syntax(self, tmp_path):
        """Test handling of malformed inheritance syntax."""
        blobify_file = tmp_path / ".blobify"
        blobify_file.write_text(
            """
[base]
+*.md

[empty:]
+*.py

[normal:base]
+*.txt
"""
        )

        # Should handle malformed syntax gracefully
        contexts = get_available_contexts(tmp_path)
        assert "empty" in contexts
        assert "normal" in contexts
        assert "base" in contexts

        # Test that empty parent is treated as no inheritance
        includes, excludes, switches, _ = read_blobify_config(tmp_path, "empty")
        assert includes == ["*.py"]

        # Test that normal inheritance still works
        includes, excludes, switches, _ = read_blobify_config(tmp_path, "normal")
        assert includes == ["*.md", "*.txt"]

    def test_context_inheritance_integration_example(self, tmp_path):
        """Test the complete example from the task description."""
        # Create git repo
        (tmp_path / ".git").mkdir()

        blobify_file = tmp_path / ".blobify"
        blobify_file.write_text(
            """
-**
@copy-to-clipboard=true

[code:default]
# "code" inherits -** and @copy-to-clipboard=true
+code

[all:code]
# "all" inherits -**, @copy-to-clipboard=true, and +code
+**
"""
        )

        # Test that "all" context gets the expected final configuration
        includes, excludes, switches, _ = read_blobify_config(tmp_path, "all")

        # Final "all" context should be evaluated as: -**, @copy-to-clipboard=true, +code, +**
        assert excludes == ["**"]
        assert switches == ["copy-to-clipboard=true"]
        assert includes == ["code", "**"]

    def test_inheritance_with_complex_patterns(self, tmp_path):
        """Test inheritance with complex pattern combinations."""
        blobify_file = tmp_path / ".blobify"
        blobify_file.write_text(
            """
# Default excludes everything, includes Python
-**
+*.py
+src/**/*.py

[docs:default]
# Add documentation
+*.md
+docs/**
-docs/private/**

[full:docs]
# Add everything else
+**
@show-excluded=false
"""
        )

        includes, excludes, switches, _ = read_blobify_config(tmp_path, "full")

        # Should have all patterns from inheritance chain
        expected_includes = ["*.py", "src/**/*.py", "*.md", "docs/**", "**"]
        expected_excludes = ["**", "docs/private/**"]
        expected_switches = ["show-excluded=false"]

        assert includes == expected_includes
        assert excludes == expected_excludes
        assert switches == expected_switches

    def test_contexts_processed_in_file_order(self, tmp_path):
        """Test that contexts can only inherit from contexts defined earlier in the file."""
        blobify_file = tmp_path / ".blobify"
        blobify_file.write_text(
            """
[first]
+*.py
@copy-to-clipboard=true

[second:first]
# Can inherit from first (defined above)
+*.md

[third:first]
# Can also inherit from first
+*.txt
"""
        )

        # Test that second inherits from first
        includes, excludes, switches, _ = read_blobify_config(tmp_path, "second")
        assert includes == ["*.py", "*.md"]
        assert switches == ["copy-to-clipboard=true"]

        # Test that third also inherits from first
        includes, excludes, switches, _ = read_blobify_config(tmp_path, "third")
        assert includes == ["*.py", "*.txt"]
        assert switches == ["copy-to-clipboard=true"]

    def test_cannot_redefine_default_context(self, tmp_path):
        """Test that attempting to redefine 'default' context raises an error."""
        blobify_file = tmp_path / ".blobify"
        blobify_file.write_text(
            """
# Default context
@copy-to-clipboard=true
+*.py

[default]
# This should error
+*.md
"""
        )

        with pytest.raises(ValueError, match="Cannot redefine 'default' context"):
            read_blobify_config(tmp_path, debug=True)

    def test_cannot_inherit_from_nonexistent_context(self, tmp_path):
        """Test that inheriting from a non-existent context raises an error."""
        blobify_file = tmp_path / ".blobify"
        blobify_file.write_text(
            """
[child:nonexistent]
+*.py
"""
        )

        with pytest.raises(ValueError, match="Parent context\\(s\\) not found: nonexistent"):
            read_blobify_config(tmp_path, "child", debug=True)

    def test_cannot_inherit_from_context_defined_later(self, tmp_path):
        """Test that inheriting from a context defined later in file raises an error."""
        blobify_file = tmp_path / ".blobify"
        blobify_file.write_text(
            """
[early:late]
+*.py

[late]
+*.md
"""
        )

        with pytest.raises(ValueError, match="Parent context\\(s\\) not found: late"):
            read_blobify_config(tmp_path, "early", debug=True)

    def test_cannot_define_context_twice(self, tmp_path):
        """Test that defining the same context twice raises an error."""
        blobify_file = tmp_path / ".blobify"
        blobify_file.write_text(
            """
[duplicate]
+*.py

[duplicate]
+*.md
"""
        )

        with pytest.raises(ValueError, match="Context 'duplicate' already defined"):
            read_blobify_config(tmp_path, debug=True)

    def test_multiple_inheritance_basic(self, tmp_path):
        """Test basic multiple inheritance from two contexts."""
        blobify_file = tmp_path / ".blobify"
        blobify_file.write_text(
            """
[base1]
@copy-to-clipboard=true
+*.py
-*.log

[base2]
@debug=true
+*.md
-*.tmp

[combined:base1,base2]
+*.txt
"""
        )

        includes, excludes, switches, _ = read_blobify_config(tmp_path, "combined")

        # Should inherit from both parents
        assert includes == ["*.py", "*.md", "*.txt"]
        assert excludes == ["*.log", "*.tmp"]
        assert switches == ["copy-to-clipboard=true", "debug=true"]

    def test_multiple_inheritance_complex(self, tmp_path):
        """Test complex multiple inheritance with nested inheritance."""
        blobify_file = tmp_path / ".blobify"
        blobify_file.write_text(
            """
# Base contexts
@copy-to-clipboard=true
+base.py

[docs:default]
+*.md
@output-metadata=false

[code:default]
+*.js
@debug=true

[combined:docs,code]
# Inherits from both docs and code (which both inherit from default)
+*.txt
@show-excluded=false
"""
        )

        includes, excludes, switches, _ = read_blobify_config(tmp_path, "combined")

        # Should inherit: base.py (from default via docs), *.md (from docs),
        # base.py again (from default via code), *.js (from code), *.txt (own)
        assert includes == ["base.py", "*.md", "base.py", "*.js", "*.txt"]
        assert switches == [
            "copy-to-clipboard=true",
            "output-metadata=false",
            "copy-to-clipboard=true",
            "debug=true",
            "show-excluded=false",
        ]

    def test_multiple_inheritance_with_duplicates(self, tmp_path):
        """Test that multiple inheritance handles duplicate patterns gracefully."""
        blobify_file = tmp_path / ".blobify"
        blobify_file.write_text(
            """
[parent1]
@copy-to-clipboard=true
+*.py
-*.log

[parent2]
@copy-to-clipboard=true
+*.py
-*.tmp

[child:parent1,parent2]
+*.md
"""
        )

        includes, excludes, switches, _ = read_blobify_config(tmp_path, "child")

        # Should have duplicates (implementation preserves order from parents)
        assert includes == ["*.py", "*.py", "*.md"]
        assert excludes == ["*.log", "*.tmp"]
        assert switches == ["copy-to-clipboard=true", "copy-to-clipboard=true"]

    def test_multiple_inheritance_missing_one_parent(self, tmp_path):
        """Test error when one of multiple parents doesn't exist."""
        blobify_file = tmp_path / ".blobify"
        blobify_file.write_text(
            """
[existing]
+*.py

[child:existing,missing]
+*.md
"""
        )

        with pytest.raises(ValueError, match="Parent context\\(s\\) not found: missing"):
            read_blobify_config(tmp_path, "child", debug=True)

    def test_multiple_inheritance_missing_multiple_parents(self, tmp_path):
        """Test error when multiple parents don't exist."""
        blobify_file = tmp_path / ".blobify"
        blobify_file.write_text(
            """
[child:missing1,missing2,missing3]
+*.md
"""
        )

        with pytest.raises(ValueError, match="Parent context\\(s\\) not found: missing1, missing2, missing3"):
            read_blobify_config(tmp_path, "child", debug=True)

    def test_multiple_inheritance_order_preserved(self, tmp_path):
        """Test that multiple inheritance preserves the order of parents."""
        blobify_file = tmp_path / ".blobify"
        blobify_file.write_text(
            """
[first]
+first.py
@first-switch=true

[second]
+second.py
@second-switch=true

[third]
+third.py
@third-switch=true

[combined:first,second,third]
+combined.py
@combined-switch=true
"""
        )

        includes, excludes, switches, _ = read_blobify_config(tmp_path, "combined")

        # Should preserve parent order
        assert includes == ["first.py", "second.py", "third.py", "combined.py"]
        assert switches == ["first-switch=true", "second-switch=true", "third-switch=true", "combined-switch=true"]

    def test_multiple_inheritance_display_in_list(self, tmp_path, capsys):
        """Test that list_available_contexts shows multiple inheritance."""
        # Create git repo
        (tmp_path / ".git").mkdir()

        blobify_file = tmp_path / ".blobify"
        blobify_file.write_text(
            """
[base1]
+*.py

[base2]
+*.md

[combined:base1,base2]
+*.txt
"""
        )

        list_available_contexts(tmp_path)

        captured = capsys.readouterr()
        assert "combined (inherits from base1,base2)" in captured.out

    def test_multiple_inheritance_help_text(self, tmp_path, capsys):
        """Test that help text includes multiple inheritance examples."""
        # Create git repo
        (tmp_path / ".git").mkdir()

        # Create empty .blobify
        (tmp_path / ".blobify").write_text("")

        list_available_contexts(tmp_path)

        captured = capsys.readouterr()
        assert "Multiple inheritance:" in captured.out
        assert "[combined:base,docs]" in captured.out
        assert "# Inherits from both base and docs contexts" in captured.out

    def test_edge_case_empty_parent_list(self, tmp_path):
        """Test handling of malformed syntax with empty parent list."""
        blobify_file = tmp_path / ".blobify"
        blobify_file.write_text(
            """
[empty:]
+*.py

[empty_with_commas:,]
+*.md

[normal]
+*.txt
"""
        )

        # Should handle empty parent lists gracefully
        includes, excludes, switches, _ = read_blobify_config(tmp_path, "empty")
        assert includes == ["*.py"]

        includes, excludes, switches, _ = read_blobify_config(tmp_path, "empty_with_commas")
        assert includes == ["*.md"]

    def test_multiple_inheritance_integration_with_blobify(self, tmp_path):
        """Test multiple inheritance works with actual blobify file processing."""
        # Create git repo
        (tmp_path / ".git").mkdir()

        blobify_file = tmp_path / ".blobify"
        blobify_file.write_text(
            """
# Default excludes all
-**

[python:default]
+*.py

[docs:default]
+*.md

[combined:python,docs]
# Inherits exclusion and both file types
@show-excluded=false
"""
        )

        # Create test files
        (tmp_path / "app.py").write_text("print('app')")
        (tmp_path / "README.md").write_text("# README")
        (tmp_path / "config.xml").write_text("<config/>")

        output_file = tmp_path / "output.txt"
        with patch("sys.argv", ["bfy", str(tmp_path), "-x", "combined", "--output-filename", str(output_file)]):
            main()

        content = output_file.read_text(encoding="utf-8")

        # Should include Python and Markdown (from multiple inheritance)
        assert "print('app')" in content
        assert "# README" in content

        # Should exclude XML file (from inherited exclusion)
        assert "<config/>" not in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

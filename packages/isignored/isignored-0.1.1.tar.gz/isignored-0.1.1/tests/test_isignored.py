"""Tests for isignored module."""

import os
import tempfile
from pathlib import Path

import pytest

from isignored import is_ignored


class TestIsIgnored:
    """Test cases for the is_ignored function."""

    def test_no_ignore_file(self, tmp_path):
        """Test that files are not ignored when no ignore file exists."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        assert not is_ignored(test_file)

    def test_simple_gitignore_pattern(self, tmp_path):
        """Test basic gitignore pattern matching."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("*.log\n")
        
        log_file = tmp_path / "test.log"
        log_file.write_text("logs")
        
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("content")
        
        assert is_ignored(log_file)
        assert not is_ignored(txt_file)

    def test_directory_pattern(self, tmp_path):
        """Test directory-specific patterns."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("build/\n")
        
        build_dir = tmp_path / "build"
        build_dir.mkdir()
        
        build_file = build_dir / "output.txt"
        build_file.write_text("content")
        
        # Directory itself should be ignored
        assert is_ignored(build_dir)
        # Files inside ignored directory should be ignored
        assert is_ignored(build_file)

    def test_anchored_pattern(self, tmp_path):
        """Test patterns anchored to the root with leading slash."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("/root_only.txt\n")
        
        root_file = tmp_path / "root_only.txt"
        root_file.write_text("content")
        
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        nested_file = subdir / "root_only.txt"
        nested_file.write_text("content")
        
        assert is_ignored(root_file)
        assert not is_ignored(nested_file)

    def test_comments_and_empty_lines(self, tmp_path):
        """Test that comments and empty lines are ignored."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("""
# This is a comment
*.tmp

# Another comment
*.bak
""")
        
        tmp_file = tmp_path / "test.tmp"
        tmp_file.write_text("content")
        
        bak_file = tmp_path / "test.bak"
        bak_file.write_text("content")
        
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("content")
        
        assert is_ignored(tmp_file)
        assert is_ignored(bak_file)
        assert not is_ignored(txt_file)

    def test_nested_gitignore(self, tmp_path):
        """Test nested gitignore files."""
        # Root gitignore
        root_gitignore = tmp_path / ".gitignore"
        root_gitignore.write_text("*.log\n")
        
        # Nested directory with its own gitignore
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        sub_gitignore = subdir / ".gitignore"
        sub_gitignore.write_text("*.tmp\n")
        
        # Files to test
        root_log = tmp_path / "test.log"
        root_log.write_text("content")
        
        sub_log = subdir / "test.log"
        sub_log.write_text("content")
        
        sub_tmp = subdir / "test.tmp"
        sub_tmp.write_text("content")
        
        sub_txt = subdir / "test.txt"
        sub_txt.write_text("content")
        
        # Root pattern applies everywhere
        assert is_ignored(root_log)
        assert is_ignored(sub_log)
        
        # Subdirectory pattern applies in subdirectory
        assert is_ignored(sub_tmp)
        assert not is_ignored(sub_txt)

    def test_git_directory_always_ignored(self, tmp_path):
        """Test that .git directories are always ignored."""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        
        git_file = git_dir / "config"
        git_file.write_text("content")
        
        assert is_ignored(git_dir)
        assert is_ignored(git_file)

    def test_multiple_ignore_files(self, tmp_path):
        """Test using multiple ignore file types."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("*.log\n")
        
        dockerignore = tmp_path / ".dockerignore"
        dockerignore.write_text("*.tmp\n")
        
        log_file = tmp_path / "test.log"
        log_file.write_text("content")
        
        tmp_file = tmp_path / "test.tmp"
        tmp_file.write_text("content")
        
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("content")
        
        # Test with both ignore files
        assert is_ignored(log_file, [".gitignore", ".dockerignore"])
        assert is_ignored(tmp_file, [".gitignore", ".dockerignore"])
        assert not is_ignored(txt_file, [".gitignore", ".dockerignore"])
        
        # Test with only gitignore
        assert is_ignored(log_file, [".gitignore"])
        assert not is_ignored(tmp_file, [".gitignore"])

    def test_fnmatch_patterns(self, tmp_path):
        """Test fnmatch-style patterns."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("test[0-9].txt\nfile?.log\n")
        
        test1 = tmp_path / "test1.txt"
        test1.write_text("content")
        
        testa = tmp_path / "testa.txt"
        testa.write_text("content")
        
        file1_log = tmp_path / "file1.log"
        file1_log.write_text("content")
        
        file12_log = tmp_path / "file12.log"
        file12_log.write_text("content")
        
        assert is_ignored(test1)
        assert not is_ignored(testa)
        assert is_ignored(file1_log)
        assert not is_ignored(file12_log)

    def test_string_and_pathlike_inputs(self, tmp_path):
        """Test that both string and PathLike inputs work."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("*.log\n")
        
        log_file = tmp_path / "test.log"
        log_file.write_text("content")
        
        # Test with Path object
        assert is_ignored(log_file)
        
        # Test with string
        assert is_ignored(str(log_file))

    def test_relative_paths(self, tmp_path):
        """Test that relative paths work correctly."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            
            gitignore = Path(".gitignore")
            gitignore.write_text("*.log\n")
            
            log_file = Path("test.log")
            log_file.write_text("content")
            
            assert is_ignored("test.log")
            assert is_ignored(log_file)
            
        finally:
            os.chdir(original_cwd)

    def test_nonexistent_path(self, tmp_path):
        """Test behavior with nonexistent paths."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("*.log\n")
        
        nonexistent = tmp_path / "nonexistent.log"
        
        # Should still work based on the pattern
        assert is_ignored(nonexistent)

    def test_empty_ignore_files_list(self, tmp_path):
        """Test with empty ignore_files list."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("*.log\n")
        
        log_file = tmp_path / "test.log"
        log_file.write_text("content")
        
        # With empty list, nothing should be ignored
        assert not is_ignored(log_file, [])

    def test_pattern_caching(self, tmp_path):
        """Test that pattern loading is cached."""
        from isignored import _load_patterns
        
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("*.log\n")
        
        # Clear cache to ensure clean test
        _load_patterns.cache_clear()
        
        # First call
        patterns1 = _load_patterns(gitignore)
        
        # Second call should use cache
        patterns2 = _load_patterns(gitignore)
        
        assert patterns1 is patterns2  # Same object due to caching
        assert patterns1 == ("*.log",)

    def test_directory_vs_file_pattern(self, tmp_path):
        """Test directory patterns only match directories."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("temp/\n")
        
        # Create a directory named temp
        temp_dir = tmp_path / "temp"
        temp_dir.mkdir()
        
        # Directory should be ignored
        assert is_ignored(temp_dir)
        
        # Remove directory and create a file with same name
        temp_dir.rmdir()
        temp_file = tmp_path / "temp"
        temp_file.write_text("content")
        
        # File with same name should not be ignored (since pattern ends with /)
        assert not is_ignored(temp_file)

    def test_repository_boundary_respected(self, tmp_path):
        """Test that gitignore files outside a repository don't affect files inside."""
        from isignored import _load_patterns
        
        # Create a parent gitignore that ignores *.txt
        parent_gitignore = tmp_path / ".gitignore"
        parent_gitignore.write_text("*.txt\n")
        
        # Create a subdirectory that represents a git repository
        repo_dir = tmp_path / "my_repo"
        repo_dir.mkdir()
        
        # Create .git directory to mark repository boundary
        git_dir = repo_dir / ".git"
        git_dir.mkdir()
        
        # Create a .txt file inside the repository
        txt_file = repo_dir / "test.txt"
        txt_file.write_text("content")
        
        # The .txt file should NOT be ignored because the parent .gitignore
        # is outside the repository boundary (marked by .git directory)
        assert not is_ignored(txt_file)
        
        # But if we create a .gitignore inside the repository, it should work
        repo_gitignore = repo_dir / ".gitignore"
        repo_gitignore.write_text("*.log\n")
        
        # Clear cache to ensure the new .gitignore file is read
        _load_patterns.cache_clear()
        
        log_file = repo_dir / "test.log"
        log_file.write_text("content")
        
        # This should be ignored by the repository's own .gitignore
        assert is_ignored(log_file)
        
        # But the .txt file should still not be ignored
        assert not is_ignored(txt_file)
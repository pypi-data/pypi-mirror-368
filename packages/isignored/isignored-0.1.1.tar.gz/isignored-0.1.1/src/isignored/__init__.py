"""
Utility for checking whether a path is ignored by one or more *ignore* files
(e.g. .gitignore, .dockerignore).

Public API
----------
is_ignored(path: str | Path, ignore_files: list[str] = [".gitignore"]) -> bool
"""

from __future__ import annotations

import fnmatch
import os
from functools import lru_cache
from pathlib import Path
from typing import Iterable, List

__version__ = "0.1.1"
__all__ = ["is_ignored"]


# --------------------------------------------------------------------------- #
# Helper utilities
# --------------------------------------------------------------------------- #
@lru_cache(maxsize=None)
def _load_patterns(ignore_file: Path) -> tuple[str, ...]:
    """
    Load and cache ignore-patterns from an ignore file.

    Empty lines and comments (# …) are skipped. The patterns are returned as a
    *tuple* so that the result is hashable and can be cached by @lru_cache.
    """
    if not ignore_file.is_file():
        return ()

    with ignore_file.open(encoding="utf-8") as f:
        patterns = tuple(
            line.strip()
            for line in f
            if line.strip() and not line.lstrip().startswith("#")
        )
    return patterns


def _iter_parent_dirs(start: Path) -> Iterable[Path]:
    """
    Yield *start* and every parent directory up to the filesystem root or 
    until we encounter a .git directory (which marks the repository boundary).
    
    The directory containing .git is yielded (so its ignore files are processed),
    but we don't go beyond it to avoid processing ignore files from outside
    the current repository.
    """
    current = start
    while True:
        yield current
        
        # Stop if we've reached the filesystem root
        if current.parent == current:
            break
            
        # Stop if current directory contains .git (repository boundary)
        # but only AFTER yielding the current directory
        if (current / ".git").exists():
            break
            
        current = current.parent


def _collect_patterns(path: Path, ignore_files: List[str]) -> List[tuple[Path, str]]:
    """
    Collect all patterns from every ignore-file encountered between *path*'s
    directory and the filesystem root.

    Returns a list of *(base_dir, pattern)* where *base_dir* is the directory
    that contained the ignore-file the pattern came from.  This is useful
    because git-style patterns are evaluated relative to the directory that
    defines them.
    """
    collected: List[tuple[Path, str]] = []

    for directory in _iter_parent_dirs(path if path.is_dir() else path.parent):
        for ignore_name in ignore_files:
            ignore_file = directory / ignore_name
            for pattern in _load_patterns(ignore_file):
                collected.append((directory, pattern))

    return collected


def _match_pattern(
    path: Path,
    base_dir: Path,
    pattern: str,
) -> bool:
    """
    Very small subset of gitignore matching sufficient for typical scripting:

    *   A bare name ("foo.txt") matches anywhere below *base_dir*.
    *   A pattern starting with "/" is anchored to *base_dir*.
    *   A pattern ending with "/" only matches directories.
    *   "*", "?", "[abc]" obey standard `fnmatch` semantics.
    *   Anything inside a ".git" directory is always ignored.
    """
    # Path relative to the directory that owns the pattern
    rel_posix = path.relative_to(base_dir).as_posix()

    is_dir_pat = pattern.endswith("/")
    pat = pattern.rstrip("/")

    # Handle anchoring: leading "/" means "from exactly this level".
    if pat.startswith("/"):
        pat = pat.lstrip("/")
        # For anchored patterns, only test exact match
        if fnmatch.fnmatch(rel_posix, pat):
            if is_dir_pat and not path.is_dir():
                return False
            return True
    else:
        # For non-anchored patterns, test both direct match and with **/ prefix
        # This handles files in the same directory and nested directories
        if fnmatch.fnmatch(rel_posix, pat):
            if is_dir_pat and not path.is_dir():
                return False
            return True
        
        # Also try with **/ prefix for nested matches
        nested_pat = f"**/{pat}"
        if fnmatch.fnmatch(rel_posix, nested_pat):
            if is_dir_pat and not path.is_dir():
                return False
            return True

    return False


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def is_ignored(path: str | os.PathLike, ignore_files: List[str] | None = None) -> bool:
    """
    Return ``True`` if *path* is ignored by **any** pattern in any of the given
    *ignore_files* (searched in *path*'s directory upward).

    Parameters
    ----------
    path
        File or directory to test (absolute or relative).
    ignore_files
        List of ignore-file names to search for.  Defaults to
        ``[".gitignore"]`` but may include additional entries such as
        ``".dockerignore"``.  Order is irrelevant.

    Notes
    -----
    The implementation intentionally provides *approximate* gitignore semantics
    sufficient for typical automation tasks.  For full compliance consider
    shelling out to `git check-ignore` or using a dedicated library.
    """
    ignore_files = ignore_files if ignore_files is not None else [".gitignore"]

    path = Path(path).resolve()
    
    # Short-circuit: never touch the repo metadata itself
    if ".git" in path.parts:
        return True

    # First, check if the path itself matches any pattern
    for base_dir, pattern in _collect_patterns(path, ignore_files):
        if _match_pattern(path, base_dir, pattern):
            return True
    
    # Then, check if any parent directory is ignored (for files inside ignored dirs)
    if not path.is_dir():
        current = path.parent
        while current != current.parent:
            for base_dir, pattern in _collect_patterns(current, ignore_files):
                if _match_pattern(current, base_dir, pattern):
                    return True
            current = current.parent

    return False

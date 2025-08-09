from __future__ import annotations

import fnmatch
import pathlib
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Set


DEFAULT_IGNORES = {
    ".git",
    ".DS_Store",
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".pytest_cache",
    ".coverage",
    "htmlcov",
    ".tox",
    ".venv",
    "venv",
    "node_modules",
    ".next",
    ".nuxt",
    "dist",
    "build",
    ".env",
}


def _normalize_path(s: str) -> str:
    return s.replace("\\", "/").strip("/")


@dataclass
class IgnoreMatcher:
    root: pathlib.Path
    patterns: List[str]

    def should_ignore(self, path: pathlib.Path) -> bool:
        rel = _normalize_path(str(path.relative_to(self.root)))
        for pattern in self.patterns:
            if _match_gitignore_like(rel, pattern):
                return True
        return False


def _match_gitignore_like(rel_path: str, pattern: str) -> bool:
    pattern = _normalize_path(pattern)

    if pattern.endswith("/"):
        pattern = pattern[:-1]
        return rel_path == pattern or rel_path.startswith(pattern + "/")

    if "/" in pattern and "*" not in pattern:
        return rel_path == pattern or rel_path.startswith(pattern + "/")

    if "*" in pattern:
        parts = rel_path.split("/")
        for part in parts:
            if fnmatch.fnmatch(part, pattern):
                return True
        if fnmatch.fnmatch(rel_path, pattern):
            return True
        return False

    parts = rel_path.split("/")
    return pattern in parts or rel_path == pattern


def load_gitignore_patterns(root: pathlib.Path) -> List[str]:
    patterns: List[str] = []
    gitignore = root / ".gitignore"
    if gitignore.exists():
        for line in gitignore.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("/"):
                line = line[1:]
            patterns.append(line)
    return patterns


def load_prjtree_ignore(root: pathlib.Path) -> List[str]:
    patterns: List[str] = []
    for name in [".prjtreeignore", "prjtree.ignore"]:
        p = root / name
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("/"):
                    line = line[1:]
                patterns.append(line)
    return patterns


def load_composite_ignores(
    root: pathlib.Path,
    *,
    respect_gitignore: bool = True,
    extra_patterns: Optional[Sequence[str]] = None,
) -> IgnoreMatcher:
    patterns: List[str] = []
    patterns.extend(sorted(DEFAULT_IGNORES))
    if respect_gitignore:
        patterns.extend(load_gitignore_patterns(root))
    patterns.extend(load_prjtree_ignore(root))
    if extra_patterns:
        patterns.extend(list(extra_patterns))
    return IgnoreMatcher(root=root, patterns=patterns)



from __future__ import annotations

import dataclasses
import fnmatch
import html
import json
import mimetypes
import os
import pathlib
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List, Optional, Sequence, Set, Tuple

from .ignore import IgnoreMatcher, load_composite_ignores
from .utils import (
    detect_project_root,
    is_probably_text_file,
    read_text_safely,
    format_size,
)


@dataclass
class GenerateOptions:
    root_path: Optional[str] = None
    detect_git_root: bool = True
    respect_gitignore: bool = True
    extra_ignore: Optional[Sequence[str]] = None
    tree_include: Optional[Sequence[str]] = None
    tree_exclude: Optional[Sequence[str]] = None
    content_include: Optional[Sequence[str]] = None
    content_exclude: Optional[Sequence[str]] = None
    max_file_chars: Optional[int] = None
    title: str = "Структура проекта"
    renderer: str = "html"  # html | md | json | ascii
    output_file: Optional[str] = None


@dataclass
class FileEntry:
    abs_path: pathlib.Path
    rel_path: str
    size_bytes: int
    show_content: bool


@dataclass
class Stats:
    files: int = 0
    dirs: int = 0
    total_size: int = 0


@dataclass
class ScanResult:
    root: pathlib.Path
    tree_lines: List[str]
    files_to_render: List[FileEntry]
    stats: Stats
    options: GenerateOptions


class Scanner:
    def __init__(self, options: GenerateOptions):
        self.options = options
        self.root = detect_project_root(options.root_path, options.detect_git_root)
        ignore_matcher = load_composite_ignores(
            self.root,
            respect_gitignore=options.respect_gitignore,
            extra_patterns=list(options.extra_ignore or []),
        )
        self.ignore = ignore_matcher
        self.tree_include = list(options.tree_include or []) or None
        self.tree_exclude = list(options.tree_exclude or []) or None
        self.content_include = list(options.content_include or []) or []
        self.content_exclude = list(options.content_exclude or []) or []

    def _pattern_match(self, rel_path: str, pattern: str) -> bool:
        if "/" in pattern and "*" not in pattern:
            folder = pattern.rstrip("/")
            return rel_path.startswith(folder + "/") or rel_path == folder
        if "*" in pattern:
            return fnmatch.fnmatch(rel_path, pattern)
        base_name = rel_path.split("/")[-1]
        return pattern in {rel_path, base_name}

    def _include_dir(self, path: pathlib.Path) -> bool:
        rel = str(path.relative_to(self.root)).replace("\\", "/")
        if self.tree_include and not any(self._pattern_match(rel, p) for p in self.tree_include):
            return False
        if self.tree_exclude and any(self._pattern_match(rel, p) for p in self.tree_exclude):
            return False
        return True

    def _include_file_in_tree(self, path: pathlib.Path) -> bool:
        rel = str(path.relative_to(self.root)).replace("\\", "/")
        if self.tree_include and not any(self._pattern_match(rel, p) for p in self.tree_include):
            return False
        if self.tree_exclude and any(self._pattern_match(rel, p) for p in self.tree_exclude):
            return False
        return True

    def _include_file_content(self, path: pathlib.Path) -> bool:
        if not self.content_include:
            return False
        rel = str(path.relative_to(self.root)).replace("\\", "/")
        name = path.name
        ext = path.suffix
        # exclude wins
        for p in self.content_exclude:
            if "/" in p and "*" not in p:
                folder = p.rstrip("/")
                if rel.startswith(folder + "/") or rel == folder:
                    return False
            if "*" in p:
                if fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(name, p):
                    return False
            if p == rel or p == name or (ext and p == ext):
                return False
        for p in self.content_include:
            if p == rel or p == name or (ext and p == ext):
                return True
        for p in self.content_include:
            if "/" in p and "*" not in p:
                folder = p.rstrip("/")
                if rel.startswith(folder + "/") or rel == folder:
                    return True
            if "*" in p:
                if fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(name, p):
                    return True
        return False

    def scan(self) -> ScanResult:
        tree_lines: List[str] = []
        files_to_render: List[FileEntry] = []
        stats = Stats()

        def walk(dir_path: pathlib.Path, level: int, parent_prefix: str):
            try:
                entries = sorted(dir_path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
                entries = [e for e in entries if not self.ignore.should_ignore(e)]
            except Exception as e:
                tree_lines.append(f"{parent_prefix}❌ Ошибка доступа к {dir_path.name}: {e}")
                return

            for i, item in enumerate(entries):
                is_last = i == len(entries) - 1
                prefix = "" if level == 0 else parent_prefix + ("└── " if is_last else "├── ")
                next_prefix = "" if level == 0 else parent_prefix + ("    " if is_last else "│   ")

                if item.is_dir():
                    if not self._include_dir(item):
                        continue
                    stats.dirs += 1
                    tree_lines.append(f"{prefix}📁 {item.name}/")
                    walk(item, level + 1, next_prefix)
                else:
                    # always count in stats even if not shown in tree
                    try:
                        size = item.stat().st_size
                        stats.total_size += size
                        stats.files += 1
                    except Exception:
                        size = 0
                    if not self._include_file_in_tree(item):
                        continue
                    rel = str(item.relative_to(self.root)).replace("\\", "/")
                    size_str = format_size(size)
                    highlighted = self._include_file_content(item)
                    icon = "⭐" if highlighted else "📄"
                    tree_lines.append(f"{prefix}{icon} {item.name} ({size_str})")
                    if highlighted:
                        files_to_render.append(
                            FileEntry(abs_path=item, rel_path=rel, size_bytes=size, show_content=True)
                        )

        walk(self.root, 0, "")

        return ScanResult(
            root=self.root,
            tree_lines=tree_lines,
            files_to_render=files_to_render,
            stats=stats,
            options=self.options,
        )


def render(result: ScanResult) -> str:
    renderer = (result.options.renderer or "html").lower()
    if renderer == "html":
        from .render_html import render_html

        return render_html(result)
    if renderer == "md" or renderer == "markdown":
        from .render_md import render_markdown

        return render_markdown(result)
    if renderer == "json":
        from .render_json import render_json

        return render_json(result)
    if renderer == "ascii":
        from .render_ascii import render_ascii

        return render_ascii(result)
    raise ValueError(f"Unknown renderer: {renderer}")


def generate(options: GenerateOptions) -> str:
    scanner = Scanner(options)
    result = scanner.scan()
    return render(result)



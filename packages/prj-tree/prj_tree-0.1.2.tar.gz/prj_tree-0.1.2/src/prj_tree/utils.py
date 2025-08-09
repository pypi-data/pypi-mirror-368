from __future__ import annotations

import html
import mimetypes
import os
import pathlib
from typing import Optional


def detect_project_root(root_path: Optional[str], detect_git_root: bool) -> pathlib.Path:
    if root_path:
        return pathlib.Path(root_path).resolve()
    cwd = pathlib.Path(os.getcwd()).resolve()
    if detect_git_root:
        for p in [cwd] + list(cwd.parents):
            if (p / ".git").exists():
                return p
    return cwd


def is_probably_text_file(path: pathlib.Path) -> bool:
    text_ext = {
        ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".scss", ".sass",
        ".json", ".xml", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
        ".md", ".txt", ".log", ".sql", ".sh", ".bash", ".zsh", ".fish",
        ".dockerfile", ".gitignore", ".gitattributes", ".editorconfig",
        ".eslintrc", ".prettierrc", ".babelrc", ".env.example", ".env.local",
        ".vue", ".svelte", ".php", ".rb", ".go", ".rs", ".java", ".kt",
        ".swift", ".c", ".cpp", ".h", ".hpp", ".cs", ".fs", ".vb", ".r",
        ".m", ".mm", ".pl", ".pm", ".tcl", ".lua", ".scala", ".clj",
        ".hs", ".ml", ".fsi", ".fsscript", ".dart", ".elm", ".ex", ".exs",
        ".erl", ".hrl", ".cl", ".lisp", ".scm", ".rkt", ".jl", ".nim",
        ".zig", ".v", ".sv", ".vhd", ".vhdl", ".asm", ".s", ".S"
    }
    if path.suffix.lower() in text_ext:
        return True
    mime_type, _ = mimetypes.guess_type(str(path))
    if mime_type and mime_type.startswith("text/"):
        return True
    try:
        with open(path, "rb") as f:
            chunk = f.read(1024)
            if b"\x00" in chunk:
                return False
            return all(b <= 127 for b in chunk)
    except Exception:
        return False


def _read_text_internal(path: pathlib.Path, max_chars: Optional[int]) -> Optional[str]:
    if not is_probably_text_file(path):
        return None
    encodings = ["utf-8", "latin-1", "cp1251", "iso-8859-1", "utf-16"]
    for enc in encodings:
        try:
            with open(path, "r", encoding=enc) as f:
                content = f.read()
                if max_chars is not None and len(content) > max_chars:
                    content = content[:max_chars] + "\n\n... (содержимое обрезано)"
                return content
        except UnicodeDecodeError:
            continue
        except Exception:
            continue
    return None


def read_text_safely(path: pathlib.Path, max_chars: Optional[int]) -> str:
    content = _read_text_internal(path, max_chars)
    if content is None:
        return f"[Бинарный файл: {path.suffix or 'без расширения'}]"
    return html.escape(content)


def read_text_raw_safely(path: pathlib.Path, max_chars: Optional[int]) -> str:
    content = _read_text_internal(path, max_chars)
    if content is None:
        return f"[Бинарный файл: {path.suffix or 'без расширения'}]"
    return content


def format_size(size_bytes: int) -> str:
    if size_bytes <= 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB"]
    i = 0
    size = float(size_bytes)
    while size >= 1024 and i < len(units) - 1:
        size /= 1024.0
        i += 1
    return f"{size:.1f} {units[i]}"


def get_prism_language_class(path: pathlib.Path) -> str:
    ext = path.suffix.lower()
    mapping = {
        ".py": "language-python",
        ".js": "language-javascript",
        ".ts": "language-typescript",
        ".jsx": "language-jsx",
        ".tsx": "language-tsx",
        ".html": "language-html",
        ".css": "language-css",
        ".scss": "language-scss",
        ".sass": "language-sass",
        ".json": "language-json",
        ".xml": "language-xml",
        ".yaml": "language-yaml",
        ".yml": "language-yaml",
        ".toml": "language-toml",
        ".ini": "language-ini",
        ".cfg": "language-ini",
        ".conf": "language-ini",
        ".md": "language-markdown",
        ".txt": "language-markup",
        ".log": "language-markup",
        ".sql": "language-sql",
        ".sh": "language-bash",
        ".bash": "language-bash",
        ".zsh": "language-bash",
        ".vue": "language-markup",
        ".svelte": "language-markup",
        ".php": "language-php",
        ".rb": "language-ruby",
        ".go": "language-go",
        ".rs": "language-rust",
        ".java": "language-java",
        ".kt": "language-kotlin",
        ".swift": "language-swift",
        ".c": "language-c",
        ".cpp": "language-cpp",
        ".h": "language-c",
        ".hpp": "language-cpp",
        ".cs": "language-csharp",
        ".dart": "language-dart",
        ".lua": "language-lua",
        ".zig": "language-zig",
    }
    return mapping.get(ext, "language-")



from __future__ import annotations

from .core import ScanResult
from .utils import read_text_safely, format_size


def render_ascii(result: ScanResult) -> str:
    lines = []
    lines.append(f"Root: {result.root}")
    lines.append("Tree:")
    lines.extend(result.tree_lines)
    lines.append(
        f"Stats: dirs={result.stats.dirs} files={result.stats.files} size={format_size(result.stats.total_size)}"
    )
    if result.files_to_render:
        lines.append("Files:")
        for f in result.files_to_render:
            lines.append(f"- {f.rel_path} ({format_size(f.size_bytes)})")
            lines.append(read_text_safely(f.abs_path, max_chars=result.options.max_file_chars))
    return "\n".join(lines)



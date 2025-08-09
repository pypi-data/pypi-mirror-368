from __future__ import annotations

import json
from .core import ScanResult
from .utils import format_size, read_text_safely


def render_json(result: ScanResult) -> str:
    obj = {
        "root": str(result.root),
        "options": {
            "title": result.options.title,
            "content_include": list(result.options.content_include or []),
            "tree_include": list(result.options.tree_include or []),
            "tree_exclude": list(result.options.tree_exclude or []),
            "max_file_chars": result.options.max_file_chars,
        },
        "stats": {
            "dirs": result.stats.dirs,
            "files": result.stats.files,
            "total_size_bytes": result.stats.total_size,
            "total_size_human": format_size(result.stats.total_size),
        },
        "tree": result.tree_lines,
        "files": [
            {
                "path": f.rel_path,
                "size_bytes": f.size_bytes,
                "size_human": format_size(f.size_bytes),
                "content": read_text_safely(f.abs_path, max_chars=result.options.max_file_chars),
            }
            for f in result.files_to_render
        ],
    }
    return json.dumps(obj, ensure_ascii=False, indent=2)



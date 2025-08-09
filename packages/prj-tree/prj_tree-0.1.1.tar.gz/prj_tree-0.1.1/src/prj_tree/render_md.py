from __future__ import annotations

import html
from datetime import datetime

from .core import ScanResult
from .utils import read_text_raw_safely, format_size


def render_markdown(result: ScanResult) -> str:
    lines = []
    lines.append(f"# {result.options.title}")
    lines.append("")
    lines.append(f"- **Корень**: `{result.root}`")
    lines.append(f"- **Дата**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if result.options.tree_include:
        lines.append(f"- **Tree include**: {', '.join(result.options.tree_include)}")
    if result.options.tree_exclude:
        lines.append(f"- **Tree exclude**: {', '.join(result.options.tree_exclude)}")
    if result.options.content_include:
        lines.append(f"- **Content include**: {', '.join(result.options.content_include)}")
    lines.append("")

    lines.append("## Дерево")
    lines.append("")
    lines.append("```text")
    lines.extend(result.tree_lines)
    lines.append("```")
    lines.append("")

    lines.append("## Статистика")
    lines.append("")
    lines.append(
        f"Папок: {result.stats.dirs} · Файлов: {result.stats.files} · Размер: {format_size(result.stats.total_size)}"
    )
    lines.append("")

    if result.files_to_render:
        lines.append("## Содержимое файлов")
        lines.append("")
        for f in result.files_to_render:
            lines.append(f"### {f.rel_path} ({format_size(f.size_bytes)})")
            lines.append("")
            content = read_text_raw_safely(f.abs_path, max_chars=result.options.max_file_chars)
            # язык не указываем — GitHub подсветит по расширению, иначе можно добавить тройной код с языком
            lines.append("```")
            lines.append(content)
            lines.append("```")
            lines.append("")

    return "\n".join(lines)



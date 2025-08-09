from __future__ import annotations

import html
from datetime import datetime

from .core import ScanResult
from .utils import read_text_safely, format_size, get_prism_language_class


def render_html(result: ScanResult) -> str:
    parts = []
    parts.append("""<!DOCTYPE html>
<html lang=\"ru\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
""")
    parts.append("  <title>" + html.escape(result.options.title) + "</title>")
    parts.append(
        """
  <link href=\"https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism.min.css\" rel=\"stylesheet\" />
  <link href=\"https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css\" rel=\"stylesheet\" />
  <style>
    body { font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, 'Helvetica Neue', Arial, 'Noto Sans', 'Apple Color Emoji', 'Segoe UI Emoji'; background: #f5f7fb; margin: 0; }
    .container { max-width: 1200px; margin: 0 auto; padding: 24px; }
    .card { background: #fff; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); margin-bottom: 20px; overflow: hidden; }
    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; padding: 18px 20px; }
    .title { font-size: 20px; margin: 0; }
    .meta { padding: 12px 20px; color: #556; font-size: 14px; border-bottom: 1px solid #eef1f5; }
    .section-title { font-weight: 600; font-size: 16px; margin: 16px 0 8px; color: #334; }
    .tree { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace; background: #fafbff; padding: 16px; white-space: pre; overflow-x: auto; border-top: 1px solid #eef1f5; }
    .stats { padding: 16px 20px; border-top: 1px solid #eef1f5; color: #334; }
    .index { padding: 16px 20px; border-top: 1px solid #eef1f5; }
    .index a { color: #2563eb; text-decoration: none; }
    .file { padding: 0 20px 20px; }
    .file-header { font-weight: 600; margin: 20px 0 8px; padding: 10px 12px; background: #f2f5ff; border-left: 4px solid #6475f3; border-radius: 6px; }
    pre { margin: 0; }
  </style>
</head>
<body>
  <div class=\"container\">"""
    )

    parts.append("<div class=\"card\">")
    parts.append("  <div class=\"header\"><h1 class=\"title\">🌳 " + html.escape(result.options.title) + "</h1></div>")
    parts.append(
        "  <div class=\"meta\">" 
        f"<div><strong>Корень:</strong> {html.escape(str(result.root))}</div>"
        f"<div><strong>Дата:</strong> {html.escape(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}</div>"
        + (f"<div><strong>Content include:</strong> {', '.join(result.options.content_include or [])}</div>" if result.options.content_include else "")
        + (f"<div><strong>Tree include:</strong> {', '.join(result.options.tree_include or [])}</div>" if result.options.tree_include else "")
        + (f"<div><strong>Tree exclude:</strong> {', '.join(result.options.tree_exclude or [])}</div>" if result.options.tree_exclude else "")
        + "  </div>"
    )

    parts.append("  <div class=\"section-title\">Структура</div>")
    parts.append("  <div class=\"tree\">")
    parts.append("\n".join(result.tree_lines))
    parts.append("  </div>")

    parts.append("  <div class=\"stats\">")
    parts.append(
        f"Папок: {result.stats.dirs} · Файлов: {result.stats.files} · Размер: {format_size(result.stats.total_size)}"
    )
    parts.append("  </div>")
    parts.append("</div>")

    if result.files_to_render:
        parts.append("<div class=\"card\">")
        parts.append("  <div class=\"header\"><h2 class=\"title\">💻 Содержимое файлов</h2></div>")
        parts.append("  <div class=\"index\">")
        for i, f in enumerate(result.files_to_render):
            parts.append(
                f"<div><a href=\"#f{i}\">📄 {html.escape(f.rel_path)} ({format_size(f.size_bytes)})</a></div>"
            )
        parts.append("  </div>")

        for i, f in enumerate(result.files_to_render):
            parts.append("  <div class=\"file\" id=\"f{}\">".format(i))
            parts.append(
                f"    <div class=\"file-header\">📄 {html.escape(f.rel_path)} ({format_size(f.size_bytes)})</div>"
            )
            content = read_text_safely(f.abs_path, max_chars=result.options.max_file_chars)
            lang_class = get_prism_language_class(f.abs_path)
            parts.append("    <pre><code class=\"" + lang_class + "\">" + content + "</code></pre>")
            parts.append("  </div>")
        parts.append("</div>")

    parts.append(
        """
  </div>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-core.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>
</body>
</html>
"""
    )
    return "\n".join(parts)



import os
import pathlib
from typing import List, Set, Optional, Iterable
import mimetypes
import html
import fnmatch
import argparse
from datetime import datetime


class ProjectTreeGenerator:
    """Генератор HTML-отчёта по структуре проекта.

    Принципы:
    - По умолчанию строится полная структура проекта (только дерево, без содержимого файлов).
    - Содержимое файлов включается ТОЛЬКО для файлов, которые не попали в игнор и явно подходят под `content_include`.
    - Есть include/exclude для дерева и отдельный include для содержимого.

    Программный API: см. `generate_project_tree()`.
    CLI: см. функцию `cli()`.
    """

    def __init__(
        self,
        root_path: Optional[str] = None,
        *,
        detect_git_root: bool = True,
        respect_gitignore: bool = True,
        extra_ignore: Optional[Iterable[str]] = None,
        tree_include: Optional[Iterable[str]] = None,
        tree_exclude: Optional[Iterable[str]] = None,
        content_include: Optional[Iterable[str]] = None,
        max_file_chars: int = 10000,
        title: str = "Структура проекта",
    ):
        # Определяем корень проекта
        self.root_path = self._resolve_root_path(root_path, detect_git_root)

        # Игнор
        self.respect_gitignore = respect_gitignore
        self.ignored_patterns = self._load_gitignore() if respect_gitignore else set()
        if extra_ignore:
            self.ignored_patterns.update(list(extra_ignore))

        # Фильтры
        self.tree_include = list(tree_include) if tree_include else None
        self.tree_exclude = list(tree_exclude) if tree_exclude else None
        self.content_include = list(content_include) if content_include else []  # пусто => содержимое не выводим

        # Параметры вывода
        self.max_file_chars = max_file_chars
        self.title = title

        # Буферы
        self.html_content: List[str] = []
        self.files_list: List[dict] = []

    def _resolve_root_path(self, root_path: Optional[str], detect_git_root: bool) -> pathlib.Path:
        if root_path:
            return pathlib.Path(root_path).resolve()
        cwd = pathlib.Path(os.getcwd()).resolve()
        if detect_git_root:
            for p in [cwd] + list(cwd.parents):
                if (p / ".git").exists():
                    return p
        return cwd

    def _load_gitignore(self) -> Set[str]:
        """Загружает паттерны из .gitignore и добавляет базовые."""
        gitignore_path = self.root_path / ".gitignore"
        ignored: Set[str] = set()

        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if line.startswith('/'):
                            line = line[1:]
                        ignored.add(line)

        add_ignored_patterns = [
            'poetry.lock',
            'ARCHITECTURE_AUDIT.md',
        ]

        ignored.update([
            '.git', '.DS_Store', '__pycache__', '*.pyc', '*.pyo', '*.pyd',
            '.pytest_cache', '.coverage', 'htmlcov', '.tox', '.venv', 'venv',
            'node_modules', '.next', '.nuxt', 'dist', 'build', '.env', '*.md'
        ])
        ignored.update(add_ignored_patterns)
        return ignored

    def _matches_gitignore_pattern(self, path: str, pattern: str) -> bool:
        """Проверяет соответствие пути паттерну .gitignore"""
        path = path.replace('\\', '/')
        pattern = pattern.replace('\\', '/')

        if pattern.endswith('/'):
            pattern = pattern[:-1]
            if path.startswith(pattern + '/') or path == pattern:
                return True
            return False

        if '/' in pattern:
            if path == pattern or path.startswith(pattern + '/'):
                return True
            return False

        if '*' in pattern:
            parts = path.split('/')
            for part in parts:
                if fnmatch.fnmatch(part, pattern):
                    return True
            return False

        parts = path.split('/')
        return pattern in parts

    def _should_ignore(self, path: pathlib.Path) -> bool:
        """Проверяет, должен ли файл/папка быть проигнорирован"""
        if not self.ignored_patterns:
            return False
        rel_path = path.relative_to(self.root_path)
        rel_path_str = str(rel_path).replace('\\', '/')
        if rel_path_str in self.ignored_patterns:
            return True
        for pattern in self.ignored_patterns:
            if self._matches_gitignore_pattern(rel_path_str, pattern):
                return True
        return False

    def _pattern_match(self, rel_path: str, pattern: str) -> bool:
        if '/' in pattern and '*' not in pattern:
            folder = pattern.rstrip('/')
            return rel_path.startswith(folder + '/') or rel_path == folder
        if '*' in pattern:
            return fnmatch.fnmatch(rel_path, pattern)
        base_name = rel_path.split('/')[-1]
        return pattern in {rel_path, base_name}

    def _should_include_directory_in_tree(self, dir_path: pathlib.Path) -> bool:
        """Фильтрация папок для дерева."""
        rel = str(dir_path.relative_to(self.root_path)).replace('\\', '/')
        if self.tree_include:
            if not any(self._pattern_match(rel, p) for p in self.tree_include):
                return False
        if self.tree_exclude:
            if any(self._pattern_match(rel, p) for p in self.tree_exclude):
                return False
        return True

    def _should_include_file_in_tree(self, file_path: pathlib.Path) -> bool:
        """Фильтрация файлов для дерева (не про содержимое)."""
        rel = str(file_path.relative_to(self.root_path)).replace('\\', '/')
        if self.tree_include:
            if not any(self._pattern_match(rel, p) for p in self.tree_include):
                return False
        if self.tree_exclude:
            if any(self._pattern_match(rel, p) for p in self.tree_exclude):
                return False
        return True

    def _should_include_file_for_code(self, file_path: pathlib.Path) -> bool:
        """Решает, нужно ли показать содержимое файла.
        Только если список content_include не пуст и файл не проигнорирован.
        """
        if not self.content_include:
            return False
        rel_path = str(file_path.relative_to(self.root_path)).replace('\\', '/')
        file_name = file_path.name
        file_ext = file_path.suffix

        for pattern in self.content_include:
            if pattern == rel_path or pattern == file_name or (file_ext and pattern == file_ext):
                return True
        for pattern in self.content_include:
            if '/' in pattern and '*' not in pattern:
                folder = pattern.rstrip('/')
                if rel_path.startswith(folder + '/') or rel_path == folder:
                    return True
            if '*' in pattern:
                if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(file_name, pattern):
                    return True
        return False

    def _get_language_class(self, file_path: pathlib.Path) -> str:
        extension = file_path.suffix.lower()
        language_map = {
            '.py': 'language-python',
            '.js': 'language-javascript',
            '.ts': 'language-typescript',
            '.jsx': 'language-jsx',
            '.tsx': 'language-tsx',
            '.html': 'language-html',
            '.css': 'language-css',
            '.scss': 'language-scss',
            '.sass': 'language-sass',
            '.json': 'language-json',
            '.xml': 'language-xml',
            '.yaml': 'language-yaml',
            '.yml': 'language-yaml',
            '.toml': 'language-toml',
            '.ini': 'language-ini',
            '.cfg': 'language-ini',
            '.conf': 'language-ini',
            '.md': 'language-markdown',
            '.txt': 'language-text',
            '.log': 'language-text',
            '.sql': 'language-sql',
            '.sh': 'language-bash',
            '.bash': 'language-bash',
            '.zsh': 'language-bash',
            '.fish': 'language-bash',
            '.dockerfile': 'language-docker',
            '.gitignore': 'language-git',
            '.gitattributes': 'language-git',
            '.editorconfig': 'language-ini',
            '.eslintrc': 'language-json',
            '.prettierrc': 'language-json',
            '.babelrc': 'language-json',
            '.env.example': 'language-env',
            '.env.local': 'language-env',
            '.vue': 'language-vue',
            '.svelte': 'language-svelte',
            '.php': 'language-php',
            '.rb': 'language-ruby',
            '.go': 'language-go',
            '.rs': 'language-rust',
            '.java': 'language-java',
            '.kt': 'language-kotlin',
            '.swift': 'language-swift',
            '.c': 'language-c',
            '.cpp': 'language-cpp',
            '.h': 'language-c',
            '.hpp': 'language-cpp',
            '.cs': 'language-csharp',
            '.fs': 'language-fsharp',
            '.vb': 'language-vbnet',
            '.r': 'language-r',
            '.m': 'language-objectivec',
            '.mm': 'language-objectivec',
            '.pl': 'language-perl',
            '.pm': 'language-perl',
            '.tcl': 'language-tcl',
            '.lua': 'language-lua',
            '.scala': 'language-scala',
            '.clj': 'language-clojure',
            '.hs': 'language-haskell',
            '.ml': 'language-ocaml',
            '.fsi': 'language-fsharp',
            '.fsscript': 'language-fsharp',
            '.dart': 'language-dart',
            '.elm': 'language-elm',
            '.ex': 'language-elixir',
            '.exs': 'language-elixir',
            '.erl': 'language-erlang',
            '.hrl': 'language-erlang',
            '.cl': 'language-common-lisp',
            '.lisp': 'language-common-lisp',
            '.scm': 'language-scheme',
            '.rkt': 'language-racket',
            '.jl': 'language-julia',
            '.nim': 'language-nim',
            '.zig': 'language-zig',
            '.v': 'language-verilog',
            '.sv': 'language-systemverilog',
            '.vhd': 'language-vhdl',
            '.vhdl': 'language-vhdl',
            '.asm': 'language-assembly',
            '.s': 'language-assembly',
            '.S': 'language-assembly',
        }
        return language_map.get(extension, 'language-text')

    def _is_text_file(self, file_path: pathlib.Path) -> bool:
        text_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss', '.sass',
            '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
            '.md', '.txt', '.log', '.sql', '.sh', '.bash', '.zsh', '.fish',
            '.dockerfile', '.gitignore', '.gitattributes', '.editorconfig',
            '.eslintrc', '.prettierrc', '.babelrc', '.env.example', '.env.local',
            '.vue', '.svelte', '.php', '.rb', '.go', '.rs', '.java', '.kt',
            '.swift', '.c', '.cpp', '.h', '.hpp', '.cs', '.fs', '.vb', '.r',
            '.m', '.mm', '.pl', '.pm', '.tcl', '.lua', '.scala', '.clj',
            '.hs', '.ml', '.fsi', '.fsscript', '.dart', '.elm', '.ex', '.exs',
            '.erl', '.hrl', '.cl', '.lisp', '.scm', '.rkt', '.jl', '.nim',
            '.zig', '.v', '.sv', '.vhd', '.vhdl', '.asm', '.s', '.S'
        }
        if file_path.suffix.lower() in text_extensions:
            return True
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type and mime_type.startswith('text/'):
            return True
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                if b'\x00' in chunk:
                    return False
                return all(b <= 127 for b in chunk)
        except Exception:
            return False

    def _get_file_content(self, file_path: pathlib.Path) -> str:
        try:
            if not self._is_text_file(file_path):
                return f"[Бинарный файл: {file_path.suffix or 'без расширения'}]"
            encodings = ['utf-8', 'latin-1', 'cp1251', 'iso-8859-1', 'utf-16']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                        if len(content) > self.max_file_chars:
                            content = content[: self.max_file_chars] + "\n\n... (содержимое обрезано)"
                        return html.escape(content)
                except UnicodeDecodeError:
                    continue
                except Exception:
                    continue
            return "[Ошибка чтения файла: не удалось определить кодировку]"
        except Exception as e:
            return f"[Ошибка чтения файла: {e}]"

    def _generate_html_header(self):
        self.html_content.append(
            f"""<!DOCTYPE html>
<html lang=\"ru\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>{html.escape(self.title)}</title>
    <link href=\"https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism.min.css\" rel=\"stylesheet\" />
    <link href=\"https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css\" rel=\"stylesheet\" />
    <style>
        body {{
            font-family: 'Courier New', monospace;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            font-size: 14px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .section {{ padding: 20px; }}
        .section-title {{
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
            padding: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 4px;
        }}
        .tree {{
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.4;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            border: 1px solid #e9ecef;
            white-space: pre;
            overflow-x: auto;
        }}
        .folder {{ color: #2c3e50; font-weight: bold; }}
        .file {{ color: #34495e; }}
        .file-highlighted {{ color: #e74c3c; font-weight: bold; }}
        .file-content {{ margin: 10px 0 20px 0; border-radius: 4px; overflow: hidden; }}
        .stats {{ background: #e9ecef; padding: 15px; margin: 20px 0; border-radius: 4px; font-size: 14px; }}
        .breadcrumb {{ background: #f8f9fa; padding: 10px 20px; border-bottom: 1px solid #e9ecef; font-size: 14px; color: #6c757d; }}
        .file-header {{ font-weight: bold; color: #2c3e50; margin-bottom: 10px; padding: 10px; background-color: #ecf0f1; border-radius: 4px; border-left: 4px solid #3498db; }}
        pre {{ margin: 0; border-radius: 4px; }}
        code {{ font-size: 12px; line-height: 1.4; }}
        .file-index {{ background: #f8f9fa; padding: 15px; margin: 20px 0; border-radius: 4px; border-left: 4px solid #27ae60; }}
        .file-link {{ color: #3498db; text-decoration: none; padding: 2px 5px; border-radius: 2px; transition: background-color 0.2s; }}
        .file-link:hover {{ background-color: #e3f2fd; }}
        .custom-files-info {{ background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; padding: 10px; border-radius: 4px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class=\"container\">
        <div class=\"header\">
            <h1>🌳 {html.escape(self.title)}</h1>
            <p>Структура файлов и папок</p>
        </div>""")

    def _generate_html_footer(self):
        self.html_content.append(
            """
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-core.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>
</body>
</html>"""
        )

    def _format_size(self, size_bytes: int) -> str:
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f} {size_names[i]}"

    def _build_tree_structure(self, directory: pathlib.Path, level: int = 0, parent_prefix: str = "") -> dict:
        stats = {'files': 0, 'dirs': 0, 'total_size': 0}
        try:
            items = sorted(directory.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
            valid_items = [item for item in items if not self._should_ignore(item)]
            for i, item in enumerate(valid_items):
                rel_path = item.relative_to(self.root_path)
                is_last = i == len(valid_items) - 1
                if level == 0:
                    prefix = ""
                    next_prefix = ""
                else:
                    prefix = parent_prefix + ("└── " if is_last else "├── ")
                    next_prefix = parent_prefix + ("    " if is_last else "│   ")

                if item.is_dir():
                    if not self._should_include_directory_in_tree(item):
                        continue
                    stats['dirs'] += 1
                    self.html_content.append(f'{prefix}📁 {item.name}/')
                    sub_stats = self._build_tree_structure(item, level + 1, next_prefix)
                    stats['files'] += sub_stats['files']
                    stats['dirs'] += sub_stats['dirs']
                    stats['total_size'] += sub_stats['total_size']
                else:
                    if not self._should_include_file_in_tree(item):
                        # статистику всё равно обновим
                        try:
                            stats['files'] += 1
                            stats['total_size'] += item.stat().st_size
                        except Exception:
                            pass
                        continue
                    stats['files'] += 1
                    try:
                        file_size = item.stat().st_size
                        stats['total_size'] += file_size
                        size_str = self._format_size(file_size)
                    except Exception:
                        size_str = "неизвестно"
                    is_highlighted = self._should_include_file_for_code(item)
                    file_icon = "⭐" if is_highlighted else "📄"
                    if is_highlighted:
                        self.files_list.append({
                            'path': item,
                            'rel_path': rel_path,
                            'size': size_str
                        })
                    self.html_content.append(f'{prefix}{file_icon} {item.name} ({size_str})')
        except PermissionError:
            self.html_content.append(f'{parent_prefix}❌ Ошибка доступа к {directory.name}')
        except Exception as e:
            self.html_content.append(f'{parent_prefix}❌ Ошибка: {e}')
        return stats

    def generate(self, output_file: str = "project_structure.html"):
        self.html_content = []
        self.files_list = []

        self._generate_html_header()

        self.html_content.append(
            f"""
        <div class=\"breadcrumb\">
            <strong>Корневая папка:</strong> {html.escape(str(self.root_path))}<br>
            <strong>Дата генерации:</strong> {html.escape(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}"""
        )
        if self.tree_include:
            self.html_content.append(
                f"""
            <br><strong>Tree include:</strong> {html.escape(', '.join(self.tree_include))}"""
            )
        if self.tree_exclude:
            self.html_content.append(
                f"""
            <br><strong>Tree exclude:</strong> {html.escape(', '.join(self.tree_exclude))}"""
            )
        if self.content_include:
            self.html_content.append(
                f"""
            <br><strong>Content include:</strong> {html.escape(', '.join(self.content_include))}"""
            )
        self.html_content.append("</div>")

        self.html_content.append('<div class="section">')
        self.html_content.append('<div class="section-title">📁 Структура проекта</div>')
        if self.content_include:
            self.html_content.append(
                '<div class="custom-files-info">'
                '<strong>ℹ️ Содержимое включено только для файлов, подходящих под Content include.</strong><br>'
                'Файлы с кодом выделены звездочкой ⭐'
                '</div>'
            )
        self.html_content.append('<div class="tree">')
        stats = self._build_tree_structure(self.root_path)
        self.html_content.append('</div>')

        self.html_content.append(
            f"""
        <div class=\"stats\">
            <strong>Статистика проекта:</strong><br>
            Папок: {stats['dirs']}<br>
            📄 Файлов: {stats['files']}<br>
            💾 Общий размер: {self._format_size(stats['total_size'])}"""
        )
        if self.content_include:
            self.html_content.append(f"<br>⭐ Файлов с кодом: {len(self.files_list)}")
        self.html_content.append("</div></div>")

        if self.files_list:
            self.html_content.append('<div class="section">')
            self.html_content.append('<div class="section-title">📋 Индекс файлов</div>')
            self.html_content.append('<div class="file-index">')
            for i, file_info in enumerate(self.files_list):
                file_id = f"file_{i}"
                self.html_content.append(f'<a href="#{file_id}" class="file-link">📄 {file_info["rel_path"]} ({file_info["size"]})</a><br>')
            self.html_content.append('</div>')
            self.html_content.append('</div>')

            self.html_content.append('<div class="section">')
            self.html_content.append('<div class="section-title">💻 Содержимое файлов</div>')
            for i, file_info in enumerate(self.files_list):
                file_id = f"file_{i}"
                content = self._get_file_content(file_info['path'])
                language_class = self._get_language_class(file_info['path'])
                self.html_content.append(f'<div id="{file_id}">')
                self.html_content.append(f'  <div class="file-header">📄 {file_info["rel_path"]} ({file_info["size"]})</div>')
                self.html_content.append(f'  <div class="file-content">')
                self.html_content.append(f'    <pre><code class="{language_class}">{content}</code></pre>')
                self.html_content.append(f'  </div>')
                self.html_content.append(f'</div>')
            self.html_content.append('</div>')
        else:
            self.html_content.append('<div class="section">')
            self.html_content.append('<div class="section-title">💻 Содержимое файлов</div>')
            self.html_content.append('<div class="custom-files-info">Нет файлов для отображения кода</div>')
            self.html_content.append('</div>')

        self._generate_html_footer()

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.html_content))

        print(f"✅ HTML файл создан: {output_file}")
        print(f"📊 Статистика: {stats['dirs']} папок, {stats['files']} файлов, {self._format_size(stats['total_size'])} общий размер")
        if self.content_include:
            print(f"⭐ Файлов с кодом: {len(self.files_list)}")
        return output_file


def generate_project_tree(
    *,
    root_path: Optional[str] = None,
    detect_git_root: bool = True,
    respect_gitignore: bool = True,
    extra_ignore: Optional[Iterable[str]] = None,
    tree_include: Optional[Iterable[str]] = None,
    tree_exclude: Optional[Iterable[str]] = None,
    content_include: Optional[Iterable[str]] = None,
    max_file_chars: int = 10000,
    title: str = "Структура проекта",
    output_file: str = "project_structure.html",
) -> str:
    """Программный API для генерации отчёта. Возвращает путь к HTML-файлу."""
    gen = ProjectTreeGenerator(
        root_path=root_path,
        detect_git_root=detect_git_root,
        respect_gitignore=respect_gitignore,
        extra_ignore=extra_ignore,
        tree_include=tree_include,
        tree_exclude=tree_exclude,
        content_include=content_include,
        max_file_chars=max_file_chars,
        title=title,
    )
    return gen.generate(output_file=output_file)


def _split_csv_or_list(values: Optional[Iterable[str]]) -> Optional[List[str]]:
    if values is None:
        return None
    result: List[str] = []
    for v in values:
        if v is None:
            continue
        parts = [p.strip() for p in str(v).split(',') if p.strip()]
        result.extend(parts)
    return result or None


def cli():
    """CLI-точка входа. По умолчанию строит полную структуру проекта без содержимого файлов."""
    parser = argparse.ArgumentParser(
        prog="aik-project-tree",
        description=(
            "Генерация HTML со структурой проекта. По умолчанию создаёт дерево всего проекта; "
            "содержимое файлов добавляется только для тех, что подходят под --content-include."
        ),
    )
    parser.add_argument("--root", dest="root_path", default=None, help="Корневая папка проекта. По умолчанию: git root или текущая")
    parser.add_argument("--no-git-root", dest="detect_git_root", action="store_false", help="Не искать git root; использовать --root или CWD")
    parser.add_argument("--no-gitignore", dest="respect_gitignore", action="store_false", help="Не учитывать .gitignore")
    parser.add_argument("--extra-ignore", nargs="*", default=None, help="Доп. игнор-паттерны (список или CSV)")
    parser.add_argument("--tree-include", nargs="*", default=None, help="Паттерны включения для дерева (список или CSV)")
    parser.add_argument("--tree-exclude", nargs="*", default=None, help="Паттерны исключения для дерева (список или CSV)")
    parser.add_argument("--content-include", nargs="*", default=None, help="Паттерны для вывода содержимого (список или CSV). Если не задано — содержимое не выводится")
    parser.add_argument("--max-file-chars", type=int, default=10000, help="Максимум символов содержимого на файл")
    parser.add_argument("--title", default="Структура проекта", help="Заголовок HTML-страницы")
    parser.add_argument("--output", default="project_structure.html", help="Путь к итоговому HTML-файлу")

    args = parser.parse_args()

    output = generate_project_tree(
        root_path=args.root_path,
        detect_git_root=args.detect_git_root,
        respect_gitignore=args.respect_gitignore,
        extra_ignore=_split_csv_or_list(args.extra_ignore),
        tree_include=_split_csv_or_list(args.tree_include),
        tree_exclude=_split_csv_or_list(args.tree_exclude),
        content_include=_split_csv_or_list(args.content_include),
        max_file_chars=args.max_file_chars,
        title=args.title,
        output_file=args.output,
    )
    print(f"\n🎉 Структура проекта сохранена в файл: {output}")
    print("Откройте файл в браузере для просмотра")


if __name__ == "__main__":
    cli()

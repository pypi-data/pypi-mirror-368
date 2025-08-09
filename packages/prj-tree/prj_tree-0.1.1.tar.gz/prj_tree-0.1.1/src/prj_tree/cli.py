from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .core import GenerateOptions, generate
from .config import load_config, merge_config
from .utils import detect_project_root


def _split_csv_or_list(values):
    if values is None:
        return None
    result = []
    for v in values:
        if v is None:
            continue
        parts = [p.strip() for p in str(v).split(',') if p.strip()]
        result.extend(parts)
    return result or None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="prj-tree",
        description=(
            "Извлечение структуры проекта и содержимого файлов. "
            "Умеет учитывать .gitignore и .prjtreeignore. Рендеры: html, md, json, ascii."
        ),
    )
    parser.add_argument("root", nargs="?", default=None, help="Корень проекта (по умолчанию — git root или CWD)")
    parser.add_argument("--no-git-root", dest="detect_git_root", action="store_false", help="Не искать git root")
    parser.add_argument("--no-gitignore", dest="respect_gitignore", action="store_false", help="Не учитывать .gitignore")
    parser.add_argument("--extra-ignore", nargs="*", default=None, help="Доп. игнор-паттерны (список или CSV)")
    parser.add_argument("--tree-include", nargs="*", default=None, help="Включить в дерево только совпадающее (список или CSV)")
    parser.add_argument("--tree-exclude", nargs="*", default=None, help="Исключить из дерева паттерны (список или CSV)")
    parser.add_argument(
        "--content-include",
        nargs="*",
        default=None,
        help="Файлы для показа содержимого: по имени, расширению (.py), пути или wildcard (список/CSV)",
    )
    parser.add_argument(
        "--content-exclude",
        nargs="*",
        default=None,
        help="Исключить содержимое для совпадающих путей/имен/расширений/wildcard, не скрывая файл из дерева",
    )
    parser.add_argument("--max-file-chars", type=int, default=10000, help="Максимум символов на файл")
    parser.add_argument("--title", default="Структура проекта", help="Заголовок отчёта")
    parser.add_argument("--renderer", default="html", choices=["html", "md", "json", "ascii"], help="Формат вывода")
    parser.add_argument("--output", default=None, help="Путь к итоговому файлу (по умолчанию зависит от renderer)")

    args = parser.parse_args(argv)

    root_for_config = detect_project_root(args.root or None, args.detect_git_root)
    cfg = load_config(root_for_config)
    cli_map = {
        "root_path": args.root or None,
        "detect_git_root": args.detect_git_root,
        "respect_gitignore": args.respect_gitignore,
        "extra_ignore": _split_csv_or_list(args.extra_ignore),
        "tree_include": _split_csv_or_list(args.tree_include),
        "tree_exclude": _split_csv_or_list(args.tree_exclude),
        "content_include": _split_csv_or_list(args.content_include),
        "content_exclude": _split_csv_or_list(args.content_exclude),
        "max_file_chars": args.max_file_chars,
        "title": args.title,
        "renderer": args.renderer,
        "output_file": args.output,
    }
    merged = merge_config(cli_map, cfg)
    opts = GenerateOptions(**merged)

    output = generate(opts)

    # Write output if file path provided or renderer dictates saving
    if opts.output_file:
        Path(opts.output_file).write_text(output, encoding="utf-8")
        print(f"✅ Файл сохранён: {opts.output_file}")
    else:
        # default targets per renderer
        default = {
            "html": "project_structure.html",
            "md": "project_structure.md",
            "json": "project_structure.json",
            "ascii": None,
        }[opts.renderer]
        if default:
            Path(default).write_text(output, encoding="utf-8")
            print(f"✅ Файл сохранён: {default}")
        else:
            # ascii -> print to stdout
            print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



"""prj_tree: извлечение структуры проекта и содержимого файлов.

Высокоуровневый API:
- generate(...) — построить структуру и отрендерить.
"""

from .core import generate, GenerateOptions, ScanResult

__all__ = [
    "generate",
    "GenerateOptions",
    "ScanResult",
]

__version__ = "0.1.0"



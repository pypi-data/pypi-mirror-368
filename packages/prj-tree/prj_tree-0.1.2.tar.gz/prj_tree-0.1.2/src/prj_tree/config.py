from __future__ import annotations

import json
import pathlib
from typing import Any, Dict, Optional


def _load_toml(path: pathlib.Path) -> Dict[str, Any]:
    try:
        try:
            import tomllib  # Python 3.11+
        except Exception:  # pragma: no cover
            import tomli as tomllib  # type: ignore
        return tomllib.loads(path.read_text(encoding="utf-8"))  # type: ignore
    except Exception:
        return {}


def _load_json(path: pathlib.Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_config(root: pathlib.Path) -> Dict[str, Any]:
    for name in [".prjtree.toml", "prjtree.toml"]:
        p = root / name
        if p.exists():
            data = _load_toml(p)
            if isinstance(data, dict):
                return data
    for name in [".prjtree.json", "prjtree.json"]:
        p = root / name
        if p.exists():
            data = _load_json(p)
            if isinstance(data, dict):
                return data
    return {}


def merge_config(cli: dict, cfg: dict) -> dict:
    # CLI overrides config when present (non-None)
    merged = dict(cfg)
    for k, v in cli.items():
        if v is not None:
            merged[k] = v
    return merged



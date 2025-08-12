from __future__ import annotations

import json
import random
from dataclasses import dataclass
from typing import Callable, List, Optional
from importlib.abc import Traversable

try:  # Python 3.9+
    from importlib.resources import files as _files
    _ir_files: Optional[Callable[[str], Traversable]] = _files
except Exception:
    _ir_files = None


@dataclass(frozen=True)
class Greeting:
    index: int
    name: str
    code: str
    codes: List[str]
    hello: str
    hello_world: str


def _read_data_text() -> str:
    if _ir_files is not None:
        data_path = _ir_files("polyglot_hello").joinpath("data/greetings.json")
        return data_path.read_text(encoding="utf-8")
    # Python 3.8: try importlib.resources.open_text using a package module
    try:
        from importlib.resources import open_text

        with open_text("polyglot_hello.data", "greetings.json", encoding="utf-8") as f:
            return f.read()
    except Exception:
        # Final fallback: pkgutil
        import pkgutil

        data_bytes = pkgutil.get_data("polyglot_hello", "data/greetings.json")
        if data_bytes is None:
            raise FileNotFoundError(
                "Unable to load greetings.json resource. Ensure package data is included."
            )
        return data_bytes.decode("utf-8")


def _load_data() -> List[Greeting]:
    raw = json.loads(_read_data_text())
    greetings: List[Greeting] = []
    for i, row in enumerate(raw):
        codes = sorted(set([row.get("code")] + row.get("codes", [])))
        primary = row.get("code") or (codes[0] if codes else "")
        greetings.append(
            Greeting(
                index=i,
                name=row["name"],
                code=primary,
                codes=codes,
                hello=row["hello"],
                hello_world=row["hello_world"],
            )
        )
    return greetings


_CACHE: Optional[List[Greeting]] = None


def _all() -> List[Greeting]:
    global _CACHE
    if _CACHE is None:
        _CACHE = _load_data()
    return _CACHE


def list_languages() -> List[str]:
    return [g.name for g in _all()]


def get_by_index(index: int) -> Greeting:
    items = _all()
    if index < 0 or index >= len(items):
        raise IndexError(f"index {index} is out of range 0..{len(items)-1}")
    return items[index]


def _normalize(s: str) -> str:
    return s.strip().lower().replace("_", "-")


def get_by_name(name: str) -> Greeting:
    key = _normalize(name)
    for g in _all():
        if _normalize(g.name) == key:
            return g
    # fallback: prefix/contains
    for g in _all():
        norm = _normalize(g.name)
        if norm.startswith(key) or key in norm:
            return g
    raise KeyError(f"language name not found: {name}")


def get_by_code(code: str) -> Greeting:
    key = _normalize(code)
    for g in _all():
        if key == _normalize(g.code) or key in [_normalize(c) for c in g.codes]:
            return g
    raise KeyError(f"language code not found: {code}")


def random_greeting() -> Greeting:
    return random.choice(_all())


def say_hello(identifier: Optional[str | int] = None) -> str:
    g = _resolve(identifier)
    return g.hello


def say_hello_world(identifier: Optional[str | int] = None) -> str:
    g = _resolve(identifier)
    return g.hello_world


def search(query: str) -> List[Greeting]:
    q = _normalize(query)
    results: List[Greeting] = []
    for g in _all():
        hay = " ".join([g.name, g.code] + g.codes + [g.hello, g.hello_world])
        if q in _normalize(hay):
            results.append(g)
    return results


def _resolve(identifier: Optional[str | int]) -> Greeting:
    if identifier is None:
        return random_greeting()
    if isinstance(identifier, int):
        return get_by_index(identifier)
    # identifier is str
    ident = identifier.strip()
    # Try exact code match first
    try:
        return get_by_code(ident)
    except KeyError:
        pass
    # Try by name
    try:
        return get_by_name(ident)
    except KeyError:
        pass
    # If numeric string
    if ident.isdigit():
        return get_by_index(int(ident))
    raise KeyError(f"could not resolve language: {identifier}")



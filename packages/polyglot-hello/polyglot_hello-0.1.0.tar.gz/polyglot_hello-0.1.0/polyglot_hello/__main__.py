from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from .api import (
    list_languages,
    say_hello,
    say_hello_world,
    search,
)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="polyglot-hello",
        description="Print 'Hello' or 'Hello World' in 200+ languages by name, code, or index.",
    )
    sub = parser.add_subparsers(dest="cmd")

    p_hello = sub.add_parser("hello", help="Print 'Hello'")
    p_hello.add_argument("identifier", nargs="?", help="language name, code, or index")

    p_world = sub.add_parser("world", help="Print 'Hello World'")
    p_world.add_argument("identifier", nargs="?", help="language name, code, or index")

    p_list = sub.add_parser("list", help="List available languages")
    p_list.add_argument("--json", action="store_true", help="Output as JSON")

    p_search = sub.add_parser("search", help="Search by substring across names/codes/translations")
    p_search.add_argument("query", help="query string")
    p_search.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args(argv)

    try:
        if args.cmd == "hello":
            print(say_hello(args.identifier))
            return 0
        if args.cmd == "world":
            print(say_hello_world(args.identifier))
            return 0
        if args.cmd == "list":
            langs = list_languages()
            if getattr(args, "json", False):
                print(json.dumps(langs, ensure_ascii=False))
            else:
                for i, name in enumerate(langs):
                    print(f"{i}: {name}")
            return 0
        if args.cmd == "search":
            results = search(args.query)
            payload = [
                {
                    "index": g.index,
                    "name": g.name,
                    "code": g.code,
                    "codes": g.codes,
                    "hello": g.hello,
                    "hello_world": g.hello_world,
                }
                for g in results
            ]
            if getattr(args, "json", False):
                print(json.dumps(payload, ensure_ascii=False))
            else:
                for item in payload:
                    print(
                        f"{item['index']:03d} | {item['name']} ({item['code']}) | "
                        f"{item['hello']} / {item['hello_world']}"
                    )
            return 0

        # default: print random hello world
        print(say_hello_world(None))
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())



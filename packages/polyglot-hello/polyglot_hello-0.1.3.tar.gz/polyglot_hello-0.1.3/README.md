### polyglot-hello
This was written with Cursor and ChatGPT-5.

Simple Python library and CLI for “Hello” and “Hello World” in 200+ languages.

- **APIs**: get by language name, code (ISO 639-1 and common alternates), or numeric index
- **CLI**: `polyglot-hello hello [id]` and `polyglot-hello world [id]`
- **Data**: 200+ curated entries with `hello` and `hello_world`

### Install

```bash
pip install polyglot-hello
```

### Usage (Python)

```python
from polyglot_hello import say_hello, say_hello_world, get_by_code, get_by_name, list_languages

print(say_hello())               # random
print(say_hello_world())         # random
print(say_hello_world("en"))    # by code
print(say_hello_world("Spanish"))

g = get_by_code("fr")
print(g.name, g.hello, g.hello_world)

langs = list_languages()
print(len(langs))
```

### CLI

```bash
polyglot-hello hello           # random “Hello”
polyglot-hello world           # random “Hello World”
polyglot-hello hello en        # by code
polyglot-hello world Spanish   # by name
polyglot-hello list            # list with indexes
polyglot-hello search hola     # fuzzy search
```

### Examples

See `examples/hello_world.py` for a minimal integration. Run with:

```bash
python examples/hello_world.py
```

### API

- **say_hello(identifier: str|int|None = None) -> str**: returns “Hello” for the resolved language
- **say_hello_world(identifier: str|int|None = None) -> str**: returns “Hello World”
- **get_by_name(name: str) -> Greeting**
- **get_by_code(code: str) -> Greeting**
- **get_by_index(index: int) -> Greeting**
- **list_languages() -> list[str]**
- **search(query: str) -> list[Greeting]**

The `Greeting` object has: `index`, `name`, `code`, `codes`, `hello`, `hello_world`.

### Language codes

Primary codes are ISO 639-1 when available (e.g., `en`, `es`, `fr`), plus helpful alternates in `codes` (e.g., ISO 639-2 `eng`, regional tags like `pt-BR`). You can pass any recognized code or the full language name.

### Contributing

PRs to add or improve languages welcome. Please ensure entries include:

```json
{
  "name": "Language Name",
  "code": "primary-code",
  "codes": ["alt1", "alt2"],
  "hello": "...",
  "hello_world": "..."
}
```

### License

Apache-2.0

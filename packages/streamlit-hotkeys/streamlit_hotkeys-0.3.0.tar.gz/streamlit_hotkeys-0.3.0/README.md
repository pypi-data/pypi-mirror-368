# Streamlit Hotkeys

[![PyPI](https://img.shields.io/pypi/v/streamlit-hotkeys.svg)](https://pypi.org/project/streamlit-hotkeys/)
[![Python Versions](https://img.shields.io/pypi/pyversions/streamlit-hotkeys.svg)](https://pypi.org/project/streamlit-hotkeys/)
[![License](https://img.shields.io/pypi/l/streamlit-hotkeys.svg)](LICENSE)
[![Wheel](https://img.shields.io/pypi/wheel/streamlit-hotkeys.svg)](https://pypi.org/project/streamlit-hotkeys/)
![Streamlit Component](https://img.shields.io/badge/streamlit-component-FF4B4B?logo=streamlit\&logoColor=white)
[![Downloads](https://static.pepy.tech/badge/streamlit-hotkeys)](https://pepy.tech/project/streamlit-hotkeys)

Keyboard hotkeys for Streamlit - capture `Ctrl/Cmd/Alt/Shift + key` anywhere in your app and trigger Python once per press (edge-triggered). Uses a single invisible manager component.

**Important:** call `activate(...)` as early as possible in each page. Activation injects CSS that collapses the manager iframe, which avoids layout flicker.

---

## Installation

```bash
pip install streamlit-hotkeys
```

## Quick start

```python
import streamlit as st
import streamlit_hotkeys as hotkeys

st.set_page_config(page_title="Hotkeys Demo")

# Activate early so the manager is hidden from the first frame
hotkeys.activate([
    hotkeys.hk("palette", "k", meta=True),                # Cmd+K (macOS)
    hotkeys.hk("palette", "k", ctrl=True),                # Ctrl+K (Windows/Linux)
    hotkeys.hk("save", "s", ctrl=True, prevent_default=True), # Ctrl+S (block browser save)
    hotkeys.hk("down", "ArrowDown"),
], key="global")

st.title("Hotkeys demo")

if hotkeys.pressed("palette"):
    st.success("Open palette")

if hotkeys.pressed("save"):
    st.success("Saved!")

if hotkeys.pressed("down"):
    st.write("Move selection down")
```

## Features

- Single invisible **manager** (one iframe for the whole page)
- Activates early and auto-collapses its iframe to avoid layout flicker
- Edge-triggered events (per-id seq; no sticky booleans)
- Bind single keys or modifier combos (`ctrl`, `alt`, `shift`, `meta`)
- Reuse the **same `id`** across multiple bindings (e.g., Cmd+K **or** Ctrl+K → `palette`)
- `prevent_default` to block browser shortcuts (e.g., Ctrl/Cmd+S)
- Layout-independent physical keys via `code="KeyK"` / `code="Digit1"`
- `ignore_repeat` to suppress repeats while a key is held
- Built-in legend: add `help="..."` in `hk(...)` and call `hotkeys.legend()`
- Multi-page friendly; use `key=` for multiple independent managers
- Optional `debug=True` to log matches in the browser console

## API

### `hk(...)` - define a binding

```python
hk(
  id: str,
  key: str | None = None,           # for example, "k", "Enter", "ArrowDown"
  *,
  code: str | None = None,          # for example, "KeyK" (if set, 'key' is ignored)
  alt: bool | None = False,         # True=require, False=forbid, None=ignore
  ctrl: bool | None = False,
  shift: bool | None = False,
  meta: bool | None = False,
  ignore_repeat: bool = True,
  prevent_default: bool = False,
  help: str | None = None,          # text shown in the legend (optional)
) -> dict
```

### `activate(*bindings, key="global", debug=False) -> None`

Register bindings and render the single manager. Accepts `hk(...)` dicts, a list of them, or a mapping `id -> spec`.

### `pressed(id, *, key="global") -> bool`

Return `True` exactly once when the binding `id` fires.

### `legend(*, key="global") -> None`

Render a grouped shortcuts list (merges multiple bindings that share the same `id`, and shows the first non-empty `help` string per id). 

### Shortcuts Legend Example

```python
import streamlit as st
import streamlit_hotkeys as hotkeys

hotkeys.activate({
    "palette": [
        {"key": "k", "meta": True,  "help": "Open command palette"},
        {"key": "k", "ctrl": True}, 
    ],
    "save": {"key": "s", "ctrl": True, "prevent_default": True, "help": "Save document"},
}, key="global")

@st.dialog("Keyboard Shortcuts")
def _shortcuts():
    hotkeys.legend()  

if hotkeys.pressed("palette"):
    _shortcuts()
```

## Notes and limitations

* Browsers reserve some shortcuts. Use `prevent_default=True` to keep the event for your app when allowed.
* Combos mean modifiers + one key. The platform does not treat two non-modifier keys pressed together (for example, `A+S`) as a single combo.
* The page must have focus; events are captured at the document level.

## Similar projects

* [streamlit-keypress] - Original "keypress to Python" component by Sudarsan.
* [streamlit-shortcuts] - Keyboard shortcuts for buttons and widgets; supports multiple bindings and hints.
* [streamlit-keyup] - Text input that emits on every keyup (useful for live filtering).
* [keyboard\_to\_url][keyboard_to_url] - Bind a key to open a URL in a new tab.

[streamlit-keypress]: https://pypi.org/project/streamlit-keypress/
[streamlit-shortcuts]: https://pypi.org/project/streamlit-shortcuts/
[streamlit-keyup]: https://pypi.org/project/streamlit-keyup/
[keyboard_to_url]: https://arnaudmiribel.github.io/streamlit-extras/extras/keyboard_url/

## Credits

Inspired by [streamlit-keypress] by **Sudarsan**. This implementation adds a multi-binding manager, edge-triggered events, modifier handling, `preventDefault`, and `KeyboardEvent.code`.

## Contributing

Issues and PRs are welcome.

## License

MIT. See `LICENSE`.

from __future__ import annotations

import os
from typing import Any, Dict, List, Mapping, Optional

import streamlit as st
import streamlit.components.v1 as components

# -------- Component declaration (single invisible manager iframe) --------

_BUILD_DIR = os.path.join(os.path.dirname(__file__), "component")
_hotkeys_manager = components.declare_component("manager", path=_BUILD_DIR)


# -------- Session-state keys --------

def _css_flag_key() -> str:
    return "__hk_css_injected__"


def _bindings_key(manager_key: str) -> str:
    return f"__hk_bindings__::{manager_key}"


def _last_event_key(manager_key: str) -> str:
    return f"__hk_last_event__::{manager_key}"


def _per_id_seq_key(manager_key: str) -> str:
    return f"__hk_last_seq_by_id__::{manager_key}"


def preload_css(*, key: str = "global") -> None:
    """
    Inject CSS that collapses the manager *by its widget key class*.
    Call this at the very top of your app/page, BEFORE `activate(...)`.

    For key="global", Streamlit gives the container class:
      .st-key-hotkeys-manager--global
    """
    css_class = f"st-key-hotkeys-manager--{key}"
    st.markdown(
        f"""
<style>
/* Collapse the specific manager container and its iframe immediately on mount */
.{css_class},
.{css_class} > div {{
  margin:0 !important; padding:0 !important;
  height:0 !important; min-height:0 !important;
  border:0 !important; overflow:hidden !important; line-height:0 !important;
}}
.{css_class} iframe {{
  width:0 !important; height:0 !important; border:0 !important;
  position:absolute !important; opacity:0 !important; pointer-events:none !important;
}}
</style>
""",
        unsafe_allow_html=True,
    )


# -------- Public helper to define a binding --------

def hk(
        id: str,
        key: Optional[str] = None,
        *,
        code: Optional[str] = None,
        alt: Optional[bool] = False,
        ctrl: Optional[bool] = False,
        shift: Optional[bool] = False,
        meta: Optional[bool] = False,
        ignore_repeat: bool = True,
        prevent_default: bool = False,
        help: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a hotkey binding for the manager.

    Args:
        id: Identifier string used with pressed(id). You may reuse the same id across multiple bindings.
        key: KeyboardEvent.key (e.g., "k", "Enter", "ArrowDown").
        code: KeyboardEvent.code (e.g., "KeyK"). If provided, 'key' is ignored.
        alt/ctrl/shift/meta:
            True=require pressed, False=forbid, None=ignore.
        ignore_repeat: Ignore held-key repeats.
        prevent_default: Prevent browser default on match (e.g., Ctrl/Cmd+S).
        help: Optional human-readable description to show in the legend.
    """
    if not id:
        raise ValueError("hk(): 'id' is required and must be non-empty")
    if key is None and code is None:
        raise ValueError("hk(): provide either 'key' or 'code'")
    return {
        "id": str(id),
        "key": key,
        "code": code,
        "alt": alt,
        "ctrl": ctrl,
        "shift": shift,
        "meta": meta,
        "ignoreRepeat": bool(ignore_repeat),
        "preventDefault": bool(prevent_default),
        "help": help,
    }


# -------- Event view used internally for edge-triggered checks --------

class _EventView:
    def __init__(self, payload: Optional[Dict[str, Any]], manager_key: str):
        self.payload = payload or {"seq": 0, "id": None}
        self.manager_key = manager_key
        seq_store = _per_id_seq_key(manager_key)
        if seq_store not in st.session_state:
            st.session_state[seq_store] = {}

    @property
    def id(self) -> Optional[str]:
        return self.payload.get("id")

    @property
    def seq(self) -> int:
        return int(self.payload.get("seq") or 0)

    def pressed(self, binding_id: str) -> bool:
        if not binding_id or self.payload.get("id") != binding_id:
            return False
        store = st.session_state[_per_id_seq_key(self.manager_key)]
        last_seen = int(store.get(binding_id, 0))
        current = self.seq
        if current > last_seen:
            store[binding_id] = current
            return True
        return False


# -------- Internal: normalize bindings passed to activate() --------

def _normalize_bindings_args(
        *bindings: Any,
        mapping: Optional[Mapping[str, Mapping[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Accepts:
      - activate(hk(...), hk(...))
      - activate([hk(...), hk(...)] )
      - activate({"save": {...}, "open": {...}})  # mapping id -> spec
    """
    out: List[Dict[str, Any]] = []

    # If a single argument is provided and it's a list/tuple: flatten it
    if len(bindings) == 1 and isinstance(bindings[0], (list, tuple)):
        bindings = tuple(bindings[0])

    # If a single argument is provided and it's a dict:
    #   - Either a single hk-dict with "id" in it
    #   - Or a mapping id -> partial spec
    if len(bindings) == 1 and isinstance(bindings[0], dict):
        d = bindings[0]
        if "id" in d:
            out.append(d)  # a single hk(...) dict
        else:
            mapping = d  # treat as mapping
            bindings = tuple()  # and ignore positional

    # Positional hk(...) dicts
    for b in bindings:
        if not isinstance(b, dict) or "id" not in b:
            raise ValueError("activate(): positional args must be hk(...) dicts")
        out.append(b)

    # Mapping id -> spec
    # Mapping id -> spec OR id -> [spec, spec, ...]
    if mapping:
        for _id, spec in mapping.items():
            if isinstance(spec, Mapping):
                out.append(
                    hk(
                        id=_id,
                        key=spec.get("key"),
                        code=spec.get("code"),
                        alt=spec.get("alt", False),
                        ctrl=spec.get("ctrl", False),
                        shift=spec.get("shift", False),
                        meta=spec.get("meta", False),
                        ignore_repeat=spec.get("ignore_repeat", True),
                        prevent_default=spec.get("prevent_default", False),
                        help=spec.get("help"),
                    )
                )
            elif isinstance(spec, (list, tuple)):
                for s in spec:
                    if not isinstance(s, Mapping):
                        raise ValueError("activate(): each item in list must be a dict-like spec")
                    out.append(
                        hk(
                            id=_id,
                            key=s.get("key"),
                            code=s.get("code"),
                            alt=s.get("alt", False),
                            ctrl=s.get("ctrl", False),
                            shift=s.get("shift", False),
                            meta=s.get("meta", False),
                            ignore_repeat=s.get("ignore_repeat", True),
                            prevent_default=s.get("prevent_default", False),
                            help=s.get("help"),
                        )
                    )
            else:
                raise ValueError("activate(): mapping values must be a dict or a list of dicts")
    return out


# -------- Core: render manager + store last payload for pressed() --------

def _render_manager(bindings: List[Dict[str, Any]], *, key: str, debug: bool) -> _EventView:
    payload = _hotkeys_manager(
        bindings=bindings,
        debug=bool(debug),
        default={"seq": 0},
        key=f"hotkeys-manager::{key}",
    )
    # Store last payload for pressed()
    st.session_state[_last_event_key(key)] = payload
    return _EventView(payload, manager_key=key)


# -------- Public API -----------------------------------------------------

def activate(
        *bindings: Any,
        key: str = "global",
        debug: bool = False,
) -> None:
    """
    Configure and activate the single hotkeys manager (render the iframe once).

    Call this early in your app (e.g., in main.py). You can pass:
      activate(hk(...), hk(...))
      activate([hk(...), hk(...)] )
      activate({"save": {"key":"s", "ctrl":True}, "palette": {"key":"k", "meta":True}})

    Args:
        *bindings: hk(...) dicts, or a single list of hk dicts, or a single mapping id->spec.
        key: Manager key (use multiple keys for independent groups if needed).
        debug: When True, frontend logs match events to the browser console.
    """
    preload_css(key=key)
    normalized = _normalize_bindings_args(*bindings)
    st.session_state[_bindings_key(key)] = normalized
    _render_manager(normalized, key=key, debug=debug)


def pressed(binding_id: str, *, key: str = "global") -> bool:
    """
    Return True exactly once when the binding `binding_id` fires.

    Requires that `activate(...)` has been called earlier in the same run (or on a prior code path).
    If not, we'll try to render with the last-known bindings (if any) so the manager exists.
    """
    # Ensure the per-id seq store exists
    seq_store = _per_id_seq_key(key)
    if seq_store not in st.session_state:
        st.session_state[seq_store] = {}

    payload = st.session_state.get(_last_event_key(key))
    if not isinstance(payload, dict):
        # Try to render with stored bindings so the manager is present
        bindings = st.session_state.get(_bindings_key(key), [])
        if not isinstance(bindings, list):
            bindings = []
        view = _render_manager(bindings, key=key, debug=False)
    else:
        view = _EventView(payload, manager_key=key)

    return view.pressed(binding_id)


def legend(*, key: str = "global") -> None:
    """
    Render a simple, grouped legend of the active shortcuts.
    - Groups multiple bindings that share the same id (e.g., Cmd+K / Ctrl+K).
    - Shows any 'help' text attached to a binding (first non-empty wins per id).
    """
    bindings = st.session_state.get(_bindings_key(key), [])
    if not bindings:
        st.info("No hotkeys configured.")
        return

    def _fmt_keyname(b: Dict[str, Any]) -> str:
        # Prefer .key label; fall back to .code for physical keys
        key = b.get("key")
        code = b.get("code")

        def sym(k: str) -> str:
            if k == " " or k == "Space":
                return "Space"
            if k == "Escape":
                return "Esc"
            if k == "ArrowLeft":
                return "←"
            if k == "ArrowRight":
                return "→"
            if k == "ArrowUp":
                return "↑"
            if k == "ArrowDown":
                return "↓"
            return k

        if key:
            k = key.upper() if len(key) == 1 else key
            return sym(k)
        if code:
            # Turn KeyK -> K, Digit1 -> 1; else show raw code
            if code.startswith("Key") and len(code) == 4:
                return code[-1]
            if code.startswith("Digit") and len(code) == 6:
                return code[-1]
            return code
        return "?"

    def _combo_label(b: Dict[str, Any]) -> str:
        parts = []
        if b.get("ctrl"):  parts.append("Ctrl")
        if b.get("alt"):   parts.append("Alt")
        if b.get("shift"): parts.append("Shift")
        if b.get("meta"):  parts.append("Cmd")  # shown as Cmd for familiarity
        parts.append(_fmt_keyname(b))
        return "+".join(parts)

    # Group combos by id
    grouped: Dict[str, Dict[str, Any]] = {}
    for b in bindings:
        _id = b.get("id")
        if not _id:
            continue
        item = grouped.setdefault(_id, {"combos": [], "help": None})
        item["combos"].append(f"`{_combo_label(b)}`")
        if not item["help"]:
            h = b.get("help")
            if isinstance(h, str) and h.strip():
                item["help"] = h.strip()

    # Render a compact table
    import pandas as pd
    rows = []
    for _id, info in grouped.items():
        rows.append({
            "Shortcut": " / ".join(info["combos"]),
            "Help": info["help"] or "",
        })
    df = pd.DataFrame(rows, columns=["Shortcut", "Help"]).set_index("Shortcut")

    st.table(df)

# custos/autocapture.py
from __future__ import annotations
import sys
import types
import inspect
import threading
from typing import Any, Callable, Optional, Tuple, Dict, List

_WRAP_NAMES = {"generate", "chat", "complete", "infer", "completions", "predict", "reply"}

_guardian = None
_lock = threading.Lock()
_installed = False

def _safe_str(x: Any) -> str:
    try:
        if isinstance(x, str):
            return x
        return str(x)
    except Exception:
        return ""

def _extract_prompt(args, kwargs) -> str:
    # Heuristics:
    # 1) first positional string
    for a in args:
        if isinstance(a, str) and a.strip():
            return a
    # 2) messages=[...], take last user message .content
    messages = kwargs.get("messages")
    if isinstance(messages, list):
        for m in reversed(messages):
            if isinstance(m, dict) and m.get("role") == "user":
                return _safe_str(m.get("content", ""))
    # 3) text=...
    txt = kwargs.get("text")
    if isinstance(txt, str) and txt.strip():
        return txt
    return ""

def _extract_response(ret: Any) -> str:
    # Common shapes: str, {"choices":[{"text":...}|{"message":{"content":...}}]}, {"generated_text":...}, list[dict]
    try:
        if isinstance(ret, str):
            return ret
        if isinstance(ret, dict):
            # openai-like
            ch = ret.get("choices")
            if isinstance(ch, list) and ch:
                c0 = ch[0]
                if isinstance(c0, dict):
                    if "text" in c0:
                        return _safe_str(c0.get("text", ""))
                    msg = c0.get("message")
                    if isinstance(msg, dict):
                        return _safe_str(msg.get("content", ""))
            # hf-like
            for key in ("generated_text", "summary_text", "answer", "output_text"):
                if key in ret:
                    return _safe_str(ret.get(key, ""))
        if isinstance(ret, list) and ret and isinstance(ret[0], dict):
            d0 = ret[0]
            for key in ("generated_text", "summary_text", "answer", "output_text", "text"):
                if key in d0:
                    return _safe_str(d0.get(key, ""))
        return _safe_str(ret)
    except Exception:
        return ""

def _wrap_callable(fn: Callable) -> Callable:
    if getattr(fn, "__custos_wrapped__", False):
        return fn

    sig = None
    try:
        sig = inspect.signature(fn)
    except Exception:
        pass

    def wrapped(*args, **kwargs):
        prompt = _extract_prompt(args, kwargs)
        ret = fn(*args, **kwargs)
        resp = _extract_response(ret)
        try:
            if _guardian:
                _guardian.evaluate(prompt, resp)  # non-blocking post
        except Exception:
            pass
        return ret

    try:
        wrapped.__name__ = getattr(fn, "__name__", "custos_wrapped")
    except Exception:
        pass
    setattr(wrapped, "__custos_wrapped__", True)
    return wrapped

def _maybe_wrap_attr(obj: Any, name: str):
    try:
        attr = getattr(obj, name, None)
        if callable(attr):
            setattr(obj, name, _wrap_callable(attr))
    except Exception:
        pass

def _scan_object(obj: Any):
    # Wrap methods with target names
    for name in dir(obj):
        if name in _WRAP_NAMES:
            _maybe_wrap_attr(obj, name)

def _scan_module(mod: types.ModuleType):
    # Wrap top-level callables
    for name, attr in list(vars(mod).items()):
        if name in _WRAP_NAMES and callable(attr):
            try:
                setattr(mod, name, _wrap_callable(attr))
            except Exception:
                pass
        # If attr is a class, scan its attributes
        try:
            if inspect.isclass(attr):
                _scan_object(attr)
        except Exception:
            pass

class _FinderHook:
    # PEP 302-compatible loader wrapper via meta_path
    def find_spec(self, fullname, path, target=None):
        return None  # we don't block normal import; we hook after load

def _post_import_hook(modname: str, mod: types.ModuleType):
    try:
        _scan_module(mod)
    except Exception:
        pass

def _install_import_hook():
    # Only install once; then hook into import machinery via sys.meta_path + module init
    global _installed
    if _installed:
        return
    _installed = True

    # Monkeypatch import to get a post-import callback without extra deps
    real_import = __import__

    def patched_import(name, globals=None, locals=None, fromlist=(), level=0):
        m = real_import(name, globals, locals, fromlist, level)
        try:
            # name may be a package; grab the actual module object(s)
            if fromlist:
                for sub in fromlist:
                    try:
                        submod = getattr(m, sub, None)
                        if isinstance(submod, types.ModuleType):
                            _post_import_hook(f"{name}.{sub}", submod)
                    except Exception:
                        pass
            if isinstance(m, types.ModuleType):
                _post_import_hook(name, m)
        except Exception:
            pass
        return m

    if not getattr(sys.modules.get("__builtin__") or sys.modules.get("builtins"), "__custos_import_patched__", False):
        import builtins
        setattr(builtins, "__custos_import_patched__", True)
        builtins.__import__ = patched_import  # type: ignore

    # Also scan already-loaded modules once
    for name, mod in list(sys.modules.items()):
        if isinstance(mod, types.ModuleType):
            _post_import_hook(name, mod)

def enable(guardian_obj) -> None:
    global _guardian
    with _lock:
        _guardian = guardian_obj
        _install_import_hook()

"""
translator_core — standalone re-export of SindarinTranslator.

Uses importlib to load lexicon.py, rules.py, and translator.py
directly from the project root, bypassing any Django app name collisions.
"""
import importlib.util
import os
import sys

# Absolute path to the project root (two levels up from web/translator_core/)
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _load_root_module(name: str):
    """
    Load <_ROOT>/<name>.py, register it in sys.modules under <name>.
    If the module is already registered (e.g. from a previous request), return it.
    """
    key = f"_root_{name}"
    if key in sys.modules:
        return sys.modules[key]

    path = os.path.join(_ROOT, f"{name}.py")
    spec = importlib.util.spec_from_file_location(key, path)
    mod  = importlib.util.module_from_spec(spec)
    # Register under both the unique key AND the plain name so that
    # cross-module imports (e.g. 'from lexicon import ...') resolve correctly.
    sys.modules[key]  = mod
    sys.modules[name] = mod   # overwrite / set plain-name slot
    spec.loader.exec_module(mod)
    return mod


# Load dependency chain — order matters!
_load_root_module("lexicon")
_load_root_module("rules")
_translator_mod = _load_root_module("translator")


class SindarinTranslator(_translator_mod.SindarinTranslator):
    """
    Subclass that fixes the default lexicon path to the absolute location
    of data/pt-sindarin.json, regardless of the server's working directory.
    """
    _DEFAULT_LEXICON = os.path.join(_ROOT, "data", "pt-sindarin.json")

    def __init__(self, lexicon_path: str | None = None):
        super().__init__(lexicon_path or self._DEFAULT_LEXICON)


__all__ = ["SindarinTranslator"]

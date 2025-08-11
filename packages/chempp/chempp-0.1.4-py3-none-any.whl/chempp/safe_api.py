"""
chempp.safe_api
Compact Safe API wrapper for the Chem++ package.

This file expects `chempp.interpreter` to exist in the same package and provide:
- Parser, lex, or parse() functionality
- Interpreter class with interpret / interpret_async methods
- chem_registry (optional)
- molecular_weight or PubChem helpers (optional)
"""

import importlib
import inspect
import asyncio
import threading
import json
import os
from typing import Optional, Any

from . import version as _v

# Discover interpreter module inside the package
try:
    from . import interpreter as interpreter_mod
except Exception as e:
    interpreter_mod = None

# Simple cache for PubChem fallback (local file)
_CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", ".chempp_safe_cache")
os.makedirs(_CACHE_DIR, exist_ok=True)
_PUBCHEM_CACHE = os.path.join(_CACHE_DIR, "pubchem_simple.json")
_PUBCHEM_LOCK = threading.Lock()


def _load_pubchem_cache():
    with _PUBCHEM_LOCK:
        try:
            with open(_PUBCHEM_CACHE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}


def _save_pubchem_cache(d):
    with _PUBCHEM_LOCK:
        with open(_PUBCHEM_CACHE, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=2)


def _cache_get(key):
    d = _load_pubchem_cache()
    return d.get(key)


def _cache_set(key, value):
    d = _load_pubchem_cache()
    d[key] = {"value": value, "ts": asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else None}
    _save_pubchem_cache(d)


# Canonical interpreter instance (lazy)
_CANONICAL_INTERPRETER = None
_CANONICAL_LOCK = threading.Lock()


def get_interpreter_instance():
    """Return a singleton interpreter instance. Instantiate if needed."""
    global _CANONICAL_INTERPRETER
    with _CANONICAL_LOCK:
        if _CANONICAL_INTERPRETER is None:
            if interpreter_mod and hasattr(interpreter_mod, "Interpreter"):
                try:
                    _CANONICAL_INTERPRETER = interpreter_mod.Interpreter()
                except Exception:
                    # try a no-arg instantiation fallback
                    _CANONICAL_INTERPRETER = interpreter_mod.Interpreter if inspect.isclass(interpreter_mod.Interpreter) else None
            else:
                raise RuntimeError("Interpreter module not available in package. Ensure chempp.interpreter is present.")
        return _CANONICAL_INTERPRETER


# Parsing helper
def parse(code_str: str):
    """
    Parse using the package parser. This wrapper tries to handle several parser shapes:
    - If interpreter_mod has Parser class and a lex function, use both.
    - If interpreter_mod provides parse(code_str) function, call it.
    """
    if interpreter_mod is None:
        raise RuntimeError("No interpreter module found (chempp.interpreter).")

    # prefer Parser + lexer
    Parser = getattr(interpreter_mod, "Parser", None)
    lex = getattr(interpreter_mod, "lex", None)
    parse_func = getattr(interpreter_mod, "parse", None)
    if Parser and lex:
        tokens = lex(code_str)
        parser = Parser(tokens)
        return parser.parse()
    elif parse_func and callable(parse_func):
        return parse_func(code_str)
    elif Parser:
        # try instantiate with raw string if supported
        try:
            p = Parser(code_str)
            return p.parse()
        except Exception as e:
            raise RuntimeError(f"Parser present but could not parse: {e}")
    else:
        raise RuntimeError("No parser available in chempp.interpreter.")


# Analyze helper (optional)
_static_analyzer = getattr(interpreter_mod, "StaticAnalyzer", None)


def analyze(ast):
    """Run static analyzer if present. Returns {'errors':[], 'warnings':[]}"""
    if _static_analyzer is None:
        return {"errors": [], "warnings": [], "note": "No static analyzer found"}
    try:
        sa = _static_analyzer()
        if hasattr(sa, "analyze"):
            sa.analyze(ast)
        return sa.report() if hasattr(sa, "report") else {"errors": getattr(sa, "errors", []), "warnings": getattr(sa, "warnings", [])}
    except Exception as e:
        return {"errors": [f"Static analyzer crashed: {e}"], "warnings": []}


# Interpretation helpers (sync and async)
async def interpret_async(ast, env=None):
    interp = get_interpreter_instance()
    # run analyzer first
    rep = analyze(ast)
    if rep.get("errors"):
        raise RuntimeError(f"Static analysis errors: {rep['errors']}")
    # prefer interpret_async on interpreter
    if hasattr(interp, "interpret_async") and inspect.iscoroutinefunction(interp.interpret_async):
        return await interp.interpret_async(ast, env)
    else:
        # run sync interpret in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        func = lambda: interp.interpret(ast, env)
        return await loop.run_in_executor(None, func)


def interpret(ast, env=None):
    interp = get_interpreter_instance()
    rep = analyze(ast)
    if rep.get("errors"):
        raise RuntimeError(f"Static analysis errors: {rep['errors']}")
    if hasattr(interp, "interpret") and not inspect.iscoroutinefunction(interp.interpret):
        return interp.interpret(ast, env)
    else:
        # fallback, run async
        return asyncio.run(interpret_async(ast, env))


def run(code_str: str, async_mode: bool = False):
    ast = parse(code_str)
    if async_mode:
        return interpret_async(ast)
    else:
        return interpret(ast)


async def run_async(code_str: str):
    ast = parse(code_str)
    return await interpret_async(ast)


# Simple unified molecular weight accessor
def get_molecular_weight(name: str):
    # try to use package function if present
    if interpreter_mod:
        mw_fn = getattr(interpreter_mod, "molecular_weight", None) or getattr(interpreter_mod, "get_molecular_weight", None)
        if callable(mw_fn):
            try:
                return float(mw_fn(name))
            except Exception:
                pass
    # fallback to local cache dictionary
    val = _cache_get(name + "::MolecularWeight")
    if val:
        return float(val["value"])
    # trivial local fallback for very common molecules
    local_fallbacks = {
        "H2O": 18.015,
        "CO2": 44.01,
        "O2": 31.998,
        "NaCl": 58.44,
    }
    if name in local_fallbacks:
        _cache_set(name + "::MolecularWeight", local_fallbacks[name])
        return float(local_fallbacks[name])
    raise RuntimeError("Molecular weight lookup unavailable for: " + name)


# Cleanup helper
def cleanup_interpreter(aggressive: bool = False):
    global _CANONICAL_INTERPRETER
    if _CANONICAL_INTERPRETER is None:
        return
    interp = _CANONICAL_INTERPRETER
    # call close if exists
    try:
        if hasattr(interp, "close") and callable(interp.close):
            interp.close()
    except Exception:
        pass
    # clear known env attributes if present
    try:
        if hasattr(interp, "global_env"):
            ge = getattr(interp, "global_env")
            if hasattr(ge, "vars"):
                try:
                    ge.vars.clear()
                except Exception:
                    pass
    except Exception:
        pass
    if aggressive:
        with _CANONICAL_LOCK:
            _CANONICAL_INTERPRETER = None


# Small diagnostics
def discovery_report():
    return {
        "interpreter_module": interpreter_mod.__name__ if interpreter_mod else None,
        "has_parser": hasattr(interpreter_mod, "Parser") or hasattr(interpreter_mod, "parse") if interpreter_mod else False,
        "has_static_analyzer": _static_analyzer is not None,
        "version": getattr(_v, "__version__", "unknown"),
    }


# Exports
__all__ = [
    "get_interpreter_instance", "parse", "analyze",
    "interpret", "interpret_async", "run", "run_async",
    "get_molecular_weight", "cleanup_interpreter", "discovery_report"
]

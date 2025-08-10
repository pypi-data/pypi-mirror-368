from __future__ import annotations

# Provide a safe alias for pywintypes.com_error without
# triggering static checker issues and allowing non-Windows envs.
try:  # pragma: no cover - environment-dependent
    import pywintypes as _pywintypes  # type: ignore
except ImportError:  # pragma: no cover - environment-dependent
    _pywintypes = None  # type: ignore

if _pywintypes is not None:  # pragma: no cover
    com_error = getattr(_pywintypes, "com_error", Exception)
else:  # pragma: no cover
    com_error = Exception

__all__ = [
    "com_error",
]

"""mdjango — a drop-in markdown-documentation Django app.

Point it at a tree of markdown (``MDJANGO_CONTENT_DIR``), include :mod:`mdjango.urls`, and get a
themed documentation site — served at runtime and/or exported static. See ``CONTEXT.md`` for the
glossary and ``docs/adr/`` for the decisions.
"""

__all__ = ["__version__"]

try:
    from ._version import __version__
except ImportError:  # a source checkout that was never built (dev harness / tests)
    __version__ = "0.0.0+dev"

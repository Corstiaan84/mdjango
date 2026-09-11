"""Domain exceptions.

Mirrors the stack convention (mfo `features/common/exceptions.py`): a single base error lives here;
feature-specific errors subclass it in their own feature package. Adapters (views, the build
command) catch `MdjangoError` for broad handling or a specific subclass for targeted handling —
they never leak framework errors out of the feature layer.
"""

from __future__ import annotations


class MdjangoError(Exception):
    """Base for every mdjango domain error."""


class ContentError(MdjangoError):
    """A structural problem in the content tree (surfaced by the build; the CI content gate)."""

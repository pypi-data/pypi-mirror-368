from __future__ import annotations

import warnings

warnings.warn(
    "inframe.legacy is deprecated and will be removed in a future release. "
    "Migrate to inframe.Recorder and inframe.Querier (v2 API).",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export legacy shims from the top-level inframe package
from .recorder import ContextRecorder  # noqa: F401
from .query import ContextQuery  # noqa: F401

__all__ = ["ContextRecorder", "ContextQuery"]



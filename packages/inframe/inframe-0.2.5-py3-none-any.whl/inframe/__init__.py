from __future__ import annotations

import warnings

# Canonical v2 API lives under this package
from .recorder import ContextRecorder as Recorder  # alias
from .query import ContextQuery as Querier  # alias


def _deprecated(name: str):
    warnings.warn(
        f"inframe.{name} is deprecated and will be removed in a future release. "
        "Use inframe.Recorder and inframe.Querier instead (v2 API), or import from inframe.legacy.",
        DeprecationWarning,
        stacklevel=3,
    )


# Legacy API shims (deprecated but still available)
class ContextRecorder(Recorder):  # type: ignore
    def __init__(self, *args, **kwargs):
        _deprecated("ContextRecorder")
        super().__init__(*args, **kwargs)


class ContextQuery(Querier):  # type: ignore
    def __init__(self, *args, **kwargs):
        _deprecated("ContextQuery")
        super().__init__(*args, **kwargs)


__all__ = ["Recorder", "Querier", "ContextRecorder", "ContextQuery"]
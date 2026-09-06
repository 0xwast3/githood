"""githood — turn a one-page spec into a repo that already builds."""

from .spec import Spec, SpecError, parse, load  # noqa: F401
from .scaffold import build, plan  # noqa: F401

__version__ = "0.1.0"

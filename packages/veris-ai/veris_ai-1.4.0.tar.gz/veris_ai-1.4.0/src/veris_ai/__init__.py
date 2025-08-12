"""Veris AI Python SDK."""

from typing import Any

__version__ = "0.1.0"

# Import lightweight modules that only use base dependencies
from .jaeger_interface import JaegerClient
from .models import ResponseExpectation
from .tool_mock import veris

# Lazy import for modules with heavy dependencies
_instrument = None


def instrument(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
    """Lazy loader for the instrument function from braintrust_tracing.

    This function requires the 'instrument' extra dependencies:
    pip install veris-ai[instrument]
    """
    global _instrument  # noqa: PLW0603
    if _instrument is None:
        try:
            from .braintrust_tracing import instrument as _instrument_impl  # noqa: PLC0415

            _instrument = _instrument_impl
        except ImportError as e:
            error_msg = (
                "The 'instrument' function requires additional dependencies. "
                "Please install them with: pip install veris-ai[instrument]"
            )
            raise ImportError(error_msg) from e
    return _instrument(*args, **kwargs)


__all__ = ["veris", "JaegerClient", "instrument", "ResponseExpectation"]

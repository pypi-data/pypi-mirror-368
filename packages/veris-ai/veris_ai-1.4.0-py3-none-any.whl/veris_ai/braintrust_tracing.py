"""Non-invasive Braintrust + Jaeger (OTEL) instrumentation helper for the `openai-agents` SDK.

Typical usage
-------------
>>> from our_sdk import braintrust_tracing
>>> braintrust_tracing.instrument(service_name="openai-agent")

After calling :func:`instrument`, any later call to
``agents.set_trace_processors([...])`` will be transparently patched so that:
  • the list always contains a BraintrustTracingProcessor (for Braintrust UI)
  • *and* an OpenTelemetry bridge processor that mirrors every span to the
    global OTEL tracer provider (Jaeger by default).

Goal: deliver full OTEL compatibility while keeping the official Braintrust
SDK integration unchanged – **no code modifications required** besides the
single `instrument()` call.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, cast

import wrapt  # type: ignore[import-untyped, import-not-found]
from braintrust.wrappers.openai import (
    BraintrustTracingProcessor,  # type: ignore[import-untyped, import-not-found]
)
from opentelemetry import context as otel_context  # type: ignore[import-untyped, import-not-found]
from opentelemetry import trace  # type: ignore[import-untyped, import-not-found]
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,  # type: ignore[import-untyped, import-not-found]
)
from opentelemetry.sdk.resources import (  # type: ignore[import-untyped, import-not-found]
    SERVICE_NAME,
    Resource,
)
from opentelemetry.sdk.trace import TracerProvider  # type: ignore[import-untyped, import-not-found]
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,  # type: ignore[import-untyped, import-not-found]
)
from opentelemetry.trace import SpanKind  # type: ignore[import-untyped, import-not-found]

from veris_ai.tool_mock import _session_id_context

# ---------------------------------------------------------------------------
#  Optional import of *agents* – we fail lazily at runtime if missing.
# ---------------------------------------------------------------------------
try:
    import agents  # type: ignore[import-untyped]  # noqa: TC002
    from agents import TracingProcessor  # type: ignore[import-untyped]

    try:
        from agents.tracing import get_trace_provider  # type: ignore[import-untyped]
    except ImportError:
        # Fallback for newer versions that have GLOBAL_TRACE_PROVIDER instead
        from agents.tracing import (  # type: ignore[import-untyped, attr-defined, import-not-found]
            GLOBAL_TRACE_PROVIDER,  # type: ignore[import-untyped, attr-defined, import-not-found]
        )

        get_trace_provider = lambda: GLOBAL_TRACE_PROVIDER  # type: ignore[no-any-return]  # noqa: E731
except ModuleNotFoundError as exc:  # pragma: no cover
    _IMPORT_ERR: ModuleNotFoundError | None = exc
    TracingProcessor = object  # type: ignore[assignment, misc]
    get_trace_provider = None  # type: ignore[assignment]
else:
    _IMPORT_ERR = None

__all__ = ["instrument"]

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
#  Internal helper – OTEL bridge processor
# ---------------------------------------------------------------------------


class AgentsOTELBridgeProcessor(TracingProcessor):  # type: ignore[misc]
    """Mirrors every Agents span into a dedicated OTEL tracer provider."""

    def __init__(
        self,
        braintrust_processor: BraintrustTracingProcessor,
        *,
        service_name: str,  # noqa: ARG002
        tracer_provider: trace.TracerProvider,
    ) -> None:  # noqa: D401,E501
        self._braintrust = braintrust_processor
        self._tracer = tracer_provider.get_tracer(__name__)
        self._otel_spans: dict[str, trace.Span] = {}
        self._provider = tracer_provider

    # ----------------------------- utils ---------------------------------
    @staticmethod
    def _flatten(prefix: str, obj: Any, out: dict[str, Any]) -> None:  # noqa: PLR0911, ANN401
        """Flatten complex objects into OTEL-compatible primitives."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                AgentsOTELBridgeProcessor._flatten(f"{prefix}.{k}" if prefix else str(k), v, out)
        elif isinstance(obj, str | int | float | bool) or obj is None:
            out[prefix] = obj
        elif isinstance(obj, list | tuple):
            try:
                if all(isinstance(i, str | int | float | bool) or i is None for i in obj):
                    out[prefix] = list(obj)
                else:
                    out[prefix] = json.dumps(obj, default=str)
            except Exception:  # pragma: no cover – defensive
                out[prefix] = json.dumps(obj, default=str)
        else:
            out[prefix] = str(obj)

    def _log_data_attributes(self, span_obj: agents.tracing.Span) -> dict[str, Any]:  # type: ignore[name-defined]
        data = self._braintrust._log_data(span_obj)  # pyright: ignore[reportPrivateUsage]  # noqa: SLF001
        flat: dict[str, Any] = {}
        self._flatten("bt", data, flat)

        # Add session_id if available
        session_id = _session_id_context.get()
        if session_id:
            flat["veris.session_id"] = session_id

        return {k: v for k, v in flat.items() if v is not None}

    # --------------------- Agents lifecycle hooks ------------------------
    def on_trace_start(self, trace_obj: Any) -> None:  # noqa: ANN401, D102
        # Get session_id at trace start
        session_id = _session_id_context.get()
        attributes = {"veris.session_id": session_id} if session_id else {}

        otel_span = self._tracer.start_span(
            name=trace_obj.name or "agent-trace",
            kind=SpanKind.INTERNAL,
            attributes=attributes,
        )
        self._otel_spans[trace_obj.trace_id] = otel_span
        logger.info(f"VERIS AI BraintrustTracingProcessor: on_trace_start: {trace_obj.trace_id}")

    def on_trace_end(self, trace_obj: Any) -> None:  # noqa: ANN401, D102
        span = self._otel_spans.pop(trace_obj.trace_id, None)
        if span:
            span.end()

    def on_span_start(self, span: Any) -> None:  # noqa: ANN401, D102
        parent_otel = (
            self._otel_spans.get(span.parent_id)
            if span.parent_id
            else self._otel_spans.get(span.trace_id)
        )
        parent_ctx = (
            trace.set_span_in_context(parent_otel) if parent_otel else otel_context.get_current()
        )

        # Get session_id at span start
        session_id = _session_id_context.get()
        attributes = {"veris.session_id": session_id} if session_id else {}

        child = self._tracer.start_span(
            name=span.span_data.__class__.__name__,
            context=parent_ctx,
            kind=SpanKind.INTERNAL,
            attributes=attributes,
        )
        self._otel_spans[span.span_id] = child
        logger.info(f"VERIS AI BraintrustTracingProcessor: on_span_start: {span.span_id}")

    def on_span_end(self, span: Any) -> None:  # noqa: ANN401, D102
        child = self._otel_spans.pop(span.span_id, None)
        logger.info(f"VERIS AI BraintrustTracingProcessor: on_span_end: {span.span_id}")
        if child:
            for k, v in self._log_data_attributes(span).items():
                try:
                    child.set_attribute(k, v)
                except Exception:  # pragma: no cover – bad value type  # noqa: S112
                    continue
            child.end()

    # --------------------- house-keeping ---------------------------------
    def shutdown(self) -> None:  # noqa: D401
        provider = cast("TracerProvider", self._provider)
        provider.shutdown()  # type: ignore[attr-defined]

    def force_flush(self) -> None:  # noqa: D401
        provider = cast("TracerProvider", self._provider)
        provider.force_flush()  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
#  Public entry point
# ---------------------------------------------------------------------------

_PATCHED: bool = False  # ensure idempotent patching


def instrument(
    *,
    service_name: str | None = None,
    otlp_endpoint: str | None = None,
) -> None:
    """Bootstrap Braintrust + OTEL instrumentation and patch Agents SDK.

    Invoke once at any point before `set_trace_processors` is called.
    """
    global _PATCHED  # noqa: PLW0603
    if _PATCHED:
        return  # already done

    if _IMPORT_ERR is not None or get_trace_provider is None:  # pragma: no cover
        error_msg = "The `agents` package is required but not installed"
        raise RuntimeError(error_msg) from _IMPORT_ERR

    # ------------------ 0. Validate inputs -----------------------------
    # Resolve service name ─ explicit argument → env var → error
    if not service_name or not str(service_name).strip():
        service_name = os.getenv("VERIS_SERVICE_NAME")

    if not service_name or not str(service_name).strip():
        error_msg = (
            "`service_name` must be provided either as an argument or via the "
            "VERIS_SERVICE_NAME environment variable"
        )
        raise ValueError(error_msg)

    # Resolve OTLP endpoint ─ explicit argument → env var → error
    if not otlp_endpoint or not str(otlp_endpoint).strip():
        otlp_endpoint = os.getenv("VERIS_OTLP_ENDPOINT")

    if not otlp_endpoint or not str(otlp_endpoint).strip():
        error_msg = (
            "`otlp_endpoint` must be provided either as an argument or via the "
            "VERIS_OTLP_ENDPOINT environment variable"
        )
        raise ValueError(error_msg)

    logger.info(f"service_name: {service_name}")
    logger.info(f"otlp_endpoint: {otlp_endpoint}")

    # ------------------ 1. Configure OTEL provider ---------------------
    # We create our own provider instance and do NOT set it globally.
    # This avoids conflicts with any other OTEL setup in the application.
    otel_provider = TracerProvider(resource=Resource.create({SERVICE_NAME: service_name}))
    otel_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)),
    )

    # ------------------ 2. Define wrapper for patching -------------------
    def _wrapper(wrapped: Any, instance: Any, args: Any, kwargs: Any) -> Any:  # noqa: ANN401, ARG001
        """This function wraps `TraceProvider.set_processors`."""
        processors = args[0] if args else []

        # Find the user's Braintrust processor to pass to our bridge.
        bt_processor = next(
            (p for p in processors if isinstance(p, BraintrustTracingProcessor)), None
        )

        # If no Braintrust processor is present, our bridge is useless.
        # Also, if a bridge is already there, don't add another one.
        has_bridge = any(isinstance(p, AgentsOTELBridgeProcessor) for p in processors)
        if not bt_processor or has_bridge:
            return wrapped(*args, **kwargs)

        # Create the bridge and add it to the list of processors.
        bridge = AgentsOTELBridgeProcessor(
            bt_processor,
            service_name=service_name,
            tracer_provider=otel_provider,
        )
        new_processors = list(processors) + [bridge]

        # Call the original function with the augmented list.
        new_args = (new_processors,) + args[1:]
        logger.info(f"VERIS AI BraintrustTracingProcessor: {new_args}")
        return wrapped(*new_args, **kwargs)

    # ------------------ 3. Patch the provider instance -------------------
    # This is more robust than patching the function, as it's independent
    # of how the user imports `set_trace_processors`.
    provider_instance = get_trace_provider()
    wrapt.wrap_function_wrapper(provider_instance, "set_processors", _wrapper)

    _PATCHED = True

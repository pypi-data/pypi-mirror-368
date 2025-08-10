# lighthouse/_client/ingest_exporter.py
import httpx, json, time
from typing import Sequence, Dict, Any, DefaultDict, List, Optional
import os
import time
import httpx
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

from lighthouse.logger import lighthouse_logger as log
from lighthouse._client.attributes import lighthouseOtelSpanAttributes


# ---------------------------
# helper
# ---------------------------


def _maybe_json(value):
    """Convert dict/list values to JSON strings so they are serializable."""
    if isinstance(value, (dict, list)):
        try:
            return json.dumps(value)
        except Exception:
            return str(value)
    return value


class LighthouseIngestExporter(SpanExporter):
    """Custom OpenTelemetry exporter that POSTs Lighthouse spans to the FastAPI ingest endpoint.

    The exporter converts finished OTEL spans into the `IngestSpan` JSON structure that
    `/api/ingest/spans` expects and sends them in batches.  Authentication is handled with
    a Supabase JWT (taken from the `SUPABASE_JWT` environment variable) sent as a Bearer token.
    """

    _INGEST_ROUTE = "/api/ingest/spans"

    def __init__(self, host: str, timeout: int | None = 5):
        self._timeout = timeout
        self._client = httpx.Client(timeout=timeout)
        self._url = host.rstrip("/") + self._INGEST_ROUTE

        # Authentication: prefer user API key over Supabase JWT
        self._api_key = os.getenv("LIGHTHOUSE_API_KEY")

        if not self._api_key:
            # fall back to Supabase JWT for backward compatibility
            token = os.getenv("SUPABASE_JWT")
            if not token:
                log.warning(
                    "Authentication: neither LIGHTHOUSE_API_KEY nor SUPABASE_JWT is set – requests will fail with 401"
                )
            self._auth_header_name = "Authorization"
            self._auth_header_value = f"Bearer {token}" if token else None
        else:
            self._auth_header_name = "X-API-KEY"
            self._auth_header_value = self._api_key

        # Buffer spans by trace until root span is available so backend always sees a root
        self._trace_buffers: Dict[str, List[ReadableSpan]] = {}
        self._trace_first_seen_ns: Dict[str, int] = {}
        self._trace_root_seen: Dict[str, bool] = {}
        # Max buffering time before giving up (seconds)
        self._buffer_timeout_s: float = float(os.getenv("LIGHTHOUSE_EXPORTER_BUFFER_TIMEOUT_S", "5"))

    # ------------------------------------------------------------------
    # OpenTelemetry-SpanExporter interface
    # ------------------------------------------------------------------
    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        if not spans:
            return SpanExportResult.SUCCESS

        now_ns = time.time_ns()

        # Stage incoming spans by trace
        traces_to_consider = set()
        for s in spans:
            trace_id = f"{s.context.trace_id:032x}"
            traces_to_consider.add(trace_id)
            buf = self._trace_buffers.setdefault(trace_id, [])
            if trace_id not in self._trace_first_seen_ns:
                self._trace_first_seen_ns[trace_id] = now_ns
            # Buffer until we are sure we also have the root span
            buf.append(s)
            if s.parent is None:
                self._trace_root_seen[trace_id] = True

        # Flush any traces that have their root, or expired
        for trace_id in list(traces_to_consider):
            has_root = self._trace_root_seen.get(trace_id, False)
            age_s = (now_ns - self._trace_first_seen_ns.get(trace_id, now_ns)) / 1e9
            should_flush = has_root or age_s >= self._buffer_timeout_s

            if not should_flush:
                continue

            spans_to_send = self._trace_buffers.pop(trace_id, [])
            self._trace_first_seen_ns.pop(trace_id, None)
            self._trace_root_seen.pop(trace_id, None)

            if not spans_to_send:
                continue

            # If no root present even after timeout, drop with error to avoid backend rejection
            if not has_root:
                log.error(
                    "Exporter drop: no root span observed for trace %s after %.2fs; dropping %d spans",
                    trace_id,
                    age_s,
                    len(spans_to_send),
                )
                continue

            payload = {"spans": [self._map_span(s) for s in spans_to_send]}
            headers: Dict[str, str] = {"Content-Type": "application/json"}
            if self._auth_header_value:
                headers[self._auth_header_name] = self._auth_header_value

            try:
                resp = self._client.post(self._url, json=payload, headers=headers)

                if resp.status_code >= 400:
                    try:
                        body = resp.json()
                    except Exception:
                        body = resp.text
                    log.error(
                        "Ingest exporter error: %s %s - Response: %s",
                        resp.status_code,
                        resp.reason_phrase,
                        body,
                    )
                    # continue flushing others; report failure at end
                    # Note: returning FAILURE triggers retry in some processors; we handle per-batch
                    return SpanExportResult.FAILURE
            except Exception as e:
                log.error("Ingest exporter transport error: %s", e)
                return SpanExportResult.FAILURE

        return SpanExportResult.SUCCESS

    def shutdown(self):
        self._client.close()
        return super().shutdown()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _map_span(self, span: ReadableSpan) -> Dict[str, Any]:
        """Translate an OTEL ReadableSpan to the backend `IngestSpan` schema."""
        # collect attributes
        attrs = {k: _maybe_json(v) for k, v in span.attributes.items()}

        # If this is a root span (no parent) and we have end_time, add latency attribute
        if span.parent is None and span.end_time is not None and span.start_time is not None:
            latency_ms = int((span.end_time - span.start_time) / 1e6)  # ns -> ms
            attrs["lh.latency_ms"] = latency_ms

        # Helper to safely fetch an attribute
        def _attr(key: str, default: Any = None):
            return attrs.get(key, default)

        # Helper: parse JSON string back to dict if needed
        def _to_dict(value: Any) -> Any:
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except Exception:
                    return None
            return value

        started_at_s = span.start_time / 1_000_000_000  # ns → seconds
        ended_at_s = span.end_time / 1_000_000_000 if span.end_time else None
        latency_ms: int | None = None
        if ended_at_s is not None:
            latency_ms = int((span.end_time - span.start_time) / 1_000_000)  # ns → ms

        # observation type defaults to "span" if not set
        span_type = _attr(lighthouseOtelSpanAttributes.OBSERVATION_TYPE, "span")

        # Globally-unique span identifier = trace_id + span_id (48 hex chars)
        span_id_global = f"{span.context.trace_id:032x}{span.context.span_id:016x}"

        parent_global_id = (
            f"{span.context.trace_id:032x}{span.parent.span_id:016x}"
            if span.parent
            else None
        )

        # Normalize cost details to ensure total_cost is present
        raw_cost = _to_dict(_attr(lighthouseOtelSpanAttributes.OBSERVATION_COST_DETAILS))
        if isinstance(raw_cost, dict):
            if "total_cost" not in raw_cost and "total" in raw_cost:
                try:
                    raw_cost["total_cost"] = float(raw_cost.get("total") or 0.0)
                except Exception:
                    raw_cost["total_cost"] = raw_cost.get("total")

        ingest_span: Dict[str, Any] = {
            "span_id": span_id_global,
            "trace_id": f"{span.context.trace_id:032x}",
            "agent_name": _attr("agent_name", "unknown"),
            "framework": _attr("framework", "Unknown"),
            "agent_version": _attr("agent_version"),
            "span_type": span_type,
            "name": span.name,
            "status": "error" if span.status.is_ok is False else "completed",
            "started_at": started_at_s,
            "ended_at": ended_at_s,
            "latency_ms": latency_ms,
            # Generation-specific fields (present for LLM calls)
            "model_name": _attr(lighthouseOtelSpanAttributes.OBSERVATION_MODEL),
            "model_parameters": _to_dict(_attr(lighthouseOtelSpanAttributes.OBSERVATION_MODEL_PARAMETERS)),
            "usage_details": _to_dict(_attr(lighthouseOtelSpanAttributes.OBSERVATION_USAGE_DETAILS)),
            "cost_details": raw_cost,
            "attributes": attrs.get(lighthouseOtelSpanAttributes.OBSERVATION_METADATA),
            "io": {
                "input": attrs.get(lighthouseOtelSpanAttributes.OBSERVATION_INPUT),
                "output": attrs.get(lighthouseOtelSpanAttributes.OBSERVATION_OUTPUT),
            },
            "error": _attr("error"),
            "parent_span_id": parent_global_id,
        }

        # Ensure prompt linkage attributes are forwarded inside the attributes payload
        try:
            prompt_attrs = {}
            for key in ("prompt_version_id", "prompt_id", "prompt_hash", "bound_agent_version_id"):
                if key in attrs and attrs.get(key) is not None:
                    prompt_attrs[key] = attrs.get(key)

            if prompt_attrs:
                # Merge with existing observation metadata if present
                if isinstance(ingest_span.get("attributes"), dict):
                    merged = dict(ingest_span["attributes"])  # type: ignore[index]
                    merged.update(prompt_attrs)
                    ingest_span["attributes"] = merged
                else:
                    ingest_span["attributes"] = prompt_attrs
        except Exception:
            # Best-effort; do not block export if anything goes wrong here
            pass

        # Debug: log the span data being sent
        log.debug(f"Sending span: {ingest_span}")
        
        return ingest_span
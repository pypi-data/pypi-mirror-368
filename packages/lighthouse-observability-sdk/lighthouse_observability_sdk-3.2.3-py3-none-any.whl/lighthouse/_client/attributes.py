"""Span attribute management for lighthouse OpenTelemetry integration.

This module defines constants and functions for managing OpenTelemetry span attributes
used by lighthouse. It provides a structured approach to creating and manipulating
attributes for different span types (trace, span, generation) while ensuring consistency.

The module includes:
- Attribute name constants organized by category
- Functions to create attribute dictionaries for different entity types
- Utilities for serializing and processing attribute values
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union

from lighthouse._utils.serializer import EventSerializer
from lighthouse.model import PromptClient
from lighthouse.types import MapValue, SpanLevel


class lighthouseOtelSpanAttributes:
    # lighthouse-Trace attributes
    TRACE_NAME = "lighthouse.trace.name"
    TRACE_USER_ID = "user.id"
    TRACE_SESSION_ID = "session.id"
    TRACE_TAGS = "lighthouse.trace.tags"
    TRACE_PUBLIC = "lighthouse.trace.public"
    TRACE_METADATA = "lighthouse.trace.metadata"
    TRACE_INPUT = "lighthouse.trace.input"
    TRACE_OUTPUT = "lighthouse.trace.output"

    # lighthouse-observation attributes
    OBSERVATION_TYPE = "lighthouse.observation.type"
    OBSERVATION_METADATA = "lighthouse.observation.metadata"
    OBSERVATION_LEVEL = "lighthouse.observation.level"
    OBSERVATION_STATUS_MESSAGE = "lighthouse.observation.status_message"
    OBSERVATION_INPUT = "lighthouse.observation.input"
    OBSERVATION_OUTPUT = "lighthouse.observation.output"

    # lighthouse-observation of type Generation attributes
    OBSERVATION_COMPLETION_START_TIME = "lighthouse.observation.completion_start_time"
    OBSERVATION_MODEL = "lighthouse.observation.model.name"
    OBSERVATION_MODEL_PARAMETERS = "lighthouse.observation.model.parameters"
    OBSERVATION_USAGE_DETAILS = "lighthouse.observation.usage_details"
    OBSERVATION_COST_DETAILS = "lighthouse.observation.cost_details"
    OBSERVATION_PROMPT_NAME = "lighthouse.observation.prompt.name"
    OBSERVATION_PROMPT_VERSION = "lighthouse.observation.prompt.version"

    # General
    ENVIRONMENT = "lighthouse.environment"
    RELEASE = "lighthouse.release"
    VERSION = "lighthouse.version"

    # Internal
    AS_ROOT = "lighthouse.internal.as_root"


def create_trace_attributes(
    *,
    name: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    version: Optional[str] = None,
    release: Optional[str] = None,
    input: Optional[Any] = None,
    output: Optional[Any] = None,
    metadata: Optional[Any] = None,
    tags: Optional[List[str]] = None,
    public: Optional[bool] = None,
) -> dict:
    attributes = {
        lighthouseOtelSpanAttributes.TRACE_NAME: name,
        lighthouseOtelSpanAttributes.TRACE_USER_ID: user_id,
        lighthouseOtelSpanAttributes.TRACE_SESSION_ID: session_id,
        lighthouseOtelSpanAttributes.VERSION: version,
        lighthouseOtelSpanAttributes.RELEASE: release,
        lighthouseOtelSpanAttributes.TRACE_INPUT: _serialize(input),
        lighthouseOtelSpanAttributes.TRACE_OUTPUT: _serialize(output),
        lighthouseOtelSpanAttributes.TRACE_TAGS: tags,
        lighthouseOtelSpanAttributes.TRACE_PUBLIC: public,
        **_flatten_and_serialize_metadata(metadata, "trace"),
    }

    return {k: v for k, v in attributes.items() if v is not None}


def create_span_attributes(
    *,
    metadata: Optional[Any] = None,
    input: Optional[Any] = None,
    output: Optional[Any] = None,
    level: Optional[SpanLevel] = None,
    status_message: Optional[str] = None,
    version: Optional[str] = None,
) -> dict:
    attributes = {
        lighthouseOtelSpanAttributes.OBSERVATION_TYPE: "span",
        lighthouseOtelSpanAttributes.OBSERVATION_LEVEL: level,
        lighthouseOtelSpanAttributes.OBSERVATION_STATUS_MESSAGE: status_message,
        lighthouseOtelSpanAttributes.VERSION: version,
        lighthouseOtelSpanAttributes.OBSERVATION_INPUT: _serialize(input),
        lighthouseOtelSpanAttributes.OBSERVATION_OUTPUT: _serialize(output),
        **_flatten_and_serialize_metadata(metadata, "observation"),
    }

    return {k: v for k, v in attributes.items() if v is not None}


def create_generation_attributes(
    *,
    name: Optional[str] = None,
    completion_start_time: Optional[datetime] = None,
    metadata: Optional[Any] = None,
    level: Optional[SpanLevel] = None,
    status_message: Optional[str] = None,
    version: Optional[str] = None,
    model: Optional[str] = None,
    model_parameters: Optional[Dict[str, MapValue]] = None,
    input: Optional[Any] = None,
    output: Optional[Any] = None,
    usage_details: Optional[Dict[str, int]] = None,
    cost_details: Optional[Dict[str, float]] = None,
    prompt: Optional[PromptClient] = None,
) -> dict:
    attributes = {
        lighthouseOtelSpanAttributes.OBSERVATION_TYPE: "generation",
        lighthouseOtelSpanAttributes.OBSERVATION_LEVEL: level,
        lighthouseOtelSpanAttributes.OBSERVATION_STATUS_MESSAGE: status_message,
        lighthouseOtelSpanAttributes.VERSION: version,
        lighthouseOtelSpanAttributes.OBSERVATION_INPUT: _serialize(input),
        lighthouseOtelSpanAttributes.OBSERVATION_OUTPUT: _serialize(output),
        lighthouseOtelSpanAttributes.OBSERVATION_MODEL: model,
        lighthouseOtelSpanAttributes.OBSERVATION_PROMPT_NAME: prompt.name
        if prompt and not prompt.is_fallback
        else None,
        lighthouseOtelSpanAttributes.OBSERVATION_PROMPT_VERSION: prompt.version
        if prompt and not prompt.is_fallback
        else None,
        lighthouseOtelSpanAttributes.OBSERVATION_USAGE_DETAILS: _serialize(usage_details),
        lighthouseOtelSpanAttributes.OBSERVATION_COST_DETAILS: _serialize(cost_details),
        lighthouseOtelSpanAttributes.OBSERVATION_COMPLETION_START_TIME: _serialize(
            completion_start_time
        ),
        lighthouseOtelSpanAttributes.OBSERVATION_MODEL_PARAMETERS: _serialize(
            model_parameters
        ),
        **_flatten_and_serialize_metadata(metadata, "observation"),
    }

    return {k: v for k, v in attributes.items() if v is not None}


def _serialize(obj: Any) -> Optional[str]:
    return json.dumps(obj, cls=EventSerializer) if obj is not None else None


def _flatten_and_serialize_metadata(
    metadata: Any, type: Literal["observation", "trace"]
) -> dict:
    prefix = (
        lighthouseOtelSpanAttributes.OBSERVATION_METADATA
        if type == "observation"
        else lighthouseOtelSpanAttributes.TRACE_METADATA
    )

    metadata_attributes: Dict[str, Union[str, int, None]] = {}

    if not isinstance(metadata, dict):
        metadata_attributes[prefix] = _serialize(metadata)
    else:
        for key, value in metadata.items():
            metadata_attributes[f"{prefix}.{key}"] = (
                value
                if isinstance(value, str) or isinstance(value, int)
                else _serialize(value)
            )

    return metadata_attributes

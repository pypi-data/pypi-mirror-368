"""OTEL span wrapper for lighthouse.

This module defines custom span classes that extend OpenTelemetry spans with
lighthouse-specific functionality. These wrapper classes provide methods for
creating, updating, and scoring various types of spans used in AI application tracing.

Classes:
- lighthouseSpanWrapper: Abstract base class for all lighthouse spans
- lighthouseSpan: Implementation for general-purpose spans
- lighthouseGeneration: Specialized span implementation for LLM generations

All span classes provide methods for media processing, attribute management,
and scoring integration specific to lighthouse's observability platform.
"""

from datetime import datetime
from time import time_ns
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Union,
    cast,
    overload,
)

from opentelemetry import trace as otel_trace_api
from opentelemetry.util._decorator import _AgnosticContextManager

from lighthouse.model import PromptClient

if TYPE_CHECKING:
    from lighthouse._client.client import lighthouse

from lighthouse._client.attributes import (
    lighthouseOtelSpanAttributes,
    create_generation_attributes,
    create_span_attributes,
    create_trace_attributes,
)
from lighthouse.logger import lighthouse_logger
from lighthouse.types import MapValue, ScoreDataType, SpanLevel


class lighthouseSpanWrapper:
    """Abstract base class for all lighthouse span types.

    This class provides common functionality for all lighthouse span types, including
    media processing, attribute management, and scoring. It wraps an OpenTelemetry
    span and extends it with lighthouse-specific features.

    Attributes:
        _otel_span: The underlying OpenTelemetry span
        _lighthouse_client: Reference to the parent lighthouse client
        trace_id: The trace ID for this span
        observation_id: The observation ID (span ID) for this span
    """

    def __init__(
        self,
        *,
        otel_span: otel_trace_api.Span,
        lighthouse_client: "lighthouse",
        as_type: Literal["span", "generation", "event"],
        input: Optional[Any] = None,
        output: Optional[Any] = None,
        metadata: Optional[Any] = None,
        environment: Optional[str] = None,
        version: Optional[str] = None,
        level: Optional[SpanLevel] = None,
        status_message: Optional[str] = None,
        completion_start_time: Optional[datetime] = None,
        model: Optional[str] = None,
        model_parameters: Optional[Dict[str, MapValue]] = None,
        usage_details: Optional[Dict[str, int]] = None,
        cost_details: Optional[Dict[str, float]] = None,
        prompt: Optional[PromptClient] = None,
    ):
        """Initialize a new lighthouse span wrapper.

        Args:
            otel_span: The OpenTelemetry span to wrap
            lighthouse_client: Reference to the parent lighthouse client
            as_type: The type of span ("span" or "generation")
            input: Input data for the span (any JSON-serializable object)
            output: Output data from the span (any JSON-serializable object)
            metadata: Additional metadata to associate with the span
            environment: The tracing environment
            version: Version identifier for the code or component
            level: Importance level of the span (info, warning, error)
            status_message: Optional status message for the span
            completion_start_time: When the model started generating the response
            model: Name/identifier of the AI model used (e.g., "gpt-4")
            model_parameters: Parameters used for the model (e.g., temperature, max_tokens)
            usage_details: Token usage information (e.g., prompt_tokens, completion_tokens)
            cost_details: Cost information for the model call
            prompt: Associated prompt template from lighthouse prompt management
        """
        self._otel_span = otel_span
        self._otel_span.set_attribute(
            lighthouseOtelSpanAttributes.OBSERVATION_TYPE, as_type
        )
        self._lighthouse_client = lighthouse_client

        self.trace_id = self._lighthouse_client._get_otel_trace_id(otel_span)
        self.id = self._lighthouse_client._get_otel_span_id(otel_span)

        self._environment = environment
        if self._environment is not None:
            self._otel_span.set_attribute(
                lighthouseOtelSpanAttributes.ENVIRONMENT, self._environment
            )

        # Handle media only if span is sampled
        if self._otel_span.is_recording():
            media_processed_input = self._process_media_and_apply_mask(
                data=input, field="input", span=self._otel_span
            )
            media_processed_output = self._process_media_and_apply_mask(
                data=output, field="output", span=self._otel_span
            )
            media_processed_metadata = self._process_media_and_apply_mask(
                data=metadata, field="metadata", span=self._otel_span
            )

            attributes = {}

            if as_type == "generation":
                attributes = create_generation_attributes(
                    input=media_processed_input,
                    output=media_processed_output,
                    metadata=media_processed_metadata,
                    version=version,
                    level=level,
                    status_message=status_message,
                    completion_start_time=completion_start_time,
                    model=model,
                    model_parameters=model_parameters,
                    usage_details=usage_details,
                    cost_details=cost_details,
                    prompt=prompt,
                )

            else:
                attributes = create_span_attributes(
                    input=media_processed_input,
                    output=media_processed_output,
                    metadata=media_processed_metadata,
                    version=version,
                    level=level,
                    status_message=status_message,
                )

            attributes.pop(lighthouseOtelSpanAttributes.OBSERVATION_TYPE, None)

            self._otel_span.set_attributes(
                {k: v for k, v in attributes.items() if v is not None}
            )

    def end(self, *, end_time: Optional[int] = None) -> "lighthouseSpanWrapper":
        """End the span, marking it as completed.

        This method ends the wrapped OpenTelemetry span, marking the end of the
        operation being traced. After this method is called, the span is considered
        complete and can no longer be modified.

        Args:
            end_time: Optional explicit end time in nanoseconds since epoch
        """
        self._otel_span.end(end_time=end_time)

        return self

    def update_trace(
        self,
        *,
        name: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        version: Optional[str] = None,
        input: Optional[Any] = None,
        output: Optional[Any] = None,
        metadata: Optional[Any] = None,
        tags: Optional[List[str]] = None,
        public: Optional[bool] = None,
    ) -> "lighthouseSpanWrapper":
        """Update the trace that this span belongs to.

        This method updates trace-level attributes of the trace that this span
        belongs to. This is useful for adding or modifying trace-wide information
        like user ID, session ID, or tags.

        Args:
            name: Updated name for the trace
            user_id: ID of the user who initiated the trace
            session_id: Session identifier for grouping related traces
            version: Version identifier for the application or service
            input: Input data for the overall trace
            output: Output data from the overall trace
            metadata: Additional metadata to associate with the trace
            tags: List of tags to categorize the trace
            public: Whether the trace should be publicly accessible
        """
        if not self._otel_span.is_recording():
            return self

        media_processed_input = self._process_media_and_apply_mask(
            data=input, field="input", span=self._otel_span
        )
        media_processed_output = self._process_media_and_apply_mask(
            data=output, field="output", span=self._otel_span
        )
        media_processed_metadata = self._process_media_and_apply_mask(
            data=metadata, field="metadata", span=self._otel_span
        )

        attributes = create_trace_attributes(
            name=name,
            user_id=user_id,
            session_id=session_id,
            version=version,
            input=media_processed_input,
            output=media_processed_output,
            metadata=media_processed_metadata,
            tags=tags,
            public=public,
        )

        self._otel_span.set_attributes(attributes)

        return self

    @overload
    def score(
        self,
        *,
        name: str,
        value: float,
        score_id: Optional[str] = None,
        data_type: Optional[Literal["NUMERIC", "BOOLEAN"]] = None,
        comment: Optional[str] = None,
        config_id: Optional[str] = None,
    ) -> None: ...

    @overload
    def score(
        self,
        *,
        name: str,
        value: str,
        score_id: Optional[str] = None,
        data_type: Optional[Literal["CATEGORICAL"]] = "CATEGORICAL",
        comment: Optional[str] = None,
        config_id: Optional[str] = None,
    ) -> None: ...

    def score(
        self,
        *,
        name: str,
        value: Union[float, str],
        score_id: Optional[str] = None,
        data_type: Optional[ScoreDataType] = None,
        comment: Optional[str] = None,
        config_id: Optional[str] = None,
    ) -> None:
        """Create a score for this specific span.

        This method creates a score associated with this specific span (observation).
        Scores can represent any kind of evaluation, feedback, or quality metric.

        Args:
            name: Name of the score (e.g., "relevance", "accuracy")
            value: Score value (numeric for NUMERIC/BOOLEAN, string for CATEGORICAL)
            score_id: Optional custom ID for the score (auto-generated if not provided)
            data_type: Type of score (NUMERIC, BOOLEAN, or CATEGORICAL)
            comment: Optional comment or explanation for the score
            config_id: Optional ID of a score config defined in lighthouse

        Example:
            ```python
            with lighthouse.start_as_current_span(name="process-query") as span:
                # Do work
                result = process_data()

                # Score the span
                span.score(
                    name="accuracy",
                    value=0.95,
                    data_type="NUMERIC",
                    comment="High accuracy result"
                )
            ```
        """
        self._lighthouse_client.create_score(
            name=name,
            value=cast(str, value),
            trace_id=self.trace_id,
            observation_id=self.id,
            score_id=score_id,
            data_type=cast(Literal["CATEGORICAL"], data_type),
            comment=comment,
            config_id=config_id,
        )

    @overload
    def score_trace(
        self,
        *,
        name: str,
        value: float,
        score_id: Optional[str] = None,
        data_type: Optional[Literal["NUMERIC", "BOOLEAN"]] = None,
        comment: Optional[str] = None,
        config_id: Optional[str] = None,
    ) -> None: ...

    @overload
    def score_trace(
        self,
        *,
        name: str,
        value: str,
        score_id: Optional[str] = None,
        data_type: Optional[Literal["CATEGORICAL"]] = "CATEGORICAL",
        comment: Optional[str] = None,
        config_id: Optional[str] = None,
    ) -> None: ...

    def score_trace(
        self,
        *,
        name: str,
        value: Union[float, str],
        score_id: Optional[str] = None,
        data_type: Optional[ScoreDataType] = None,
        comment: Optional[str] = None,
        config_id: Optional[str] = None,
    ) -> None:
        """Create a score for the entire trace that this span belongs to.

        This method creates a score associated with the entire trace that this span
        belongs to, rather than the specific span. This is useful for overall
        evaluations that apply to the complete trace.

        Args:
            name: Name of the score (e.g., "user_satisfaction", "overall_quality")
            value: Score value (numeric for NUMERIC/BOOLEAN, string for CATEGORICAL)
            score_id: Optional custom ID for the score (auto-generated if not provided)
            data_type: Type of score (NUMERIC, BOOLEAN, or CATEGORICAL)
            comment: Optional comment or explanation for the score
            config_id: Optional ID of a score config defined in lighthouse

        Example:
            ```python
            with lighthouse.start_as_current_span(name="handle-request") as span:
                # Process the complete request
                result = process_request()

                # Score the entire trace (not just this span)
                span.score_trace(
                    name="overall_quality",
                    value=0.9,
                    data_type="NUMERIC",
                    comment="Good overall experience"
                )
            ```
        """
        self._lighthouse_client.create_score(
            name=name,
            value=cast(str, value),
            trace_id=self.trace_id,
            score_id=score_id,
            data_type=cast(Literal["CATEGORICAL"], data_type),
            comment=comment,
            config_id=config_id,
        )

    def _set_processed_span_attributes(
        self,
        *,
        span: otel_trace_api.Span,
        as_type: Optional[Literal["span", "generation", "event"]] = None,
        input: Optional[Any] = None,
        output: Optional[Any] = None,
        metadata: Optional[Any] = None,
    ) -> None:
        """Set span attributes after processing media and applying masks.

        Internal method that processes media in the input, output, and metadata
        and applies any configured masking before setting them as span attributes.

        Args:
            span: The OpenTelemetry span to set attributes on
            as_type: The type of span ("span" or "generation")
            input: Input data to process and set
            output: Output data to process and set
            metadata: Metadata to process and set
        """
        processed_input = self._process_media_and_apply_mask(
            span=span,
            data=input,
            field="input",
        )
        processed_output = self._process_media_and_apply_mask(
            span=span,
            data=output,
            field="output",
        )
        processed_metadata = self._process_media_and_apply_mask(
            span=span,
            data=metadata,
            field="metadata",
        )

        media_processed_attributes = (
            create_generation_attributes(
                input=processed_input,
                output=processed_output,
                metadata=processed_metadata,
            )
            if as_type == "generation"
            else create_span_attributes(
                input=processed_input,
                output=processed_output,
                metadata=processed_metadata,
            )
        )

        span.set_attributes(media_processed_attributes)

    def _process_media_and_apply_mask(
        self,
        *,
        data: Optional[Any] = None,
        span: otel_trace_api.Span,
        field: Union[Literal["input"], Literal["output"], Literal["metadata"]],
    ) -> Optional[Any]:
        """Process media in an attribute and apply masking.

        Internal method that processes any media content in the data and applies
        the configured masking function to the result.

        Args:
            data: The data to process
            span: The OpenTelemetry span context
            field: Which field this data represents (input, output, or metadata)

        Returns:
            The processed and masked data
        """
        return self._mask_attribute(
            data=self._process_media_in_attribute(data=data, field=field)
        )

    def _mask_attribute(self, *, data: Any) -> Any:
        """Apply the configured mask function to data.

        Internal method that applies the client's configured masking function to
        the provided data, with error handling and fallback.

        Args:
            data: The data to mask

        Returns:
            The masked data, or the original data if no mask is configured
        """
        if not self._lighthouse_client._mask:
            return data

        try:
            return self._lighthouse_client._mask(data=data)
        except Exception as e:
            lighthouse_logger.error(
                f"Masking error: Custom mask function threw exception when processing data. Using fallback masking. Error: {e}"
            )

            return "<fully masked due to failed mask function>"

    def _process_media_in_attribute(
        self,
        *,
        data: Optional[Any] = None,
        field: Union[Literal["input"], Literal["output"], Literal["metadata"]],
    ) -> Optional[Any]:
        """Process any media content in the attribute data.

        Internal method that identifies and processes any media content in the
        provided data, using the client's media manager.

        Args:
            data: The data to process for media content
            span: The OpenTelemetry span context
            field: Which field this data represents (input, output, or metadata)

        Returns:
            The data with any media content processed
        """
        if self._lighthouse_client._resources is not None:
            return (
                self._lighthouse_client._resources._media_manager._find_and_process_media(
                    data=data,
                    field=field,
                    trace_id=self.trace_id,
                    observation_id=self.id,
                )
            )

        return data


class lighthouseSpan(lighthouseSpanWrapper):
    """Standard span implementation for general operations in lighthouse.

    This class represents a general-purpose span that can be used to trace
    any operation in your application. It extends the base lighthouseSpanWrapper
    with specific methods for creating child spans, generations, and updating
    span-specific attributes.
    """

    def __init__(
        self,
        *,
        otel_span: otel_trace_api.Span,
        lighthouse_client: "lighthouse",
        input: Optional[Any] = None,
        output: Optional[Any] = None,
        metadata: Optional[Any] = None,
        environment: Optional[str] = None,
        version: Optional[str] = None,
        level: Optional[SpanLevel] = None,
        status_message: Optional[str] = None,
    ):
        """Initialize a new lighthouseSpan.

        Args:
            otel_span: The OpenTelemetry span to wrap
            lighthouse_client: Reference to the parent lighthouse client
            input: Input data for the span (any JSON-serializable object)
            output: Output data from the span (any JSON-serializable object)
            metadata: Additional metadata to associate with the span
            environment: The tracing environment
            version: Version identifier for the code or component
            level: Importance level of the span (info, warning, error)
            status_message: Optional status message for the span
        """
        super().__init__(
            otel_span=otel_span,
            as_type="span",
            lighthouse_client=lighthouse_client,
            input=input,
            output=output,
            metadata=metadata,
            environment=environment,
            version=version,
            level=level,
            status_message=status_message,
        )

    def update(
        self,
        *,
        name: Optional[str] = None,
        input: Optional[Any] = None,
        output: Optional[Any] = None,
        metadata: Optional[Any] = None,
        version: Optional[str] = None,
        level: Optional[SpanLevel] = None,
        status_message: Optional[str] = None,
        **kwargs: Any,
    ) -> "lighthouseSpan":
        """Update this span with new information.

        This method updates the span with new information that becomes available
        during execution, such as outputs, metadata, or status changes.

        Args:
            name: Span name
            input: Updated input data for the operation
            output: Output data from the operation
            metadata: Additional metadata to associate with the span
            version: Version identifier for the code or component
            level: Importance level of the span (info, warning, error)
            status_message: Optional status message for the span
            **kwargs: Additional keyword arguments (ignored)

        Example:
            ```python
            span = lighthouse.start_span(name="process-data")
            try:
                # Do work
                result = process_data()
                span.update(output=result, metadata={"processing_time": 350})
            finally:
                span.end()
            ```
        """
        if not self._otel_span.is_recording():
            return self

        processed_input = self._process_media_and_apply_mask(
            data=input, field="input", span=self._otel_span
        )
        processed_output = self._process_media_and_apply_mask(
            data=output, field="output", span=self._otel_span
        )
        processed_metadata = self._process_media_and_apply_mask(
            data=metadata, field="metadata", span=self._otel_span
        )

        if name:
            self._otel_span.update_name(name)

        attributes = create_span_attributes(
            input=processed_input,
            output=processed_output,
            metadata=processed_metadata,
            version=version,
            level=level,
            status_message=status_message,
        )

        self._otel_span.set_attributes(attributes=attributes)

        return self

    def start_span(
        self,
        name: str,
        input: Optional[Any] = None,
        output: Optional[Any] = None,
        metadata: Optional[Any] = None,
        version: Optional[str] = None,
        level: Optional[SpanLevel] = None,
        status_message: Optional[str] = None,
    ) -> "lighthouseSpan":
        """Create a new child span.

        This method creates a new child span with this span as the parent.
        Unlike start_as_current_span(), this method does not set the new span
        as the current span in the context.

        Args:
            name: Name of the span (e.g., function or operation name)
            input: Input data for the operation
            output: Output data from the operation
            metadata: Additional metadata to associate with the span
            version: Version identifier for the code or component
            level: Importance level of the span (info, warning, error)
            status_message: Optional status message for the span

        Returns:
            A new lighthouseSpan that must be ended with .end() when complete

        Example:
            ```python
            parent_span = lighthouse.start_span(name="process-request")
            try:
                # Create a child span
                child_span = parent_span.start_span(name="validate-input")
                try:
                    # Do validation work
                    validation_result = validate(request_data)
                    child_span.update(output=validation_result)
                finally:
                    child_span.end()

                # Continue with parent span
                result = process_validated_data(validation_result)
                parent_span.update(output=result)
            finally:
                parent_span.end()
            ```
        """
        with otel_trace_api.use_span(self._otel_span):
            new_otel_span = self._lighthouse_client._otel_tracer.start_span(name=name)

        return lighthouseSpan(
            otel_span=new_otel_span,
            lighthouse_client=self._lighthouse_client,
            environment=self._environment,
            input=input,
            output=output,
            metadata=metadata,
            version=version,
            level=level,
            status_message=status_message,
        )

    def start_as_current_span(
        self,
        *,
        name: str,
        input: Optional[Any] = None,
        output: Optional[Any] = None,
        metadata: Optional[Any] = None,
        version: Optional[str] = None,
        level: Optional[SpanLevel] = None,
        status_message: Optional[str] = None,
    ) -> _AgnosticContextManager["lighthouseSpan"]:
        """Create a new child span and set it as the current span in a context manager.

        This method creates a new child span and sets it as the current span within
        a context manager. It should be used with a 'with' statement to automatically
        manage the span's lifecycle.

        Args:
            name: Name of the span (e.g., function or operation name)
            input: Input data for the operation
            output: Output data from the operation
            metadata: Additional metadata to associate with the span
            version: Version identifier for the code or component
            level: Importance level of the span (info, warning, error)
            status_message: Optional status message for the span

        Returns:
            A context manager that yields a new lighthouseSpan

        Example:
            ```python
            with lighthouse.start_as_current_span(name="process-request") as parent_span:
                # Parent span is active here

                # Create a child span with context management
                with parent_span.start_as_current_span(name="validate-input") as child_span:
                    # Child span is active here
                    validation_result = validate(request_data)
                    child_span.update(output=validation_result)

                # Back to parent span context
                result = process_validated_data(validation_result)
                parent_span.update(output=result)
            ```
        """
        return cast(
            _AgnosticContextManager["lighthouseSpan"],
            self._lighthouse_client._create_span_with_parent_context(
                name=name,
                as_type="span",
                remote_parent_span=None,
                parent=self._otel_span,
                input=input,
                output=output,
                metadata=metadata,
                version=version,
                level=level,
                status_message=status_message,
            ),
        )

    def start_generation(
        self,
        *,
        name: str,
        input: Optional[Any] = None,
        output: Optional[Any] = None,
        metadata: Optional[Any] = None,
        version: Optional[str] = None,
        level: Optional[SpanLevel] = None,
        status_message: Optional[str] = None,
        completion_start_time: Optional[datetime] = None,
        model: Optional[str] = None,
        model_parameters: Optional[Dict[str, MapValue]] = None,
        usage_details: Optional[Dict[str, int]] = None,
        cost_details: Optional[Dict[str, float]] = None,
        prompt: Optional[PromptClient] = None,
    ) -> "lighthouseGeneration":
        """Create a new child generation span.

        This method creates a new child generation span with this span as the parent.
        Generation spans are specialized for AI/LLM operations and include additional
        fields for model information, usage stats, and costs.

        Unlike start_as_current_generation(), this method does not set the new span
        as the current span in the context.

        Args:
            name: Name of the generation operation
            input: Input data for the model (e.g., prompts)
            output: Output from the model (e.g., completions)
            metadata: Additional metadata to associate with the generation
            version: Version identifier for the model or component
            level: Importance level of the generation (info, warning, error)
            status_message: Optional status message for the generation
            completion_start_time: When the model started generating the response
            model: Name/identifier of the AI model used (e.g., "gpt-4")
            model_parameters: Parameters used for the model (e.g., temperature, max_tokens)
            usage_details: Token usage information (e.g., prompt_tokens, completion_tokens)
            cost_details: Cost information for the model call
            prompt: Associated prompt template from lighthouse prompt management

        Returns:
            A new lighthouseGeneration that must be ended with .end() when complete

        Example:
            ```python
            span = lighthouse.start_span(name="process-query")
            try:
                # Create a generation child span
                generation = span.start_generation(
                    name="generate-answer",
                    model="gpt-4",
                    input={"prompt": "Explain quantum computing"}
                )
                try:
                    # Call model API
                    response = llm.generate(...)

                    generation.update(
                        output=response.text,
                        usage_details={
                            "prompt_tokens": response.usage.prompt_tokens,
                            "completion_tokens": response.usage.completion_tokens
                        }
                    )
                finally:
                    generation.end()

                # Continue with parent span
                span.update(output={"answer": response.text, "source": "gpt-4"})
            finally:
                span.end()
            ```
        """
        with otel_trace_api.use_span(self._otel_span):
            new_otel_span = self._lighthouse_client._otel_tracer.start_span(name=name)

        return lighthouseGeneration(
            otel_span=new_otel_span,
            lighthouse_client=self._lighthouse_client,
            environment=self._environment,
            input=input,
            output=output,
            metadata=metadata,
            version=version,
            level=level,
            status_message=status_message,
            completion_start_time=completion_start_time,
            model=model,
            model_parameters=model_parameters,
            usage_details=usage_details,
            cost_details=cost_details,
            prompt=prompt,
        )

    def start_as_current_generation(
        self,
        *,
        name: str,
        input: Optional[Any] = None,
        output: Optional[Any] = None,
        metadata: Optional[Any] = None,
        version: Optional[str] = None,
        level: Optional[SpanLevel] = None,
        status_message: Optional[str] = None,
        completion_start_time: Optional[datetime] = None,
        model: Optional[str] = None,
        model_parameters: Optional[Dict[str, MapValue]] = None,
        usage_details: Optional[Dict[str, int]] = None,
        cost_details: Optional[Dict[str, float]] = None,
        prompt: Optional[PromptClient] = None,
    ) -> _AgnosticContextManager["lighthouseGeneration"]:
        """Create a new child generation span and set it as the current span in a context manager.

        This method creates a new child generation span and sets it as the current span
        within a context manager. Generation spans are specialized for AI/LLM operations
        and include additional fields for model information, usage stats, and costs.

        Args:
            name: Name of the generation operation
            input: Input data for the model (e.g., prompts)
            output: Output from the model (e.g., completions)
            metadata: Additional metadata to associate with the generation
            version: Version identifier for the model or component
            level: Importance level of the generation (info, warning, error)
            status_message: Optional status message for the generation
            completion_start_time: When the model started generating the response
            model: Name/identifier of the AI model used (e.g., "gpt-4")
            model_parameters: Parameters used for the model (e.g., temperature, max_tokens)
            usage_details: Token usage information (e.g., prompt_tokens, completion_tokens)
            cost_details: Cost information for the model call
            prompt: Associated prompt template from lighthouse prompt management

        Returns:
            A context manager that yields a new lighthouseGeneration

        Example:
            ```python
            with lighthouse.start_as_current_span(name="process-request") as span:
                # Prepare data
                query = preprocess_user_query(user_input)

                # Create a generation span with context management
                with span.start_as_current_generation(
                    name="generate-answer",
                    model="gpt-4",
                    input={"query": query}
                ) as generation:
                    # Generation span is active here
                    response = llm.generate(query)

                    # Update with results
                    generation.update(
                        output=response.text,
                        usage_details={
                            "prompt_tokens": response.usage.prompt_tokens,
                            "completion_tokens": response.usage.completion_tokens
                        }
                    )

                # Back to parent span context
                span.update(output={"answer": response.text, "source": "gpt-4"})
            ```
        """
        return cast(
            _AgnosticContextManager["lighthouseGeneration"],
            self._lighthouse_client._create_span_with_parent_context(
                name=name,
                as_type="generation",
                remote_parent_span=None,
                parent=self._otel_span,
                input=input,
                output=output,
                metadata=metadata,
                version=version,
                level=level,
                status_message=status_message,
                completion_start_time=completion_start_time,
                model=model,
                model_parameters=model_parameters,
                usage_details=usage_details,
                cost_details=cost_details,
                prompt=prompt,
            ),
        )

    def create_event(
        self,
        *,
        name: str,
        input: Optional[Any] = None,
        output: Optional[Any] = None,
        metadata: Optional[Any] = None,
        version: Optional[str] = None,
        level: Optional[SpanLevel] = None,
        status_message: Optional[str] = None,
    ) -> "lighthouseEvent":
        """Create a new lighthouse observation of type 'EVENT'.

        Args:
            name: Name of the span (e.g., function or operation name)
            input: Input data for the operation (can be any JSON-serializable object)
            output: Output data from the operation (can be any JSON-serializable object)
            metadata: Additional metadata to associate with the span
            version: Version identifier for the code or component
            level: Importance level of the span (info, warning, error)
            status_message: Optional status message for the span

        Returns:
            The lighthouseEvent object

        Example:
            ```python
            event = lighthouse.create_event(name="process-event")
            ```
        """
        timestamp = time_ns()

        with otel_trace_api.use_span(self._otel_span):
            new_otel_span = self._lighthouse_client._otel_tracer.start_span(
                name=name, start_time=timestamp
            )

        return cast(
            "lighthouseEvent",
            lighthouseEvent(
                otel_span=new_otel_span,
                lighthouse_client=self._lighthouse_client,
                input=input,
                output=output,
                metadata=metadata,
                environment=self._environment,
                version=version,
                level=level,
                status_message=status_message,
            ).end(end_time=timestamp),
        )


class lighthouseGeneration(lighthouseSpanWrapper):
    """Specialized span implementation for AI model generations in lighthouse.

    This class represents a generation span specifically designed for tracking
    AI/LLM operations. It extends the base lighthouseSpanWrapper with specialized
    attributes for model details, token usage, and costs.
    """

    def __init__(
        self,
        *,
        otel_span: otel_trace_api.Span,
        lighthouse_client: "lighthouse",
        input: Optional[Any] = None,
        output: Optional[Any] = None,
        metadata: Optional[Any] = None,
        environment: Optional[str] = None,
        version: Optional[str] = None,
        level: Optional[SpanLevel] = None,
        status_message: Optional[str] = None,
        completion_start_time: Optional[datetime] = None,
        model: Optional[str] = None,
        model_parameters: Optional[Dict[str, MapValue]] = None,
        usage_details: Optional[Dict[str, int]] = None,
        cost_details: Optional[Dict[str, float]] = None,
        prompt: Optional[PromptClient] = None,
    ):
        """Initialize a new lighthouseGeneration span.

        Args:
            otel_span: The OpenTelemetry span to wrap
            lighthouse_client: Reference to the parent lighthouse client
            input: Input data for the generation (e.g., prompts)
            output: Output from the generation (e.g., completions)
            metadata: Additional metadata to associate with the generation
            environment: The tracing environment
            version: Version identifier for the model or component
            level: Importance level of the generation (info, warning, error)
            status_message: Optional status message for the generation
            completion_start_time: When the model started generating the response
            model: Name/identifier of the AI model used (e.g., "gpt-4")
            model_parameters: Parameters used for the model (e.g., temperature, max_tokens)
            usage_details: Token usage information (e.g., prompt_tokens, completion_tokens)
            cost_details: Cost information for the model call
            prompt: Associated prompt template from lighthouse prompt management
        """
        super().__init__(
            otel_span=otel_span,
            as_type="generation",
            lighthouse_client=lighthouse_client,
            input=input,
            output=output,
            metadata=metadata,
            environment=environment,
            version=version,
            level=level,
            status_message=status_message,
            completion_start_time=completion_start_time,
            model=model,
            model_parameters=model_parameters,
            usage_details=usage_details,
            cost_details=cost_details,
            prompt=prompt,
        )

    def update(
        self,
        *,
        name: Optional[str] = None,
        input: Optional[Any] = None,
        output: Optional[Any] = None,
        metadata: Optional[Any] = None,
        version: Optional[str] = None,
        level: Optional[SpanLevel] = None,
        status_message: Optional[str] = None,
        completion_start_time: Optional[datetime] = None,
        model: Optional[str] = None,
        model_parameters: Optional[Dict[str, MapValue]] = None,
        usage_details: Optional[Dict[str, int]] = None,
        cost_details: Optional[Dict[str, float]] = None,
        prompt: Optional[PromptClient] = None,
        **kwargs: Dict[str, Any],
    ) -> "lighthouseGeneration":
        """Update this generation span with new information.

        This method updates the generation span with new information that becomes
        available during or after the model generation, such as model outputs,
        token usage statistics, or cost details.

        Args:
            name: The generation name
            input: Updated input data for the model
            output: Output from the model (e.g., completions)
            metadata: Additional metadata to associate with the generation
            version: Version identifier for the model or component
            level: Importance level of the generation (info, warning, error)
            status_message: Optional status message for the generation
            completion_start_time: When the model started generating the response
            model: Name/identifier of the AI model used (e.g., "gpt-4")
            model_parameters: Parameters used for the model (e.g., temperature, max_tokens)
            usage_details: Token usage information (e.g., prompt_tokens, completion_tokens)
            cost_details: Cost information for the model call
            prompt: Associated prompt template from lighthouse prompt management
            **kwargs: Additional keyword arguments (ignored)

        Example:
            ```python
            generation = lighthouse.start_generation(
                name="answer-generation",
                model="gpt-4",
                input={"prompt": "Explain quantum computing"}
            )
            try:
                # Call model API
                response = llm.generate(...)

                # Update with results
                generation.update(
                    output=response.text,
                    usage_details={
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    },
                    cost_details={
                        "total_cost": 0.0035
                    }
                )
            finally:
                generation.end()
            ```
        """
        if not self._otel_span.is_recording():
            return self

        processed_input = self._process_media_and_apply_mask(
            data=input, field="input", span=self._otel_span
        )
        processed_output = self._process_media_and_apply_mask(
            data=output, field="output", span=self._otel_span
        )
        processed_metadata = self._process_media_and_apply_mask(
            data=metadata, field="metadata", span=self._otel_span
        )

        if name:
            self._otel_span.update_name(name)

        attributes = create_generation_attributes(
            input=processed_input,
            output=processed_output,
            metadata=processed_metadata,
            version=version,
            level=level,
            status_message=status_message,
            completion_start_time=completion_start_time,
            model=model,
            model_parameters=model_parameters,
            usage_details=usage_details,
            cost_details=cost_details,
            prompt=prompt,
        )

        self._otel_span.set_attributes(attributes=attributes)

        return self


class lighthouseEvent(lighthouseSpanWrapper):
    """Specialized span implementation for lighthouse Events."""

    def __init__(
        self,
        *,
        otel_span: otel_trace_api.Span,
        lighthouse_client: "lighthouse",
        input: Optional[Any] = None,
        output: Optional[Any] = None,
        metadata: Optional[Any] = None,
        environment: Optional[str] = None,
        version: Optional[str] = None,
        level: Optional[SpanLevel] = None,
        status_message: Optional[str] = None,
    ):
        """Initialize a new lighthouseEvent span.

        Args:
            otel_span: The OpenTelemetry span to wrap
            lighthouse_client: Reference to the parent lighthouse client
            input: Input data for the event
            output: Output from the event
            metadata: Additional metadata to associate with the generation
            environment: The tracing environment
            version: Version identifier for the model or component
            level: Importance level of the generation (info, warning, error)
            status_message: Optional status message for the generation
        """
        super().__init__(
            otel_span=otel_span,
            as_type="event",
            lighthouse_client=lighthouse_client,
            input=input,
            output=output,
            metadata=metadata,
            environment=environment,
            version=version,
            level=level,
            status_message=status_message,
        )

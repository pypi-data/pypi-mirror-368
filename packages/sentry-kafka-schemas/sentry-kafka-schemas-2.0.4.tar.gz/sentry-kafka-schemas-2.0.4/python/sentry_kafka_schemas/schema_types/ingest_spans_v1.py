from typing import Required, TypedDict, Union, Dict, Any


class SpanEvent(TypedDict, total=False):
    """ span_event. """

    event_id: "_Uuid"
    """
    minLength: 32
    maxLength: 36
    """

    organization_id: Required["_Uint"]
    """
    minimum: 0

    Required property
    """

    project_id: Required["_Uint"]
    """
    minimum: 0

    Required property
    """

    trace_id: Required["_Uuid"]
    """
    minLength: 32
    maxLength: 36

    Required property
    """

    span_id: Required[str]
    """
    The span ID is a unique identifier for a span within a trace. It is an 8 byte hexadecimal string.

    Required property
    """

    parent_span_id: Union[str, None]
    """ The parent span ID is the ID of the span that caused this span. It is an 8 byte hexadecimal string. """

    profile_id: "_Uuid"
    """
    minLength: 32
    maxLength: 36
    """

    start_timestamp_ms: Required["_Uint"]
    """
    minimum: 0

    Required property
    """

    start_timestamp_precise: Required["_PositiveFloat"]
    """
    minimum: 0

    Required property
    """

    end_timestamp_precise: Required["_PositiveFloat"]
    """
    minimum: 0

    Required property
    """

    duration_ms: Required["_Uint32"]
    """
    minimum: 0
    maximum: 4294967295

    Required property
    """

    retention_days: Required["_Uint16"]
    """
    minimum: 0
    maximum: 65535

    Required property
    """

    received: Required["_PositiveFloat"]
    """
    minimum: 0

    Required property
    """

    description: str
    tags: "_SpanEventTags"
    """
     Manual key/value tag pairs.

    Aggregation type: anyOf
    """

    sentry_tags: "_SentryExtractedTags"
    """
    Tags extracted by sentry. These are kept separate from customer tags

    Aggregation type: anyOf
    """

    measurements: Dict[str, "_MeasurementValue"]
    data: Dict[str, Any]


class _MeasurementValue(TypedDict, total=False):
    value: Required[Union[int, float]]
    """ Required property """

    unit: str


_PositiveFloat = Union[int, float]
""" minimum: 0 """



_SentryExtractedTags = Union["_SentryExtractedTagsAnyof0"]
"""
Tags extracted by sentry. These are kept separate from customer tags

Aggregation type: anyOf
"""



_SentryExtractedTagsAnyof0 = TypedDict('_SentryExtractedTagsAnyof0', {
    'http.method': str,
    'action': str,
    'domain': str,
    'module': str,
    'group': str,
    'system': str,
    'status': str,
    'status_code': str,
    'transaction': str,
    'transaction.op': str,
    'op': str,
    'transaction.method': str,
}, total=False)


_SpanEventTags = Union[Dict[str, str], None]
"""
 Manual key/value tag pairs.

Aggregation type: anyOf
"""



_Uint = int
""" minimum: 0 """



_Uint16 = int
"""
minimum: 0
maximum: 65535
"""



_Uint32 = int
"""
minimum: 0
maximum: 4294967295
"""



_Uuid = str
"""
minLength: 32
maxLength: 36
"""


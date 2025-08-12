from typing import Required, TypedDict, Union, List, Dict, Any


class BufferedSegment(TypedDict, total=False):
    """ buffered_segment. """

    spans: Required["_SegmentSpans"]
    """
    minItems: 1

    Required property
    """



class MeasurementValue(TypedDict, total=False):
    """ measurement_value. """

    value: Required[Union[int, float]]
    """ Required property """

    unit: str


class SegmentSpan(TypedDict, total=False):
    """ segment_span. """

    event_id: "_Uuid"
    """
    minLength: 32
    maxLength: 36
    """

    organization_id: "_Uint"
    """ minimum: 0 """

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

    segment_id: Union[str, None]
    """ The segment ID is a unique identifier for a segment within a trace. It is an 8 byte hexadecimal string. """

    profile_id: "_Uuid"
    """
    minLength: 32
    maxLength: 36
    """

    is_segment: Required[bool]
    """
    Whether this span is a segment or not.

    Required property
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
    tags: "_SegmentSpanTags"
    """
     Manual key/value tag pairs.

    Aggregation type: anyOf
    """

    sentry_tags: "_SentryExtractedTags"
    """
    Tags extracted by sentry. These are kept separate from customer tags

    Aggregation type: anyOf
    """

    measurements: Dict[str, "MeasurementValue"]
    data: Dict[str, Any]
    links: List["SpanLink"]
    """ Relationships to other spans """



class SpanLink(TypedDict, total=False):
    """ span_link. """

    trace_id: Required["_Uuid"]
    """
    minLength: 32
    maxLength: 36

    Required property
    """

    span_id: Required[str]
    """ Required property """

    sampled: bool
    attributes: "_SpanLinkAttributes"
    """ Aggregation type: anyOf """



_PositiveFloat = Union[int, float]
""" minimum: 0 """



_SegmentSpanTags = Union[Dict[str, str], None]
"""
 Manual key/value tag pairs.

Aggregation type: anyOf
"""



_SegmentSpans = List["SegmentSpan"]
""" minItems: 1 """



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


_SpanLinkAttributes = Union[Dict[str, Any], None]
""" Aggregation type: anyOf """



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


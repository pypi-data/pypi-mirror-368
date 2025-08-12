import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TimeOrdering(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ASCENDING: _ClassVar[TimeOrdering]
    DESCENDING: _ClassVar[TimeOrdering]
ASCENDING: TimeOrdering
DESCENDING: TimeOrdering

class ListMetricsRequest(_message.Message):
    __slots__ = ("dimensions", "filter")
    DIMENSIONS_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    dimensions: _containers.RepeatedCompositeFieldContainer[Dimension]
    filter: str
    def __init__(self, dimensions: _Optional[_Iterable[_Union[Dimension, _Mapping]]] = ..., filter: _Optional[str] = ...) -> None: ...

class ListMetricsResponse(_message.Message):
    __slots__ = ("Metrics",)
    class Metric(_message.Message):
        __slots__ = ("name", "description")
        NAME_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        name: str
        description: str
        def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...
    METRICS_FIELD_NUMBER: _ClassVar[int]
    Metrics: _containers.RepeatedCompositeFieldContainer[ListMetricsResponse.Metric]
    def __init__(self, Metrics: _Optional[_Iterable[_Union[ListMetricsResponse.Metric, _Mapping]]] = ...) -> None: ...

class GetMetricValueRequest(_message.Message):
    __slots__ = ("dimensions", "metrics", "options", "startDate", "endDate")
    class OptionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    DIMENSIONS_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    STARTDATE_FIELD_NUMBER: _ClassVar[int]
    ENDDATE_FIELD_NUMBER: _ClassVar[int]
    dimensions: _containers.RepeatedCompositeFieldContainer[Dimension]
    metrics: _containers.RepeatedScalarFieldContainer[str]
    options: _containers.ScalarMap[str, str]
    startDate: _timestamp_pb2.Timestamp
    endDate: _timestamp_pb2.Timestamp
    def __init__(self, dimensions: _Optional[_Iterable[_Union[Dimension, _Mapping]]] = ..., metrics: _Optional[_Iterable[str]] = ..., options: _Optional[_Mapping[str, str]] = ..., startDate: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., endDate: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class GetMetricValueResponse(_message.Message):
    __slots__ = ("frames",)
    class Frame(_message.Message):
        __slots__ = ("metric", "timestamp", "fields", "meta")
        METRIC_FIELD_NUMBER: _ClassVar[int]
        TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
        FIELDS_FIELD_NUMBER: _ClassVar[int]
        META_FIELD_NUMBER: _ClassVar[int]
        metric: str
        timestamp: _timestamp_pb2.Timestamp
        fields: _containers.RepeatedCompositeFieldContainer[SingleValueField]
        meta: FrameMeta
        def __init__(self, metric: _Optional[str] = ..., timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., fields: _Optional[_Iterable[_Union[SingleValueField, _Mapping]]] = ..., meta: _Optional[_Union[FrameMeta, _Mapping]] = ...) -> None: ...
    FRAMES_FIELD_NUMBER: _ClassVar[int]
    frames: _containers.RepeatedCompositeFieldContainer[GetMetricValueResponse.Frame]
    def __init__(self, frames: _Optional[_Iterable[_Union[GetMetricValueResponse.Frame, _Mapping]]] = ...) -> None: ...

class GetOptionsRequest(_message.Message):
    __slots__ = ("queryType", "selectedOptions")
    class QueryType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        GetMetricHistory: _ClassVar[GetOptionsRequest.QueryType]
        GetMetricValue: _ClassVar[GetOptionsRequest.QueryType]
        GetMetricAggregate: _ClassVar[GetOptionsRequest.QueryType]
    GetMetricHistory: GetOptionsRequest.QueryType
    GetMetricValue: GetOptionsRequest.QueryType
    GetMetricAggregate: GetOptionsRequest.QueryType
    class SelectedOptionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    QUERYTYPE_FIELD_NUMBER: _ClassVar[int]
    SELECTEDOPTIONS_FIELD_NUMBER: _ClassVar[int]
    queryType: GetOptionsRequest.QueryType
    selectedOptions: _containers.ScalarMap[str, str]
    def __init__(self, queryType: _Optional[_Union[GetOptionsRequest.QueryType, str]] = ..., selectedOptions: _Optional[_Mapping[str, str]] = ...) -> None: ...

class EnumValue(_message.Message):
    __slots__ = ("id", "description", "label", "default")
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_FIELD_NUMBER: _ClassVar[int]
    id: str
    description: str
    label: str
    default: bool
    def __init__(self, id: _Optional[str] = ..., description: _Optional[str] = ..., label: _Optional[str] = ..., default: bool = ...) -> None: ...

class Option(_message.Message):
    __slots__ = ("id", "description", "type", "enumValues", "required", "label")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        Enum: _ClassVar[Option.Type]
        Boolean: _ClassVar[Option.Type]
    Enum: Option.Type
    Boolean: Option.Type
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ENUMVALUES_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    id: str
    description: str
    type: Option.Type
    enumValues: _containers.RepeatedCompositeFieldContainer[EnumValue]
    required: bool
    label: str
    def __init__(self, id: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[_Union[Option.Type, str]] = ..., enumValues: _Optional[_Iterable[_Union[EnumValue, _Mapping]]] = ..., required: bool = ..., label: _Optional[str] = ...) -> None: ...

class GetOptionsResponse(_message.Message):
    __slots__ = ("options",)
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    options: _containers.RepeatedCompositeFieldContainer[Option]
    def __init__(self, options: _Optional[_Iterable[_Union[Option, _Mapping]]] = ...) -> None: ...

class GetMetricAggregateRequest(_message.Message):
    __slots__ = ("dimensions", "metrics", "startDate", "endDate", "maxItems", "timeOrdering", "startingToken", "intervalMs", "options")
    class OptionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    DIMENSIONS_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    STARTDATE_FIELD_NUMBER: _ClassVar[int]
    ENDDATE_FIELD_NUMBER: _ClassVar[int]
    MAXITEMS_FIELD_NUMBER: _ClassVar[int]
    TIMEORDERING_FIELD_NUMBER: _ClassVar[int]
    STARTINGTOKEN_FIELD_NUMBER: _ClassVar[int]
    INTERVALMS_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    dimensions: _containers.RepeatedCompositeFieldContainer[Dimension]
    metrics: _containers.RepeatedScalarFieldContainer[str]
    startDate: _timestamp_pb2.Timestamp
    endDate: _timestamp_pb2.Timestamp
    maxItems: int
    timeOrdering: TimeOrdering
    startingToken: str
    intervalMs: int
    options: _containers.ScalarMap[str, str]
    def __init__(self, dimensions: _Optional[_Iterable[_Union[Dimension, _Mapping]]] = ..., metrics: _Optional[_Iterable[str]] = ..., startDate: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., endDate: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., maxItems: _Optional[int] = ..., timeOrdering: _Optional[_Union[TimeOrdering, str]] = ..., startingToken: _Optional[str] = ..., intervalMs: _Optional[int] = ..., options: _Optional[_Mapping[str, str]] = ...) -> None: ...

class GetMetricAggregateResponse(_message.Message):
    __slots__ = ("frames", "nextToken")
    FRAMES_FIELD_NUMBER: _ClassVar[int]
    NEXTTOKEN_FIELD_NUMBER: _ClassVar[int]
    frames: _containers.RepeatedCompositeFieldContainer[Frame]
    nextToken: str
    def __init__(self, frames: _Optional[_Iterable[_Union[Frame, _Mapping]]] = ..., nextToken: _Optional[str] = ...) -> None: ...

class GetMetricHistoryRequest(_message.Message):
    __slots__ = ("dimensions", "metrics", "startDate", "endDate", "maxItems", "timeOrdering", "startingToken", "options")
    class OptionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    DIMENSIONS_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    STARTDATE_FIELD_NUMBER: _ClassVar[int]
    ENDDATE_FIELD_NUMBER: _ClassVar[int]
    MAXITEMS_FIELD_NUMBER: _ClassVar[int]
    TIMEORDERING_FIELD_NUMBER: _ClassVar[int]
    STARTINGTOKEN_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    dimensions: _containers.RepeatedCompositeFieldContainer[Dimension]
    metrics: _containers.RepeatedScalarFieldContainer[str]
    startDate: _timestamp_pb2.Timestamp
    endDate: _timestamp_pb2.Timestamp
    maxItems: int
    timeOrdering: TimeOrdering
    startingToken: str
    options: _containers.ScalarMap[str, str]
    def __init__(self, dimensions: _Optional[_Iterable[_Union[Dimension, _Mapping]]] = ..., metrics: _Optional[_Iterable[str]] = ..., startDate: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., endDate: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., maxItems: _Optional[int] = ..., timeOrdering: _Optional[_Union[TimeOrdering, str]] = ..., startingToken: _Optional[str] = ..., options: _Optional[_Mapping[str, str]] = ...) -> None: ...

class GetMetricHistoryResponse(_message.Message):
    __slots__ = ("frames", "nextToken")
    FRAMES_FIELD_NUMBER: _ClassVar[int]
    NEXTTOKEN_FIELD_NUMBER: _ClassVar[int]
    frames: _containers.RepeatedCompositeFieldContainer[Frame]
    nextToken: str
    def __init__(self, frames: _Optional[_Iterable[_Union[Frame, _Mapping]]] = ..., nextToken: _Optional[str] = ...) -> None: ...

class Label(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class Field(_message.Message):
    __slots__ = ("name", "labels", "config", "values", "stringValues")
    NAME_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    STRINGVALUES_FIELD_NUMBER: _ClassVar[int]
    name: str
    labels: _containers.RepeatedCompositeFieldContainer[Label]
    config: config
    values: _containers.RepeatedScalarFieldContainer[float]
    stringValues: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, name: _Optional[str] = ..., labels: _Optional[_Iterable[_Union[Label, _Mapping]]] = ..., config: _Optional[_Union[config, _Mapping]] = ..., values: _Optional[_Iterable[float]] = ..., stringValues: _Optional[_Iterable[str]] = ...) -> None: ...

class ValueMapping(_message.Message):
    __slots__ = ("to", "value", "text", "color")
    FROM_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    COLOR_FIELD_NUMBER: _ClassVar[int]
    to: float
    value: str
    text: str
    color: str
    def __init__(self, to: _Optional[float] = ..., value: _Optional[str] = ..., text: _Optional[str] = ..., color: _Optional[str] = ..., **kwargs) -> None: ...

class config(_message.Message):
    __slots__ = ("unit", "Mappings")
    UNIT_FIELD_NUMBER: _ClassVar[int]
    MAPPINGS_FIELD_NUMBER: _ClassVar[int]
    unit: str
    Mappings: _containers.RepeatedCompositeFieldContainer[ValueMapping]
    def __init__(self, unit: _Optional[str] = ..., Mappings: _Optional[_Iterable[_Union[ValueMapping, _Mapping]]] = ...) -> None: ...

class SingleValueField(_message.Message):
    __slots__ = ("name", "labels", "config", "value", "stringValue")
    NAME_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    STRINGVALUE_FIELD_NUMBER: _ClassVar[int]
    name: str
    labels: _containers.RepeatedCompositeFieldContainer[Label]
    config: config
    value: float
    stringValue: str
    def __init__(self, name: _Optional[str] = ..., labels: _Optional[_Iterable[_Union[Label, _Mapping]]] = ..., config: _Optional[_Union[config, _Mapping]] = ..., value: _Optional[float] = ..., stringValue: _Optional[str] = ...) -> None: ...

class Frame(_message.Message):
    __slots__ = ("metric", "timestamps", "fields", "meta")
    METRIC_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMPS_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    metric: str
    timestamps: _containers.RepeatedCompositeFieldContainer[_timestamp_pb2.Timestamp]
    fields: _containers.RepeatedCompositeFieldContainer[Field]
    meta: FrameMeta
    def __init__(self, metric: _Optional[str] = ..., timestamps: _Optional[_Iterable[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]]] = ..., fields: _Optional[_Iterable[_Union[Field, _Mapping]]] = ..., meta: _Optional[_Union[FrameMeta, _Mapping]] = ...) -> None: ...

class FrameMeta(_message.Message):
    __slots__ = ("type", "Notices", "PreferredVisualization", "executedQueryString")
    class FrameType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FrameTypeUnknown: _ClassVar[FrameMeta.FrameType]
        FrameTypeTimeSeriesWide: _ClassVar[FrameMeta.FrameType]
        FrameTypeTimeSeriesLong: _ClassVar[FrameMeta.FrameType]
        FrameTypeTimeSeriesMany: _ClassVar[FrameMeta.FrameType]
        FrameTypeDirectoryListing: _ClassVar[FrameMeta.FrameType]
        FrameTypeTable: _ClassVar[FrameMeta.FrameType]
    FrameTypeUnknown: FrameMeta.FrameType
    FrameTypeTimeSeriesWide: FrameMeta.FrameType
    FrameTypeTimeSeriesLong: FrameMeta.FrameType
    FrameTypeTimeSeriesMany: FrameMeta.FrameType
    FrameTypeDirectoryListing: FrameMeta.FrameType
    FrameTypeTable: FrameMeta.FrameType
    class VisType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        VisTypeGraph: _ClassVar[FrameMeta.VisType]
        VisTypeTable: _ClassVar[FrameMeta.VisType]
        VisTypeLogs: _ClassVar[FrameMeta.VisType]
        VisTypeTrace: _ClassVar[FrameMeta.VisType]
        VisTypeNodeGraph: _ClassVar[FrameMeta.VisType]
    VisTypeGraph: FrameMeta.VisType
    VisTypeTable: FrameMeta.VisType
    VisTypeLogs: FrameMeta.VisType
    VisTypeTrace: FrameMeta.VisType
    VisTypeNodeGraph: FrameMeta.VisType
    class Notice(_message.Message):
        __slots__ = ("Severity", "text", "link", "inspect")
        class NoticeSeverity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            NoticeSeverityInfo: _ClassVar[FrameMeta.Notice.NoticeSeverity]
            NoticeSeverityWarning: _ClassVar[FrameMeta.Notice.NoticeSeverity]
            NoticeSeverityError: _ClassVar[FrameMeta.Notice.NoticeSeverity]
        NoticeSeverityInfo: FrameMeta.Notice.NoticeSeverity
        NoticeSeverityWarning: FrameMeta.Notice.NoticeSeverity
        NoticeSeverityError: FrameMeta.Notice.NoticeSeverity
        class InspectType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            InspectTypeNone: _ClassVar[FrameMeta.Notice.InspectType]
            InspectTypeMeta: _ClassVar[FrameMeta.Notice.InspectType]
            InspectTypeError: _ClassVar[FrameMeta.Notice.InspectType]
            InspectTypeData: _ClassVar[FrameMeta.Notice.InspectType]
            InspectTypeStats: _ClassVar[FrameMeta.Notice.InspectType]
        InspectTypeNone: FrameMeta.Notice.InspectType
        InspectTypeMeta: FrameMeta.Notice.InspectType
        InspectTypeError: FrameMeta.Notice.InspectType
        InspectTypeData: FrameMeta.Notice.InspectType
        InspectTypeStats: FrameMeta.Notice.InspectType
        SEVERITY_FIELD_NUMBER: _ClassVar[int]
        TEXT_FIELD_NUMBER: _ClassVar[int]
        LINK_FIELD_NUMBER: _ClassVar[int]
        INSPECT_FIELD_NUMBER: _ClassVar[int]
        Severity: FrameMeta.Notice.NoticeSeverity
        text: str
        link: str
        inspect: FrameMeta.Notice.InspectType
        def __init__(self, Severity: _Optional[_Union[FrameMeta.Notice.NoticeSeverity, str]] = ..., text: _Optional[str] = ..., link: _Optional[str] = ..., inspect: _Optional[_Union[FrameMeta.Notice.InspectType, str]] = ...) -> None: ...
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NOTICES_FIELD_NUMBER: _ClassVar[int]
    PREFERREDVISUALIZATION_FIELD_NUMBER: _ClassVar[int]
    EXECUTEDQUERYSTRING_FIELD_NUMBER: _ClassVar[int]
    type: FrameMeta.FrameType
    Notices: _containers.RepeatedCompositeFieldContainer[FrameMeta.Notice]
    PreferredVisualization: FrameMeta.VisType
    executedQueryString: str
    def __init__(self, type: _Optional[_Union[FrameMeta.FrameType, str]] = ..., Notices: _Optional[_Iterable[_Union[FrameMeta.Notice, _Mapping]]] = ..., PreferredVisualization: _Optional[_Union[FrameMeta.VisType, str]] = ..., executedQueryString: _Optional[str] = ...) -> None: ...

class ListDimensionKeysRequest(_message.Message):
    __slots__ = ("filter", "selected_dimensions")
    FILTER_FIELD_NUMBER: _ClassVar[int]
    SELECTED_DIMENSIONS_FIELD_NUMBER: _ClassVar[int]
    filter: str
    selected_dimensions: _containers.RepeatedCompositeFieldContainer[Dimension]
    def __init__(self, filter: _Optional[str] = ..., selected_dimensions: _Optional[_Iterable[_Union[Dimension, _Mapping]]] = ...) -> None: ...

class ListDimensionKeysResponse(_message.Message):
    __slots__ = ("results",)
    class Result(_message.Message):
        __slots__ = ("key", "description")
        KEY_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        key: str
        description: str
        def __init__(self, key: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[ListDimensionKeysResponse.Result]
    def __init__(self, results: _Optional[_Iterable[_Union[ListDimensionKeysResponse.Result, _Mapping]]] = ...) -> None: ...

class ListDimensionValuesRequest(_message.Message):
    __slots__ = ("dimension_key", "filter", "selected_dimensions")
    DIMENSION_KEY_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    SELECTED_DIMENSIONS_FIELD_NUMBER: _ClassVar[int]
    dimension_key: str
    filter: str
    selected_dimensions: _containers.RepeatedCompositeFieldContainer[Dimension]
    def __init__(self, dimension_key: _Optional[str] = ..., filter: _Optional[str] = ..., selected_dimensions: _Optional[_Iterable[_Union[Dimension, _Mapping]]] = ...) -> None: ...

class ListDimensionValuesResponse(_message.Message):
    __slots__ = ("results",)
    class Result(_message.Message):
        __slots__ = ("value", "description")
        VALUE_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        value: str
        description: str
        def __init__(self, value: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[ListDimensionValuesResponse.Result]
    def __init__(self, results: _Optional[_Iterable[_Union[ListDimensionValuesResponse.Result, _Mapping]]] = ...) -> None: ...

class TimeRange(_message.Message):
    __slots__ = ("fromEpochMS", "toEpochMS")
    FROMEPOCHMS_FIELD_NUMBER: _ClassVar[int]
    TOEPOCHMS_FIELD_NUMBER: _ClassVar[int]
    fromEpochMS: int
    toEpochMS: int
    def __init__(self, fromEpochMS: _Optional[int] = ..., toEpochMS: _Optional[int] = ...) -> None: ...

class Dimension(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class QueryRequest(_message.Message):
    __slots__ = ("refId", "maxDataPoints", "intervalMS", "timeRange", "startKey", "dimensions")
    REFID_FIELD_NUMBER: _ClassVar[int]
    MAXDATAPOINTS_FIELD_NUMBER: _ClassVar[int]
    INTERVALMS_FIELD_NUMBER: _ClassVar[int]
    TIMERANGE_FIELD_NUMBER: _ClassVar[int]
    STARTKEY_FIELD_NUMBER: _ClassVar[int]
    DIMENSIONS_FIELD_NUMBER: _ClassVar[int]
    refId: str
    maxDataPoints: int
    intervalMS: int
    timeRange: TimeRange
    startKey: int
    dimensions: _containers.RepeatedCompositeFieldContainer[Dimension]
    def __init__(self, refId: _Optional[str] = ..., maxDataPoints: _Optional[int] = ..., intervalMS: _Optional[int] = ..., timeRange: _Optional[_Union[TimeRange, _Mapping]] = ..., startKey: _Optional[int] = ..., dimensions: _Optional[_Iterable[_Union[Dimension, _Mapping]]] = ...) -> None: ...

class QueryResponse(_message.Message):
    __slots__ = ("refId", "nextKey", "values")
    class Value(_message.Message):
        __slots__ = ("timestamp", "value")
        TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        timestamp: int
        value: float
        def __init__(self, timestamp: _Optional[int] = ..., value: _Optional[float] = ...) -> None: ...
    REFID_FIELD_NUMBER: _ClassVar[int]
    NEXTKEY_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    refId: str
    nextKey: int
    values: _containers.RepeatedCompositeFieldContainer[QueryResponse.Value]
    def __init__(self, refId: _Optional[str] = ..., nextKey: _Optional[int] = ..., values: _Optional[_Iterable[_Union[QueryResponse.Value, _Mapping]]] = ...) -> None: ...

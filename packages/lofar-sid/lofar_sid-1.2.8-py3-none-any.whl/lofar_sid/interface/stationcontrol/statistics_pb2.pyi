import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FrequencyBand(_message.Message):
    __slots__ = ("antenna_type", "clock", "nyquist_zone")
    ANTENNA_TYPE_FIELD_NUMBER: _ClassVar[int]
    CLOCK_FIELD_NUMBER: _ClassVar[int]
    NYQUIST_ZONE_FIELD_NUMBER: _ClassVar[int]
    antenna_type: str
    clock: int
    nyquist_zone: int
    def __init__(self, antenna_type: _Optional[str] = ..., clock: _Optional[int] = ..., nyquist_zone: _Optional[int] = ...) -> None: ...

class BstRequest(_message.Message):
    __slots__ = ("antenna_field", "maxage")
    ANTENNA_FIELD_FIELD_NUMBER: _ClassVar[int]
    MAXAGE_FIELD_NUMBER: _ClassVar[int]
    antenna_field: str
    maxage: int
    def __init__(self, antenna_field: _Optional[str] = ..., maxage: _Optional[int] = ...) -> None: ...

class BstResult(_message.Message):
    __slots__ = ("timestamp", "frequency_band", "integration_interval", "beamlets")
    class BstBeamlet(_message.Message):
        __slots__ = ("beamlet", "x_power_db", "y_power_db")
        BEAMLET_FIELD_NUMBER: _ClassVar[int]
        X_POWER_DB_FIELD_NUMBER: _ClassVar[int]
        Y_POWER_DB_FIELD_NUMBER: _ClassVar[int]
        beamlet: int
        x_power_db: float
        y_power_db: float
        def __init__(self, beamlet: _Optional[int] = ..., x_power_db: _Optional[float] = ..., y_power_db: _Optional[float] = ...) -> None: ...
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    FREQUENCY_BAND_FIELD_NUMBER: _ClassVar[int]
    INTEGRATION_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    BEAMLETS_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    frequency_band: FrequencyBand
    integration_interval: float
    beamlets: _containers.RepeatedCompositeFieldContainer[BstResult.BstBeamlet]
    def __init__(self, timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., frequency_band: _Optional[_Union[FrequencyBand, _Mapping]] = ..., integration_interval: _Optional[float] = ..., beamlets: _Optional[_Iterable[_Union[BstResult.BstBeamlet, _Mapping]]] = ...) -> None: ...

class BstReply(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: BstResult
    def __init__(self, result: _Optional[_Union[BstResult, _Mapping]] = ...) -> None: ...

class SstRequest(_message.Message):
    __slots__ = ("antenna_field", "maxage")
    ANTENNA_FIELD_FIELD_NUMBER: _ClassVar[int]
    MAXAGE_FIELD_NUMBER: _ClassVar[int]
    antenna_field: str
    maxage: int
    def __init__(self, antenna_field: _Optional[str] = ..., maxage: _Optional[int] = ...) -> None: ...

class SstResult(_message.Message):
    __slots__ = ("timestamp", "frequency_band", "integration_interval", "subbands")
    class SstSubband(_message.Message):
        __slots__ = ("subband", "frequency", "antennas")
        class SstAntenna(_message.Message):
            __slots__ = ("antenna", "x_power_db", "y_power_db")
            ANTENNA_FIELD_NUMBER: _ClassVar[int]
            X_POWER_DB_FIELD_NUMBER: _ClassVar[int]
            Y_POWER_DB_FIELD_NUMBER: _ClassVar[int]
            antenna: int
            x_power_db: float
            y_power_db: float
            def __init__(self, antenna: _Optional[int] = ..., x_power_db: _Optional[float] = ..., y_power_db: _Optional[float] = ...) -> None: ...
        SUBBAND_FIELD_NUMBER: _ClassVar[int]
        FREQUENCY_FIELD_NUMBER: _ClassVar[int]
        ANTENNAS_FIELD_NUMBER: _ClassVar[int]
        subband: int
        frequency: float
        antennas: _containers.RepeatedCompositeFieldContainer[SstResult.SstSubband.SstAntenna]
        def __init__(self, subband: _Optional[int] = ..., frequency: _Optional[float] = ..., antennas: _Optional[_Iterable[_Union[SstResult.SstSubband.SstAntenna, _Mapping]]] = ...) -> None: ...
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    FREQUENCY_BAND_FIELD_NUMBER: _ClassVar[int]
    INTEGRATION_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    SUBBANDS_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    frequency_band: FrequencyBand
    integration_interval: float
    subbands: _containers.RepeatedCompositeFieldContainer[SstResult.SstSubband]
    def __init__(self, timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., frequency_band: _Optional[_Union[FrequencyBand, _Mapping]] = ..., integration_interval: _Optional[float] = ..., subbands: _Optional[_Iterable[_Union[SstResult.SstSubband, _Mapping]]] = ...) -> None: ...

class SstReply(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: SstResult
    def __init__(self, result: _Optional[_Union[SstResult, _Mapping]] = ...) -> None: ...

class XstRequest(_message.Message):
    __slots__ = ("antenna_field", "maxage")
    ANTENNA_FIELD_FIELD_NUMBER: _ClassVar[int]
    MAXAGE_FIELD_NUMBER: _ClassVar[int]
    antenna_field: str
    maxage: int
    def __init__(self, antenna_field: _Optional[str] = ..., maxage: _Optional[int] = ...) -> None: ...

class XstResult(_message.Message):
    __slots__ = ("timestamp", "frequency_band", "integration_interval", "subband", "frequency", "baselines")
    class XstBaseline(_message.Message):
        __slots__ = ("antenna1", "antenna2", "xx", "xy", "yx", "yy")
        class XstValue(_message.Message):
            __slots__ = ("power_db", "phase")
            POWER_DB_FIELD_NUMBER: _ClassVar[int]
            PHASE_FIELD_NUMBER: _ClassVar[int]
            power_db: float
            phase: float
            def __init__(self, power_db: _Optional[float] = ..., phase: _Optional[float] = ...) -> None: ...
        ANTENNA1_FIELD_NUMBER: _ClassVar[int]
        ANTENNA2_FIELD_NUMBER: _ClassVar[int]
        XX_FIELD_NUMBER: _ClassVar[int]
        XY_FIELD_NUMBER: _ClassVar[int]
        YX_FIELD_NUMBER: _ClassVar[int]
        YY_FIELD_NUMBER: _ClassVar[int]
        antenna1: int
        antenna2: int
        xx: XstResult.XstBaseline.XstValue
        xy: XstResult.XstBaseline.XstValue
        yx: XstResult.XstBaseline.XstValue
        yy: XstResult.XstBaseline.XstValue
        def __init__(self, antenna1: _Optional[int] = ..., antenna2: _Optional[int] = ..., xx: _Optional[_Union[XstResult.XstBaseline.XstValue, _Mapping]] = ..., xy: _Optional[_Union[XstResult.XstBaseline.XstValue, _Mapping]] = ..., yx: _Optional[_Union[XstResult.XstBaseline.XstValue, _Mapping]] = ..., yy: _Optional[_Union[XstResult.XstBaseline.XstValue, _Mapping]] = ...) -> None: ...
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    FREQUENCY_BAND_FIELD_NUMBER: _ClassVar[int]
    INTEGRATION_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    SUBBAND_FIELD_NUMBER: _ClassVar[int]
    FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    BASELINES_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    frequency_band: FrequencyBand
    integration_interval: float
    subband: int
    frequency: float
    baselines: _containers.RepeatedCompositeFieldContainer[XstResult.XstBaseline]
    def __init__(self, timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., frequency_band: _Optional[_Union[FrequencyBand, _Mapping]] = ..., integration_interval: _Optional[float] = ..., subband: _Optional[int] = ..., frequency: _Optional[float] = ..., baselines: _Optional[_Iterable[_Union[XstResult.XstBaseline, _Mapping]]] = ...) -> None: ...

class XstReply(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: XstResult
    def __init__(self, result: _Optional[_Union[XstResult, _Mapping]] = ...) -> None: ...

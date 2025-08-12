from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Station_State(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OFF: _ClassVar[Station_State]
    HIBERNATE: _ClassVar[Station_State]
    STANDBY: _ClassVar[Station_State]
    ON: _ClassVar[Station_State]
OFF: Station_State
HIBERNATE: Station_State
STANDBY: Station_State
ON: Station_State

class SetStationStateRequest(_message.Message):
    __slots__ = ("station_state",)
    STATION_STATE_FIELD_NUMBER: _ClassVar[int]
    station_state: Station_State
    def __init__(self, station_state: _Optional[_Union[Station_State, str]] = ...) -> None: ...

class GetStationStateRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SoftStationResetRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HardStationResetRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StationStateResult(_message.Message):
    __slots__ = ("station_state",)
    STATION_STATE_FIELD_NUMBER: _ClassVar[int]
    station_state: Station_State
    def __init__(self, station_state: _Optional[_Union[Station_State, str]] = ...) -> None: ...

class StationStateReply(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: StationStateResult
    def __init__(self, result: _Optional[_Union[StationStateResult, _Mapping]] = ...) -> None: ...

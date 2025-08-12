from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class StartObservationRequest(_message.Message):
    __slots__ = ("configuration",)
    CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    configuration: str
    def __init__(self, configuration: _Optional[str] = ...) -> None: ...

class StopObservationRequest(_message.Message):
    __slots__ = ("observation_id",)
    OBSERVATION_ID_FIELD_NUMBER: _ClassVar[int]
    observation_id: int
    def __init__(self, observation_id: _Optional[int] = ...) -> None: ...

class ObservationReply(_message.Message):
    __slots__ = ("success", "exception")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    EXCEPTION_FIELD_NUMBER: _ClassVar[int]
    success: bool
    exception: str
    def __init__(self, success: bool = ..., exception: _Optional[str] = ...) -> None: ...

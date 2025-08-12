from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Antennafield_Power_Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Antennafield_POWER_OFF: _ClassVar[Antennafield_Power_Status]
    Antennafield_POWER_ON: _ClassVar[Antennafield_Power_Status]
Antennafield_POWER_OFF: Antennafield_Power_Status
Antennafield_POWER_ON: Antennafield_Power_Status

class AntennafieldIdentifier(_message.Message):
    __slots__ = ("antennafield_id",)
    ANTENNAFIELD_ID_FIELD_NUMBER: _ClassVar[int]
    antennafield_id: str
    def __init__(self, antennafield_id: _Optional[str] = ...) -> None: ...

class SetAntennafieldRequest(_message.Message):
    __slots__ = ("identifier", "power_status")
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    POWER_STATUS_FIELD_NUMBER: _ClassVar[int]
    identifier: AntennafieldIdentifier
    power_status: Antennafield_Power_Status
    def __init__(self, identifier: _Optional[_Union[AntennafieldIdentifier, _Mapping]] = ..., power_status: _Optional[_Union[Antennafield_Power_Status, str]] = ...) -> None: ...

class GetAntennafieldRequest(_message.Message):
    __slots__ = ("identifier",)
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    identifier: AntennafieldIdentifier
    def __init__(self, identifier: _Optional[_Union[AntennafieldIdentifier, _Mapping]] = ...) -> None: ...

class AntennafieldResult(_message.Message):
    __slots__ = ("identifier", "power_status")
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    POWER_STATUS_FIELD_NUMBER: _ClassVar[int]
    identifier: AntennafieldIdentifier
    power_status: Antennafield_Power_Status
    def __init__(self, identifier: _Optional[_Union[AntennafieldIdentifier, _Mapping]] = ..., power_status: _Optional[_Union[Antennafield_Power_Status, str]] = ...) -> None: ...

class AntennafieldReply(_message.Message):
    __slots__ = ("success", "exception", "result")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    EXCEPTION_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    exception: str
    result: AntennafieldResult
    def __init__(self, success: bool = ..., exception: _Optional[str] = ..., result: _Optional[_Union[AntennafieldResult, _Mapping]] = ...) -> None: ...

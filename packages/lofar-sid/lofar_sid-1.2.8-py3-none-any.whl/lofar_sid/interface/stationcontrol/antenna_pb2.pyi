from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Antenna_Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OK: _ClassVar[Antenna_Status]
    SUSPICIOUS: _ClassVar[Antenna_Status]
    BROKEN: _ClassVar[Antenna_Status]
    BEYOND_REPAIR: _ClassVar[Antenna_Status]
    NOT_AVAILABLE: _ClassVar[Antenna_Status]

class Antenna_Use(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AUTO: _ClassVar[Antenna_Use]
    ON: _ClassVar[Antenna_Use]
    OFF: _ClassVar[Antenna_Use]

class Antenna_Power_Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Antenna_POWER_OFF: _ClassVar[Antenna_Power_Status]
    Antenna_POWER_ON: _ClassVar[Antenna_Power_Status]
OK: Antenna_Status
SUSPICIOUS: Antenna_Status
BROKEN: Antenna_Status
BEYOND_REPAIR: Antenna_Status
NOT_AVAILABLE: Antenna_Status
AUTO: Antenna_Use
ON: Antenna_Use
OFF: Antenna_Use
Antenna_POWER_OFF: Antenna_Power_Status
Antenna_POWER_ON: Antenna_Power_Status

class Identifier(_message.Message):
    __slots__ = ("antennafield_name", "antenna_name")
    ANTENNAFIELD_NAME_FIELD_NUMBER: _ClassVar[int]
    ANTENNA_NAME_FIELD_NUMBER: _ClassVar[int]
    antennafield_name: str
    antenna_name: str
    def __init__(self, antennafield_name: _Optional[str] = ..., antenna_name: _Optional[str] = ...) -> None: ...

class SetAntennaStatusRequest(_message.Message):
    __slots__ = ("identifier", "antenna_status")
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    ANTENNA_STATUS_FIELD_NUMBER: _ClassVar[int]
    identifier: Identifier
    antenna_status: Antenna_Status
    def __init__(self, identifier: _Optional[_Union[Identifier, _Mapping]] = ..., antenna_status: _Optional[_Union[Antenna_Status, str]] = ...) -> None: ...

class GetAntennaRequest(_message.Message):
    __slots__ = ("identifier",)
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    identifier: Identifier
    def __init__(self, identifier: _Optional[_Union[Identifier, _Mapping]] = ...) -> None: ...

class SetAntennaUseRequest(_message.Message):
    __slots__ = ("identifier", "antenna_use")
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    ANTENNA_USE_FIELD_NUMBER: _ClassVar[int]
    identifier: Identifier
    antenna_use: Antenna_Use
    def __init__(self, identifier: _Optional[_Union[Identifier, _Mapping]] = ..., antenna_use: _Optional[_Union[Antenna_Use, str]] = ...) -> None: ...

class AntennaResult(_message.Message):
    __slots__ = ("identifier", "antenna_use", "antenna_status")
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    ANTENNA_USE_FIELD_NUMBER: _ClassVar[int]
    ANTENNA_STATUS_FIELD_NUMBER: _ClassVar[int]
    identifier: Identifier
    antenna_use: Antenna_Use
    antenna_status: Antenna_Status
    def __init__(self, identifier: _Optional[_Union[Identifier, _Mapping]] = ..., antenna_use: _Optional[_Union[Antenna_Use, str]] = ..., antenna_status: _Optional[_Union[Antenna_Status, str]] = ...) -> None: ...

class AntennaReply(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: AntennaResult
    def __init__(self, result: _Optional[_Union[AntennaResult, _Mapping]] = ...) -> None: ...

class GetAntennaPowerRequest(_message.Message):
    __slots__ = ("identifier",)
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    identifier: Identifier
    def __init__(self, identifier: _Optional[_Union[Identifier, _Mapping]] = ...) -> None: ...

class SetAntennaPowerRequest(_message.Message):
    __slots__ = ("identifier", "power_status")
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    POWER_STATUS_FIELD_NUMBER: _ClassVar[int]
    identifier: Identifier
    power_status: Antenna_Power_Status
    def __init__(self, identifier: _Optional[_Union[Identifier, _Mapping]] = ..., power_status: _Optional[_Union[Antenna_Power_Status, str]] = ...) -> None: ...

class AntennaPowerResult(_message.Message):
    __slots__ = ("identifier", "power_status")
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    POWER_STATUS_FIELD_NUMBER: _ClassVar[int]
    identifier: Identifier
    power_status: Antenna_Power_Status
    def __init__(self, identifier: _Optional[_Union[Identifier, _Mapping]] = ..., power_status: _Optional[_Union[Antenna_Power_Status, str]] = ...) -> None: ...

class GetAntennaPowerReply(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: AntennaPowerResult
    def __init__(self, result: _Optional[_Union[AntennaPowerResult, _Mapping]] = ...) -> None: ...

class SetAntennaPowerReply(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: AntennaPowerResult
    def __init__(self, result: _Optional[_Union[AntennaPowerResult, _Mapping]] = ...) -> None: ...

class GetAntennaElementPowerRequest(_message.Message):
    __slots__ = ("identifier", "element_index")
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    ELEMENT_INDEX_FIELD_NUMBER: _ClassVar[int]
    identifier: Identifier
    element_index: int
    def __init__(self, identifier: _Optional[_Union[Identifier, _Mapping]] = ..., element_index: _Optional[int] = ...) -> None: ...

class AntennaElementPowerResult(_message.Message):
    __slots__ = ("identifier", "element_index", "power_status")
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    ELEMENT_INDEX_FIELD_NUMBER: _ClassVar[int]
    POWER_STATUS_FIELD_NUMBER: _ClassVar[int]
    identifier: Identifier
    element_index: int
    power_status: Antenna_Power_Status
    def __init__(self, identifier: _Optional[_Union[Identifier, _Mapping]] = ..., element_index: _Optional[int] = ..., power_status: _Optional[_Union[Antenna_Power_Status, str]] = ...) -> None: ...

class GetAntennaElementPowerReply(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: AntennaElementPowerResult
    def __init__(self, result: _Optional[_Union[AntennaElementPowerResult, _Mapping]] = ...) -> None: ...

class SetAntennaElementPowerRequest(_message.Message):
    __slots__ = ("identifier", "element_index", "power_status")
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    ELEMENT_INDEX_FIELD_NUMBER: _ClassVar[int]
    POWER_STATUS_FIELD_NUMBER: _ClassVar[int]
    identifier: Identifier
    element_index: int
    power_status: Antenna_Power_Status
    def __init__(self, identifier: _Optional[_Union[Identifier, _Mapping]] = ..., element_index: _Optional[int] = ..., power_status: _Optional[_Union[Antenna_Power_Status, str]] = ...) -> None: ...

class SetAntennaElementPowerReply(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: AntennaElementPowerResult
    def __init__(self, result: _Optional[_Union[AntennaElementPowerResult, _Mapping]] = ...) -> None: ...

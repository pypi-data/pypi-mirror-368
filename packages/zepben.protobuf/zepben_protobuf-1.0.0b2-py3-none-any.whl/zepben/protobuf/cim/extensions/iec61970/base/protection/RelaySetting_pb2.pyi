from zepben.protobuf.cim.iec61970.base.domain import UnitSymbol_pb2 as _UnitSymbol_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RelaySetting(_message.Message):
    __slots__ = ("name", "unitSymbol", "value")
    NAME_FIELD_NUMBER: _ClassVar[int]
    UNITSYMBOL_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    name: str
    unitSymbol: _UnitSymbol_pb2.UnitSymbol
    value: float
    def __init__(self, name: _Optional[str] = ..., unitSymbol: _Optional[_Union[_UnitSymbol_pb2.UnitSymbol, str]] = ..., value: _Optional[float] = ...) -> None: ...

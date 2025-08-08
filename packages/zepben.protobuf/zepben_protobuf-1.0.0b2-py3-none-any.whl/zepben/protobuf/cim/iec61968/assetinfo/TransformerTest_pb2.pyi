from zepben.protobuf.cim.iec61970.base.core import IdentifiedObject_pb2 as _IdentifiedObject_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TransformerTest(_message.Message):
    __slots__ = ("io", "basePower", "temperature")
    IO_FIELD_NUMBER: _ClassVar[int]
    BASEPOWER_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    io: _IdentifiedObject_pb2.IdentifiedObject
    basePower: int
    temperature: float
    def __init__(self, io: _Optional[_Union[_IdentifiedObject_pb2.IdentifiedObject, _Mapping]] = ..., basePower: _Optional[int] = ..., temperature: _Optional[float] = ...) -> None: ...

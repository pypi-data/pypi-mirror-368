from zepben.protobuf.cim.iec61970.base.core import ConductingEquipment_pb2 as _ConductingEquipment_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Conductor(_message.Message):
    __slots__ = ("ce", "length", "designTemperature", "designRating")
    CE_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    DESIGNTEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    DESIGNRATING_FIELD_NUMBER: _ClassVar[int]
    ce: _ConductingEquipment_pb2.ConductingEquipment
    length: float
    designTemperature: int
    designRating: float
    def __init__(self, ce: _Optional[_Union[_ConductingEquipment_pb2.ConductingEquipment, _Mapping]] = ..., length: _Optional[float] = ..., designTemperature: _Optional[int] = ..., designRating: _Optional[float] = ...) -> None: ...

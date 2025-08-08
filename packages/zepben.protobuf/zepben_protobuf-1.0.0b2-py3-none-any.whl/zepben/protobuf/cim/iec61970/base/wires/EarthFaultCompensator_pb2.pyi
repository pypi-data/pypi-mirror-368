from zepben.protobuf.cim.iec61970.base.core import ConductingEquipment_pb2 as _ConductingEquipment_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EarthFaultCompensator(_message.Message):
    __slots__ = ("ce", "r")
    CE_FIELD_NUMBER: _ClassVar[int]
    R_FIELD_NUMBER: _ClassVar[int]
    ce: _ConductingEquipment_pb2.ConductingEquipment
    r: float
    def __init__(self, ce: _Optional[_Union[_ConductingEquipment_pb2.ConductingEquipment, _Mapping]] = ..., r: _Optional[float] = ...) -> None: ...

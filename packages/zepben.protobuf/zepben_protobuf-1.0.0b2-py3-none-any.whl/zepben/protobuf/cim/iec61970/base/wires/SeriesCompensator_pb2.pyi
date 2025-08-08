from zepben.protobuf.cim.iec61970.base.core import ConductingEquipment_pb2 as _ConductingEquipment_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SeriesCompensator(_message.Message):
    __slots__ = ("ce", "r", "r0", "x", "x0", "varistorRatedCurrent", "varistorVoltageThreshold")
    CE_FIELD_NUMBER: _ClassVar[int]
    R_FIELD_NUMBER: _ClassVar[int]
    R0_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    X0_FIELD_NUMBER: _ClassVar[int]
    VARISTORRATEDCURRENT_FIELD_NUMBER: _ClassVar[int]
    VARISTORVOLTAGETHRESHOLD_FIELD_NUMBER: _ClassVar[int]
    ce: _ConductingEquipment_pb2.ConductingEquipment
    r: float
    r0: float
    x: float
    x0: float
    varistorRatedCurrent: int
    varistorVoltageThreshold: int
    def __init__(self, ce: _Optional[_Union[_ConductingEquipment_pb2.ConductingEquipment, _Mapping]] = ..., r: _Optional[float] = ..., r0: _Optional[float] = ..., x: _Optional[float] = ..., x0: _Optional[float] = ..., varistorRatedCurrent: _Optional[int] = ..., varistorVoltageThreshold: _Optional[int] = ...) -> None: ...

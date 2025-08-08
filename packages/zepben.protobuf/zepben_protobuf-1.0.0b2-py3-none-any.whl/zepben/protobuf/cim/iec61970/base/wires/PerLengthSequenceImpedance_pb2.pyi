from zepben.protobuf.cim.iec61970.base.wires import PerLengthImpedance_pb2 as _PerLengthImpedance_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PerLengthSequenceImpedance(_message.Message):
    __slots__ = ("pli", "r", "x", "r0", "x0", "bch", "b0ch", "gch", "g0ch")
    PLI_FIELD_NUMBER: _ClassVar[int]
    R_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    R0_FIELD_NUMBER: _ClassVar[int]
    X0_FIELD_NUMBER: _ClassVar[int]
    BCH_FIELD_NUMBER: _ClassVar[int]
    B0CH_FIELD_NUMBER: _ClassVar[int]
    GCH_FIELD_NUMBER: _ClassVar[int]
    G0CH_FIELD_NUMBER: _ClassVar[int]
    pli: _PerLengthImpedance_pb2.PerLengthImpedance
    r: float
    x: float
    r0: float
    x0: float
    bch: float
    b0ch: float
    gch: float
    g0ch: float
    def __init__(self, pli: _Optional[_Union[_PerLengthImpedance_pb2.PerLengthImpedance, _Mapping]] = ..., r: _Optional[float] = ..., x: _Optional[float] = ..., r0: _Optional[float] = ..., x0: _Optional[float] = ..., bch: _Optional[float] = ..., b0ch: _Optional[float] = ..., gch: _Optional[float] = ..., g0ch: _Optional[float] = ...) -> None: ...

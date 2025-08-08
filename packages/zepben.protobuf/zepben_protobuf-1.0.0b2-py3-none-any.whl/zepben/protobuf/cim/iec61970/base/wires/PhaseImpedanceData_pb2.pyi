from zepben.protobuf.cim.iec61970.base.wires import SinglePhaseKind_pb2 as _SinglePhaseKind_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PhaseImpedanceData(_message.Message):
    __slots__ = ("b", "fromPhase", "toPhase", "g", "r", "x")
    B_FIELD_NUMBER: _ClassVar[int]
    FROMPHASE_FIELD_NUMBER: _ClassVar[int]
    TOPHASE_FIELD_NUMBER: _ClassVar[int]
    G_FIELD_NUMBER: _ClassVar[int]
    R_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    b: float
    fromPhase: _SinglePhaseKind_pb2.SinglePhaseKind
    toPhase: _SinglePhaseKind_pb2.SinglePhaseKind
    g: float
    r: float
    x: float
    def __init__(self, b: _Optional[float] = ..., fromPhase: _Optional[_Union[_SinglePhaseKind_pb2.SinglePhaseKind, str]] = ..., toPhase: _Optional[_Union[_SinglePhaseKind_pb2.SinglePhaseKind, str]] = ..., g: _Optional[float] = ..., r: _Optional[float] = ..., x: _Optional[float] = ...) -> None: ...

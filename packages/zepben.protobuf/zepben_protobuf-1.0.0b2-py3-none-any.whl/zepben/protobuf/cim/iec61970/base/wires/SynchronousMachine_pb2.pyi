from zepben.protobuf.cim.iec61970.base.wires import RotatingMachine_pb2 as _RotatingMachine_pb2
from zepben.protobuf.cim.iec61970.base.wires import SynchronousMachineKind_pb2 as _SynchronousMachineKind_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SynchronousMachine(_message.Message):
    __slots__ = ("rm", "baseQ", "condenserP", "earthing", "earthingStarPointR", "earthingStarPointX", "ikk", "maxQ", "maxU", "minQ", "minU", "mu", "r", "r0", "r2", "satDirectSubtransX", "satDirectSyncX", "satDirectTransX", "x0", "x2", "type", "operatingMode", "reactiveCapabilityCurveMRIDs")
    RM_FIELD_NUMBER: _ClassVar[int]
    BASEQ_FIELD_NUMBER: _ClassVar[int]
    CONDENSERP_FIELD_NUMBER: _ClassVar[int]
    EARTHING_FIELD_NUMBER: _ClassVar[int]
    EARTHINGSTARPOINTR_FIELD_NUMBER: _ClassVar[int]
    EARTHINGSTARPOINTX_FIELD_NUMBER: _ClassVar[int]
    IKK_FIELD_NUMBER: _ClassVar[int]
    MAXQ_FIELD_NUMBER: _ClassVar[int]
    MAXU_FIELD_NUMBER: _ClassVar[int]
    MINQ_FIELD_NUMBER: _ClassVar[int]
    MINU_FIELD_NUMBER: _ClassVar[int]
    MU_FIELD_NUMBER: _ClassVar[int]
    R_FIELD_NUMBER: _ClassVar[int]
    R0_FIELD_NUMBER: _ClassVar[int]
    R2_FIELD_NUMBER: _ClassVar[int]
    SATDIRECTSUBTRANSX_FIELD_NUMBER: _ClassVar[int]
    SATDIRECTSYNCX_FIELD_NUMBER: _ClassVar[int]
    SATDIRECTTRANSX_FIELD_NUMBER: _ClassVar[int]
    X0_FIELD_NUMBER: _ClassVar[int]
    X2_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    OPERATINGMODE_FIELD_NUMBER: _ClassVar[int]
    REACTIVECAPABILITYCURVEMRIDS_FIELD_NUMBER: _ClassVar[int]
    rm: _RotatingMachine_pb2.RotatingMachine
    baseQ: float
    condenserP: int
    earthing: bool
    earthingStarPointR: float
    earthingStarPointX: float
    ikk: float
    maxQ: float
    maxU: int
    minQ: float
    minU: int
    mu: float
    r: float
    r0: float
    r2: float
    satDirectSubtransX: float
    satDirectSyncX: float
    satDirectTransX: float
    x0: float
    x2: float
    type: _SynchronousMachineKind_pb2.SynchronousMachineKind
    operatingMode: _SynchronousMachineKind_pb2.SynchronousMachineKind
    reactiveCapabilityCurveMRIDs: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, rm: _Optional[_Union[_RotatingMachine_pb2.RotatingMachine, _Mapping]] = ..., baseQ: _Optional[float] = ..., condenserP: _Optional[int] = ..., earthing: bool = ..., earthingStarPointR: _Optional[float] = ..., earthingStarPointX: _Optional[float] = ..., ikk: _Optional[float] = ..., maxQ: _Optional[float] = ..., maxU: _Optional[int] = ..., minQ: _Optional[float] = ..., minU: _Optional[int] = ..., mu: _Optional[float] = ..., r: _Optional[float] = ..., r0: _Optional[float] = ..., r2: _Optional[float] = ..., satDirectSubtransX: _Optional[float] = ..., satDirectSyncX: _Optional[float] = ..., satDirectTransX: _Optional[float] = ..., x0: _Optional[float] = ..., x2: _Optional[float] = ..., type: _Optional[_Union[_SynchronousMachineKind_pb2.SynchronousMachineKind, str]] = ..., operatingMode: _Optional[_Union[_SynchronousMachineKind_pb2.SynchronousMachineKind, str]] = ..., reactiveCapabilityCurveMRIDs: _Optional[_Iterable[str]] = ...) -> None: ...

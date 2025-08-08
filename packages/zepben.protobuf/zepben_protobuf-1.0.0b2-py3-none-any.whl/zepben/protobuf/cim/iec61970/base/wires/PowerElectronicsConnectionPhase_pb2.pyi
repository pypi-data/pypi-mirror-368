from zepben.protobuf.cim.iec61970.base.core import PowerSystemResource_pb2 as _PowerSystemResource_pb2
from zepben.protobuf.cim.iec61970.base.wires import SinglePhaseKind_pb2 as _SinglePhaseKind_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PowerElectronicsConnectionPhase(_message.Message):
    __slots__ = ("psr", "p", "phase", "q", "powerElectronicsConnectionMRID")
    PSR_FIELD_NUMBER: _ClassVar[int]
    P_FIELD_NUMBER: _ClassVar[int]
    PHASE_FIELD_NUMBER: _ClassVar[int]
    Q_FIELD_NUMBER: _ClassVar[int]
    POWERELECTRONICSCONNECTIONMRID_FIELD_NUMBER: _ClassVar[int]
    psr: _PowerSystemResource_pb2.PowerSystemResource
    p: float
    phase: _SinglePhaseKind_pb2.SinglePhaseKind
    q: float
    powerElectronicsConnectionMRID: str
    def __init__(self, psr: _Optional[_Union[_PowerSystemResource_pb2.PowerSystemResource, _Mapping]] = ..., p: _Optional[float] = ..., phase: _Optional[_Union[_SinglePhaseKind_pb2.SinglePhaseKind, str]] = ..., q: _Optional[float] = ..., powerElectronicsConnectionMRID: _Optional[str] = ...) -> None: ...

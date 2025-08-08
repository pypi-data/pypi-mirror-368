from zepben.protobuf.cim.extensions.iec61970.base.protection import ProtectionRelayFunction_pb2 as _ProtectionRelayFunction_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DistanceRelay(_message.Message):
    __slots__ = ("prf", "backwardBlind", "backwardReach", "backwardReactance", "forwardBlind", "forwardReach", "forwardReactance", "operationPhaseAngle1", "operationPhaseAngle2", "operationPhaseAngle3")
    PRF_FIELD_NUMBER: _ClassVar[int]
    BACKWARDBLIND_FIELD_NUMBER: _ClassVar[int]
    BACKWARDREACH_FIELD_NUMBER: _ClassVar[int]
    BACKWARDREACTANCE_FIELD_NUMBER: _ClassVar[int]
    FORWARDBLIND_FIELD_NUMBER: _ClassVar[int]
    FORWARDREACH_FIELD_NUMBER: _ClassVar[int]
    FORWARDREACTANCE_FIELD_NUMBER: _ClassVar[int]
    OPERATIONPHASEANGLE1_FIELD_NUMBER: _ClassVar[int]
    OPERATIONPHASEANGLE2_FIELD_NUMBER: _ClassVar[int]
    OPERATIONPHASEANGLE3_FIELD_NUMBER: _ClassVar[int]
    prf: _ProtectionRelayFunction_pb2.ProtectionRelayFunction
    backwardBlind: float
    backwardReach: float
    backwardReactance: float
    forwardBlind: float
    forwardReach: float
    forwardReactance: float
    operationPhaseAngle1: float
    operationPhaseAngle2: float
    operationPhaseAngle3: float
    def __init__(self, prf: _Optional[_Union[_ProtectionRelayFunction_pb2.ProtectionRelayFunction, _Mapping]] = ..., backwardBlind: _Optional[float] = ..., backwardReach: _Optional[float] = ..., backwardReactance: _Optional[float] = ..., forwardBlind: _Optional[float] = ..., forwardReach: _Optional[float] = ..., forwardReactance: _Optional[float] = ..., operationPhaseAngle1: _Optional[float] = ..., operationPhaseAngle2: _Optional[float] = ..., operationPhaseAngle3: _Optional[float] = ...) -> None: ...

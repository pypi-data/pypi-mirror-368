from zepben.protobuf.cim.iec61970.base.wires import RegulatingCondEq_pb2 as _RegulatingCondEq_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RotatingMachine(_message.Message):
    __slots__ = ("rce", "ratedPowerFactor", "ratedS", "ratedU", "p", "q")
    RCE_FIELD_NUMBER: _ClassVar[int]
    RATEDPOWERFACTOR_FIELD_NUMBER: _ClassVar[int]
    RATEDS_FIELD_NUMBER: _ClassVar[int]
    RATEDU_FIELD_NUMBER: _ClassVar[int]
    P_FIELD_NUMBER: _ClassVar[int]
    Q_FIELD_NUMBER: _ClassVar[int]
    rce: _RegulatingCondEq_pb2.RegulatingCondEq
    ratedPowerFactor: float
    ratedS: float
    ratedU: int
    p: float
    q: float
    def __init__(self, rce: _Optional[_Union[_RegulatingCondEq_pb2.RegulatingCondEq, _Mapping]] = ..., ratedPowerFactor: _Optional[float] = ..., ratedS: _Optional[float] = ..., ratedU: _Optional[int] = ..., p: _Optional[float] = ..., q: _Optional[float] = ...) -> None: ...

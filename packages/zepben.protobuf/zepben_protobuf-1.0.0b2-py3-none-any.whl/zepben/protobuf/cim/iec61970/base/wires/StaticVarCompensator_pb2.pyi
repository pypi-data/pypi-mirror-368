from zepben.protobuf.cim.iec61970.base.wires import RegulatingCondEq_pb2 as _RegulatingCondEq_pb2
from zepben.protobuf.cim.iec61970.base.wires import SVCControlMode_pb2 as _SVCControlMode_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StaticVarCompensator(_message.Message):
    __slots__ = ("rce", "capacitiveRating", "inductiveRating", "q", "svcControlMode", "voltageSetPoint")
    RCE_FIELD_NUMBER: _ClassVar[int]
    CAPACITIVERATING_FIELD_NUMBER: _ClassVar[int]
    INDUCTIVERATING_FIELD_NUMBER: _ClassVar[int]
    Q_FIELD_NUMBER: _ClassVar[int]
    SVCCONTROLMODE_FIELD_NUMBER: _ClassVar[int]
    VOLTAGESETPOINT_FIELD_NUMBER: _ClassVar[int]
    rce: _RegulatingCondEq_pb2.RegulatingCondEq
    capacitiveRating: float
    inductiveRating: float
    q: float
    svcControlMode: _SVCControlMode_pb2.SVCControlMode
    voltageSetPoint: int
    def __init__(self, rce: _Optional[_Union[_RegulatingCondEq_pb2.RegulatingCondEq, _Mapping]] = ..., capacitiveRating: _Optional[float] = ..., inductiveRating: _Optional[float] = ..., q: _Optional[float] = ..., svcControlMode: _Optional[_Union[_SVCControlMode_pb2.SVCControlMode, str]] = ..., voltageSetPoint: _Optional[int] = ...) -> None: ...

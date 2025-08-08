from google.protobuf import struct_pb2 as _struct_pb2
from zepben.protobuf.cim.iec61970.base.wires import RegulatingControl_pb2 as _RegulatingControl_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TapChangerControl(_message.Message):
    __slots__ = ("rc", "limitVoltage", "lineDropCompensationNull", "lineDropCompensationSet", "lineDropR", "lineDropX", "reverseLineDropR", "reverseLineDropX", "forwardLDCBlockingNull", "forwardLDCBlockingSet", "timeDelay", "coGenerationEnabledNull", "coGenerationEnabledSet")
    RC_FIELD_NUMBER: _ClassVar[int]
    LIMITVOLTAGE_FIELD_NUMBER: _ClassVar[int]
    LINEDROPCOMPENSATIONNULL_FIELD_NUMBER: _ClassVar[int]
    LINEDROPCOMPENSATIONSET_FIELD_NUMBER: _ClassVar[int]
    LINEDROPR_FIELD_NUMBER: _ClassVar[int]
    LINEDROPX_FIELD_NUMBER: _ClassVar[int]
    REVERSELINEDROPR_FIELD_NUMBER: _ClassVar[int]
    REVERSELINEDROPX_FIELD_NUMBER: _ClassVar[int]
    FORWARDLDCBLOCKINGNULL_FIELD_NUMBER: _ClassVar[int]
    FORWARDLDCBLOCKINGSET_FIELD_NUMBER: _ClassVar[int]
    TIMEDELAY_FIELD_NUMBER: _ClassVar[int]
    COGENERATIONENABLEDNULL_FIELD_NUMBER: _ClassVar[int]
    COGENERATIONENABLEDSET_FIELD_NUMBER: _ClassVar[int]
    rc: _RegulatingControl_pb2.RegulatingControl
    limitVoltage: int
    lineDropCompensationNull: _struct_pb2.NullValue
    lineDropCompensationSet: bool
    lineDropR: float
    lineDropX: float
    reverseLineDropR: float
    reverseLineDropX: float
    forwardLDCBlockingNull: _struct_pb2.NullValue
    forwardLDCBlockingSet: bool
    timeDelay: float
    coGenerationEnabledNull: _struct_pb2.NullValue
    coGenerationEnabledSet: bool
    def __init__(self, rc: _Optional[_Union[_RegulatingControl_pb2.RegulatingControl, _Mapping]] = ..., limitVoltage: _Optional[int] = ..., lineDropCompensationNull: _Optional[_Union[_struct_pb2.NullValue, str]] = ..., lineDropCompensationSet: bool = ..., lineDropR: _Optional[float] = ..., lineDropX: _Optional[float] = ..., reverseLineDropR: _Optional[float] = ..., reverseLineDropX: _Optional[float] = ..., forwardLDCBlockingNull: _Optional[_Union[_struct_pb2.NullValue, str]] = ..., forwardLDCBlockingSet: bool = ..., timeDelay: _Optional[float] = ..., coGenerationEnabledNull: _Optional[_Union[_struct_pb2.NullValue, str]] = ..., coGenerationEnabledSet: bool = ...) -> None: ...

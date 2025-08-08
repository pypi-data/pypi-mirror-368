from zepben.protobuf.cim.iec61970.base.equivalents import EquivalentEquipment_pb2 as _EquivalentEquipment_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EquivalentBranch(_message.Message):
    __slots__ = ("ee", "negativeR12", "negativeR21", "negativeX12", "negativeX21", "positiveR12", "positiveR21", "positiveX12", "positiveX21", "r", "r21", "x", "x21", "zeroR12", "zeroR21", "zeroX12", "zeroX21")
    EE_FIELD_NUMBER: _ClassVar[int]
    NEGATIVER12_FIELD_NUMBER: _ClassVar[int]
    NEGATIVER21_FIELD_NUMBER: _ClassVar[int]
    NEGATIVEX12_FIELD_NUMBER: _ClassVar[int]
    NEGATIVEX21_FIELD_NUMBER: _ClassVar[int]
    POSITIVER12_FIELD_NUMBER: _ClassVar[int]
    POSITIVER21_FIELD_NUMBER: _ClassVar[int]
    POSITIVEX12_FIELD_NUMBER: _ClassVar[int]
    POSITIVEX21_FIELD_NUMBER: _ClassVar[int]
    R_FIELD_NUMBER: _ClassVar[int]
    R21_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    X21_FIELD_NUMBER: _ClassVar[int]
    ZEROR12_FIELD_NUMBER: _ClassVar[int]
    ZEROR21_FIELD_NUMBER: _ClassVar[int]
    ZEROX12_FIELD_NUMBER: _ClassVar[int]
    ZEROX21_FIELD_NUMBER: _ClassVar[int]
    ee: _EquivalentEquipment_pb2.EquivalentEquipment
    negativeR12: float
    negativeR21: float
    negativeX12: float
    negativeX21: float
    positiveR12: float
    positiveR21: float
    positiveX12: float
    positiveX21: float
    r: float
    r21: float
    x: float
    x21: float
    zeroR12: float
    zeroR21: float
    zeroX12: float
    zeroX21: float
    def __init__(self, ee: _Optional[_Union[_EquivalentEquipment_pb2.EquivalentEquipment, _Mapping]] = ..., negativeR12: _Optional[float] = ..., negativeR21: _Optional[float] = ..., negativeX12: _Optional[float] = ..., negativeX21: _Optional[float] = ..., positiveR12: _Optional[float] = ..., positiveR21: _Optional[float] = ..., positiveX12: _Optional[float] = ..., positiveX21: _Optional[float] = ..., r: _Optional[float] = ..., r21: _Optional[float] = ..., x: _Optional[float] = ..., x21: _Optional[float] = ..., zeroR12: _Optional[float] = ..., zeroR21: _Optional[float] = ..., zeroX12: _Optional[float] = ..., zeroX21: _Optional[float] = ...) -> None: ...

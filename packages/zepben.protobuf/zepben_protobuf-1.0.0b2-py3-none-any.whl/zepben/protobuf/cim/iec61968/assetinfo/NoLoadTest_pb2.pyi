from zepben.protobuf.cim.iec61968.assetinfo import TransformerTest_pb2 as _TransformerTest_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class NoLoadTest(_message.Message):
    __slots__ = ("tt", "energisedEndVoltage", "excitingCurrent", "excitingCurrentZero", "loss", "lossZero")
    TT_FIELD_NUMBER: _ClassVar[int]
    ENERGISEDENDVOLTAGE_FIELD_NUMBER: _ClassVar[int]
    EXCITINGCURRENT_FIELD_NUMBER: _ClassVar[int]
    EXCITINGCURRENTZERO_FIELD_NUMBER: _ClassVar[int]
    LOSS_FIELD_NUMBER: _ClassVar[int]
    LOSSZERO_FIELD_NUMBER: _ClassVar[int]
    tt: _TransformerTest_pb2.TransformerTest
    energisedEndVoltage: int
    excitingCurrent: float
    excitingCurrentZero: float
    loss: int
    lossZero: int
    def __init__(self, tt: _Optional[_Union[_TransformerTest_pb2.TransformerTest, _Mapping]] = ..., energisedEndVoltage: _Optional[int] = ..., excitingCurrent: _Optional[float] = ..., excitingCurrentZero: _Optional[float] = ..., loss: _Optional[int] = ..., lossZero: _Optional[int] = ...) -> None: ...

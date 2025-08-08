from zepben.protobuf.cim.iec61968.assetinfo import TransformerTest_pb2 as _TransformerTest_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ShortCircuitTest(_message.Message):
    __slots__ = ("tt", "current", "energisedEndStep", "groundedEndStep", "leakageImpedance", "leakageImpedanceZero", "loss", "lossZero", "power", "voltage", "voltageOhmicPart")
    TT_FIELD_NUMBER: _ClassVar[int]
    CURRENT_FIELD_NUMBER: _ClassVar[int]
    ENERGISEDENDSTEP_FIELD_NUMBER: _ClassVar[int]
    GROUNDEDENDSTEP_FIELD_NUMBER: _ClassVar[int]
    LEAKAGEIMPEDANCE_FIELD_NUMBER: _ClassVar[int]
    LEAKAGEIMPEDANCEZERO_FIELD_NUMBER: _ClassVar[int]
    LOSS_FIELD_NUMBER: _ClassVar[int]
    LOSSZERO_FIELD_NUMBER: _ClassVar[int]
    POWER_FIELD_NUMBER: _ClassVar[int]
    VOLTAGE_FIELD_NUMBER: _ClassVar[int]
    VOLTAGEOHMICPART_FIELD_NUMBER: _ClassVar[int]
    tt: _TransformerTest_pb2.TransformerTest
    current: float
    energisedEndStep: int
    groundedEndStep: int
    leakageImpedance: float
    leakageImpedanceZero: float
    loss: int
    lossZero: int
    power: int
    voltage: float
    voltageOhmicPart: float
    def __init__(self, tt: _Optional[_Union[_TransformerTest_pb2.TransformerTest, _Mapping]] = ..., current: _Optional[float] = ..., energisedEndStep: _Optional[int] = ..., groundedEndStep: _Optional[int] = ..., leakageImpedance: _Optional[float] = ..., leakageImpedanceZero: _Optional[float] = ..., loss: _Optional[int] = ..., lossZero: _Optional[int] = ..., power: _Optional[int] = ..., voltage: _Optional[float] = ..., voltageOhmicPart: _Optional[float] = ...) -> None: ...

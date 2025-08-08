from zepben.protobuf.cim.iec61968.assetinfo import TransformerTest_pb2 as _TransformerTest_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OpenCircuitTest(_message.Message):
    __slots__ = ("tt", "energisedEndStep", "energisedEndVoltage", "openEndStep", "openEndVoltage", "phaseShift")
    TT_FIELD_NUMBER: _ClassVar[int]
    ENERGISEDENDSTEP_FIELD_NUMBER: _ClassVar[int]
    ENERGISEDENDVOLTAGE_FIELD_NUMBER: _ClassVar[int]
    OPENENDSTEP_FIELD_NUMBER: _ClassVar[int]
    OPENENDVOLTAGE_FIELD_NUMBER: _ClassVar[int]
    PHASESHIFT_FIELD_NUMBER: _ClassVar[int]
    tt: _TransformerTest_pb2.TransformerTest
    energisedEndStep: int
    energisedEndVoltage: int
    openEndStep: int
    openEndVoltage: int
    phaseShift: float
    def __init__(self, tt: _Optional[_Union[_TransformerTest_pb2.TransformerTest, _Mapping]] = ..., energisedEndStep: _Optional[int] = ..., energisedEndVoltage: _Optional[int] = ..., openEndStep: _Optional[int] = ..., openEndVoltage: _Optional[int] = ..., phaseShift: _Optional[float] = ...) -> None: ...

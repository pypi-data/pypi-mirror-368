from zepben.protobuf.cim.iec61970.base.wires import TapChanger_pb2 as _TapChanger_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RatioTapChanger(_message.Message):
    __slots__ = ("tc", "stepVoltageIncrement", "transformerEndMRID")
    TC_FIELD_NUMBER: _ClassVar[int]
    STEPVOLTAGEINCREMENT_FIELD_NUMBER: _ClassVar[int]
    TRANSFORMERENDMRID_FIELD_NUMBER: _ClassVar[int]
    tc: _TapChanger_pb2.TapChanger
    stepVoltageIncrement: float
    transformerEndMRID: str
    def __init__(self, tc: _Optional[_Union[_TapChanger_pb2.TapChanger, _Mapping]] = ..., stepVoltageIncrement: _Optional[float] = ..., transformerEndMRID: _Optional[str] = ...) -> None: ...

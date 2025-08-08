from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class CurveData(_message.Message):
    __slots__ = ("xValue", "y1Value", "y2Value", "y3Value")
    XVALUE_FIELD_NUMBER: _ClassVar[int]
    Y1VALUE_FIELD_NUMBER: _ClassVar[int]
    Y2VALUE_FIELD_NUMBER: _ClassVar[int]
    Y3VALUE_FIELD_NUMBER: _ClassVar[int]
    xValue: float
    y1Value: float
    y2Value: float
    y3Value: float
    def __init__(self, xValue: _Optional[float] = ..., y1Value: _Optional[float] = ..., y2Value: _Optional[float] = ..., y3Value: _Optional[float] = ...) -> None: ...

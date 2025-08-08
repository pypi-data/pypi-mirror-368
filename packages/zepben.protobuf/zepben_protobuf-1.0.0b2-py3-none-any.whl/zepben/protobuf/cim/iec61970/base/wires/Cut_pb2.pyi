from zepben.protobuf.cim.iec61970.base.wires import Switch_pb2 as _Switch_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Cut(_message.Message):
    __slots__ = ("sw", "lengthFromTerminal1", "acLineSegmentMRID")
    SW_FIELD_NUMBER: _ClassVar[int]
    LENGTHFROMTERMINAL1_FIELD_NUMBER: _ClassVar[int]
    ACLINESEGMENTMRID_FIELD_NUMBER: _ClassVar[int]
    sw: _Switch_pb2.Switch
    lengthFromTerminal1: float
    acLineSegmentMRID: str
    def __init__(self, sw: _Optional[_Union[_Switch_pb2.Switch, _Mapping]] = ..., lengthFromTerminal1: _Optional[float] = ..., acLineSegmentMRID: _Optional[str] = ...) -> None: ...

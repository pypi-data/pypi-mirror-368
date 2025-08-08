from zepben.protobuf.cim.iec61970.base.core import IdentifiedObject_pb2 as _IdentifiedObject_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TransformerEnd(_message.Message):
    __slots__ = ("io", "terminalMRID", "baseVoltageMRID", "endNumber", "ratioTapChangerMRID", "grounded", "rGround", "xGround", "starImpedanceMRID")
    IO_FIELD_NUMBER: _ClassVar[int]
    TERMINALMRID_FIELD_NUMBER: _ClassVar[int]
    BASEVOLTAGEMRID_FIELD_NUMBER: _ClassVar[int]
    ENDNUMBER_FIELD_NUMBER: _ClassVar[int]
    RATIOTAPCHANGERMRID_FIELD_NUMBER: _ClassVar[int]
    GROUNDED_FIELD_NUMBER: _ClassVar[int]
    RGROUND_FIELD_NUMBER: _ClassVar[int]
    XGROUND_FIELD_NUMBER: _ClassVar[int]
    STARIMPEDANCEMRID_FIELD_NUMBER: _ClassVar[int]
    io: _IdentifiedObject_pb2.IdentifiedObject
    terminalMRID: str
    baseVoltageMRID: str
    endNumber: int
    ratioTapChangerMRID: str
    grounded: bool
    rGround: float
    xGround: float
    starImpedanceMRID: str
    def __init__(self, io: _Optional[_Union[_IdentifiedObject_pb2.IdentifiedObject, _Mapping]] = ..., terminalMRID: _Optional[str] = ..., baseVoltageMRID: _Optional[str] = ..., endNumber: _Optional[int] = ..., ratioTapChangerMRID: _Optional[str] = ..., grounded: bool = ..., rGround: _Optional[float] = ..., xGround: _Optional[float] = ..., starImpedanceMRID: _Optional[str] = ...) -> None: ...

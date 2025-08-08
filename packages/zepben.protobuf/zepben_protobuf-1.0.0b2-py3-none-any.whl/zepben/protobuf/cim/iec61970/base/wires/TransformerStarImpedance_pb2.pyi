from zepben.protobuf.cim.iec61970.base.core import IdentifiedObject_pb2 as _IdentifiedObject_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TransformerStarImpedance(_message.Message):
    __slots__ = ("io", "r", "r0", "x", "x0", "transformerEndInfoMRID")
    IO_FIELD_NUMBER: _ClassVar[int]
    R_FIELD_NUMBER: _ClassVar[int]
    R0_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    X0_FIELD_NUMBER: _ClassVar[int]
    TRANSFORMERENDINFOMRID_FIELD_NUMBER: _ClassVar[int]
    io: _IdentifiedObject_pb2.IdentifiedObject
    r: float
    r0: float
    x: float
    x0: float
    transformerEndInfoMRID: str
    def __init__(self, io: _Optional[_Union[_IdentifiedObject_pb2.IdentifiedObject, _Mapping]] = ..., r: _Optional[float] = ..., r0: _Optional[float] = ..., x: _Optional[float] = ..., x0: _Optional[float] = ..., transformerEndInfoMRID: _Optional[str] = ...) -> None: ...

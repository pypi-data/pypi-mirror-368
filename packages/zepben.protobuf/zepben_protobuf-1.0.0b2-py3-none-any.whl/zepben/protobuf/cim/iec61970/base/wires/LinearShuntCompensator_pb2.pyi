from zepben.protobuf.cim.iec61970.base.wires import ShuntCompensator_pb2 as _ShuntCompensator_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LinearShuntCompensator(_message.Message):
    __slots__ = ("sc", "b0PerSection", "bPerSection", "g0PerSection", "gPerSection")
    SC_FIELD_NUMBER: _ClassVar[int]
    B0PERSECTION_FIELD_NUMBER: _ClassVar[int]
    BPERSECTION_FIELD_NUMBER: _ClassVar[int]
    G0PERSECTION_FIELD_NUMBER: _ClassVar[int]
    GPERSECTION_FIELD_NUMBER: _ClassVar[int]
    sc: _ShuntCompensator_pb2.ShuntCompensator
    b0PerSection: float
    bPerSection: float
    g0PerSection: float
    gPerSection: float
    def __init__(self, sc: _Optional[_Union[_ShuntCompensator_pb2.ShuntCompensator, _Mapping]] = ..., b0PerSection: _Optional[float] = ..., bPerSection: _Optional[float] = ..., g0PerSection: _Optional[float] = ..., gPerSection: _Optional[float] = ...) -> None: ...

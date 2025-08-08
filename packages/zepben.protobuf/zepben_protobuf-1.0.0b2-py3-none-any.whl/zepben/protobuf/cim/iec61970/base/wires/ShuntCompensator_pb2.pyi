from zepben.protobuf.cim.iec61970.base.wires import PhaseShuntConnectionKind_pb2 as _PhaseShuntConnectionKind_pb2
from zepben.protobuf.cim.iec61970.base.wires import RegulatingCondEq_pb2 as _RegulatingCondEq_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ShuntCompensator(_message.Message):
    __slots__ = ("rce", "sections", "grounded", "nomU", "phaseConnection")
    RCE_FIELD_NUMBER: _ClassVar[int]
    SECTIONS_FIELD_NUMBER: _ClassVar[int]
    GROUNDED_FIELD_NUMBER: _ClassVar[int]
    NOMU_FIELD_NUMBER: _ClassVar[int]
    PHASECONNECTION_FIELD_NUMBER: _ClassVar[int]
    rce: _RegulatingCondEq_pb2.RegulatingCondEq
    sections: float
    grounded: bool
    nomU: int
    phaseConnection: _PhaseShuntConnectionKind_pb2.PhaseShuntConnectionKind
    def __init__(self, rce: _Optional[_Union[_RegulatingCondEq_pb2.RegulatingCondEq, _Mapping]] = ..., sections: _Optional[float] = ..., grounded: bool = ..., nomU: _Optional[int] = ..., phaseConnection: _Optional[_Union[_PhaseShuntConnectionKind_pb2.PhaseShuntConnectionKind, str]] = ...) -> None: ...

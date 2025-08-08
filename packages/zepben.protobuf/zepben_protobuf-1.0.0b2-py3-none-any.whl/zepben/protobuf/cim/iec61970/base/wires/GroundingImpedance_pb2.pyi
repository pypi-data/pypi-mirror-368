from zepben.protobuf.cim.iec61970.base.wires import EarthFaultCompensator_pb2 as _EarthFaultCompensator_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GroundingImpedance(_message.Message):
    __slots__ = ("efc", "x")
    EFC_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    efc: _EarthFaultCompensator_pb2.EarthFaultCompensator
    x: float
    def __init__(self, efc: _Optional[_Union[_EarthFaultCompensator_pb2.EarthFaultCompensator, _Mapping]] = ..., x: _Optional[float] = ...) -> None: ...

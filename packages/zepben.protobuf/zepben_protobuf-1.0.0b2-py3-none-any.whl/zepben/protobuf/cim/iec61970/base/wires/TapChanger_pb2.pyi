from zepben.protobuf.cim.iec61970.base.core import PowerSystemResource_pb2 as _PowerSystemResource_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TapChanger(_message.Message):
    __slots__ = ("psr", "highStep", "lowStep", "step", "neutralStep", "neutralU", "normalStep", "controlEnabled", "tapChangerControlMRID")
    PSR_FIELD_NUMBER: _ClassVar[int]
    HIGHSTEP_FIELD_NUMBER: _ClassVar[int]
    LOWSTEP_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    NEUTRALSTEP_FIELD_NUMBER: _ClassVar[int]
    NEUTRALU_FIELD_NUMBER: _ClassVar[int]
    NORMALSTEP_FIELD_NUMBER: _ClassVar[int]
    CONTROLENABLED_FIELD_NUMBER: _ClassVar[int]
    TAPCHANGERCONTROLMRID_FIELD_NUMBER: _ClassVar[int]
    psr: _PowerSystemResource_pb2.PowerSystemResource
    highStep: int
    lowStep: int
    step: float
    neutralStep: int
    neutralU: int
    normalStep: int
    controlEnabled: bool
    tapChangerControlMRID: str
    def __init__(self, psr: _Optional[_Union[_PowerSystemResource_pb2.PowerSystemResource, _Mapping]] = ..., highStep: _Optional[int] = ..., lowStep: _Optional[int] = ..., step: _Optional[float] = ..., neutralStep: _Optional[int] = ..., neutralU: _Optional[int] = ..., normalStep: _Optional[int] = ..., controlEnabled: bool = ..., tapChangerControlMRID: _Optional[str] = ...) -> None: ...

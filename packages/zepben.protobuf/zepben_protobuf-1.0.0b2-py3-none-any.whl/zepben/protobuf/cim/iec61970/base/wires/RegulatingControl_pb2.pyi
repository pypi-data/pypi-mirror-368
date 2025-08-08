from zepben.protobuf.cim.iec61970.base.core import PhaseCode_pb2 as _PhaseCode_pb2
from zepben.protobuf.cim.iec61970.base.core import PowerSystemResource_pb2 as _PowerSystemResource_pb2
from zepben.protobuf.cim.iec61970.base.wires import RegulatingControlModeKind_pb2 as _RegulatingControlModeKind_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RegulatingControl(_message.Message):
    __slots__ = ("psr", "discreteNull", "discreteSet", "mode", "monitoredPhase", "targetDeadband", "targetValue", "enabledNull", "enabledSet", "maxAllowedTargetValue", "minAllowedTargetValue", "terminalMRID", "regulatingCondEqMRIDs", "ratedCurrent", "ctPrimary", "minTargetDeadband")
    PSR_FIELD_NUMBER: _ClassVar[int]
    DISCRETENULL_FIELD_NUMBER: _ClassVar[int]
    DISCRETESET_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    MONITOREDPHASE_FIELD_NUMBER: _ClassVar[int]
    TARGETDEADBAND_FIELD_NUMBER: _ClassVar[int]
    TARGETVALUE_FIELD_NUMBER: _ClassVar[int]
    ENABLEDNULL_FIELD_NUMBER: _ClassVar[int]
    ENABLEDSET_FIELD_NUMBER: _ClassVar[int]
    MAXALLOWEDTARGETVALUE_FIELD_NUMBER: _ClassVar[int]
    MINALLOWEDTARGETVALUE_FIELD_NUMBER: _ClassVar[int]
    TERMINALMRID_FIELD_NUMBER: _ClassVar[int]
    REGULATINGCONDEQMRIDS_FIELD_NUMBER: _ClassVar[int]
    RATEDCURRENT_FIELD_NUMBER: _ClassVar[int]
    CTPRIMARY_FIELD_NUMBER: _ClassVar[int]
    MINTARGETDEADBAND_FIELD_NUMBER: _ClassVar[int]
    psr: _PowerSystemResource_pb2.PowerSystemResource
    discreteNull: _struct_pb2.NullValue
    discreteSet: bool
    mode: _RegulatingControlModeKind_pb2.RegulatingControlModeKind
    monitoredPhase: _PhaseCode_pb2.PhaseCode
    targetDeadband: float
    targetValue: float
    enabledNull: _struct_pb2.NullValue
    enabledSet: bool
    maxAllowedTargetValue: float
    minAllowedTargetValue: float
    terminalMRID: str
    regulatingCondEqMRIDs: _containers.RepeatedScalarFieldContainer[str]
    ratedCurrent: float
    ctPrimary: float
    minTargetDeadband: float
    def __init__(self, psr: _Optional[_Union[_PowerSystemResource_pb2.PowerSystemResource, _Mapping]] = ..., discreteNull: _Optional[_Union[_struct_pb2.NullValue, str]] = ..., discreteSet: bool = ..., mode: _Optional[_Union[_RegulatingControlModeKind_pb2.RegulatingControlModeKind, str]] = ..., monitoredPhase: _Optional[_Union[_PhaseCode_pb2.PhaseCode, str]] = ..., targetDeadband: _Optional[float] = ..., targetValue: _Optional[float] = ..., enabledNull: _Optional[_Union[_struct_pb2.NullValue, str]] = ..., enabledSet: bool = ..., maxAllowedTargetValue: _Optional[float] = ..., minAllowedTargetValue: _Optional[float] = ..., terminalMRID: _Optional[str] = ..., regulatingCondEqMRIDs: _Optional[_Iterable[str]] = ..., ratedCurrent: _Optional[float] = ..., ctPrimary: _Optional[float] = ..., minTargetDeadband: _Optional[float] = ...) -> None: ...

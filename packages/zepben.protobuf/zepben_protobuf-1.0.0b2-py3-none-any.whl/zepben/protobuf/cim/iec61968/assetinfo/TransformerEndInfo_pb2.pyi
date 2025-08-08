from zepben.protobuf.cim.iec61968.assets import AssetInfo_pb2 as _AssetInfo_pb2
from zepben.protobuf.cim.iec61970.base.wires import WindingConnection_pb2 as _WindingConnection_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TransformerEndInfo(_message.Message):
    __slots__ = ("ai", "connectionKind", "emergencyS", "endNumber", "insulationU", "phaseAngleClock", "r", "ratedS", "ratedU", "shortTermS", "transformerTankInfoMRID", "transformerStarImpedanceMRID", "energisedEndNoLoadTestsMRID", "energisedEndShortCircuitTestsMRID", "groundedEndShortCircuitTestsMRID", "openEndOpenCircuitTestsMRID", "energisedEndOpenCircuitTestsMRID")
    AI_FIELD_NUMBER: _ClassVar[int]
    CONNECTIONKIND_FIELD_NUMBER: _ClassVar[int]
    EMERGENCYS_FIELD_NUMBER: _ClassVar[int]
    ENDNUMBER_FIELD_NUMBER: _ClassVar[int]
    INSULATIONU_FIELD_NUMBER: _ClassVar[int]
    PHASEANGLECLOCK_FIELD_NUMBER: _ClassVar[int]
    R_FIELD_NUMBER: _ClassVar[int]
    RATEDS_FIELD_NUMBER: _ClassVar[int]
    RATEDU_FIELD_NUMBER: _ClassVar[int]
    SHORTTERMS_FIELD_NUMBER: _ClassVar[int]
    TRANSFORMERTANKINFOMRID_FIELD_NUMBER: _ClassVar[int]
    TRANSFORMERSTARIMPEDANCEMRID_FIELD_NUMBER: _ClassVar[int]
    ENERGISEDENDNOLOADTESTSMRID_FIELD_NUMBER: _ClassVar[int]
    ENERGISEDENDSHORTCIRCUITTESTSMRID_FIELD_NUMBER: _ClassVar[int]
    GROUNDEDENDSHORTCIRCUITTESTSMRID_FIELD_NUMBER: _ClassVar[int]
    OPENENDOPENCIRCUITTESTSMRID_FIELD_NUMBER: _ClassVar[int]
    ENERGISEDENDOPENCIRCUITTESTSMRID_FIELD_NUMBER: _ClassVar[int]
    ai: _AssetInfo_pb2.AssetInfo
    connectionKind: _WindingConnection_pb2.WindingConnection
    emergencyS: int
    endNumber: int
    insulationU: int
    phaseAngleClock: int
    r: float
    ratedS: int
    ratedU: int
    shortTermS: int
    transformerTankInfoMRID: str
    transformerStarImpedanceMRID: str
    energisedEndNoLoadTestsMRID: str
    energisedEndShortCircuitTestsMRID: str
    groundedEndShortCircuitTestsMRID: str
    openEndOpenCircuitTestsMRID: str
    energisedEndOpenCircuitTestsMRID: str
    def __init__(self, ai: _Optional[_Union[_AssetInfo_pb2.AssetInfo, _Mapping]] = ..., connectionKind: _Optional[_Union[_WindingConnection_pb2.WindingConnection, str]] = ..., emergencyS: _Optional[int] = ..., endNumber: _Optional[int] = ..., insulationU: _Optional[int] = ..., phaseAngleClock: _Optional[int] = ..., r: _Optional[float] = ..., ratedS: _Optional[int] = ..., ratedU: _Optional[int] = ..., shortTermS: _Optional[int] = ..., transformerTankInfoMRID: _Optional[str] = ..., transformerStarImpedanceMRID: _Optional[str] = ..., energisedEndNoLoadTestsMRID: _Optional[str] = ..., energisedEndShortCircuitTestsMRID: _Optional[str] = ..., groundedEndShortCircuitTestsMRID: _Optional[str] = ..., openEndOpenCircuitTestsMRID: _Optional[str] = ..., energisedEndOpenCircuitTestsMRID: _Optional[str] = ...) -> None: ...

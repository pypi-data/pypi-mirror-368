from zepben.protobuf.cim.extensions.iec61970.base.wires import TransformerEndRatedS_pb2 as _TransformerEndRatedS_pb2
from zepben.protobuf.cim.iec61970.base.wires import TransformerEnd_pb2 as _TransformerEnd_pb2
from zepben.protobuf.cim.iec61970.base.wires import WindingConnection_pb2 as _WindingConnection_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PowerTransformerEnd(_message.Message):
    __slots__ = ("te", "powerTransformerMRID", "ratedS", "ratedU", "r", "x", "r0", "x0", "connectionKind", "b", "b0", "g", "g0", "phaseAngleClock", "ratings")
    TE_FIELD_NUMBER: _ClassVar[int]
    POWERTRANSFORMERMRID_FIELD_NUMBER: _ClassVar[int]
    RATEDS_FIELD_NUMBER: _ClassVar[int]
    RATEDU_FIELD_NUMBER: _ClassVar[int]
    R_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    R0_FIELD_NUMBER: _ClassVar[int]
    X0_FIELD_NUMBER: _ClassVar[int]
    CONNECTIONKIND_FIELD_NUMBER: _ClassVar[int]
    B_FIELD_NUMBER: _ClassVar[int]
    B0_FIELD_NUMBER: _ClassVar[int]
    G_FIELD_NUMBER: _ClassVar[int]
    G0_FIELD_NUMBER: _ClassVar[int]
    PHASEANGLECLOCK_FIELD_NUMBER: _ClassVar[int]
    RATINGS_FIELD_NUMBER: _ClassVar[int]
    te: _TransformerEnd_pb2.TransformerEnd
    powerTransformerMRID: str
    ratedS: int
    ratedU: int
    r: float
    x: float
    r0: float
    x0: float
    connectionKind: _WindingConnection_pb2.WindingConnection
    b: float
    b0: float
    g: float
    g0: float
    phaseAngleClock: int
    ratings: _containers.RepeatedCompositeFieldContainer[_TransformerEndRatedS_pb2.TransformerEndRatedS]
    def __init__(self, te: _Optional[_Union[_TransformerEnd_pb2.TransformerEnd, _Mapping]] = ..., powerTransformerMRID: _Optional[str] = ..., ratedS: _Optional[int] = ..., ratedU: _Optional[int] = ..., r: _Optional[float] = ..., x: _Optional[float] = ..., r0: _Optional[float] = ..., x0: _Optional[float] = ..., connectionKind: _Optional[_Union[_WindingConnection_pb2.WindingConnection, str]] = ..., b: _Optional[float] = ..., b0: _Optional[float] = ..., g: _Optional[float] = ..., g0: _Optional[float] = ..., phaseAngleClock: _Optional[int] = ..., ratings: _Optional[_Iterable[_Union[_TransformerEndRatedS_pb2.TransformerEndRatedS, _Mapping]]] = ...) -> None: ...

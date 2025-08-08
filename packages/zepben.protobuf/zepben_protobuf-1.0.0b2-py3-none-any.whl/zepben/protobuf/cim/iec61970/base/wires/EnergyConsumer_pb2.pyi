from zepben.protobuf.cim.iec61970.base.wires import EnergyConnection_pb2 as _EnergyConnection_pb2
from zepben.protobuf.cim.iec61970.base.wires import PhaseShuntConnectionKind_pb2 as _PhaseShuntConnectionKind_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EnergyConsumer(_message.Message):
    __slots__ = ("ec", "energyConsumerPhasesMRIDs", "customerCount", "grounded", "p", "pFixed", "phaseConnection", "q", "qFixed")
    EC_FIELD_NUMBER: _ClassVar[int]
    ENERGYCONSUMERPHASESMRIDS_FIELD_NUMBER: _ClassVar[int]
    CUSTOMERCOUNT_FIELD_NUMBER: _ClassVar[int]
    GROUNDED_FIELD_NUMBER: _ClassVar[int]
    P_FIELD_NUMBER: _ClassVar[int]
    PFIXED_FIELD_NUMBER: _ClassVar[int]
    PHASECONNECTION_FIELD_NUMBER: _ClassVar[int]
    Q_FIELD_NUMBER: _ClassVar[int]
    QFIXED_FIELD_NUMBER: _ClassVar[int]
    ec: _EnergyConnection_pb2.EnergyConnection
    energyConsumerPhasesMRIDs: _containers.RepeatedScalarFieldContainer[str]
    customerCount: int
    grounded: bool
    p: float
    pFixed: float
    phaseConnection: _PhaseShuntConnectionKind_pb2.PhaseShuntConnectionKind
    q: float
    qFixed: float
    def __init__(self, ec: _Optional[_Union[_EnergyConnection_pb2.EnergyConnection, _Mapping]] = ..., energyConsumerPhasesMRIDs: _Optional[_Iterable[str]] = ..., customerCount: _Optional[int] = ..., grounded: bool = ..., p: _Optional[float] = ..., pFixed: _Optional[float] = ..., phaseConnection: _Optional[_Union[_PhaseShuntConnectionKind_pb2.PhaseShuntConnectionKind, str]] = ..., q: _Optional[float] = ..., qFixed: _Optional[float] = ...) -> None: ...

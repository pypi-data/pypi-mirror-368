from zepben.protobuf.cim.iec61970.base.wires import EnergyConnection_pb2 as _EnergyConnection_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EnergySource(_message.Message):
    __slots__ = ("ec", "energySourcePhasesMRIDs", "activePower", "reactivePower", "voltageAngle", "voltageMagnitude", "r", "x", "pMax", "pMin", "r0", "rn", "x0", "xn", "isExternalGrid", "rMin", "rnMin", "r0Min", "xMin", "xnMin", "x0Min", "rMax", "rnMax", "r0Max", "xMax", "xnMax", "x0Max")
    EC_FIELD_NUMBER: _ClassVar[int]
    ENERGYSOURCEPHASESMRIDS_FIELD_NUMBER: _ClassVar[int]
    ACTIVEPOWER_FIELD_NUMBER: _ClassVar[int]
    REACTIVEPOWER_FIELD_NUMBER: _ClassVar[int]
    VOLTAGEANGLE_FIELD_NUMBER: _ClassVar[int]
    VOLTAGEMAGNITUDE_FIELD_NUMBER: _ClassVar[int]
    R_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    PMAX_FIELD_NUMBER: _ClassVar[int]
    PMIN_FIELD_NUMBER: _ClassVar[int]
    R0_FIELD_NUMBER: _ClassVar[int]
    RN_FIELD_NUMBER: _ClassVar[int]
    X0_FIELD_NUMBER: _ClassVar[int]
    XN_FIELD_NUMBER: _ClassVar[int]
    ISEXTERNALGRID_FIELD_NUMBER: _ClassVar[int]
    RMIN_FIELD_NUMBER: _ClassVar[int]
    RNMIN_FIELD_NUMBER: _ClassVar[int]
    R0MIN_FIELD_NUMBER: _ClassVar[int]
    XMIN_FIELD_NUMBER: _ClassVar[int]
    XNMIN_FIELD_NUMBER: _ClassVar[int]
    X0MIN_FIELD_NUMBER: _ClassVar[int]
    RMAX_FIELD_NUMBER: _ClassVar[int]
    RNMAX_FIELD_NUMBER: _ClassVar[int]
    R0MAX_FIELD_NUMBER: _ClassVar[int]
    XMAX_FIELD_NUMBER: _ClassVar[int]
    XNMAX_FIELD_NUMBER: _ClassVar[int]
    X0MAX_FIELD_NUMBER: _ClassVar[int]
    ec: _EnergyConnection_pb2.EnergyConnection
    energySourcePhasesMRIDs: _containers.RepeatedScalarFieldContainer[str]
    activePower: float
    reactivePower: float
    voltageAngle: float
    voltageMagnitude: float
    r: float
    x: float
    pMax: float
    pMin: float
    r0: float
    rn: float
    x0: float
    xn: float
    isExternalGrid: bool
    rMin: float
    rnMin: float
    r0Min: float
    xMin: float
    xnMin: float
    x0Min: float
    rMax: float
    rnMax: float
    r0Max: float
    xMax: float
    xnMax: float
    x0Max: float
    def __init__(self, ec: _Optional[_Union[_EnergyConnection_pb2.EnergyConnection, _Mapping]] = ..., energySourcePhasesMRIDs: _Optional[_Iterable[str]] = ..., activePower: _Optional[float] = ..., reactivePower: _Optional[float] = ..., voltageAngle: _Optional[float] = ..., voltageMagnitude: _Optional[float] = ..., r: _Optional[float] = ..., x: _Optional[float] = ..., pMax: _Optional[float] = ..., pMin: _Optional[float] = ..., r0: _Optional[float] = ..., rn: _Optional[float] = ..., x0: _Optional[float] = ..., xn: _Optional[float] = ..., isExternalGrid: bool = ..., rMin: _Optional[float] = ..., rnMin: _Optional[float] = ..., r0Min: _Optional[float] = ..., xMin: _Optional[float] = ..., xnMin: _Optional[float] = ..., x0Min: _Optional[float] = ..., rMax: _Optional[float] = ..., rnMax: _Optional[float] = ..., r0Max: _Optional[float] = ..., xMax: _Optional[float] = ..., xnMax: _Optional[float] = ..., x0Max: _Optional[float] = ...) -> None: ...

from google.protobuf import struct_pb2 as _struct_pb2
from zepben.protobuf.cim.iec61970.base.wires import RegulatingCondEq_pb2 as _RegulatingCondEq_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PowerElectronicsConnection(_message.Message):
    __slots__ = ("rce", "maxIFault", "maxQ", "minQ", "p", "q", "ratedS", "ratedU", "powerElectronicsUnitMRIDs", "powerElectronicsConnectionPhaseMRIDs", "inverterStandard", "sustainOpOvervoltLimit", "stopAtOverFreq", "stopAtUnderFreq", "invVoltWattRespModeNull", "invVoltWattRespModeSet", "invWattRespV1", "invWattRespV2", "invWattRespV3", "invWattRespV4", "invWattRespPAtV1", "invWattRespPAtV2", "invWattRespPAtV3", "invWattRespPAtV4", "invVoltVarRespModeNull", "invVoltVarRespModeSet", "invVarRespV1", "invVarRespV2", "invVarRespV3", "invVarRespV4", "invVarRespQAtV1", "invVarRespQAtV2", "invVarRespQAtV3", "invVarRespQAtV4", "invReactivePowerModeNull", "invReactivePowerModeSet", "invFixReactivePower")
    RCE_FIELD_NUMBER: _ClassVar[int]
    MAXIFAULT_FIELD_NUMBER: _ClassVar[int]
    MAXQ_FIELD_NUMBER: _ClassVar[int]
    MINQ_FIELD_NUMBER: _ClassVar[int]
    P_FIELD_NUMBER: _ClassVar[int]
    Q_FIELD_NUMBER: _ClassVar[int]
    RATEDS_FIELD_NUMBER: _ClassVar[int]
    RATEDU_FIELD_NUMBER: _ClassVar[int]
    POWERELECTRONICSUNITMRIDS_FIELD_NUMBER: _ClassVar[int]
    POWERELECTRONICSCONNECTIONPHASEMRIDS_FIELD_NUMBER: _ClassVar[int]
    INVERTERSTANDARD_FIELD_NUMBER: _ClassVar[int]
    SUSTAINOPOVERVOLTLIMIT_FIELD_NUMBER: _ClassVar[int]
    STOPATOVERFREQ_FIELD_NUMBER: _ClassVar[int]
    STOPATUNDERFREQ_FIELD_NUMBER: _ClassVar[int]
    INVVOLTWATTRESPMODENULL_FIELD_NUMBER: _ClassVar[int]
    INVVOLTWATTRESPMODESET_FIELD_NUMBER: _ClassVar[int]
    INVWATTRESPV1_FIELD_NUMBER: _ClassVar[int]
    INVWATTRESPV2_FIELD_NUMBER: _ClassVar[int]
    INVWATTRESPV3_FIELD_NUMBER: _ClassVar[int]
    INVWATTRESPV4_FIELD_NUMBER: _ClassVar[int]
    INVWATTRESPPATV1_FIELD_NUMBER: _ClassVar[int]
    INVWATTRESPPATV2_FIELD_NUMBER: _ClassVar[int]
    INVWATTRESPPATV3_FIELD_NUMBER: _ClassVar[int]
    INVWATTRESPPATV4_FIELD_NUMBER: _ClassVar[int]
    INVVOLTVARRESPMODENULL_FIELD_NUMBER: _ClassVar[int]
    INVVOLTVARRESPMODESET_FIELD_NUMBER: _ClassVar[int]
    INVVARRESPV1_FIELD_NUMBER: _ClassVar[int]
    INVVARRESPV2_FIELD_NUMBER: _ClassVar[int]
    INVVARRESPV3_FIELD_NUMBER: _ClassVar[int]
    INVVARRESPV4_FIELD_NUMBER: _ClassVar[int]
    INVVARRESPQATV1_FIELD_NUMBER: _ClassVar[int]
    INVVARRESPQATV2_FIELD_NUMBER: _ClassVar[int]
    INVVARRESPQATV3_FIELD_NUMBER: _ClassVar[int]
    INVVARRESPQATV4_FIELD_NUMBER: _ClassVar[int]
    INVREACTIVEPOWERMODENULL_FIELD_NUMBER: _ClassVar[int]
    INVREACTIVEPOWERMODESET_FIELD_NUMBER: _ClassVar[int]
    INVFIXREACTIVEPOWER_FIELD_NUMBER: _ClassVar[int]
    rce: _RegulatingCondEq_pb2.RegulatingCondEq
    maxIFault: int
    maxQ: float
    minQ: float
    p: float
    q: float
    ratedS: int
    ratedU: int
    powerElectronicsUnitMRIDs: _containers.RepeatedScalarFieldContainer[str]
    powerElectronicsConnectionPhaseMRIDs: _containers.RepeatedScalarFieldContainer[str]
    inverterStandard: str
    sustainOpOvervoltLimit: int
    stopAtOverFreq: float
    stopAtUnderFreq: float
    invVoltWattRespModeNull: _struct_pb2.NullValue
    invVoltWattRespModeSet: bool
    invWattRespV1: int
    invWattRespV2: int
    invWattRespV3: int
    invWattRespV4: int
    invWattRespPAtV1: float
    invWattRespPAtV2: float
    invWattRespPAtV3: float
    invWattRespPAtV4: float
    invVoltVarRespModeNull: _struct_pb2.NullValue
    invVoltVarRespModeSet: bool
    invVarRespV1: int
    invVarRespV2: int
    invVarRespV3: int
    invVarRespV4: int
    invVarRespQAtV1: float
    invVarRespQAtV2: float
    invVarRespQAtV3: float
    invVarRespQAtV4: float
    invReactivePowerModeNull: _struct_pb2.NullValue
    invReactivePowerModeSet: bool
    invFixReactivePower: float
    def __init__(self, rce: _Optional[_Union[_RegulatingCondEq_pb2.RegulatingCondEq, _Mapping]] = ..., maxIFault: _Optional[int] = ..., maxQ: _Optional[float] = ..., minQ: _Optional[float] = ..., p: _Optional[float] = ..., q: _Optional[float] = ..., ratedS: _Optional[int] = ..., ratedU: _Optional[int] = ..., powerElectronicsUnitMRIDs: _Optional[_Iterable[str]] = ..., powerElectronicsConnectionPhaseMRIDs: _Optional[_Iterable[str]] = ..., inverterStandard: _Optional[str] = ..., sustainOpOvervoltLimit: _Optional[int] = ..., stopAtOverFreq: _Optional[float] = ..., stopAtUnderFreq: _Optional[float] = ..., invVoltWattRespModeNull: _Optional[_Union[_struct_pb2.NullValue, str]] = ..., invVoltWattRespModeSet: bool = ..., invWattRespV1: _Optional[int] = ..., invWattRespV2: _Optional[int] = ..., invWattRespV3: _Optional[int] = ..., invWattRespV4: _Optional[int] = ..., invWattRespPAtV1: _Optional[float] = ..., invWattRespPAtV2: _Optional[float] = ..., invWattRespPAtV3: _Optional[float] = ..., invWattRespPAtV4: _Optional[float] = ..., invVoltVarRespModeNull: _Optional[_Union[_struct_pb2.NullValue, str]] = ..., invVoltVarRespModeSet: bool = ..., invVarRespV1: _Optional[int] = ..., invVarRespV2: _Optional[int] = ..., invVarRespV3: _Optional[int] = ..., invVarRespV4: _Optional[int] = ..., invVarRespQAtV1: _Optional[float] = ..., invVarRespQAtV2: _Optional[float] = ..., invVarRespQAtV3: _Optional[float] = ..., invVarRespQAtV4: _Optional[float] = ..., invReactivePowerModeNull: _Optional[_Union[_struct_pb2.NullValue, str]] = ..., invReactivePowerModeSet: bool = ..., invFixReactivePower: _Optional[float] = ...) -> None: ...

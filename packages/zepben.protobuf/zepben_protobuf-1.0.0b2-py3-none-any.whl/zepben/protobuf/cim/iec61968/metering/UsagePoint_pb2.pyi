from zepben.protobuf.cim.iec61970.base.core import IdentifiedObject_pb2 as _IdentifiedObject_pb2
from zepben.protobuf.cim.iec61970.base.core import PhaseCode_pb2 as _PhaseCode_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UsagePoint(_message.Message):
    __slots__ = ("io", "usagePointLocationMRID", "equipmentMRIDs", "endDeviceMRIDs", "isVirtual", "connectionCategory", "ratedPower", "approvedInverterCapacity", "phaseCode")
    IO_FIELD_NUMBER: _ClassVar[int]
    USAGEPOINTLOCATIONMRID_FIELD_NUMBER: _ClassVar[int]
    EQUIPMENTMRIDS_FIELD_NUMBER: _ClassVar[int]
    ENDDEVICEMRIDS_FIELD_NUMBER: _ClassVar[int]
    ISVIRTUAL_FIELD_NUMBER: _ClassVar[int]
    CONNECTIONCATEGORY_FIELD_NUMBER: _ClassVar[int]
    RATEDPOWER_FIELD_NUMBER: _ClassVar[int]
    APPROVEDINVERTERCAPACITY_FIELD_NUMBER: _ClassVar[int]
    PHASECODE_FIELD_NUMBER: _ClassVar[int]
    io: _IdentifiedObject_pb2.IdentifiedObject
    usagePointLocationMRID: str
    equipmentMRIDs: _containers.RepeatedScalarFieldContainer[str]
    endDeviceMRIDs: _containers.RepeatedScalarFieldContainer[str]
    isVirtual: bool
    connectionCategory: str
    ratedPower: int
    approvedInverterCapacity: int
    phaseCode: _PhaseCode_pb2.PhaseCode
    def __init__(self, io: _Optional[_Union[_IdentifiedObject_pb2.IdentifiedObject, _Mapping]] = ..., usagePointLocationMRID: _Optional[str] = ..., equipmentMRIDs: _Optional[_Iterable[str]] = ..., endDeviceMRIDs: _Optional[_Iterable[str]] = ..., isVirtual: bool = ..., connectionCategory: _Optional[str] = ..., ratedPower: _Optional[int] = ..., approvedInverterCapacity: _Optional[int] = ..., phaseCode: _Optional[_Union[_PhaseCode_pb2.PhaseCode, str]] = ...) -> None: ...

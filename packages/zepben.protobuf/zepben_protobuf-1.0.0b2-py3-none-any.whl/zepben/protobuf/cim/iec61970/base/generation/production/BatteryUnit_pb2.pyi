from zepben.protobuf.cim.iec61970.base.generation.production import PowerElectronicsUnit_pb2 as _PowerElectronicsUnit_pb2
from zepben.protobuf.cim.iec61970.base.generation.production import BatteryStateKind_pb2 as _BatteryStateKind_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BatteryUnit(_message.Message):
    __slots__ = ("peu", "batteryState", "ratedE", "storedE", "batteryControlMRIDs")
    PEU_FIELD_NUMBER: _ClassVar[int]
    BATTERYSTATE_FIELD_NUMBER: _ClassVar[int]
    RATEDE_FIELD_NUMBER: _ClassVar[int]
    STOREDE_FIELD_NUMBER: _ClassVar[int]
    BATTERYCONTROLMRIDS_FIELD_NUMBER: _ClassVar[int]
    peu: _PowerElectronicsUnit_pb2.PowerElectronicsUnit
    batteryState: _BatteryStateKind_pb2.BatteryStateKind
    ratedE: int
    storedE: int
    batteryControlMRIDs: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, peu: _Optional[_Union[_PowerElectronicsUnit_pb2.PowerElectronicsUnit, _Mapping]] = ..., batteryState: _Optional[_Union[_BatteryStateKind_pb2.BatteryStateKind, str]] = ..., ratedE: _Optional[int] = ..., storedE: _Optional[int] = ..., batteryControlMRIDs: _Optional[_Iterable[str]] = ...) -> None: ...

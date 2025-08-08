from zepben.protobuf.cim.iec61970.base.wires import RegulatingControl_pb2 as _RegulatingControl_pb2
from zepben.protobuf.cim.extensions.iec61970.base.wires import BatteryControlMode_pb2 as _BatteryControlMode_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BatteryControl(_message.Message):
    __slots__ = ("rc", "chargingRate", "dischargingRate", "reservePercent", "controlMode")
    RC_FIELD_NUMBER: _ClassVar[int]
    CHARGINGRATE_FIELD_NUMBER: _ClassVar[int]
    DISCHARGINGRATE_FIELD_NUMBER: _ClassVar[int]
    RESERVEPERCENT_FIELD_NUMBER: _ClassVar[int]
    CONTROLMODE_FIELD_NUMBER: _ClassVar[int]
    rc: _RegulatingControl_pb2.RegulatingControl
    chargingRate: float
    dischargingRate: float
    reservePercent: float
    controlMode: _BatteryControlMode_pb2.BatteryControlMode
    def __init__(self, rc: _Optional[_Union[_RegulatingControl_pb2.RegulatingControl, _Mapping]] = ..., chargingRate: _Optional[float] = ..., dischargingRate: _Optional[float] = ..., reservePercent: _Optional[float] = ..., controlMode: _Optional[_Union[_BatteryControlMode_pb2.BatteryControlMode, str]] = ...) -> None: ...

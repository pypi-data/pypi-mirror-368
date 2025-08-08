from zepben.protobuf.cim.iec61968.assets import AssetInfo_pb2 as _AssetInfo_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ShuntCompensatorInfo(_message.Message):
    __slots__ = ("ai", "maxPowerLoss", "ratedCurrent", "ratedReactivePower", "ratedVoltage")
    AI_FIELD_NUMBER: _ClassVar[int]
    MAXPOWERLOSS_FIELD_NUMBER: _ClassVar[int]
    RATEDCURRENT_FIELD_NUMBER: _ClassVar[int]
    RATEDREACTIVEPOWER_FIELD_NUMBER: _ClassVar[int]
    RATEDVOLTAGE_FIELD_NUMBER: _ClassVar[int]
    ai: _AssetInfo_pb2.AssetInfo
    maxPowerLoss: int
    ratedCurrent: int
    ratedReactivePower: int
    ratedVoltage: int
    def __init__(self, ai: _Optional[_Union[_AssetInfo_pb2.AssetInfo, _Mapping]] = ..., maxPowerLoss: _Optional[int] = ..., ratedCurrent: _Optional[int] = ..., ratedReactivePower: _Optional[int] = ..., ratedVoltage: _Optional[int] = ...) -> None: ...

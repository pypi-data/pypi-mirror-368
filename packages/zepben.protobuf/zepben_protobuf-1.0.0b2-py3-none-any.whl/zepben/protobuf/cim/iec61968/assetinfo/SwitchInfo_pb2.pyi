from zepben.protobuf.cim.iec61968.assets import AssetInfo_pb2 as _AssetInfo_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SwitchInfo(_message.Message):
    __slots__ = ("ai", "ratedInterruptingTime")
    AI_FIELD_NUMBER: _ClassVar[int]
    RATEDINTERRUPTINGTIME_FIELD_NUMBER: _ClassVar[int]
    ai: _AssetInfo_pb2.AssetInfo
    ratedInterruptingTime: float
    def __init__(self, ai: _Optional[_Union[_AssetInfo_pb2.AssetInfo, _Mapping]] = ..., ratedInterruptingTime: _Optional[float] = ...) -> None: ...

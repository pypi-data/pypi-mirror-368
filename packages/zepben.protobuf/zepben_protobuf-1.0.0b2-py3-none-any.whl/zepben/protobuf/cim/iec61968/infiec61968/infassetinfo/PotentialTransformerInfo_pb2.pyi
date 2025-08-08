from zepben.protobuf.cim.iec61968.assets import AssetInfo_pb2 as _AssetInfo_pb2
from zepben.protobuf.cim.iec61968.infiec61968.infcommon import Ratio_pb2 as _Ratio_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PotentialTransformerInfo(_message.Message):
    __slots__ = ("ai", "accuracyClass", "nominalRatio", "primaryRatio", "ptClass", "ratedVoltage", "secondaryRatio")
    AI_FIELD_NUMBER: _ClassVar[int]
    ACCURACYCLASS_FIELD_NUMBER: _ClassVar[int]
    NOMINALRATIO_FIELD_NUMBER: _ClassVar[int]
    PRIMARYRATIO_FIELD_NUMBER: _ClassVar[int]
    PTCLASS_FIELD_NUMBER: _ClassVar[int]
    RATEDVOLTAGE_FIELD_NUMBER: _ClassVar[int]
    SECONDARYRATIO_FIELD_NUMBER: _ClassVar[int]
    ai: _AssetInfo_pb2.AssetInfo
    accuracyClass: str
    nominalRatio: _Ratio_pb2.Ratio
    primaryRatio: float
    ptClass: str
    ratedVoltage: int
    secondaryRatio: float
    def __init__(self, ai: _Optional[_Union[_AssetInfo_pb2.AssetInfo, _Mapping]] = ..., accuracyClass: _Optional[str] = ..., nominalRatio: _Optional[_Union[_Ratio_pb2.Ratio, _Mapping]] = ..., primaryRatio: _Optional[float] = ..., ptClass: _Optional[str] = ..., ratedVoltage: _Optional[int] = ..., secondaryRatio: _Optional[float] = ...) -> None: ...

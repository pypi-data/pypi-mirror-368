from zepben.protobuf.cim.iec61968.assets import AssetInfo_pb2 as _AssetInfo_pb2
from zepben.protobuf.cim.iec61968.infiec61968.infcommon import Ratio_pb2 as _Ratio_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CurrentTransformerInfo(_message.Message):
    __slots__ = ("ai", "accuracyClass", "accuracyLimit", "coreCount", "ctClass", "kneePointVoltage", "maxRatio", "nominalRatio", "primaryRatio", "ratedCurrent", "secondaryFlsRating", "secondaryRatio", "usage")
    AI_FIELD_NUMBER: _ClassVar[int]
    ACCURACYCLASS_FIELD_NUMBER: _ClassVar[int]
    ACCURACYLIMIT_FIELD_NUMBER: _ClassVar[int]
    CORECOUNT_FIELD_NUMBER: _ClassVar[int]
    CTCLASS_FIELD_NUMBER: _ClassVar[int]
    KNEEPOINTVOLTAGE_FIELD_NUMBER: _ClassVar[int]
    MAXRATIO_FIELD_NUMBER: _ClassVar[int]
    NOMINALRATIO_FIELD_NUMBER: _ClassVar[int]
    PRIMARYRATIO_FIELD_NUMBER: _ClassVar[int]
    RATEDCURRENT_FIELD_NUMBER: _ClassVar[int]
    SECONDARYFLSRATING_FIELD_NUMBER: _ClassVar[int]
    SECONDARYRATIO_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    ai: _AssetInfo_pb2.AssetInfo
    accuracyClass: str
    accuracyLimit: float
    coreCount: int
    ctClass: str
    kneePointVoltage: int
    maxRatio: _Ratio_pb2.Ratio
    nominalRatio: _Ratio_pb2.Ratio
    primaryRatio: float
    ratedCurrent: int
    secondaryFlsRating: int
    secondaryRatio: float
    usage: str
    def __init__(self, ai: _Optional[_Union[_AssetInfo_pb2.AssetInfo, _Mapping]] = ..., accuracyClass: _Optional[str] = ..., accuracyLimit: _Optional[float] = ..., coreCount: _Optional[int] = ..., ctClass: _Optional[str] = ..., kneePointVoltage: _Optional[int] = ..., maxRatio: _Optional[_Union[_Ratio_pb2.Ratio, _Mapping]] = ..., nominalRatio: _Optional[_Union[_Ratio_pb2.Ratio, _Mapping]] = ..., primaryRatio: _Optional[float] = ..., ratedCurrent: _Optional[int] = ..., secondaryFlsRating: _Optional[int] = ..., secondaryRatio: _Optional[float] = ..., usage: _Optional[str] = ...) -> None: ...

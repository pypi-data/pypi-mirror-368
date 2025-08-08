from zepben.protobuf.cim.iec61968.assetinfo import WireMaterialKind_pb2 as _WireMaterialKind_pb2
from zepben.protobuf.cim.iec61968.assets import AssetInfo_pb2 as _AssetInfo_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class WireInfo(_message.Message):
    __slots__ = ("ai", "ratedCurrent", "material")
    AI_FIELD_NUMBER: _ClassVar[int]
    RATEDCURRENT_FIELD_NUMBER: _ClassVar[int]
    MATERIAL_FIELD_NUMBER: _ClassVar[int]
    ai: _AssetInfo_pb2.AssetInfo
    ratedCurrent: int
    material: _WireMaterialKind_pb2.WireMaterialKind
    def __init__(self, ai: _Optional[_Union[_AssetInfo_pb2.AssetInfo, _Mapping]] = ..., ratedCurrent: _Optional[int] = ..., material: _Optional[_Union[_WireMaterialKind_pb2.WireMaterialKind, str]] = ...) -> None: ...

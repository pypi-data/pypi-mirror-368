from zepben.protobuf.cim.iec61968.common import StreetDetail_pb2 as _StreetDetail_pb2
from zepben.protobuf.cim.iec61968.common import TownDetail_pb2 as _TownDetail_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StreetAddress(_message.Message):
    __slots__ = ("postalCode", "townDetail", "poBox", "streetDetail")
    POSTALCODE_FIELD_NUMBER: _ClassVar[int]
    TOWNDETAIL_FIELD_NUMBER: _ClassVar[int]
    POBOX_FIELD_NUMBER: _ClassVar[int]
    STREETDETAIL_FIELD_NUMBER: _ClassVar[int]
    postalCode: str
    townDetail: _TownDetail_pb2.TownDetail
    poBox: str
    streetDetail: _StreetDetail_pb2.StreetDetail
    def __init__(self, postalCode: _Optional[str] = ..., townDetail: _Optional[_Union[_TownDetail_pb2.TownDetail, _Mapping]] = ..., poBox: _Optional[str] = ..., streetDetail: _Optional[_Union[_StreetDetail_pb2.StreetDetail, _Mapping]] = ...) -> None: ...

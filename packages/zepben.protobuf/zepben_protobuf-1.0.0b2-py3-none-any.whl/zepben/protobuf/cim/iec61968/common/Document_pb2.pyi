from google.protobuf import timestamp_pb2 as _timestamp_pb2
from zepben.protobuf.cim.iec61970.base.core import IdentifiedObject_pb2 as _IdentifiedObject_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Document(_message.Message):
    __slots__ = ("io", "title", "createdDateTime", "authorName", "type", "status", "comment")
    IO_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    CREATEDDATETIME_FIELD_NUMBER: _ClassVar[int]
    AUTHORNAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    io: _IdentifiedObject_pb2.IdentifiedObject
    title: str
    createdDateTime: _timestamp_pb2.Timestamp
    authorName: str
    type: str
    status: str
    comment: str
    def __init__(self, io: _Optional[_Union[_IdentifiedObject_pb2.IdentifiedObject, _Mapping]] = ..., title: _Optional[str] = ..., createdDateTime: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., authorName: _Optional[str] = ..., type: _Optional[str] = ..., status: _Optional[str] = ..., comment: _Optional[str] = ...) -> None: ...

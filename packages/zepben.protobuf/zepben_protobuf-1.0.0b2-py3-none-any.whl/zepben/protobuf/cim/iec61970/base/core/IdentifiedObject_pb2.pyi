from zepben.protobuf.cim.iec61970.base.core import Name_pb2 as _Name_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class IdentifiedObject(_message.Message):
    __slots__ = ("mRID", "name", "numDiagramObjects", "description", "names")
    MRID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NUMDIAGRAMOBJECTS_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    NAMES_FIELD_NUMBER: _ClassVar[int]
    mRID: str
    name: str
    numDiagramObjects: int
    description: str
    names: _containers.RepeatedCompositeFieldContainer[_Name_pb2.Name]
    def __init__(self, mRID: _Optional[str] = ..., name: _Optional[str] = ..., numDiagramObjects: _Optional[int] = ..., description: _Optional[str] = ..., names: _Optional[_Iterable[_Union[_Name_pb2.Name, _Mapping]]] = ...) -> None: ...

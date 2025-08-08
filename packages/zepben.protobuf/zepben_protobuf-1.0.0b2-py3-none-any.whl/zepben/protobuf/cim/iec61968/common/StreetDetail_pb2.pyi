from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class StreetDetail(_message.Message):
    __slots__ = ("buildingName", "floorIdentification", "name", "number", "suiteNumber", "type", "displayAddress")
    BUILDINGNAME_FIELD_NUMBER: _ClassVar[int]
    FLOORIDENTIFICATION_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    SUITENUMBER_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DISPLAYADDRESS_FIELD_NUMBER: _ClassVar[int]
    buildingName: str
    floorIdentification: str
    name: str
    number: str
    suiteNumber: str
    type: str
    displayAddress: str
    def __init__(self, buildingName: _Optional[str] = ..., floorIdentification: _Optional[str] = ..., name: _Optional[str] = ..., number: _Optional[str] = ..., suiteNumber: _Optional[str] = ..., type: _Optional[str] = ..., displayAddress: _Optional[str] = ...) -> None: ...

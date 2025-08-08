from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class TownDetail(_message.Message):
    __slots__ = ("name", "stateOrProvince")
    NAME_FIELD_NUMBER: _ClassVar[int]
    STATEORPROVINCE_FIELD_NUMBER: _ClassVar[int]
    name: str
    stateOrProvince: str
    def __init__(self, name: _Optional[str] = ..., stateOrProvince: _Optional[str] = ...) -> None: ...

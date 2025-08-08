from zepben.protobuf.cim.iec61970.base.core import Equipment_pb2 as _Equipment_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PowerElectronicsUnit(_message.Message):
    __slots__ = ("eq", "maxP", "minP", "powerElectronicsConnectionMRID")
    EQ_FIELD_NUMBER: _ClassVar[int]
    MAXP_FIELD_NUMBER: _ClassVar[int]
    MINP_FIELD_NUMBER: _ClassVar[int]
    POWERELECTRONICSCONNECTIONMRID_FIELD_NUMBER: _ClassVar[int]
    eq: _Equipment_pb2.Equipment
    maxP: int
    minP: int
    powerElectronicsConnectionMRID: str
    def __init__(self, eq: _Optional[_Union[_Equipment_pb2.Equipment, _Mapping]] = ..., maxP: _Optional[int] = ..., minP: _Optional[int] = ..., powerElectronicsConnectionMRID: _Optional[str] = ...) -> None: ...

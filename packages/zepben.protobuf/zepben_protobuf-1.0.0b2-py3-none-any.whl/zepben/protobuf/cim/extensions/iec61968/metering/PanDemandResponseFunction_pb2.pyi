from zepben.protobuf.cim.iec61968.metering import EndDeviceFunction_pb2 as _EndDeviceFunction_pb2
from zepben.protobuf.cim.iec61968.metering import EndDeviceFunctionKind_pb2 as _EndDeviceFunctionKind_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PanDemandResponseFunction(_message.Message):
    __slots__ = ("edf", "kind", "appliance")
    EDF_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    APPLIANCE_FIELD_NUMBER: _ClassVar[int]
    edf: _EndDeviceFunction_pb2.EndDeviceFunction
    kind: _EndDeviceFunctionKind_pb2.EndDeviceFunctionKind
    appliance: int
    def __init__(self, edf: _Optional[_Union[_EndDeviceFunction_pb2.EndDeviceFunction, _Mapping]] = ..., kind: _Optional[_Union[_EndDeviceFunctionKind_pb2.EndDeviceFunctionKind, str]] = ..., appliance: _Optional[int] = ...) -> None: ...

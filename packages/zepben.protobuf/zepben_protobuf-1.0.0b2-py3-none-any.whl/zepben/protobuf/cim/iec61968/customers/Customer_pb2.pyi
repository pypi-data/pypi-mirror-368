from zepben.protobuf.cim.iec61968.common import OrganisationRole_pb2 as _OrganisationRole_pb2
from zepben.protobuf.cim.iec61968.customers import CustomerKind_pb2 as _CustomerKind_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Customer(_message.Message):
    __slots__ = ("kind", "customerAgreementMRIDs", "numEndDevices", "specialNeed")
    OR_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    CUSTOMERAGREEMENTMRIDS_FIELD_NUMBER: _ClassVar[int]
    NUMENDDEVICES_FIELD_NUMBER: _ClassVar[int]
    SPECIALNEED_FIELD_NUMBER: _ClassVar[int]
    kind: _CustomerKind_pb2.CustomerKind
    customerAgreementMRIDs: _containers.RepeatedScalarFieldContainer[str]
    numEndDevices: int
    specialNeed: str
    def __init__(self, kind: _Optional[_Union[_CustomerKind_pb2.CustomerKind, str]] = ..., customerAgreementMRIDs: _Optional[_Iterable[str]] = ..., numEndDevices: _Optional[int] = ..., specialNeed: _Optional[str] = ..., **kwargs) -> None: ...

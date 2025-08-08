from ..constants import CLIENT_ID_ENCODING as CLIENT_ID_ENCODING, CRYPTO_BASE64_ENCODING as CRYPTO_BASE64_ENCODING, SERVICE_ID_ENCODING as SERVICE_ID_ENCODING
from .auth import ClientOTPResponse as ClientOTPResponse
from .exceptions import CertificateParsingError as CertificateParsingError
from .extensions import RADKitEndpointDescriptionExtension as RADKitEndpointDescriptionExtension, RADKitEndpointExtension as RADKitEndpointExtension, RADKitEndpointIdentityExtension as RADKitEndpointIdentityExtension, RADKitEndpointOwnerExtension as RADKitEndpointOwnerExtension, RADKitEndpointRequesterExtension as RADKitEndpointRequesterExtension, RADKitEndpointTypeExtension as RADKitEndpointTypeExtension
from _typeshed import Incomplete
from cryptography import x509
from cryptography.x509 import Certificate as Certificate
from dataclasses import dataclass
from datetime import datetime
from pydantic import AwareDatetime as AwareDatetime, BaseModel, BeforeValidator as BeforeValidator
from radkit_common.access.types import RADKIT_ENDPOINT_TYPE_ADMIN as RADKIT_ENDPOINT_TYPE_ADMIN, RADKIT_ENDPOINT_TYPE_CLIENT as RADKIT_ENDPOINT_TYPE_CLIENT, RADKIT_ENDPOINT_TYPE_SERVICE as RADKIT_ENDPOINT_TYPE_SERVICE, REVOCATION_REASONS as REVOCATION_REASONS
from radkit_common.identities import ClientID as ClientID, Email as Email, EndpointID as EndpointID, ServiceID as ServiceID, parse_endpoint_id as parse_endpoint_id
from radkit_common.utils.validators import convert_to_utc as convert_to_utc
from typing import Annotated, Literal

class ObjectIdentifier(BaseModel):
    dotted_string: str
    model_config: Incomplete
    @property
    def x509(self) -> x509.ObjectIdentifier: ...

class NameAttribute(BaseModel):
    oid: ObjectIdentifier
    value: str
    model_config: Incomplete
    @property
    def x509(self) -> x509.NameAttribute: ...

class RelativeDistinguishedName(BaseModel):
    data: list[NameAttribute]
    @property
    def oid(self) -> x509.ObjectIdentifier: ...
    @property
    def value(self) -> str: ...
    @property
    def x509(self) -> x509.NameAttribute: ...
    model_config: Incomplete

class SubjectName(BaseModel):
    rdns: list[RelativeDistinguishedName]
    model_config: Incomplete
    @property
    def attributes(self) -> list[x509.NameAttribute]: ...
    @property
    def x509(self) -> x509.Name: ...

class CertificateRequester(BaseModel):
    email: Email
    name: str | None

class CertificateOwner(BaseModel):
    email: Email
    name: str | None
    @property
    def domain(self) -> str: ...

class IssueCertificateRequest(BaseModel):
    csr: str
    requester: CertificateRequester | None
    owner: CertificateOwner | None
    admin: bool
    dry_run: bool
    description: str
    model_config: Incomplete

class ClientCertificateResponse(BaseModel):
    certificate_serial_number: str
    get_certificate_otp: ClientOTPResponse | None
    retrieve_after: int
    model_config: Incomplete

class GetCertificateResponse(BaseModel):
    certificate: str
    certificate_chain: str
    requester: CertificateRequester
    owner: CertificateOwner
    subject_name: SubjectName | None
    @property
    def certificate_serial_number(self) -> str: ...
    @property
    def x509(self) -> Certificate: ...
    @property
    def parsed(self) -> RADKitCertificate: ...
    model_config: Incomplete

class CertificateData(BaseModel):
    id: str
    backend_id: str
    domain: str
    serial_number: str
    status: Literal['requested', 'valid', 'expired', 'revoked']
    requester: CertificateRequester
    owner: CertificateOwner
    identity: str
    subject_name: SubjectName | None
    certificate: str | None
    certificate_chain: str | None
    valid_until: Annotated[AwareDatetime | None, None]

@dataclass
class ClientGetCertificateResponse:
    certificate: str
    certificate_chain: str
    def __post_init__(self) -> None: ...
    @property
    def certificate_serial_number(self) -> str: ...
    @property
    def certificate_requester(self) -> str: ...
    @property
    def endpoint_id(self) -> str: ...
    @property
    def endpoint_type(self) -> str: ...
    @property
    def endpoint_owner(self) -> str: ...

class RevokeCertificateRequest(BaseModel):
    revocation_reason: REVOCATION_REASONS

@dataclass
class RADKitCertificate:
    certificate: Certificate
    def __post_init__(self) -> None: ...
    @property
    def serial_number(self) -> str: ...
    @property
    def identity(self) -> EndpointID: ...
    @property
    def endpoint_type(self) -> str: ...
    @property
    def owner(self) -> Email: ...
    @property
    def requester(self) -> Email: ...
    @property
    def description(self) -> str: ...
    @property
    def valid_from(self) -> datetime: ...
    @property
    def valid_until(self) -> datetime: ...
    @property
    def is_admin(self) -> bool: ...
    @property
    def is_service(self) -> bool: ...
    @property
    def is_client(self) -> bool: ...
    @classmethod
    def from_x509(cls, certificate: Certificate) -> RADKitCertificate: ...
    @classmethod
    def from_pem(cls, pem: bytes) -> RADKitCertificate: ...
    @classmethod
    def from_certificate_data(cls, data: CertificateData) -> RADKitCertificate: ...

def get_endpoint_type(certificate: Certificate | bytes | str) -> str: ...
def get_endpoint_identity(certificate: Certificate | bytes | str) -> str: ...
def get_endpoint_requester_identity(certificate: Certificate | bytes | str) -> Email: ...
def get_endpoint_owner_identity(certificate: Certificate | bytes | str) -> Email: ...
def get_endpoint_description(certificate: Certificate | bytes | str) -> str: ...
def get_certificate_extension_value(extension: type[RADKitEndpointExtension], certificate: Certificate | bytes | str) -> str: ...

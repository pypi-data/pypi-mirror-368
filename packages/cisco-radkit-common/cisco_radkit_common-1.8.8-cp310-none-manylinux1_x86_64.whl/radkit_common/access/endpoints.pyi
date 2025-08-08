from ..utils.validators import convert_to_utc as convert_to_utc
from .claims import CLAIMS as CLAIMS
from .exceptions import InvalidEndpointTypeError as InvalidEndpointTypeError
from .helpers import match_domains as match_domains
from .types import RADKIT_ENDPOINT_TYPE_ADMIN as RADKIT_ENDPOINT_TYPE_ADMIN, RADKIT_ENDPOINT_TYPE_CLIENT as RADKIT_ENDPOINT_TYPE_CLIENT, RADKIT_ENDPOINT_TYPE_SERVICE as RADKIT_ENDPOINT_TYPE_SERVICE
from _typeshed import Incomplete
from pydantic import AwareDatetime as AwareDatetime, BaseModel, BeforeValidator as BeforeValidator
from radkit_common.identities import ClientID as ClientID, Email as Email, EndpointID as EndpointID, ServiceID as ServiceID
from typing import Annotated
from typing_extensions import Literal

class User(BaseModel):
    user_id: Email
    maximum_admin_level: int
    claims: list[CLAIMS]
    revoked_base_permissions: list[str]
    banned: bool
    @property
    def domain(self) -> str: ...

class UserData(BaseModel):
    id: Email
    owned_certificates: list[str]
    requested_certificates: list[str]
    owned_endpoints: list[EndpointID]
    requested_endpoints: list[EndpointID]

class EndpointOrg(BaseModel):
    id: str
    name: str
    type: str
    domain: str

class EndpointCertificateValidity(BaseModel):
    starts: Annotated[AwareDatetime, None]
    ends: Annotated[AwareDatetime, None]
    @property
    def expired(self) -> bool: ...
    @property
    def active(self) -> bool: ...

class EndpointCertificateData(BaseModel):
    serial_number: str
    validity: EndpointCertificateValidity | None
    status: Literal['requested', 'valid', 'expired', 'revoked']
    @property
    def expired(self) -> bool: ...
    @property
    def valid(self) -> bool: ...
    @property
    def revoked(self) -> bool: ...

class EndpointData(BaseModel):
    type: str
    id: str
    requesters: list[Email]
    owners: list[Email]
    model_config: Incomplete

class ServiceData(EndpointData):
    type: Literal['Service']
    id: ServiceID

class ClientData(EndpointData):
    type: Literal['Client']
    id: ClientID

class AdminClientData(EndpointData):
    type: Literal['Admin']
    id: ClientID

class RADKitEndpoint(BaseModel):
    data: ServiceData | ClientData | AdminClientData
    certificates: list[EndpointCertificateData]
    org_ids: list[str]
    created: Annotated[AwareDatetime, None]
    last_login: Annotated[AwareDatetime | None, None]
    @property
    def id(self) -> EndpointID: ...
    @property
    def certificate_serial_numbers(self) -> list[str]: ...
    @property
    def is_service(self) -> bool: ...
    @property
    def is_client(self) -> bool: ...
    @property
    def is_admin_client(self) -> bool: ...
    @property
    def active(self) -> bool: ...
    @property
    def online(self) -> bool: ...
    @property
    def client_id_domain(self) -> str | None: ...
    @property
    def endpoint_owner_domains(self) -> list[str]: ...
    @property
    def endpoint_requester_domains(self) -> list[str]: ...
    def match_domains(self, domains: list[str]) -> bool: ...

class UserRADKitEndpoints(BaseModel):
    user: Email
    endpoints: list[RADKitEndpoint]
    model_config: Incomplete
    @property
    def certificate_serial_numbers(self) -> list[str]: ...
    @property
    def owned_endpoints(self) -> list[RADKitEndpoint]: ...
    @property
    def owned_services(self) -> list[RADKitEndpoint]: ...
    @property
    def owned_clients(self) -> list[RADKitEndpoint]: ...
    @property
    def owned_admin_clients(self) -> list[RADKitEndpoint]: ...
    @property
    def owned_service_ids(self) -> list[ServiceID]: ...
    @property
    def owned_client_ids(self) -> list[ClientID]: ...
    @property
    def owned_admin_client_ids(self) -> list[ClientID]: ...
    @property
    def proxied_endpoints(self) -> list[RADKitEndpoint]: ...
    @property
    def proxied_services(self) -> list[RADKitEndpoint]: ...
    @property
    def proxied_clients(self) -> list[RADKitEndpoint]: ...
    @property
    def proxied_admin_clients(self) -> list[RADKitEndpoint]: ...
    @property
    def proxied_service_ids(self) -> list[ServiceID]: ...
    @property
    def proxied_client_ids(self) -> list[ClientID]: ...
    @property
    def proxied_admin_client_ids(self) -> list[ClientID]: ...

class EndpointDomainFilter(BaseModel):
    names: list[str]
    identity: bool
    requester: bool
    owner: bool

class EndpointUserFilter(BaseModel):
    ids: list[Email]
    requester: bool
    owner: bool

class EndpointCertificateFilter(BaseModel):
    active: bool | None
    expire_in: int | None
    serial_numbers: list[str]

class EndpointSearchFilter(BaseModel):
    type: Literal['Service', 'Client', 'Admin'] | list[Literal['Service', 'Client', 'Admin']] | None
    id: EndpointID | list[EndpointID] | None
    users: EndpointUserFilter
    domains: EndpointDomainFilter
    certificates: EndpointCertificateFilter
    @property
    def authorization_domains(self) -> list[str]: ...

class EndpointSearchResult(BaseModel):
    endpoints: list[RADKitEndpoint]

class ServiceState(BaseModel):
    service_id: ServiceID
    active: bool
    online: bool
    @classmethod
    def from_endpoint(cls, endpoint: RADKitEndpoint) -> ServiceState: ...

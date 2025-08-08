import jwt
from ..settings import get_settings as get_settings
from ..types import JTI as JTI, JWTIssuer as JWTIssuer
from ..utils.formatting import iso_format_utc as iso_format_utc
from ..utils.validators import convert_to_utc as convert_to_utc
from .claims import CLAIMS as CLAIMS, OTP_CLAIMS as OTP_CLAIMS
from .exceptions import InvalidOTPRequestError as InvalidOTPRequestError, InvalidToken as InvalidToken
from .generators import generate_otp as generate_otp
from .oauth import OIDCProvider as OIDCProvider
from .types import Days as Days, Seconds as Seconds
from _typeshed import Incomplete
from datetime import datetime
from pydantic import AwareDatetime as AwareDatetime, BaseModel, BeforeValidator as BeforeValidator, GetCoreSchemaHandler as GetCoreSchemaHandler
from pydantic_core import core_schema
from pydantic_core.core_schema import ValidationInfo as ValidationInfo
from radkit_common.identities import ClientID as ClientID, Email as Email, EndpointID as EndpointID, Identity as Identity, ServiceID as ServiceID
from typing import Annotated
from typing_extensions import Literal

class AccessToken(BaseModel):
    type: str
    access_token: str
    token_type: str
    expires_at: int
    admin_level: int
    @property
    def expired(self) -> bool: ...
    @property
    def expires_in(self) -> int: ...

class ExternalOAuthToken(AccessToken):
    type: Literal['access_token', 'Bearer']
    provider: str

class OAuthToken(AccessToken):
    type: Literal['oauth']
    provider: str
    refresh_token: str | None
    id_token: str | None

class ServiceAccessToken(AccessToken):
    type: Literal['service_access_token']
    service_id: ServiceID

class ClientAccessToken(AccessToken):
    type: Literal['client_access_token']
    client_id: ClientID

class OTP(AccessToken):
    type: Literal['OTP']
    access_token: str
    token_type: str
    expires_at: int
ACCESS_TOKEN_TYPES = ServiceAccessToken | ClientAccessToken | OTP | OAuthToken | ExternalOAuthToken

class NewAccessTokenRequest(BaseModel):
    credentials: CREDENTIALS_METADATA
    endpoint_data: dict[str, str | int]
    lifetime: Seconds

class NewServiceAccessTokenRequest(NewAccessTokenRequest):
    service_id: ServiceID

class NewClientAccessTokenRequest(NewAccessTokenRequest):
    client_id: ClientID
    admin_level: int
    api_token: bool

class OTPRequester(BaseModel):
    email: Email
    @property
    def domain(self) -> str: ...

class OTPRequestService(BaseModel):
    type: Literal['service']
    service_id: ServiceID | None
    model_config: Incomplete
    def validate_service_id(cls, value: ServiceID | str | None) -> ServiceID | None: ...

class OTPRequestClient(BaseModel):
    type: Literal['console', 'client']
    client_id: ClientID
    model_config: Incomplete
    @property
    def domain(self) -> str: ...

class OTPRequestCertificate(BaseModel):
    type: Literal['certificate']
    certificate_serial_numbers: list[str]
    model_config: Incomplete

class GenerateCertificateOTPRequest(BaseModel):
    owner: Email
    endpoint_id: EndpointID
    description: str

class OTPRequest(BaseModel):
    owner: OTPRequester
    consumer: OTPRequestService | OTPRequestClient | OTPRequestCertificate
    description: str
    model_config: Incomplete
    @property
    def domain(self) -> str: ...
    @classmethod
    def from_generate_certificate_otp_request(cls, request: GenerateCertificateOTPRequest) -> OTPRequest: ...

class OTPData(BaseModel):
    otp: OTP
    request: OTPRequest
    requester: Email
    claim: OTP_CLAIMS
    endpoint_data: dict[str, str | int]
    @property
    def owner(self) -> Email: ...
    @property
    def endpoint_id(self) -> EndpointID | None: ...

class CredentialsMetadata(BaseModel):
    type: str

class CertificateMetadata(CredentialsMetadata):
    type: Literal['certificate']
    serial_number: str
    requester: Email
    owner: Email
    description: str

class OIDCMetadata(CredentialsMetadata):
    type: Literal['oidc']
    provider: OIDCProvider

class JWTMetadata(CredentialsMetadata):
    type: Literal['jwt', 'api_token']
    jti: JTI
    issuer: JWTIssuer

class BasicCredentialsMetadata(CredentialsMetadata):
    type: Literal['basic_credentials']
    username: ClientID

class ClientCredentialsMetadata(CredentialsMetadata):
    type: Literal['client_credentials']
    client_id: Identity
CREDENTIALS_METADATA = CertificateMetadata | JWTMetadata | OIDCMetadata | BasicCredentialsMetadata | ClientCredentialsMetadata

class TokenMetadata(BaseModel):
    type: str
    requester: Email
    endpoint_id: EndpointID
    jti: JTI
    issued: datetime
    expires: datetime
    credentials: CREDENTIALS_METADATA

class AccessTokenMetadata(TokenMetadata):
    type: Literal['access_token']

class APITokenMetadata(TokenMetadata):
    type: Literal['api_token']
TOKEN_METADATA = AccessTokenMetadata | APITokenMetadata

class TokenMetadataLoader(BaseModel):
    token: TOKEN_METADATA

class APITokenRevocationRequest(BaseModel):
    tokens: list[JWT] | None
    jtis: list[JTI] | None
    issued_before: datetime | None
    def serialize_generated_at(self, v: datetime | None) -> str | None: ...

class ClientCredentialsRequest(BaseModel):
    requester: Email
    endpoint_id: EndpointID
    lifetime: Days
    description: str

class ClientCredentialsRevocationRequest(BaseModel):
    client_ids: list[Identity] | None
    issued_before: datetime | None
    def serialize_generated_at(self, v: datetime | None) -> str | None: ...

class AuthToken(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    scope: str

class ClientIDDescription(BaseModel):
    client_id: Identity
    issued: Annotated[AwareDatetime, None]
    description: str

class BaseUser(BaseModel):
    id: str
    max_admin_level: int
    claims: list[CLAIMS]

class BaseOAuthUser(BaseUser):
    id: ClientID
    max_admin_level: int
    model_config: Incomplete

class OAuthUser(BaseOAuthUser):
    type: Literal['OAuthUser']
    provider: str
    endpoint_data: dict[str, str | int]
    @property
    def credentials(self) -> OIDCMetadata: ...

class AuthenticatedRADKitEndpoint(BaseUser):
    credentials: CREDENTIALS_METADATA
    endpoint_data: dict[str, str | int]
    model_config: Incomplete

class AuthenticatedRADKitService(AuthenticatedRADKitEndpoint):
    type: Literal['AuthenticatedRADKitService']
    id: ServiceID

class AuthenticatedRADKitClient(AuthenticatedRADKitEndpoint):
    type: Literal['AuthenticatedRADKitClient']
    id: ClientID
USER_TYPES = OAuthUser | AuthenticatedRADKitClient | AuthenticatedRADKitService

class TokenData(BaseModel):
    token: ACCESS_TOKEN_TYPES
    user_info: USER_TYPES

class _UserInfo(BaseModel):
    user_info: USER_TYPES

class TokenValidationResult(BaseModel):
    active: bool
    type: str
    expires_at: int
    expires_in: int
    user_info: USER_TYPES | None
    model_config: Incomplete
    def calculate_expires_in(cls, value: int, info: ValidationInfo) -> int: ...

class JWT(str):
    token: str
    issuer: JWTIssuer
    audience: str
    issued_at: int
    expires_at: int
    valid_yet: bool
    expired: bool
    user_info: USER_TYPES | None
    id: EndpointID | None
    jti: JTI
    is_api_token: bool
    def __new__(cls, token: str) -> JWT: ...
    def __init__(self, token: str) -> None: ...
    @classmethod
    def __get_pydantic_core_schema__(cls, source: type, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema: ...

def decode_jwt(token: str) -> dict[str, str]: ...

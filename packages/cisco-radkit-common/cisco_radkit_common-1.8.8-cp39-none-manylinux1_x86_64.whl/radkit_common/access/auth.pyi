from _typeshed import Incomplete
from pydantic import AwareDatetime as AwareDatetime, BaseModel, BeforeValidator as BeforeValidator, ValidationInfo as ValidationInfo
from radkit_common.access.claims import OTP_CLAIMS as OTP_CLAIMS
from radkit_common.access.token import JWT as JWT
from radkit_common.access.types import Seconds as Seconds
from radkit_common.identities import EndpointID as EndpointID, Identity as Identity
from radkit_common.settings import get_settings as get_settings
from radkit_common.types import OAuthProvider as OAuthProvider
from radkit_common.utils.validators import convert_to_utc as convert_to_utc
from typing import Annotated

class EndpointAuthToken(BaseModel):
    access_token: str
    token_type: str
    received_expires_in: int
    expires_at: int | None
    endpoint_id: EndpointID | None
    admin_level: int
    refresh_remaining_lifetime: int | None
    def calculate_expires_at(cls, value: int | None, info: ValidationInfo) -> int: ...
    @property
    def expires_in(self) -> int | None: ...
    @property
    def expired(self) -> bool: ...
    @property
    def ready_for_refresh(self) -> bool: ...
    model_config: Incomplete

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    endpoint_id: EndpointID | None
    admin_level: int
    refresh_remaining_lifetime: Seconds
    model_config: Incomplete

class FailedAuthResponse(BaseModel):
    message: str

class ClientOTP(BaseModel):
    access_token: str
    token_type: str
    received_expires_in: int
    expires_at: int | None
    identity: EndpointID | None
    def calculate_expires_at(cls, value: int | None, info: ValidationInfo) -> int: ...
    @property
    def expires_in(self) -> int | None: ...
    @property
    def expired(self) -> bool: ...
    model_config: Incomplete

class GenerateCertificateOTPResponse(BaseModel):
    otp: str

class ClientOTPResponse(BaseModel):
    otp: ClientOTP
    claim: OTP_CLAIMS
    model_config: Incomplete

class OTP(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    identity: EndpointID | None
    model_config: Incomplete

class OTPResponse(BaseModel):
    otp: OTP
    claim: OTP_CLAIMS
    model_config: Incomplete

class DomainOAuthProviderInfo(BaseModel):
    domain: str
    provider: OAuthProvider
    @property
    def label(self) -> str: ...

class APIToken(BaseModel):
    token: JWT
    expires_at: Annotated[AwareDatetime, None]

class ClientCredentials(BaseModel):
    client_id: Identity
    client_secret: str
    expires_at: Annotated[AwareDatetime, None]

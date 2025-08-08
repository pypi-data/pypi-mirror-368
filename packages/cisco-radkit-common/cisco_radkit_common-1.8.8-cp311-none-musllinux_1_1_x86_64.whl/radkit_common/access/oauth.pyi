from enum import Enum
from pydantic import BaseModel, HttpUrl, WebsocketUrl
from radkit_common.access.exceptions import RADKitAccessError
from radkit_common.identities import Email
from radkit_common.types import OAuthProvider
from typing_extensions import TypeAlias

__all__ = ['OAuthRedirectURI', 'ClientInfo', 'OAuthSessionData', 'OAuthConnectRequest', 'OAuthConnectResponse', 'OAuthAuthorizationResponse', 'OAuthSessionConfirmationData', 'DomainOAuthProviders', 'OAuthEnabledTools', 'OIDCProvider']

OIDCProvider: TypeAlias = str

class NoOAuthProviderDefinedForDomainError(RADKitAccessError):
    message: str
    status_code: int

class OAuthRedirectURI(BaseModel):
    nonce: str
    url: HttpUrl
    state: str
    code_verifier: str | None

class ClientInfo(BaseModel):
    client_host: str
    client_port: str
    client_user_agent: str

class OAuthSessionData(BaseModel):
    name: str
    email: Email | None
    state: str
    nonce: str
    code_verifier: str | None
    redirect_uri: str
    client_info: ClientInfo
    admin_level: int
    final_redirect_url: HttpUrl | None

class OAuthConnectRequest(BaseModel):
    auth_provider: OAuthProvider
    email: Email
    websockets: bool
    admin_level: int
    final_redirect_url: HttpUrl | None

class OAuthConnectResponse(BaseModel):
    sso_url: HttpUrl
    token_url: WebsocketUrl
    max_session_ttl: int
    provider: OAuthProvider
    @property
    def ttl(self) -> float: ...

class OAuthAuthorizationResponse(BaseModel):
    message: str
    session_id: str
    status_code: int

class OAuthSessionConfirmationData(BaseModel):
    session_id: str
    state: str
    token: str
    provider: str
    redirect_url: HttpUrl | None
    user_agent: str

class OAuthEnabledTools(str, Enum):
    SWIMS = 'swims'
    CXD = 'cxd'
    BDB = 'bdb'

class DomainOAuthProviders(BaseModel):
    domain: str
    providers: list[OAuthProvider]
    tool_mappings: dict[OAuthEnabledTools | str, str]
    @property
    def default(self) -> OAuthProvider: ...

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from radkit_common.types import OAuthProvider

__all__ = ['UserAgent', 'AuthenticationResult', 'OIDCAuthenticationResult']

class AccessServiceNow(BaseModel):
    now: datetime

class UserAgent(str, Enum):
    AdminClient = 'RADKit Admin Client'
    Client = 'RADKit Client'
    Service = 'RADKit Service'
    ServiceUI = 'RADKit Service Web UI'

@dataclass
class AuthenticationResult:
    success: bool
    error_details: str = ...

@dataclass
class OIDCAuthenticationResult(AuthenticationResult):
    provider: OAuthProvider | None = ...

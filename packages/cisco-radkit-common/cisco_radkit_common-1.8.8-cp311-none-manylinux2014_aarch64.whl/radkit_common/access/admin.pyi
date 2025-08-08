from enum import Enum
from pydantic import BaseModel, PositiveInt as PositiveInt
from pydantic_core.core_schema import ValidationInfo as ValidationInfo
from radkit_common.access.exceptions import RADKitAccessError as RADKitAccessError

class InvalidResourceIdentifierError(RADKitAccessError):
    message: str
    status_code: int

class InvalidResourceLimitError(RADKitAccessError):
    message: str

class ResourceTypes(str, Enum):
    CERTIFICATE = 'CERTIFICATE'
    SERVICE_ID = 'SERVICE_ID'
    CONNECTION = 'CONNECTION'
    API_TOKEN = 'API_TOKEN'
    CLIENT_CREDENTIALS = 'CLIENT_CREDENTIALS'
    CLIENT_CREDENTIALS_AUTHENTICATION = 'CLIENT_CREDENTIALS_AUTHENTICATION'

class Rate(BaseModel):
    max: PositiveInt
    interval: PositiveInt

class Resource(BaseModel):
    type: ResourceTypes
    identifier: str
    def validate_identifier(cls, value: str) -> str: ...
    @property
    def base_key(self) -> str: ...

class ResourceRateLimit(BaseModel):
    resource: Resource
    limit: Rate
    burst: Rate
    @property
    def key(self) -> str: ...
    @property
    def burst_key(self) -> str: ...
    @classmethod
    def ensure_limit_interval_ge_burst_interval(cls, value: Rate, info: ValidationInfo) -> Rate: ...

class CurrentResourceRateLimit(BaseModel):
    resource: Resource
    current_count: int
    current_burst: int

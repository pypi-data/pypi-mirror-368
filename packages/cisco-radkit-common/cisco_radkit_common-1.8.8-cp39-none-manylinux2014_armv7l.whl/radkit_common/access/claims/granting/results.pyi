from pydantic import BaseModel
from radkit_common.access.claims.types import ServiceIDPrefix as ServiceIDPrefix
from radkit_common.identities import ClientID as ClientID, Email as Email, ServiceID as ServiceID

class BaseGrantingResult(BaseModel):
    granted: bool
    root_grant: bool

class FailedGrantingResult(BaseGrantingResult):
    granted: bool
    type_mismatch: bool
    reason: str
    try_other_claims: bool

class SuccessfulGrantingResult(BaseGrantingResult):
    granted: bool
    permission: str
    granted_by: Email
    granted_to: Email

class GrantingClientIDsResult(SuccessfulGrantingResult):
    granted_client_ids: list[ClientID]

class GrantedServiceID(BaseModel):
    service_id: ServiceID
    endpoint_creation_allowed: bool

class GrantingServiceIDsResult(SuccessfulGrantingResult):
    granted_service_ids: list[GrantedServiceID]

class GrantingProxyResult(SuccessfulGrantingResult):
    granted_owner_domains: list[str]

class GrantingProxyClientIDsResult(SuccessfulGrantingResult):
    granted_client_id_domains: list[str]
    granted_owner_domains: list[str]

class GrantingProxyServiceIDsResult(SuccessfulGrantingResult):
    granted_service_id_prefixes: list[ServiceIDPrefix]
    granted_owner_domains: list[str]
    granted_match_any_prefix: bool

class GrantingUserDomainsResult(SuccessfulGrantingResult):
    granted_user_domains: list[str]

class GrantingEndpointDomainsResult(SuccessfulGrantingResult):
    granted_endpoint_domains: list[str]

class GrantsEverythingGrantingResult(SuccessfulGrantingResult):
    root_grant: bool
    granted_client_id_domains: list[str]
    granted_service_id_prefixes: list[ServiceIDPrefix]
    granted_owner_domains: list[str]
    granted_admin_domains: list[str]
    granted_user_domains: list[str]
    granted_endpoint_domains: list[str]

from ...endpoints import User as User
from ..base import AuthClaim as AuthClaim
from ..models import AdminDomains as AdminDomains, ClientIDDomains as ClientIDDomains, ClientIDs as ClientIDs, EndpointDomains as EndpointDomains, EndpointOwnerDomains as EndpointOwnerDomains, ServiceIDPrefixes as ServiceIDPrefixes, ServiceIDs as ServiceIDs, UserDomains as UserDomains
from ..types import ServiceIDPrefix as ServiceIDPrefix
from .results import BaseGrantingResult as BaseGrantingResult, FailedGrantingResult as FailedGrantingResult, GrantedServiceID as GrantedServiceID, GrantingClientIDsResult as GrantingClientIDsResult, GrantingEndpointDomainsResult as GrantingEndpointDomainsResult, GrantingProxyClientIDsResult as GrantingProxyClientIDsResult, GrantingProxyResult as GrantingProxyResult, GrantingProxyServiceIDsResult as GrantingProxyServiceIDsResult, GrantingServiceIDsResult as GrantingServiceIDsResult, GrantingUserDomainsResult as GrantingUserDomainsResult, GrantsEverythingGrantingResult as GrantsEverythingGrantingResult
from radkit_common.access.helpers import match_domains as match_domains

class GrantsClientIDs(ClientIDDomains, EndpointOwnerDomains):
    def grant_claim(self, claim: AuthClaim, admin: User, user: User) -> BaseGrantingResult: ...

class GrantsServiceIDs(ServiceIDPrefixes, EndpointOwnerDomains):
    def grant_claim(self, claim: AuthClaim, admin: User, user: User) -> BaseGrantingResult: ...

class GrantsProxy(AdminDomains, EndpointOwnerDomains):
    def grant_claim(self, claim: AuthClaim, admin: User, user: User) -> BaseGrantingResult: ...

class GrantsProxyClientIDs(AdminDomains, ClientIDDomains, EndpointOwnerDomains):
    def grant_claim(self, claim: AuthClaim, admin: User, user: User) -> BaseGrantingResult: ...

class GrantsProxyServiceIDs(AdminDomains, ServiceIDPrefixes, EndpointOwnerDomains):
    def grant_claim(self, claim: AuthClaim, admin: User, user: User) -> BaseGrantingResult: ...

class GrantsUserDomains(AdminDomains, UserDomains):
    def grant_claim(self, claim: AuthClaim, admin: User, user: User) -> BaseGrantingResult: ...

class GrantsEndpointDomains(AdminDomains, EndpointDomains):
    def grant_claim(self, claim: AuthClaim, admin: User, user: User) -> BaseGrantingResult: ...

class GrantsEverything(ClientIDDomains, ServiceIDPrefixes, EndpointOwnerDomains, AdminDomains, UserDomains, EndpointDomains):
    def grant_claim(self, claim: AuthClaim, admin: User, user: User) -> BaseGrantingResult: ...

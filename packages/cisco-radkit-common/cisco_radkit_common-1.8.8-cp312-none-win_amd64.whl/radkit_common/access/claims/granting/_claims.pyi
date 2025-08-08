from .. import CLAIMS as CLAIMS
from ...endpoints import User as User
from .._claims import AddUserClaim as AddUserClaim, DeleteUserClaim as DeleteUserClaim, GenerateRequestClientCertificateOTPClaim as GenerateRequestClientCertificateOTPClaim, GenerateRequestServiceCertificateOTPClaim as GenerateRequestServiceCertificateOTPClaim, GetUserClaim as GetUserClaim, NON_GRANTING_CLAIMS as NON_GRANTING_CLAIMS, ProxyGenerateClientOTPClaim as ProxyGenerateClientOTPClaim, ProxyGenerateServiceOTPClaim as ProxyGenerateServiceOTPClaim, ProxyGetCertificateClaim as ProxyGetCertificateClaim, ProxyRequestClientCertificateClaim as ProxyRequestClientCertificateClaim, ProxyRequestServiceCertificateClaim as ProxyRequestServiceCertificateClaim, ProxyRevokeCertificateClaim as ProxyRevokeCertificateClaim, RateLimiterDataClaim as RateLimiterDataClaim, ReadAuditorDataClaim as ReadAuditorDataClaim, ReadCDNARateLimiterDataClaim as ReadCDNARateLimiterDataClaim, ReadRateLimiterDataClaim as ReadRateLimiterDataClaim, RequestAPITokenClaim as RequestAPITokenClaim, RequestClientCertificateClaim as RequestClientCertificateClaim, RequestClientCredentialsClaim as RequestClientCredentialsClaim, RequestServiceCertificateClaim as RequestServiceCertificateClaim, ResourceRateLimitClaim as ResourceRateLimitClaim, SearchEndpointsClaim as SearchEndpointsClaim, UpdateUserClaim as UpdateUserClaim, WriteAuditorDataClaim as WriteAuditorDataClaim, WriteCDNARateLimiterDataClaim as WriteCDNARateLimiterDataClaim, WriteRateLimiterDataClaim as WriteRateLimiterDataClaim
from ..base import AuthClaim as AuthClaim, CloudAdminClaim as CloudAdminClaim
from .base import GrantingClaim as GrantingClaim
from .models import GrantsClientIDs as GrantsClientIDs, GrantsEndpointDomains as GrantsEndpointDomains, GrantsEverything as GrantsEverything, GrantsProxy as GrantsProxy, GrantsProxyClientIDs as GrantsProxyClientIDs, GrantsProxyServiceIDs as GrantsProxyServiceIDs, GrantsServiceIDs as GrantsServiceIDs, GrantsUserDomains as GrantsUserDomains
from .results import BaseGrantingResult as BaseGrantingResult, FailedGrantingResult as FailedGrantingResult
from radkit_common import nglog as nglog
from radkit_common.access.helpers import match_domains as match_domains
from radkit_common.settings import get_settings as get_settings
from typing_extensions import Literal

class GrantRequestClientCertificateClaim(GrantingClaim, GrantsClientIDs):
    permission: Literal['grant_request_client_certificate']
    admin_level: int
    def grant_claim(self, claim: AuthClaim, admin: User, user: User) -> BaseGrantingResult: ...

class GrantRequestServiceCertificateClaim(GrantingClaim, GrantsServiceIDs):
    permission: Literal['grant_request_service_certificate']
    admin_level: int
    def grant_claim(self, claim: AuthClaim, admin: User, user: User) -> BaseGrantingResult: ...

class GrantProxyRequestClientCertificateClaim(GrantingClaim, GrantsProxyClientIDs):
    permission: Literal['grant_proxy_request_certificate', 'grant_proxy_request_client_certificate']
    admin_level: int
    def grant_claim(self, claim: AuthClaim, admin: User, user: User) -> BaseGrantingResult: ...

class GrantProxyRequestServiceCertificateClaim(GrantingClaim, GrantsProxyServiceIDs):
    permission: Literal['grant_proxy_request_service_certificate']
    admin_level: int
    def grant_claim(self, claim: AuthClaim, admin: User, user: User) -> BaseGrantingResult: ...

class GrantProxyGetCertificateClaim(GrantingClaim, GrantsProxy):
    permission: Literal['grant_proxy_get_certificate']
    admin_level: int
    def grant_claim(self, claim: AuthClaim, admin: User, user: User) -> BaseGrantingResult: ...

class GrantProxyRevokeCertificateClaim(GrantingClaim, GrantsProxy):
    permission: Literal['grant_proxy_revoke_certificate']
    admin_level: int
    def grant_claim(self, claim: AuthClaim, admin: User, user: User) -> BaseGrantingResult: ...

class GrantGenerateRequestServiceCertificateOTPClaim(GrantingClaim, GrantsServiceIDs):
    permission: Literal['grant_generate_request_service_certificate_otp']
    admin_level: int
    def grant_claim(self, claim: AuthClaim, admin: User, user: User) -> BaseGrantingResult: ...

class GrantGenerateRequestClientCertificateOTPClaim(GrantingClaim, GrantsClientIDs):
    permission: Literal['grant_generate_request_client_certificate_otp']
    admin_level: int
    def grant_claim(self, claim: AuthClaim, admin: User, user: User) -> BaseGrantingResult: ...

class GrantProxyGenerateClientOTPClaim(GrantingClaim, GrantsProxyClientIDs):
    permission: Literal['grant_proxy_generate_otp', 'grant_proxy_generate_client_otp']
    admin_level: int
    def grant_claim(self, claim: AuthClaim, admin: User, user: User) -> BaseGrantingResult: ...

class GrantProxyGenerateServiceOTPClaim(GrantingClaim, GrantsProxyServiceIDs):
    permission: Literal['grant_proxy_generate_service_otp']
    admin_level: int
    def grant_claim(self, claim: AuthClaim, admin: User, user: User) -> BaseGrantingResult: ...

class GrantAddUserClaim(GrantingClaim, GrantsUserDomains):
    permission: Literal['grant_add_user']
    admin_level: int
    def grant_claim(self, claim: AuthClaim, admin: User, user: User) -> BaseGrantingResult: ...

class GrantGetUserClaim(GrantingClaim, GrantsUserDomains):
    permission: Literal['grant_get_user']
    admin_level: int
    def grant_claim(self, claim: AuthClaim, admin: User, user: User) -> BaseGrantingResult: ...

class GrantUpdateUserClaim(GrantingClaim, GrantsUserDomains):
    permission: Literal['grant_update_user']
    admin_level: int
    def grant_claim(self, claim: AuthClaim, admin: User, user: User) -> BaseGrantingResult: ...

class GrantDeleteUserClaim(GrantingClaim, GrantsUserDomains):
    permission: Literal['grant_delete_user']
    admin_level: int
    def grant_claim(self, claim: AuthClaim, admin: User, user: User) -> BaseGrantingResult: ...

class GrantSearchEndpointsClaim(GrantingClaim, GrantsEndpointDomains):
    permission: Literal['grant_search_endpoints']
    admin_level: int
    def grant_claim(self, claim: AuthClaim, admin: User, user: User) -> BaseGrantingResult: ...

class GrantRateLimiterDataClaim(GrantingClaim, GrantsClientIDs, GrantsUserDomains, GrantsServiceIDs):
    permission: Literal['grant_rate_limiter_data']
    admin_level: int
    def grant_claim(self, claim: AuthClaim, admin: User, user: User) -> BaseGrantingResult: ...

class GrantResourceRateLimitClaim(GrantingClaim):
    permission: Literal['grant_resource_rate_limit']
    admin_level: int
    def grant_claim(self, claim: AuthClaim, admin: User, user: User) -> BaseGrantingResult: ...

class GrantRequestAPITokenClaim(GrantingClaim):
    permission: Literal['grant_request_api_token', 'grant_request_long_lived_token']
    admin_level: int
    def grant_claim(self, claim: AuthClaim, admin: User, user: User) -> BaseGrantingResult: ...

class GrantRequestClientCredentialsClaim(GrantingClaim):
    permission: Literal['grant_request_client_credentials']
    admin_level: int
    def grant_claim(self, claim: AuthClaim, admin: User, user: User) -> BaseGrantingResult: ...

class GrantCloudAdminClaim(GrantingClaim):
    permission: Literal['grant_cloud_admin']
    admin_level: int
    def grant_claim(self, claim: AuthClaim, admin: User, user: User) -> BaseGrantingResult: ...

class RootGrantingClaim(GrantingClaim, GrantsEverything):
    permission: Literal['root_grant']
    admin_level: int
    def grant_claim(self, claim: AuthClaim, admin: User, user: User) -> BaseGrantingResult: ...
GRANTING_CLAIMS = GrantRequestServiceCertificateClaim | GrantRequestClientCertificateClaim | GrantGenerateRequestServiceCertificateOTPClaim | GrantGenerateRequestClientCertificateOTPClaim | GrantProxyRequestClientCertificateClaim | GrantProxyRequestServiceCertificateClaim | GrantProxyGetCertificateClaim | GrantProxyRevokeCertificateClaim | GrantProxyGenerateClientOTPClaim | GrantProxyGenerateServiceOTPClaim | GrantAddUserClaim | GrantGetUserClaim | GrantUpdateUserClaim | GrantDeleteUserClaim | GrantSearchEndpointsClaim | GrantRateLimiterDataClaim | GrantResourceRateLimitClaim | GrantRequestAPITokenClaim | GrantRequestClientCredentialsClaim | GrantCloudAdminClaim | RootGrantingClaim
ROOT_CLAIMS: dict[type[NON_GRANTING_CLAIMS], GRANTING_CLAIMS]

def get_root_granting_claim(claim_type: type[CLAIMS]) -> GRANTING_CLAIMS: ...

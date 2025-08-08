from ..admin import Rate as Rate, ResourceTypes as ResourceTypes
from ..exceptions import InvalidIdentityError as InvalidIdentityError
from .base import AuthClaim as AuthClaim, CloudAdminClaim as CloudAdminClaim
from .models import CertificateSerialNumbers as CertificateSerialNumbers, ClientIDDomains as ClientIDDomains, ClientIDs as ClientIDs, EndpointDomains as EndpointDomains, EndpointOwnerDomains as EndpointOwnerDomains, ServiceIDPrefixes as ServiceIDPrefixes, ServiceIDs as ServiceIDs, UserDomains as UserDomains
from radkit_common.identities import ClientID as ClientID, EndpointID as EndpointID, ServiceID as ServiceID
from typing_extensions import Literal, Self

class RequestClientCertificateClaim(AuthClaim, ClientIDs):
    permission: Literal['request_client_certificate']
    admin_level: int
    def authorize(self, endpoint_id: EndpointID | None = None, certificate_serial_number: str | None = None, client_id_domain: str | None = None, endpoint_owner_domain: str | None = None, endpoint_requester_domain: str | None = None, admin_domain: str | None = None, user_domain: str | None = None, endpoint_domain: str | None = None) -> bool: ...
    @classmethod
    def root(cls) -> RequestClientCertificateClaim: ...

class RequestServiceCertificateClaim(AuthClaim, ServiceIDs):
    permission: Literal['request_service_certificate']
    admin_level: int
    def authorize(self, endpoint_id: EndpointID | None = None, certificate_serial_number: str | None = None, client_id_domain: str | None = None, endpoint_owner_domain: str | None = None, endpoint_requester_domain: str | None = None, admin_domain: str | None = None, user_domain: str | None = None, endpoint_domain: str | None = None) -> bool: ...
    @classmethod
    def root(cls) -> RequestServiceCertificateClaim: ...

class GetCertificateClaim(AuthClaim, CertificateSerialNumbers):
    permission: Literal['get_certificate']
    admin_level: int
    def authorize(self, endpoint_id: EndpointID | None = None, certificate_serial_number: str | None = None, client_id_domain: str | None = None, endpoint_owner_domain: str | None = None, endpoint_requester_domain: str | None = None, admin_domain: str | None = None, user_domain: str | None = None, endpoint_domain: str | None = None) -> bool: ...
    @classmethod
    def root(cls) -> GetCertificateClaim: ...

class RevokeCertificateClaim(AuthClaim, CertificateSerialNumbers):
    permission: Literal['revoke_certificate']
    admin_level: int
    def authorize(self, endpoint_id: EndpointID | None = None, certificate_serial_number: str | None = None, client_id_domain: str | None = None, endpoint_owner_domain: str | None = None, endpoint_requester_domain: str | None = None, admin_domain: str | None = None, user_domain: str | None = None, endpoint_domain: str | None = None) -> bool: ...
    @classmethod
    def root(cls) -> RevokeCertificateClaim: ...

class GenerateRequestServiceCertificateOTPClaim(AuthClaim, ServiceIDs):
    permission: Literal['generate_request_service_certificate_otp']
    admin_level: int
    def authorize(self, endpoint_id: EndpointID | None = None, certificate_serial_number: str | None = None, client_id_domain: str | None = None, endpoint_owner_domain: str | None = None, endpoint_requester_domain: str | None = None, admin_domain: str | None = None, user_domain: str | None = None, endpoint_domain: str | None = None) -> bool: ...
    @classmethod
    def root(cls) -> GenerateRequestServiceCertificateOTPClaim: ...

class GenerateRequestClientCertificateOTPClaim(AuthClaim, ClientIDs):
    permission: Literal['generate_request_client_certificate_otp']
    admin_level: int
    def authorize(self, endpoint_id: EndpointID | None = None, certificate_serial_number: str | None = None, client_id_domain: str | None = None, endpoint_owner_domain: str | None = None, endpoint_requester_domain: str | None = None, admin_domain: str | None = None, user_domain: str | None = None, endpoint_domain: str | None = None) -> bool: ...
    @classmethod
    def root(cls) -> GenerateRequestClientCertificateOTPClaim: ...

class ProxyRequestClientCertificateClaim(AuthClaim, ClientIDDomains, EndpointOwnerDomains):
    permission: Literal['proxy_request_certificate', 'proxy_request_client_certificate']
    admin_level: int
    def authorize(self, endpoint_id: EndpointID | None = None, certificate_serial_number: str | None = None, client_id_domain: str | None = None, endpoint_owner_domain: str | None = None, endpoint_requester_domain: str | None = None, admin_domain: str | None = None, user_domain: str | None = None, endpoint_domain: str | None = None) -> bool: ...
    @classmethod
    def root(cls) -> ProxyRequestClientCertificateClaim: ...

class ProxyRequestServiceCertificateClaim(AuthClaim, ServiceIDPrefixes, EndpointOwnerDomains):
    permission: Literal['proxy_request_service_certificate']
    admin_level: int
    def authorize(self, endpoint_id: EndpointID | None = None, certificate_serial_number: str | None = None, client_id_domain: str | None = None, endpoint_owner_domain: str | None = None, endpoint_requester_domain: str | None = None, admin_domain: str | None = None, user_domain: str | None = None, endpoint_domain: str | None = None) -> bool: ...
    @classmethod
    def root(cls) -> ProxyRequestServiceCertificateClaim: ...

class ProxyGetCertificateClaim(AuthClaim, EndpointOwnerDomains):
    permission: Literal['proxy_get_certificate']
    admin_level: int
    def authorize(self, endpoint_id: EndpointID | None = None, certificate_serial_number: str | None = None, client_id_domain: str | None = None, endpoint_owner_domain: str | None = None, endpoint_requester_domain: str | None = None, admin_domain: str | None = None, user_domain: str | None = None, endpoint_domain: str | None = None) -> bool: ...
    @classmethod
    def root(cls) -> ProxyGetCertificateClaim: ...

class ProxyRevokeCertificateClaim(AuthClaim, EndpointOwnerDomains):
    permission: Literal['proxy_revoke_certificate']
    admin_level: int
    def authorize(self, endpoint_id: EndpointID | None = None, certificate_serial_number: str | None = None, client_id_domain: str | None = None, endpoint_owner_domain: str | None = None, endpoint_requester_domain: str | None = None, admin_domain: str | None = None, user_domain: str | None = None, endpoint_domain: str | None = None) -> bool: ...
    @classmethod
    def root(cls) -> ProxyRevokeCertificateClaim: ...

class ProxyGenerateClientOTPClaim(AuthClaim, ClientIDDomains, EndpointOwnerDomains):
    permission: Literal['proxy_generate_otp', 'proxy_generate_client_otp']
    admin_level: int
    def authorize(self, endpoint_id: EndpointID | None = None, certificate_serial_number: str | None = None, client_id_domain: str | None = None, endpoint_owner_domain: str | None = None, endpoint_requester_domain: str | None = None, admin_domain: str | None = None, user_domain: str | None = None, endpoint_domain: str | None = None) -> bool: ...
    @classmethod
    def root(cls) -> ProxyGenerateClientOTPClaim: ...

class ProxyGenerateServiceOTPClaim(AuthClaim, ServiceIDPrefixes, EndpointOwnerDomains):
    permission: Literal['proxy_generate_service_otp']
    admin_level: int
    def authorize(self, endpoint_id: EndpointID | None = None, certificate_serial_number: str | None = None, client_id_domain: str | None = None, endpoint_owner_domain: str | None = None, endpoint_requester_domain: str | None = None, admin_domain: str | None = None, user_domain: str | None = None, endpoint_domain: str | None = None) -> bool: ...
    @classmethod
    def root(cls) -> ProxyGenerateServiceOTPClaim: ...

class AddUserClaim(AuthClaim, UserDomains):
    permission: Literal['add_user']
    admin_level: int
    def authorize(self, endpoint_id: EndpointID | None = None, certificate_serial_number: str | None = None, client_id_domain: str | None = None, endpoint_owner_domain: str | None = None, endpoint_requester_domain: str | None = None, admin_domain: str | None = None, user_domain: str | None = None, endpoint_domain: str | None = None) -> bool: ...
    @classmethod
    def root(cls) -> AddUserClaim: ...

class GetUserClaim(AuthClaim, UserDomains):
    permission: Literal['get_user']
    admin_level: int
    def authorize(self, endpoint_id: EndpointID | None = None, certificate_serial_number: str | None = None, client_id_domain: str | None = None, endpoint_owner_domain: str | None = None, endpoint_requester_domain: str | None = None, admin_domain: str | None = None, user_domain: str | None = None, endpoint_domain: str | None = None) -> bool: ...
    @classmethod
    def root(cls) -> GetUserClaim: ...

class UpdateUserClaim(AuthClaim, UserDomains):
    permission: Literal['update_user']
    admin_level: int
    def authorize(self, endpoint_id: EndpointID | None = None, certificate_serial_number: str | None = None, client_id_domain: str | None = None, endpoint_owner_domain: str | None = None, endpoint_requester_domain: str | None = None, admin_domain: str | None = None, user_domain: str | None = None, endpoint_domain: str | None = None) -> bool: ...
    @classmethod
    def root(cls) -> UpdateUserClaim: ...

class DeleteUserClaim(AuthClaim, UserDomains):
    permission: Literal['delete_user']
    admin_level: int
    def authorize(self, endpoint_id: EndpointID | None = None, certificate_serial_number: str | None = None, client_id_domain: str | None = None, endpoint_owner_domain: str | None = None, endpoint_requester_domain: str | None = None, admin_domain: str | None = None, user_domain: str | None = None, endpoint_domain: str | None = None) -> bool: ...
    @classmethod
    def root(cls) -> DeleteUserClaim: ...

class SearchEndpointsClaim(AuthClaim, EndpointDomains):
    permission: Literal['search_endpoints']
    admin_level: int
    def authorize(self, endpoint_id: EndpointID | None = None, certificate_serial_number: str | None = None, client_id_domain: str | None = None, endpoint_owner_domain: str | None = None, endpoint_requester_domain: str | None = None, admin_domain: str | None = None, user_domain: str | None = None, endpoint_domain: str | None = None) -> bool: ...
    @classmethod
    def root(cls) -> SearchEndpointsClaim: ...

class ReadAuditorDataClaim(CloudAdminClaim):
    permission: Literal['get_auditor_data']
    admin_level: int
    @classmethod
    def root(cls) -> ReadAuditorDataClaim: ...

class WriteAuditorDataClaim(CloudAdminClaim):
    permission: Literal['reset_rate_limit']
    admin_level: int
    @classmethod
    def root(cls) -> WriteAuditorDataClaim: ...

class RateLimiterDataClaim(AuthClaim, ClientIDs, ClientIDDomains, ServiceIDs):
    client_id_domains: list[str]
    def authorize(self, endpoint_id: EndpointID | None = None, certificate_serial_number: str | None = None, client_id_domain: str | None = None, endpoint_owner_domain: str | None = None, endpoint_requester_domain: str | None = None, admin_domain: str | None = None, user_domain: str | None = None, endpoint_domain: str | None = None) -> bool: ...

class ReadRateLimiterDataClaim(RateLimiterDataClaim):
    permission: Literal['get_rate_limiter_data']
    admin_level: int
    @classmethod
    def root(cls) -> Self: ...

class WriteRateLimiterDataClaim(RateLimiterDataClaim):
    permission: Literal['reset_rate_limiter']
    admin_level: int
    @classmethod
    def root(cls) -> Self: ...

class CDNARateLimiterDataClaim(CloudAdminClaim):
    def authorize(self, endpoint_id: str | None = None, certificate_serial_number: str | None = None, client_id_domain: str | None = None, endpoint_owner_domain: str | None = None, endpoint_requester_domain: str | None = None, admin_domain: str | None = None, user_domain: str | None = None, endpoint_domain: str | None = None) -> bool: ...

class ReadCDNARateLimiterDataClaim(CDNARateLimiterDataClaim):
    permission: Literal['get_cdna_rate_limiter_data']
    admin_level: int
    @classmethod
    def root(cls) -> Self: ...

class WriteCDNARateLimiterDataClaim(CDNARateLimiterDataClaim):
    permission: Literal['reset_cdna_rate_limiter']
    admin_level: int
    @classmethod
    def root(cls) -> Self: ...

class ResourceRateLimitClaim(AuthClaim):
    permission: Literal['resource_rate_limit']
    admin_level: int
    resource_type: ResourceTypes
    limit: Rate
    burst: Rate

class RequestAPITokenClaim(AuthClaim):
    permission: Literal['request_api_token', 'request_long_lived_token']
    admin_level: int
    allow_block_bypass: bool
    def authorize(self, endpoint_id: EndpointID | None = None, certificate_serial_number: str | None = None, client_id_domain: str | None = None, endpoint_owner_domain: str | None = None, endpoint_requester_domain: str | None = None, admin_domain: str | None = None, user_domain: str | None = None, endpoint_domain: str | None = None) -> bool: ...
    @classmethod
    def root(cls) -> Self: ...

class RequestClientCredentialsClaim(AuthClaim):
    permission: Literal['request_client_credentials']
    admin_level: int
    def authorize(self, endpoint_id: EndpointID | None = None, certificate_serial_number: str | None = None, client_id_domain: str | None = None, endpoint_owner_domain: str | None = None, endpoint_requester_domain: str | None = None, admin_domain: str | None = None, user_domain: str | None = None, endpoint_domain: str | None = None) -> bool: ...
    @classmethod
    def root(cls) -> Self: ...
DIRECT_CLAIMS = RequestClientCertificateClaim | RequestServiceCertificateClaim | GenerateRequestClientCertificateOTPClaim | GenerateRequestServiceCertificateOTPClaim | GetCertificateClaim | RevokeCertificateClaim
PROXY_CLAIMS = ProxyRequestClientCertificateClaim | ProxyRequestServiceCertificateClaim | ProxyGetCertificateClaim | ProxyRevokeCertificateClaim | ProxyGenerateClientOTPClaim | ProxyGenerateServiceOTPClaim
ADMIN_CLAIMS = AddUserClaim | GetUserClaim | UpdateUserClaim | DeleteUserClaim | SearchEndpointsClaim | ReadAuditorDataClaim | WriteAuditorDataClaim | ReadCDNARateLimiterDataClaim | WriteCDNARateLimiterDataClaim | ReadRateLimiterDataClaim | WriteRateLimiterDataClaim | ResourceRateLimitClaim | RequestAPITokenClaim | RequestClientCredentialsClaim
NON_GRANTING_CLAIMS = DIRECT_CLAIMS | PROXY_CLAIMS | ADMIN_CLAIMS

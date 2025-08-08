from pydantic import BaseModel
from radkit_common.identities import EndpointID as EndpointID

class AuthClaim(BaseModel):
    permission: str
    admin_level: int
    log_at_grant: bool
    log_at_use: bool
    def authorize(self, endpoint_id: EndpointID | None = None, certificate_serial_number: str | None = None, client_id_domain: str | None = None, endpoint_owner_domain: str | None = None, endpoint_requester_domain: str | None = None, admin_domain: str | None = None, user_domain: str | None = None, endpoint_domain: str | None = None) -> bool: ...

class CloudAdminClaim(AuthClaim):
    def authorize(self, endpoint_id: EndpointID | None = None, certificate_serial_number: str | None = None, client_id_domain: str | None = None, endpoint_owner_domain: str | None = None, endpoint_requester_domain: str | None = None, admin_domain: str | None = None, user_domain: str | None = None, endpoint_domain: str | None = None) -> bool: ...

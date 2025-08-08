from ...endpoints import User as User
from ..base import AuthClaim as AuthClaim
from ..granting.results import BaseGrantingResult as BaseGrantingResult, FailedGrantingResult as FailedGrantingResult, SuccessfulGrantingResult as SuccessfulGrantingResult

class GrantingClaim(AuthClaim):
    def grant_claim(self, claim: AuthClaim, admin: User, user: User) -> BaseGrantingResult: ...

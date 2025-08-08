__all__ = ['RADKitAccessError', 'RADKitAccessInternalError', 'OAuthLoginError', 'OAuthLoginTimeoutWarning', 'InvalidCertificateObjectError', 'UnknownCertificateOIDError', 'InvalidCSRError', 'CertificateNotFoundError', 'InvalidOTPRequestError', 'CAError', 'TokenError', 'AuthDataStoreError', 'OAuthError', 'InvalidIdentityError', 'InvalidState', 'InvalidToken', 'UserNotFoundError', 'InvalidDomainError', 'RADKitCertificateError', 'RADKitCertificateInternalError', 'CertificateParsingError', 'UnknownTokenProviderError', 'UnknownAuthProviderError', 'RefreshTokenNotFound', 'TokenRefreshNotSupported', 'CertificatePendingError', 'CertificateRevokedError', 'CertificateRevokedOutOfBandError', 'CertificateStateUnexpectedError', 'CertificateExpiredError', 'CertificateMissingError', 'AuthProvidersStoreError', 'InvalidEndpointTypeError', 'InvalidServiceIDError', 'UnknownResourceError', 'MaxAPITokenCountExceededError']

class RADKitAccessError(Exception):
    message: str
    status_code: int
    def __init__(self, message: str | None = None, status_code: int | None = None) -> None: ...
    @property
    def error_dict(self) -> dict[str, str]: ...

class RADKitAccessInternalError(RADKitAccessError):
    message: str
    status_code: int

class RADKitAccessClientError(RADKitAccessError):
    message: str

class OAuthLoginError(RADKitAccessClientError):
    message: str

class OAuthLoginTimeoutWarning(OAuthLoginError):
    message: str

class UnknownCertificateOIDError(RADKitAccessClientError):
    message: str

class InvalidCertificateObjectError(RADKitAccessClientError):
    message: str

class CAError(RADKitAccessError):
    message: str
    status_code: int

class InvalidCSRError(CAError):
    message: str
    status_code: int

class CertificateNotFoundError(CAError):
    message: str
    status_code: int

class InvalidOTPRequestError(RADKitAccessError):
    message: str
    status_code: int

class InvalidIdentityError(RADKitAccessError):
    message: str
    status_code: int

class InvalidDomainError(RADKitAccessError):
    message: str
    status_code: int

class TokenError(RADKitAccessError):
    status_code: int

class AuthDataStoreError(RADKitAccessError):
    message: str
    status_code: int

class OAuthError(RADKitAccessError):
    status_code: int

class InvalidState(TokenError):
    message: str
    status_code: int

class TokenNotValidYet(TokenError):
    message: str
    status_code: int

class InvalidToken(TokenError):
    message: str
    status_code: int

class RefreshTokenNotFound(TokenError):
    message: str
    status_code: int

class TokenRefreshNotSupported(TokenError):
    message: str
    status_code: int

class UserNotFoundError(RADKitAccessError):
    message: str
    status_code: int

class RADKitCertificateError(RADKitAccessError):
    message: str
    status_code: int

class RADKitCertificateInternalError(RADKitAccessInternalError):
    message: str
    status_code: int

class CertificateParsingError(RADKitCertificateError):
    message: str

class CertificateExpiredError(RADKitCertificateError):
    message: str

class CertificateRevokedError(RADKitCertificateError):
    message: str

class CertificateRevokedOutOfBandError(RADKitCertificateInternalError):
    message: str

class CertificatePendingError(RADKitCertificateError):
    message: str

class CertificateMissingError(RADKitCertificateError):
    message: str

class CertificateStateUnexpectedError(RADKitCertificateInternalError):
    message: str

class UnknownResourceError(RADKitAccessError):
    message: str
    status_code: int

class UnknownTokenProviderError(RADKitAccessError):
    message: str
    status_code: int

class UnknownAuthProviderError(RADKitAccessError):
    message: str
    status_code: int

class AuthProvidersStoreError(RADKitAccessInternalError):
    message: str
    status_code: int

class InvalidServiceIDError(RADKitAccessError):
    message: str
    status_code: int

class InvalidEndpointTypeError(RADKitAccessError):
    message: str
    status_code: int

class MaxAPITokenCountExceededError(RADKitAccessError):
    message: str
    status_code: int

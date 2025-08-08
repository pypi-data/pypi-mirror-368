from _typeshed import Incomplete
from pydantic import BaseModel, HttpUrl as HttpUrl

class ChallengeData(BaseModel):
    challenge_id: str
    challenge: str
    auth_url: HttpUrl

class ChallengeResponse(BaseModel):
    signature: str
    nonce: str
    certificate_serial_number: str
    challenge_id: str
    admin_level: int
    certificate_pem: str | None
    model_config: Incomplete

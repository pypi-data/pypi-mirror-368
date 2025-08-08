from _typeshed import Incomplete
from enum import Enum
from pydantic import AwareDatetime as AwareDatetime, BaseModel, BeforeValidator as BeforeValidator
from radkit_common.utils.validators import convert_to_utc as convert_to_utc
from typing import Annotated

class CSOneAutomationTag(str, Enum):
    CXD = 'RADKit: CXD'
    INTERACTIVE = 'RADKit: Interactive'
    DATA_PIPING = 'RADKit: Data Piping'
    DATA_COLLECTION = 'RADKit: Data Collection'
    SESSION = 'RADKit: Connection'
    DIAGNOSTICS = 'RADKit: Diagnostics'
    AUTOMATION = 'RADKit: Automation'
    OTHER = 'RADKit: Other'

class CaseNoteStatus(str, Enum):
    INTERNAL = 'Internal'
    EXTERNAL = 'External'

class CaseNoteType(str, Enum):
    ROUTING_DECISION = 'ROUTING DECISION'
    CUSTOMER_TROUBLESHOOTING = 'CUSTOMER TROUBLESHOOTING'
    CUSTOMER_SYMPTOMS = 'CUSTOMER SYMPTOMS'
    CASE_REVIEW = 'CASE REVIEW'
    EMAIL_IN = 'EMAIL IN'
    ENTITLEMENT = 'ENTITLEMENT'
    INITIAL_CUSTOMER_TROUBLESHOOTING = 'INITIAL CUSTOMER TROUBLESHOOTING'
    CONTRACT_NUMBER = 'CONTRACT NUMBER'
    PROBLEM_DESCRIPTION = 'PROBLEM DESCRIPTION'
    OTHER = 'Other'
    SUBSCRIPTION = 'SUBSCRIPTION'
    ATTACHMENT_ADDED = 'ATTACHMENT ADDED'
    ATTACHMENT_DELETE = 'ATTACHMENT DELETE'

class CaseNote(BaseModel):
    id: str | None
    note: str
    note_detail: str
    note_status: CaseNoteStatus
    note_type: CaseNoteType
    created_date: Annotated[AwareDatetime | None, None]
    created_by: str | None
    model_config: Incomplete

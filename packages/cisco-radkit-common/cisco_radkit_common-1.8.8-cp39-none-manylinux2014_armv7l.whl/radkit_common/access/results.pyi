from pydantic import BaseModel
from typing_extensions import Literal

class Result(BaseModel):
    success: bool
    details: str
    retry: bool

class SuccessResult(BaseModel):
    success: Literal[True]
    details: str

class ErrorResult(BaseModel):
    success: Literal[False]
    details: str
    retry: bool
AnyResult = SuccessResult | ErrorResult

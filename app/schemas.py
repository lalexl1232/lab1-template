from typing import Optional
from pydantic import BaseModel, Field


class PersonRequest(BaseModel):
    name: str = Field(..., min_length=1)
    age: Optional[int] = None
    address: Optional[str] = None
    work: Optional[str] = None


class PersonResponse(BaseModel):
    id: int
    name: str
    age: Optional[int] = None
    address: Optional[str] = None
    work: Optional[str] = None

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    message: str


class ValidationErrorResponse(BaseModel):
    message: str
    errors: dict[str, str]

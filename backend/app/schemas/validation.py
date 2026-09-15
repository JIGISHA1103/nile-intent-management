from pydantic import BaseModel


class ValidationResult(BaseModel):
    valid: bool
    errors: list[str] = []
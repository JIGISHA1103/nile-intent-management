from pydantic import BaseModel, Field


class IntentRequest(BaseModel):
    message: str = Field(
        min_length=1,
        description="Natural-language travel request from the customer",
    )
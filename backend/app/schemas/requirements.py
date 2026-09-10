from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class Budget(BaseModel):
    amount: float = Field(gt=0)
    currency: str = "INR"


class TravelRequirement(BaseModel):
    origin: Optional[str] = None
    destination: str

    start_date: Optional[date] = None
    end_date: Optional[date] = None
    duration_days: Optional[int] = Field(default=None, gt=0)

    group_size: Optional[int] = Field(default=None, gt=0)

    budget: Optional[Budget] = None

    preferences: List[str] = Field(default_factory=list)
    activities: List[str] = Field(default_factory=list)

    transport_preferences: List[str] = Field(default_factory=list)
    dietary_preferences: List[str] = Field(default_factory=list)
    special_requirements: List[str] = Field(default_factory=list)
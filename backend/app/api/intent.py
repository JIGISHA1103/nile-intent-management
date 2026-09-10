from fastapi import APIRouter

from backend.app.schemas.intent import IntentRequest
from backend.app.schemas.requirements import TravelRequirement


router = APIRouter(
    prefix="/intent",
    tags=["Customer Intent"],
)


@router.post("/", response_model=TravelRequirement)
def create_intent(requirement: TravelRequirement):
    return requirement


@router.post("/message")
def process_intent_message(request: IntentRequest):
    return {
        "message": request.message,
        "status": "received",
    }
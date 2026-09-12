from fastapi import APIRouter

from backend.app.schemas.intent import IntentRequest
from backend.app.schemas.requirements import TravelRequirement
from backend.app.services.intent_service import extract_intent


router = APIRouter(
    prefix="/intent",
    tags=["Customer Intent"],
)


@router.post("/", response_model=TravelRequirement)
def create_intent(requirement: TravelRequirement):
    return requirement


@router.post("/message", response_model=TravelRequirement)
def process_intent_message(request: IntentRequest):
    return extract_intent(request.message)
from fastapi import APIRouter, HTTPException

from backend.app.schemas.intent import IntentRequest
from backend.app.schemas.requirements import TravelRequirement
from backend.app.services.intent_service import extract_intent
from backend.app.services.requirement_validator import validate_requirement


router = APIRouter(
    prefix="/intent",
    tags=["Customer Intent"],
)


@router.post("/", response_model=TravelRequirement)
def create_intent(requirement: TravelRequirement):
    validation_result = validate_requirement(requirement)

    if not validation_result.valid:
        raise HTTPException(
            status_code=422,
            detail=validation_result.errors,
        )

    return requirement


@router.post("/message", response_model=TravelRequirement)
def process_intent_message(request: IntentRequest):
    requirement = extract_intent(request.message)

    validation_result = validate_requirement(requirement)

    if not validation_result.valid:
        raise HTTPException(
            status_code=422,
            detail=validation_result.errors,
        )

    return requirement
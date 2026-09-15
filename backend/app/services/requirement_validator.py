from backend.app.schemas.requirements import TravelRequirement
from backend.app.schemas.validation import ValidationResult


def validate_requirement(
    requirement: TravelRequirement,
) -> ValidationResult:
    """
    Validate a structured travel requirement.

    Returns a structured validation result containing:
    - valid: whether the requirement passes validation
    - errors: list of validation errors
    """

    errors: list[str] = []

    # ---------------------------------------------------------
    # Destination
    # ---------------------------------------------------------
    if not requirement.destination:
        errors.append("Destination is required.")

    elif requirement.destination.strip().lower() == "unknown":
        errors.append("Destination could not be determined.")

    # ---------------------------------------------------------
    # Start / end dates
    # ---------------------------------------------------------
    if (
        requirement.start_date is not None
        and requirement.end_date is not None
    ):
        if requirement.end_date < requirement.start_date:
            errors.append(
                "End date cannot be before start date."
            )

    # ---------------------------------------------------------
    # Duration
    # ---------------------------------------------------------
    if requirement.duration_days is not None:
        if requirement.duration_days <= 0:
            errors.append(
                "Duration must be greater than zero."
            )

    # ---------------------------------------------------------
    # Date + duration consistency
    # ---------------------------------------------------------
    if (
        requirement.start_date is not None
        and requirement.end_date is not None
        and requirement.duration_days is not None
    ):
        calculated_duration = (
            requirement.end_date - requirement.start_date
        ).days

        if calculated_duration != requirement.duration_days:
            errors.append(
                "Duration does not match the provided travel dates."
            )

    # ---------------------------------------------------------
    # Group size
    # ---------------------------------------------------------
    if requirement.group_size is not None:
        if requirement.group_size <= 0:
            errors.append(
                "Group size must be greater than zero."
            )

    # ---------------------------------------------------------
    # Budget
    # ---------------------------------------------------------
    if requirement.budget is not None:
        if requirement.budget.amount <= 0:
            errors.append(
                "Budget must be greater than zero."
            )

        if not requirement.budget.currency:
            errors.append(
                "Budget currency is required."
            )

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
    )
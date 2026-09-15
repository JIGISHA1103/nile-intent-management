from datetime import date

from backend.app.schemas.requirements import (
    Budget,
    TravelRequirement,
)
from backend.app.services.requirement_validator import (
    validate_requirement,
)


def test_valid_requirement():
    requirement = TravelRequirement(
        origin="Bangalore",
        destination="Goa",
        start_date=date(2026, 10, 15),
        end_date=date(2026, 10, 18),
        duration_days=3,
        group_size=5,
        budget=Budget(
            amount=40000,
            currency="INR",
        ),
    )

    result = validate_requirement(requirement)

    assert result.valid is True
    assert result.errors == []


def test_invalid_date_range():
    requirement = TravelRequirement(
        origin="Bangalore",
        destination="Goa",
        start_date=date(2026, 10, 18),
        end_date=date(2026, 10, 15),
    )

    result = validate_requirement(requirement)

    assert result.valid is False
    assert "End date cannot be before start date." in result.errors


def test_inconsistent_duration():
    requirement = TravelRequirement(
        origin="Bangalore",
        destination="Goa",
        start_date=date(2026, 10, 15),
        end_date=date(2026, 10, 18),
        duration_days=5,
    )

    result = validate_requirement(requirement)

    assert result.valid is False
    assert (
        "Duration does not match the provided travel dates."
        in result.errors
    )


def test_missing_destination():
    requirement = TravelRequirement(
        origin="Bangalore",
        destination="Unknown",
    )

    result = validate_requirement(requirement)

    assert result.valid is False
    assert "Destination could not be determined." in result.errors
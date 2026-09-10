from datetime import date

from backend.app.schemas.requirements import (
    Budget,
    TravelRequirement,
)


def test_complete_travel_requirement():
    requirement = TravelRequirement(
        origin="Bangalore",
        destination="Goa",
        start_date=date(2026, 10, 15),
        end_date=date(2026, 10, 18),
        group_size=5,
        duration_days=3,
        
        budget=Budget(
            amount=50000,
            currency="INR",
        ),
        preferences=[
            "beach resort",
            "nightlife",
        ],
        activities=[
            "water sports",
        ],
    )

    assert requirement.origin == "Bangalore"
    assert requirement.destination == "Goa"
    assert requirement.group_size == 5
    assert requirement.budget.amount == 50000
    assert "nightlife" in requirement.preferences
    assert "water sports" in requirement.activities
    assert requirement.duration_days == 3
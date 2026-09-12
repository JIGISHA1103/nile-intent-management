from datetime import date

from backend.app.services.intent_service import extract_intent


def test_extract_basic_travel_intent():
    message = (
        "I want to go from Bangalore to Goa for 3 days "
        "with 4 friends, budget around 40000, "
        "preferably a beach resort and nightlife, with water sports."
    )

    requirement = extract_intent(message)

    assert requirement.origin == "Bangalore"
    assert requirement.destination == "Goa"
    assert requirement.duration_days == 3
    assert requirement.group_size == 5
    assert requirement.budget.amount == 40000
    assert requirement.budget.currency == "INR"
    assert "beach resort" in requirement.preferences
    assert "nightlife" in requirement.preferences
    assert "water sports" in requirement.activities


def test_extract_travel_dates():
    message = (
        "I want to travel from Bangalore to Goa "
        "from 15 October 2026 to 18 October 2026."
    )

    requirement = extract_intent(message)

    assert requirement.origin == "Bangalore"
    assert requirement.destination == "Goa"
    assert requirement.start_date == date(2026, 10, 15)
    assert requirement.end_date == date(2026, 10, 18)
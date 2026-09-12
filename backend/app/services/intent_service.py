import re
from typing import Optional

from backend.app.schemas.requirements import Budget, TravelRequirement


def extract_intent(message: str) -> TravelRequirement:
    """
    Extract basic travel requirements from a natural-language message.

    This is the initial deterministic extractor.
    LLM-based extraction can replace this implementation later.
    """

    # ---------------------------------------------------------
    # Route extraction
    # Example:
    # "I want to go from Bangalore to Goa for 3 days"
    #
    # Expected:
    # origin = Bangalore
    # destination = Goa
    # ---------------------------------------------------------
    route_match = re.search(
        r"\bfrom\s+([A-Za-z][A-Za-z\s-]*?)\s+to\s+"
        r"([A-Za-z][A-Za-z\s-]*?)"
        r"(?=\s+for\b|\s+with\b|\s+budget\b|,|\.|$)",
        message,
        re.IGNORECASE,
    )

    origin = None
    destination = None

    if route_match:
        origin = route_match.group(1).strip(" ,.")
        destination = route_match.group(2).strip(" ,.")

    # ---------------------------------------------------------
    # Fallback destination extraction
    # Used when the message does not contain a clear
    # "from X to Y" route.
    # ---------------------------------------------------------
    if not destination:
        destination = _extract_route_value(
            message,
            r"\bto\s+([A-Za-z][A-Za-z\s-]*?)"
            r"(?=\s+for\b|\s+with\b|\s+budget\b|,|\.|$)",
        )

    # ---------------------------------------------------------
    # Duration
    # Example:
    # "for 3 days"
    # ---------------------------------------------------------
    duration_days = _extract_int(
        message,
        r"\bfor\s+(\d+)\s+days?\b",
    )

    # ---------------------------------------------------------
    # Group size
    # Example:
    # "with 4 friends"
    #
    # Interpreted as 4 friends + the customer = 5 people.
    # ---------------------------------------------------------
    group_size = _extract_group_size(message)

    # ---------------------------------------------------------
    # Budget
    # Example:
    # "budget around 40000"
    # "budget ₹40,000"
    # "under INR 50000"
    # ---------------------------------------------------------
    budget_amount = _extract_budget(message)

    budget: Optional[Budget] = None

    if budget_amount is not None:
        budget = Budget(
            amount=budget_amount,
            currency="INR",
        )

    # ---------------------------------------------------------
    # Preferences
    # ---------------------------------------------------------
    preferences = _extract_preferences(message)

    # ---------------------------------------------------------
    # Activities
    # ---------------------------------------------------------
    activities = _extract_activities(message)

    # ---------------------------------------------------------
    # Build structured travel requirement
    # ---------------------------------------------------------
    return TravelRequirement(
        origin=origin,
        destination=destination or "Unknown",
        duration_days=duration_days,
        group_size=group_size,
        budget=budget,
        preferences=preferences,
        activities=activities,
    )


def _extract_route_value(
    message: str,
    pattern: str,
) -> Optional[str]:
    """
    Extract a route-related value using a regular expression.
    """

    match = re.search(
        pattern,
        message,
        re.IGNORECASE,
    )

    if not match:
        return None

    return match.group(1).strip(" ,.")


def _extract_int(
    message: str,
    pattern: str,
) -> Optional[int]:
    """
    Extract an integer value from the message.
    """

    match = re.search(
        pattern,
        message,
        re.IGNORECASE,
    )

    if not match:
        return None

    return int(match.group(1))


def _extract_group_size(message: str) -> Optional[int]:
    """
    Extract group size from phrases such as:

    - with 4 friends
    - with 3 people
    - with 5 members

    If the customer says "with 4 friends", the customer
    is included, so the total group size becomes 5.
    """

    match = re.search(
        r"\bwith\s+(\d+)\s+"
        r"(?:friends?|people|persons?|members?)\b",
        message,
        re.IGNORECASE,
    )

    if match:
        return int(match.group(1)) + 1

    return None


def _extract_budget(message: str) -> Optional[float]:
    """
    Extract budget amount from natural-language text.

    Supported examples:

    - budget around 40000
    - budget ₹40000
    - budget ₹40,000
    - budget INR 50000
    - under 30000
    - within Rs. 50000
    """

    match = re.search(
        r"(?:budget|around|under|within)"
        r"\s*"
        r"(?:₹|rs\.?|inr)?"
        r"\s*"
        r"([\d,]+)",
        message,
        re.IGNORECASE,
    )

    if not match:
        return None

    return float(
        match.group(1).replace(",", "")
    )


def _extract_preferences(message: str) -> list[str]:
    """
    Extract known travel preferences from the message.
    """

    preferences = []

    preference_keywords = [
        "beach resort",
        "nightlife",
        "luxury",
        "budget-friendly",
        "family-friendly",
        "nature",
        "adventure",
    ]

    message_lower = message.lower()

    for preference in preference_keywords:
        if preference in message_lower:
            preferences.append(preference)

    return preferences


def _extract_activities(message: str) -> list[str]:
    """
    Extract known travel activities from the message.
    """

    activities = []

    activity_keywords = [
        "water sports",
        "sightseeing",
        "trekking",
        "hiking",
        "scuba diving",
        "snorkeling",
        "shopping",
    ]

    message_lower = message.lower()

    for activity in activity_keywords:
        if activity in message_lower:
            activities.append(activity)

    return activities
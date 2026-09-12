import re
from datetime import date
from typing import Optional

from backend.app.schemas.requirements import Budget, TravelRequirement


MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


def extract_intent(message: str) -> TravelRequirement:
    """
    Extract basic travel requirements from a natural-language message.

    This is the initial deterministic extractor.
    LLM-based extraction can replace this implementation later.
    """

    # ---------------------------------------------------------
    # Route extraction
    # ---------------------------------------------------------
    route_match = re.search(
        r"\bfrom\s+([A-Za-z][A-Za-z\s-]*?)\s+to\s+"
        r"([A-Za-z][A-Za-z\s-]*?)"
        r"(?=\s+for\b|\s+with\b|\s+budget\b|\s+from\b|,|\.|$)",
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
    # ---------------------------------------------------------
    if not destination:
        destination = _extract_route_value(
            message,
            r"\bto\s+([A-Za-z][A-Za-z\s-]*?)"
            r"(?=\s+for\b|\s+with\b|\s+budget\b|\s+from\b|,|\.|$)",
        )

    # ---------------------------------------------------------
    # Dates
    # ---------------------------------------------------------
    start_date, end_date = _extract_dates(message)

    # ---------------------------------------------------------
    # Duration
    # ---------------------------------------------------------
    duration_days = _extract_int(
        message,
        r"\bfor\s+(\d+)\s+days?\b",
    )

    # ---------------------------------------------------------
    # Group size
    # ---------------------------------------------------------
    group_size = _extract_group_size(message)

    # ---------------------------------------------------------
    # Budget
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
        start_date=start_date,
        end_date=end_date,
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


def _extract_dates(
    message: str,
) -> tuple[Optional[date], Optional[date]]:
    """
    Extract travel dates from common natural-language formats.

    Supported examples:

    - from 15 October 2026 to 18 October 2026
    - from October 15 2026 to October 18 2026
    - from 15 Oct 2026 to 18 Oct 2026
    - on 15 October 2026

    We do not infer dates from duration alone.
    """

    month_pattern = (
        r"(January|February|March|April|May|June|July|August|"
        r"September|October|November|December|"
        r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)"
    )

    # Format:
    # 15 October 2026 to 18 October 2026
    day_first_pattern = re.compile(
        rf"\b(\d{{1,2}})\s+{month_pattern}\s+(\d{{4}})"
        rf"\s+(?:to|-)\s+"
        rf"(\d{{1,2}})\s+{month_pattern}\s+(\d{{4}})\b",
        re.IGNORECASE,
    )

    match = day_first_pattern.search(message)

    if match:
        start = _build_date(
            match.group(1),
            match.group(2),
            match.group(3),
        )
        end = _build_date(
            match.group(4),
            match.group(5),
            match.group(6),
        )

        return start, end

    # Format:
    # October 15 2026 to October 18 2026
    month_first_pattern = re.compile(
        rf"\b{month_pattern}\s+(\d{{1,2}})\s+(\d{{4}})"
        rf"\s+(?:to|-)\s+"
        rf"{month_pattern}\s+(\d{{1,2}})\s+(\d{{4}})\b",
        re.IGNORECASE,
    )

    match = month_first_pattern.search(message)

    if match:
        start = _build_date(
            match.group(2),
            match.group(1),
            match.group(3),
        )
        end = _build_date(
            match.group(5),
            match.group(4),
            match.group(6),
        )

        return start, end

    # Single date:
    # on 15 October 2026
    single_date_pattern = re.compile(
        rf"\b(?:on|starting|start(?:ing)?\s+on)\s+"
        rf"(\d{{1,2}})\s+{month_pattern}\s+(\d{{4}})\b",
        re.IGNORECASE,
    )

    match = single_date_pattern.search(message)

    if match:
        start = _build_date(
            match.group(1),
            match.group(2),
            match.group(3),
        )

        return start, None

    return None, None


def _build_date(
    day: str,
    month: str,
    year: str,
) -> Optional[date]:
    """
    Safely construct a date from extracted components.
    """

    month_number = _month_number(month)

    if month_number is None:
        return None

    try:
        return date(
            int(year),
            month_number,
            int(day),
        )
    except ValueError:
        return None


def _month_number(month: str) -> Optional[int]:
    """
    Convert a month name or abbreviation into its number.
    """

    normalized = month.lower().rstrip(".")

    if normalized == "sept":
        normalized = "september"

    if len(normalized) >= 3 and normalized not in MONTHS:
        for full_month in MONTHS:
            if full_month.startswith(normalized):
                normalized = full_month
                break

    return MONTHS.get(normalized)


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
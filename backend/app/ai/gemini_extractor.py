import json
import os
from typing import Any

from dotenv import load_dotenv
from google import genai

from backend.app.schemas.requirements import TravelRequirement


load_dotenv()

GEMINI_MODEL = "gemini-3.6-flash"


def extract_intent_with_gemini(user_message: str) -> TravelRequirement:
    """
    Extract structured travel requirements from a natural-language
    travel request using Gemini.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=api_key)

    system_instruction = """
You are a travel-intent extraction system.

Extract structured travel requirements from the user's
natural-language travel request.

Return ONLY valid JSON.
Do not return markdown.
Do not return explanations.

Use exactly these fields:

{
  "origin": string or null,
  "destination": string,
  "start_date": string or null,
  "end_date": string or null,
  "duration_days": integer or null,
  "group_size": integer or null,
  "budget": {
    "amount": number,
    "currency": string
  } or null,
  "preferences": [],
  "activities": [],
  "transport_preferences": [],
  "dietary_preferences": [],
  "special_requirements": []
}

Rules:

1. Extract the starting city as origin.

2. Extract only the destination city or place as destination.

3. Extract the number of travel days when explicitly provided.

4. Calculate TOTAL travelers.
   Example: "with 4 friends" means user + 4 friends = 5 travelers.

5. Extract the numeric budget.
   If no currency is specified, assume INR.

6. Put accommodation and travel-style preferences
   in preferences.

7. Put requested activities in activities.

8. Only populate transport_preferences when the user
   explicitly mentions a preferred transport method.

9. Only populate dietary_preferences when the user
   explicitly mentions food or dietary requirements.

10. Put other explicit special requirements in
    special_requirements.

11. Use null when dates are not provided.

12. DO NOT INVENT INFORMATION.
    Missing information must be null or an empty list.

Return valid JSON only.
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=user_message,
        config={
            "system_instruction": system_instruction,
            "temperature": 0,
            "response_mime_type": "application/json",
        },
    )

    content = response.text

    if not content:
        raise ValueError("Gemini returned an empty response.")

    try:
        data: dict[str, Any] = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Gemini returned invalid JSON: {content}"
        ) from exc

    return TravelRequirement.model_validate(data)
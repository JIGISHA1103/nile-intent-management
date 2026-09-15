import json
import os
from typing import Any

from dotenv import load_dotenv
from groq import Groq

from backend.app.schemas.requirements import TravelRequirement


load_dotenv()


def extract_intent_with_groq(user_message: str) -> TravelRequirement:
    """
    Extract structured travel requirements from a natural-language
    travel request using Groq.
    """

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is not configured.")

    client = Groq(api_key=api_key)

    system_prompt = """
You are a travel-intent extraction system.

Your job is to extract structured travel requirements from
the user's natural-language travel request.

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

Extraction rules:

1. ORIGIN
   Extract the starting city.
   Example:
   "from Bangalore to Goa" -> origin = "Bangalore"

2. DESTINATION
   Extract only the destination city/place.
   Example:
   "from Bangalore to Goa" -> destination = "Goa"

3. DURATION
   Extract the number of travel days when explicitly provided.
   Example:
   "for 3 days" -> duration_days = 3

4. GROUP SIZE
   Calculate the TOTAL number of travelers.
   Example:
   "with 4 friends" means the user + 4 friends = 5 travelers.

5. BUDGET
   Extract the numeric budget.
   If no currency is specified, assume INR.
   Example:
   "budget around 40000" ->
   {
     "amount": 40000,
     "currency": "INR"
   }

6. PREFERENCES
   Put accommodation and travel-style preferences here.
   Examples:
   "beach resort" -> preferences
   "nightlife" -> preferences

7. ACTIVITIES
   Put activities the traveler wants to do here.
   Example:
   "water sports" -> activities

8. TRANSPORT PREFERENCES
   Only populate this when the user explicitly mentions
   a preferred transport method.

9. DIETARY PREFERENCES
   Only populate this when the user explicitly mentions
   food or dietary requirements.

10. SPECIAL REQUIREMENTS
    Put other explicit special requirements here.

11. DATES
    Use null when the user does not provide dates.

12. DO NOT INVENT INFORMATION.
    If information is missing, use null or an empty list.

Return valid JSON only.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("Groq returned an empty response.")

    try:
        data: dict[str, Any] = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Groq returned invalid JSON: {content}"
        ) from exc

    return TravelRequirement.model_validate(data)
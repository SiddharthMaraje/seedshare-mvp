# ai_utils.py

import json
import re
import streamlit as st
from google import genai


def get_gemini_client():
    api_key = st.secrets["GEMINI_API_KEY"]
    return genai.Client(api_key=api_key)


def generate_balcony_gardening_advice(
    location: str,
    balcony_size: str,
    month_or_season: str,
    gardening_experience: str,
    balcony_sunlight: str,
    main_interest: str,
):
    try:
        client = get_gemini_client()

        prompt = f"""
You are the AI Gardening Assistant for SeedShare Berlin.

User inputs:
- Location: {location}
- Balcony size: {balcony_size}
- Month or season: {month_or_season}
- Gardening experience: {gardening_experience}
- Balcony sunlight: {balcony_sunlight}
- Main interest / seed type: {main_interest}

Create a helpful, beginner-friendly recommendation.

Use these sections:
1. Best seed ideas for this user
2. Why these seeds fit
3. Growing setup
4. Watering and sunlight advice
5. Step-by-step action plan
6. Common mistakes to avoid
7. SeedShare tip
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        return {
            "advice": response.text,
            "prompt": prompt,
        }

    except Exception as e:
        return {
            "advice": f"""
AI recommendation could not be generated right now.

Technical error: {e}

Fallback advice:
For Berlin balconies, beginner-friendly options include basil, parsley, chives, mint, marigold, nasturtium, lettuce, radish, and cherry tomatoes.
""",
            "prompt": "Prompt generation failed.",
        }


def semantic_profile_matching(looking_for: str, candidate_profiles: list):
    """
    Uses Gemini to semantically rank possible SeedShare profile matches.
    Returns a list of dictionaries with:
    - profile_id
    - score
    - reason
    """

    if not looking_for or not candidate_profiles:
        return []

    try:
        client = get_gemini_client()

        prompt = f"""
You are a matching assistant for SeedShare Berlin.

The current user is looking for:
"{looking_for}"

Candidate profiles and listings:
{json.dumps(candidate_profiles, indent=2)}

Task:
Rank only genuinely relevant matches.

A match can be relevant if:
- the user is offering something related
- the user's listings contain relevant seeds or seedlings
- related plant types match semantically
- synonyms or categories match, for example basil = herb, marigold = flower, tomato = vegetable

Return ONLY valid JSON in this exact format:

[
  {{
    "profile_id": "profile id here",
    "score": 85,
    "reason": "Short reason why this is a good match"
  }}
]

Rules:
- score must be from 0 to 100
- only include profiles with score 50 or higher
- do not include the current user
- do not add markdown
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        raw_text = response.text.strip()

        json_match = re.search(r"\[.*\]", raw_text, re.DOTALL)

        if not json_match:
            return []

        return json.loads(json_match.group(0))

    except Exception:
        return []
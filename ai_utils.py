# ai_utils.py

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
    """
    Generates personalized gardening advice for SeedShare Berlin users.
    """

    try:
        client = get_gemini_client()

        prompt = f"""
You are the AI Gardening Assistant for SeedShare Berlin.

The user wants practical balcony gardening advice based on their situation.

User inputs:
- Location: {location}
- Balcony size: {balcony_size}
- Month or season: {month_or_season}
- Gardening experience: {gardening_experience}
- Balcony sunlight: {balcony_sunlight}
- Main interest / seed type: {main_interest}

Create a helpful, beginner-friendly recommendation.

Please structure the answer with these sections:

1. Best seed ideas for this user
Suggest suitable seeds or plants based on the inputs.

2. Why these seeds fit
Explain why they match the location, balcony size, season, experience level, and sunlight.

3. Growing setup
Give advice about pots, soil, spacing, drainage, and balcony placement.

4. Watering and sunlight advice
Give simple care instructions.

5. Step-by-step action plan
Give 5 practical steps the user can follow this week.

6. Common mistakes to avoid
Mention realistic beginner mistakes.

7. SeedShare tip
Suggest how the user could use SeedShare Berlin, for example by finding, sharing, or listing seeds.

Keep the tone friendly, practical, and suitable for urban balcony gardeners.
Avoid overly technical language.
If the season is not ideal for sowing, suggest alternatives such as indoor starting, planning, or choosing hardy plants.
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
For Berlin balconies, beginner-friendly options often include basil, parsley, chives, mint, marigold, nasturtium, lettuce, radish, and cherry tomatoes during the warmer growing season.
""",
            "prompt": "Prompt generation failed.",
        }
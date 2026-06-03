import json
import re
import streamlit as st
from groq import Groq


GROQ_MODEL = "llama-3.3-70b-versatile"


def get_groq_client():
    api_key = st.secrets["GROQ_API_KEY"]
    return Groq(api_key=api_key)


def generate_balcony_gardening_advice(
    location: str,
    balcony_size: str,
    month_or_season: str,
    gardening_experience: str,
    balcony_sunlight: str,
    main_interest: str,
):
    prompt = f"""
You are the AI Gardening Assistant for Sprouty, a seed-sharing platform for Berlin balcony gardeners.

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
7. Sprouty tip

Keep the answer practical, friendly, and suitable for a Weiterbildung MVP demo.
"""

    try:
        client = get_groq_client()

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a friendly balcony gardening assistant for Berlin users.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.7,
            max_tokens=900,
        )

        advice = response.choices[0].message.content

        return {
            "advice": advice,
            "prompt": prompt,
        }

    except Exception as e:
        return {
            "advice": f"""
Sprouty's AI helper is temporarily unavailable.

You can still try these beginner-friendly Berlin balcony options:

1. Best seed ideas for this user
- Basil
- Parsley
- Chives
- Mint
- Marigold
- Nasturtium
- Lettuce
- Radish
- Cherry tomatoes

2. Why these seeds fit
These are common beginner-friendly plants that can grow well in containers, windowsills, or balconies.

3. Growing setup
Use pots with drainage holes, fresh potting soil, and place the plants according to their sunlight needs.

4. Watering and sunlight advice
Water when the top layer of soil feels dry. Avoid overwatering.

5. Step-by-step action plan
Choose 2 or 3 easy plants, prepare small pots, sow seeds, water gently, and monitor growth weekly.

6. Common mistakes to avoid
Avoid too much water, overcrowding seeds, and placing sun-loving plants in deep shade.

7. Sprouty tip
Check Browse Seeds to find local seeds from other Berlin gardeners.

Technical note for developer:
{e}
""",
            "prompt": prompt,
        }


def semantic_profile_matching(looking_for: str, candidate_profiles: list):
    """
    Uses Groq to semantically rank possible Sprouty profile matches.
    Returns a list of dictionaries with:
    - profile_id
    - score
    - reason
    """

    if not looking_for or not candidate_profiles:
        return []

    prompt = f"""
You are a matching assistant for Sprouty, a seed-sharing platform for Berlin gardeners.

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

    try:
        client = get_groq_client()

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You return only valid JSON. Do not use markdown.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.2,
            max_tokens=800,
        )

        raw_text = response.choices[0].message.content.strip()

        json_match = re.search(r"\[.*\]", raw_text, re.DOTALL)

        if not json_match:
            return []

        return json.loads(json_match.group(0))

    except Exception:
        return []
import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime
from google import genai

from supabase import create_client

# ------------------------------------------------------------
# SeedShare / Community Seed Sharing MVP
# Streamlit + Gemini AI
# ------------------------------------------------------------

APP_TITLE = "SeedShare Berlin MVP"
DATA_FILE = Path("seed_listings.json")

# Optional old Ollama config kept for future fallback/local demo
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "deepseek-r1:7b"

# Gemini model
GEMINI_MODEL = "gemini-2.5-flash"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🌱",
    layout="wide"
)


# ------------------------------------------------------------
# Data helpers
# ------------------------------------------------------------

# def load_seed_data():
#     if DATA_FILE.exists():
#         try:
#             with open(DATA_FILE, "r", encoding="utf-8") as file:
#                 return json.load(file)
#         except json.JSONDecodeError:
#             return []
#     return []


# def save_seed_data(data):
#     with open(DATA_FILE, "w", encoding="utf-8") as file:
#         json.dump(data, file, indent=4, ensure_ascii=False)


# def add_seed_listing(listing):
#     data = load_seed_data()
#     data.append(listing)
#     save_seed_data(data)


# def get_sample_data():
#     return [
#         {
#             "seed_name": "Cherry Tomato Seeds",
#             "category": "Vegetable",
#             "district": "Neukölln",
#             "quantity": "Small handful",
#             "balcony_suitability": "Sunny balcony",
#             "experience_level": "Beginner-friendly",
#             "description": "Good for containers. Needs sunlight and regular watering.",
#             "owner_name": "Sofia",
#             "contact": "sofia@example.com",
#             "created_at": "Sample listing"
#         },
#         {
#             "seed_name": "Basil Seeds",
#             "category": "Herb",
#             "district": "Kreuzberg",
#             "quantity": "Half packet",
#             "balcony_suitability": "Sunny or partially sunny balcony",
#             "experience_level": "Beginner-friendly",
#             "description": "Great for pots and kitchen windows. Best started in warm conditions.",
#             "owner_name": "Jonas",
#             "contact": "jonas@example.com",
#             "created_at": "Sample listing"
#         },
#         {
#             "seed_name": "Marigold Seeds",
#             "category": "Flower",
#             "district": "Prenzlauer Berg",
#             "quantity": "Enough for 3-4 pots",
#             "balcony_suitability": "Sunny balcony",
#             "experience_level": "Beginner-friendly",
#             "description": "Bright flowers, useful companion plant, easy to grow.",
#             "owner_name": "Mina",
#             "contact": "mina@example.com",
#             "created_at": "Sample listing"
#         }
#     ]

# ------------------------------------------------------------
# Supabase data helpers
# ------------------------------------------------------------

SUPABASE_TABLE = "seed_listings"


def get_supabase_client():
    supabase_url = st.secrets.get("SUPABASE_URL")
    supabase_key = st.secrets.get("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        st.error(
            "Supabase is not configured. Please add SUPABASE_URL and SUPABASE_KEY "
            "to Streamlit secrets."
        )
        return None

    return create_client(supabase_url, supabase_key)


def load_seed_data():
    try:
        client = get_supabase_client()

        if client is None:
            return []

        response = (
            client
            .table(SUPABASE_TABLE)
            .select("*")
            .order("id", desc=True)
            .execute()
        )

        return response.data or []

    except Exception as error:
        st.error(f"Could not load seed listings from Supabase: {error}")
        return []


def save_seed_data(data):
    """
    Kept for compatibility.
    For Supabase, we normally add rows one by one using add_seed_listing().
    """
    try:
        client = get_supabase_client()

        if client is None:
            return

        for item in data:
            client.table(SUPABASE_TABLE).insert(item).execute()

    except Exception as error:
        st.error(f"Could not save seed listings to Supabase: {error}")


def add_seed_listing(listing):
    try:
        client = get_supabase_client()

        if client is None:
            return

        client.table(SUPABASE_TABLE).insert(listing).execute()

    except Exception as error:
        st.error(f"Could not add listing to Supabase: {error}")


# ------------------------------------------------------------
# AI helpers
# ------------------------------------------------------------

def get_gemini_api_key():
    """
    Reads the Gemini API key from Streamlit secrets first,
    then from the local environment variable.

    Recommended .streamlit/secrets.toml:
    GEMINI_API_KEY = "your-api-key"
    """
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

    return os.getenv("GEMINI_API_KEY")


def ask_gemini(prompt):
    api_key = get_gemini_api_key()

    if not api_key:
        return (
            "AI is not configured yet.\n\n"
            "Please add your Gemini API key as GEMINI_API_KEY in "
            ".streamlit/secrets.toml or as an environment variable."
        )

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        if hasattr(response, "text") and response.text:
            return response.text

        return "The AI service returned an empty response. Please try again."

    except Exception as error:
        return (
            "AI recommendation could not be generated right now.\n\n"
            f"Technical error: {error}\n\n"
            "Fallback advice: Check the seed packet for sowing season, sunlight needs, "
            "watering frequency, and expiry date. For Berlin balconies, herbs such as basil, "
            "parsley, chives, and easy flowers such as marigold are often good beginner options "
            "during the warmer growing season."
        )


def ask_deepseek(prompt):
    """
    Optional local Ollama fallback.
    Not used by default, but kept for demo flexibility.
    """
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "No response generated.")
    except requests.exceptions.ConnectionError:
        return (
            "Could not connect to Ollama. Please make sure Ollama is running and the model "
            f"'{OLLAMA_MODEL}' is available."
        )
    except requests.exceptions.Timeout:
        return "The AI response took too long. Try a shorter request."
    except Exception as error:
        return f"AI error: {error}"


def build_gardening_prompt(location, month, sunlight, balcony_size, experience, interest):
    return f"""
You are a friendly balcony gardening assistant for a community seed-sharing app in Berlin.

Give practical, beginner-friendly advice.
Keep the answer concise and structured.
Avoid medical, legal, or guaranteed claims.
Focus on seeds and seedlings suitable for balcony or container gardening.
Mention that local conditions and seed packet instructions should be checked.

User context:
- City/location: {location}
- Month/season: {month}
- Balcony sunlight: {sunlight}
- Balcony size: {balcony_size}
- Gardening experience: {experience}
- Plant interest: {interest}

Please provide:
1. 3 suitable seed or seedling recommendations
2. Why they fit this balcony situation
3. Simple care tips
4. One common mistake to avoid
5. A friendly note encouraging seed sharing with neighbours
"""


# ------------------------------------------------------------
# UI
# ------------------------------------------------------------

st.title("🌱 SeedShare Berlin MVP")
st.caption("A simple community seed and seedling sharing prototype for Berlin balcony growers.")

with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Go to",
        ["Home", "Browse Seeds", "Add Listing", "AI Gardening Assistant", "Project Notes"]
    )

    st.divider()
    st.caption("MVP scope")
    st.write("Seed listings + simple browsing + AI growing advice")


if page == "Home":
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Meet your gardening neighbour")
        st.write(
            "This MVP helps Berlin balcony gardeners share surplus seeds and seedlings with people nearby. "
            "Beginners can discover what grows well locally, while experienced growers can share both plants and knowledge."
        )

        st.markdown("""
        **Core idea:**  
        Many people buy seed packets but only use a small amount. Instead of wasting the rest, they can share seeds with neighbours.

        **MVP features:**
        - Add a seed or seedling listing
        - Browse available listings by district and category
        - Get AI-supported balcony gardening tips
        """)

    with col2:
        st.info(
            "Demo flow:\n\n"
            "1. Browse available seeds\n"
            "2. Add a test listing\n"
            "3. Ask the AI assistant what to grow\n"
            "4. Discuss how this supports community sharing"
        )


elif page == "Browse Seeds":
    st.subheader("Browse available seeds and seedlings")

    data = load_seed_data()
    if not data:
        st.warning("No saved listings yet. Showing sample listings for demo purposes.")
        data = get_sample_data()

    df = pd.DataFrame(data)

    required_columns = ["district", "category", "seed_name"]
    for column in required_columns:
        if column not in df.columns:
            df[column] = ""

    col1, col2, col3 = st.columns(3)

    with col1:
        district_filter = st.selectbox(
            "District",
            ["All"] + sorted(df["district"].dropna().unique().tolist())
        )

    with col2:
        category_filter = st.selectbox(
            "Category",
            ["All"] + sorted(df["category"].dropna().unique().tolist())
        )

    with col3:
        search_term = st.text_input("Search by seed name")

    filtered_df = df.copy()

    if district_filter != "All":
        filtered_df = filtered_df[filtered_df["district"] == district_filter]

    if category_filter != "All":
        filtered_df = filtered_df[filtered_df["category"] == category_filter]

    if search_term:
        filtered_df = filtered_df[
            filtered_df["seed_name"].str.contains(search_term, case=False, na=False)
        ]

    if filtered_df.empty:
        st.info("No listings match your filters.")
    else:
        for index, row in filtered_df.iterrows():
            with st.container(border=True):
                col_a, col_b = st.columns([3, 1])

                with col_a:
                    st.markdown(f"### {row.get('seed_name', 'Unnamed listing')}")
                    st.write(row.get("description", "No description provided."))
                    st.caption(
                        f"Category: {row.get('category', 'N/A')} | "
                        f"District: {row.get('district', 'N/A')} | "
                        f"Quantity: {row.get('quantity', 'N/A')}"
                    )
                    st.caption(
                        f"Balcony fit: {row.get('balcony_suitability', 'N/A')} | "
                        f"Level: {row.get('experience_level', 'N/A')}"
                    )

                with col_b:
                    st.write(f"Shared by: **{row.get('owner_name', 'Neighbour')}**")
                    button_key = f"request_{index}_{row.get('seed_name', 'seed')}"
                    if st.button(f"Request {row.get('seed_name', 'seed')}", key=button_key):
                        st.success(
                            f"Request simulated. In a real app, this would contact "
                            f"{row.get('owner_name', 'the owner')}."
                        )
                        st.write(f"Contact: {row.get('contact', 'Not provided')}")


elif page == "Add Listing":
    st.subheader("Add a seed or seedling listing")
    st.write("Use this form to share surplus seeds or seedlings with nearby balcony gardeners.")

    with st.form("add_seed_form"):
        col1, col2 = st.columns(2)

        with col1:
            seed_name = st.text_input("Seed or seedling name", placeholder="e.g., Basil seeds")
            category = st.selectbox("Category", ["Herb", "Vegetable", "Flower", "Other"])
            district = st.selectbox(
                "Berlin district / Kiez",
                [
                    "Neukölln", "Kreuzberg", "Friedrichshain", "Prenzlauer Berg",
                    "Mitte", "Wedding", "Charlottenburg", "Tempelhof", "Other"
                ]
            )
            quantity = st.text_input("Quantity", placeholder="e.g., Half packet, 5 seedlings")

        with col2:
            balcony_suitability = st.selectbox(
                "Best balcony condition",
                ["Sunny balcony", "Partially sunny balcony", "Shaded balcony", "Indoor/window", "Not sure"]
            )
            experience_level = st.selectbox(
                "Suitable for",
                ["Beginner-friendly", "Some experience needed", "Experienced growers"]
            )
            owner_name = st.text_input("Your name or nickname", placeholder="e.g., Sofia")
            contact = st.text_input("Contact", placeholder="Email or preferred contact")

        description = st.text_area(
            "Short description / growing tip",
            placeholder="e.g., Grows well in pots, needs regular watering."
        )

        submitted = st.form_submit_button("Add listing")

        if submitted:
            if not seed_name or not owner_name:
                st.error("Please enter at least a seed name and your name/nickname.")
            else:
                listing = {
                    "seed_name": seed_name,
                    "category": category,
                    "district": district,
                    "quantity": quantity,
                    "balcony_suitability": balcony_suitability,
                    "experience_level": experience_level,
                    "description": description,
                    "owner_name": owner_name,
                    "contact": contact,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                }

                add_seed_listing(listing)
                st.success("Listing added successfully. You can now see it under Browse Seeds.")


elif page == "AI Gardening Assistant":
    st.subheader("AI Balcony Gardening Assistant")
    st.write(
        "Ask for practical growing suggestions based on Berlin balcony conditions. "
        "This version uses Gemini via the current Google GenAI SDK."
    )

    col1, col2 = st.columns(2)

    with col1:
        location = st.text_input("Location", value="Berlin")
        month = st.selectbox(
            "Month / season",
            [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ],
            index=4
        )
        sunlight = st.selectbox(
            "Balcony sunlight",
            ["Full sun", "Partial sun", "Mostly shade", "Not sure"]
        )

    with col2:
        balcony_size = st.selectbox(
            "Balcony size",
            ["Tiny balcony", "Small balcony", "Medium balcony", "Large balcony", "Windowsill only"]
        )
        experience = st.selectbox(
            "Gardening experience",
            ["Complete beginner", "Some experience", "Experienced gardener"]
        )
        interest = st.selectbox(
            "Main interest",
            ["Herbs", "Vegetables", "Flowers", "Easy beginner plants", "Anything suitable"]
        )

    if st.button("Get AI growing advice"):
        prompt = build_gardening_prompt(
            location,
            month,
            sunlight,
            balcony_size,
            experience,
            interest
        )

        with st.spinner("Generating AI growing advice..."):
            ai_response = ask_gemini(prompt)

        st.markdown("### AI recommendation")
        st.write(ai_response)

        with st.expander("Show prompt used"):
            st.code(prompt)


elif page == "Project Notes":
    st.subheader("Project management notes")

    st.markdown("""
    ### MVP goal
    Validate whether a simple seed-sharing web app can make Berlin balcony gardening communities more visible and easier to access.

    ### In scope for 3-week module project
    - Seed/seedling listing form
    - Browse and filter listings
    - Simulated request action
    - AI-supported gardening advice
    - Local JSON-based storage

    ### Out of scope for MVP
    - Real user accounts
    - Payment systems
    - Live chat
    - Advanced maps/geolocation
    - Complex moderation workflows
    - Production-grade security

    ### AI use in the project
    - Supports beginners with practical growing advice
    - Reduces knowledge barrier for first-time balcony gardeners
    - Makes the project more innovative while keeping the technical scope feasible

    ### Technical risk note
    External AI APIs can change model names, SDKs, or supported endpoints.  
    This MVP reduces risk by using a current model name, checking for missing API keys, and showing fallback guidance if AI generation fails.

    ### Suggested success criteria
    - A teammate can add a listing in under 2 minutes
    - A teammate can find a relevant seed listing using filters
    - A beginner receives understandable AI growing guidance
    - The demo clearly communicates sustainability and community value
    """)
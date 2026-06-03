import streamlit as st
from streamlit_folium import st_folium

from auth_utils import (
    init_auth_state,
    sign_up,
    sign_in,
    sign_out,
    get_current_user,
    is_logged_in,
)

from profile_utils import (
    get_profile,
    upsert_profile,
    get_all_profiles,
)

from listing_utils import (
    get_all_listings,
    get_my_listings,
    create_listing,
    delete_listing,
    update_listing_status,
)

from rating_utils import (
    get_rating_summary,
    get_my_rating_for_user,
    upsert_profile_rating,
)

from ai_utils import generate_balcony_gardening_advice
from map_utils import create_seed_map
from match_utils import find_profile_matches


st.set_page_config(
    page_title="Sprouty | Share seeds, grow together",
    page_icon="🌱",
    layout="wide",
)


init_auth_state()


# -----------------------------
# Global Design CSS
# -----------------------------

def inject_design():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Inter:wght@400;500;600;700;800&display=swap');

        :root {
            --forest: #254D17;
            --leaf: #6FAE4F;
            --sage: #E8E6DA;
            --cream: #F8F6F1;
            --cream2: #F1EEE5;
            --text: #2A2A2A;
            --muted: #6B6B5F;
            --border: rgba(37, 77, 23, 0.16);
            --shadow: 0 16px 40px rgba(37, 77, 23, 0.10);
        }

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background: var(--cream);
            color: var(--text);
        }

        .block-container {
            max-width: 1180px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }

        div[role="radiogroup"] {
            justify-content: center;
            gap: 0.25rem;
            margin-bottom: 1rem;
        }

        div[role="radiogroup"] label {
            font-size: 0.85rem;
            font-weight: 700;
        }

        .stRadio div[role="radiogroup"] {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 0.55rem;
            margin-top: 0.35rem;
            margin-bottom: 1.35rem;
        }

        .stRadio div[role="radiogroup"] label {
            background: rgba(255, 255, 255, 0.76);
            border: 1px solid var(--border);
            border-radius: 999px;
            padding: 0.25rem 0.65rem;
            box-shadow: 0 8px 20px rgba(37, 77, 23, 0.06);
        }

        h1, h2, h3 {
            font-family: 'Cormorant Garamond', serif;
            color: var(--forest);
            letter-spacing: -0.03em;
        }

        h1 {
            font-size: 3.2rem !important;
        }

        h2 {
            font-size: 2.25rem !important;
        }

        section[data-testid="stSidebar"] {
            background: var(--cream2);
            border-right: 1px solid var(--border);
        }

        section[data-testid="stSidebar"] .stButton > button {
            width: 100%;
            justify-content: flex-start;
            text-align: left;
        }

        div.stButton > button,
        div.stFormSubmitButton > button {
            background: var(--forest);
            color: white;
            border: 0;
            border-radius: 999px;
            padding: 0.7rem 1.25rem;
            font-weight: 800;
            box-shadow: 0 10px 24px rgba(37, 77, 23, 0.18);
        }

        div.stButton > button:hover,
        div.stFormSubmitButton > button:hover {
            background: #1E3E13;
            color: white;
            border: 0;
        }

        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.76);
            border: 1px solid var(--border);
            border-radius: 22px;
            padding: 1rem;
            box-shadow: var(--shadow);
        }

        .hero {
            background:
                radial-gradient(circle at 78% 24%, rgba(111, 174, 79, 0.38), transparent 28%),
                linear-gradient(135deg, #254D17 0%, #17350F 100%);
            border-radius: 34px;
            padding: 3rem;
            min-height: 470px;
            color: white;
            box-shadow: var(--shadow);
            position: relative;
            overflow: hidden;
            margin-bottom: 1.5rem;
        }

        .hero h1 {
            color: white !important;
            font-size: 4.8rem !important;
            line-height: 0.95 !important;
            margin-bottom: 1rem;
            max-width: 680px;
        }

        .hero h1 em {
            color: #DCEBD0;
            font-style: italic;
        }

        .hero p {
            color: #F1F6EA;
            font-size: 1.15rem;
            line-height: 1.65;
            max-width: 560px;
        }

        .hero-kicker {
            display: inline-flex;
            background: rgba(255,255,255,0.13);
            border: 1px solid rgba(255,255,255,0.22);
            border-radius: 999px;
            padding: 0.45rem 0.85rem;
            font-weight: 800;
            color: #F8F6F1;
            margin-bottom: 1.1rem;
        }

        .hero-buttons {
            display: flex;
            gap: 0.8rem;
            flex-wrap: wrap;
            margin-top: 1.4rem;
        }

        .cta-primary,
        .cta-secondary {
            display: inline-flex;
            text-decoration: none !important;
            border-radius: 999px;
            padding: 0.85rem 1.2rem;
            font-weight: 900;
        }

        .cta-primary {
            background: #F8F6F1;
            color: var(--forest) !important;
        }

        .cta-secondary {
            background: transparent;
            color: #F8F6F1 !important;
            border: 1px solid rgba(255,255,255,0.45);
        }

        .floating-card {
            background: rgba(248, 246, 241, 0.96);
            border-radius: 26px;
            padding: 1.15rem;
            border: 1px solid rgba(255,255,255,0.45);
            box-shadow: 0 18px 40px rgba(0,0,0,0.18);
            color: var(--text);
            position: absolute;
            width: 260px;
        }

        .floating-card h3 {
            margin: 0.2rem 0;
            font-size: 1.45rem !important;
        }

        .float-one {
            right: 3rem;
            top: 4rem;
            transform: rotate(2deg);
        }

        .float-two {
            right: 9rem;
            bottom: 3rem;
            transform: rotate(-3deg);
        }

        .page-header {
            background: linear-gradient(135deg, #E8E6DA 0%, #F8F6F1 100%);
            border: 1px solid var(--border);
            border-radius: 28px;
            padding: 2rem;
            margin-bottom: 1.4rem;
            box-shadow: var(--shadow);
        }

        .page-header p {
            color: var(--muted);
            font-size: 1.05rem;
            max-width: 720px;
        }

        .section-card,
        .seed-card,
        .profile-card {
            background: rgba(255,255,255,0.80);
            border: 1px solid var(--border);
            border-radius: 26px;
            padding: 1.25rem;
            box-shadow: var(--shadow);
            margin-bottom: 1rem;
        }

        .seed-card h3,
        .profile-card h3 {
            margin-bottom: 0.3rem;
            font-size: 1.55rem !important;
        }

        .mini-title {
            font-weight: 900;
            color: var(--forest);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-size: 0.76rem;
        }

        .seed-meta {
            color: var(--muted);
            font-weight: 700;
            font-size: 0.9rem;
            margin-bottom: 0.8rem;
        }

        .badge-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            margin-top: 0.75rem;
        }

        .badge {
            background: #E8E6DA;
            color: var(--forest);
            padding: 0.35rem 0.6rem;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 800;
        }

        .muted {
            color: var(--muted);
        }

        .avatar {
            width: 58px;
            height: 58px;
            border-radius: 50%;
            background: linear-gradient(135deg, #6FAE4F, #254D17);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 900;
            font-size: 1.35rem;
            margin-bottom: 0.8rem;
        }

        .empty-state {
            text-align: center;
            padding: 3rem 1.5rem;
            background: rgba(255,255,255,0.72);
            border: 1px dashed rgba(37,77,23,0.28);
            border-radius: 30px;
            margin-top: 1rem;
        }

        .big-emoji {
            font-size: 3.5rem;
            margin-bottom: 0.5rem;
        }

        @media (max-width: 900px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
                padding-top: 1rem;
            }

            .hero {
                padding: 1.6rem;
                min-height: auto;
                border-radius: 28px;
            }

            .hero h1 {
                font-size: 3rem !important;
            }

            .hero p {
                font-size: 1rem;
                line-height: 1.55;
            }

            .page-header {
                padding: 1.5rem;
                border-radius: 26px;
            }

            .page-header h1 {
                font-size: 2.6rem !important;
            }

            .float-one,
            .float-two {
                display: none;
            }

            .stRadio div[role="radiogroup"] {
                flex-wrap: nowrap;
                justify-content: flex-start;
                overflow-x: auto;
                padding-bottom: 0.5rem;
                margin-top: 0.6rem;
                margin-bottom: 1.1rem;
            }

            .stRadio div[role="radiogroup"] label {
                min-width: max-content;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_design()


# -----------------------------
# Helper UI Components
# -----------------------------

def page_header(title, subtitle):
    st.markdown(
        f"""
        <div class="page-header">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def listing_card(listing):
    status = listing.get("status", "Available")

    status_badge = "🌱 Available" if status == "Available" else "✓ Exchanged"

    st.markdown(
        f"""
        <div class="seed-card">
            <div class="mini-title">{listing.get('category', 'Seed')}</div>
            <h3>🌿 {listing.get('seed_name', 'Unnamed seed or seedling')}</h3>
            <div class="seed-meta">
                {listing.get('berlin_district', 'Berlin')} · {status_badge}
            </div>
            <p>{listing.get('description', '')}</p>
            <div class="badge-row">
                <span class="badge">☀ {listing.get('best_balcony_condition', 'Not specified')}</span>
                <span class="badge">🌱 {listing.get('suitable_for', 'Not specified')}</span>
            </div>
            <br>
            <p><b>Quantity:</b> {listing.get('quantity', 'Not specified')}</p>
            <p><b>Shared by:</b> {listing.get('owner_name', 'Not specified')}</p>
            <p><b>Contact:</b> {listing.get('contact', 'Not specified')}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def profile_card(profile, rating_summary=None):
    display_name = profile.get("display_name") or profile.get("username", "Unnamed user")
    initials = "".join([part[0] for part in display_name.split()[:2]]).upper() or "🌱"

    if rating_summary and rating_summary["count"] > 0:
        rating_text = f"⭐ {rating_summary['average']}/5 from {rating_summary['count']} rating(s)"
    else:
        rating_text = "No ratings yet"

    st.markdown(
        f"""
        <div class="profile-card">
            <div class="avatar">{initials}</div>
            <h3>{display_name}</h3>
            <div class="seed-meta">
                {profile.get('gardening_level', 'Gardener')} · {profile.get('neighbourhood', 'Berlin')}
            </div>
            <p>{profile.get('short_bio', '')}</p>
            <div class="badge-row">
                <span class="badge">{rating_text}</span>
                <span class="badge">🌱 Seed sharer</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# Page navigation state
# -----------------------------

PAGES = [
    "Home",
    "Browse Seeds",
    "Seed Map",
    "Add Listing",
    "AI Assistant",
    "Community",
    "My Profile",
    "My Listings",
]

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

if st.session_state.current_page not in PAGES:
    st.session_state.current_page = "Home"


def go_to_page(page_name: str):
    st.session_state.current_page = page_name
    st.rerun()


# -----------------------------
# Sidebar authentication and navigation
# -----------------------------

with st.sidebar:
    st.header("Account")

    if is_logged_in():
        user = get_current_user()
        st.success(f"Logged in as {user.email}")

        if st.button("Log out", use_container_width=True):
            sign_out()
            st.rerun()

    else:
        auth_tab = st.radio(
            "Choose action",
            ["Login", "Sign up"],
        )

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if auth_tab == "Login":
            if st.button("Login", use_container_width=True):
                try:
                    response = sign_in(email, password)

                    if response.user:
                        st.success("Login successful.")
                        st.rerun()
                    else:
                        st.error("Login failed.")

                except Exception as e:
                    st.error("Login failed.")
                    st.caption(str(e))

        if auth_tab == "Sign up":
            if st.button("Create account", use_container_width=True):
                try:
                    response = sign_up(email, password)

                    if response.user:
                        st.success(
                            "Account created. Please log in. If email confirmation is enabled, check your inbox."
                        )
                    else:
                        st.error("Sign-up failed.")

                except Exception as e:
                    st.error("Sign-up failed.")
                    st.caption(str(e))

    st.divider()
    st.markdown("### Pages")

    page_icons = {
        "Home": "🏠",
        "Browse Seeds": "🌿",
        "Seed Map": "🗺️",
        "Add Listing": "＋",
        "AI Assistant": "🪴",
        "Community": "👥",
        "My Profile": "👤",
        "My Listings": "📦",
    }

    for page_name in PAGES:
        label = f"{page_icons.get(page_name, '•')} {page_name}"
        if st.button(label, key=f"sidebar_nav_{page_name}", use_container_width=True):
            go_to_page(page_name)


# -----------------------------
# Session state
# -----------------------------

if "selected_profile_id" not in st.session_state:
    st.session_state.selected_profile_id = None


# -----------------------------
# Navigation helper
# -----------------------------

def render_navigation():
    # Navigation is now handled by clickable buttons in the sidebar.
    return


# -----------------------------
# Home
# -----------------------------

if st.session_state.current_page == "Home":
    listings = get_all_listings()
    profiles = get_all_profiles()

    available_count = len(
        [listing for listing in listings if listing.get("status", "Available") == "Available"]
    )

    st.markdown(
        """
<div class="hero">
    <div class="hero-kicker">🌱 Sprouty · SeedShare Berlin</div>
    <h1>Share seeds,<br><em>grow together.</em></h1>
    <p>
        Discover, exchange, and grow seeds with fellow Berlin urban gardeners.<br>
        Every balcony can become a garden.
    </p>
</div>
        """,
        unsafe_allow_html=True,
    )

    render_navigation()

    hero_col1, hero_col2, hero_col3 = st.columns([1, 1, 4])

    with hero_col1:
        if st.button("🌿 Browse Seeds", key="home_go_browse"):
            st.session_state.current_page = "Browse Seeds"
            st.rerun()

    with hero_col2:
        if st.button("＋ Add Listing", key="home_go_add"):
            st.session_state.current_page = "Add Listing"
            st.rerun()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Listings", len(listings))

    with col2:
        st.metric("Available Seeds", available_count)

    with col3:
        st.metric("Active Gardeners", len(profiles))

    st.markdown("## How Sprouty works")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
            <div class="section-card">
                <h3>1. Find seeds</h3>
                <p class="muted">Browse and filter seed listings shared by local Berlin gardeners.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
            <div class="section-card">
                <h3>2. Connect locally</h3>
                <p class="muted">Use profiles, ratings, and contact details to arrange a friendly exchange.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            """
            <div class="section-card">
                <h3>3. Grow together</h3>
                <p class="muted">Share seeds, mark exchanges, and get AI gardening advice for your balcony.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# -----------------------------
# Browse Seeds
# -----------------------------

if st.session_state.current_page == "Browse Seeds":
    render_navigation()
    st.markdown('<div id="browse-seeds"></div>', unsafe_allow_html=True)
    page_header(
        "Browse Seeds",
        "Find seeds and seedlings shared by gardeners across Berlin.",
    )

    listings = get_all_listings()

    if not listings:
        st.markdown(
            """
            <div class="empty-state">
                <div class="big-emoji">🌱</div>
                <h2>No seed listings yet</h2>
                <p class="muted">Be the first person to share seeds with the Sprouty community.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:
        st.markdown("### Search and filter")

        col1, col2, col3 = st.columns(3)

        with col1:
            search_text = st.text_input(
                "Search by seed name, description, or owner",
                placeholder="e.g. basil, tomato, balcony, Anna",
            )

        with col2:
            category_filter = st.selectbox(
                "Filter by category",
                [
                    "All",
                    "Herb",
                    "Vegetable",
                    "Flower",
                    "Fruit",
                    "Pollinator-friendly",
                    "Other",
                ],
            )

        with col3:
            district_filter = st.selectbox(
                "Filter by Berlin district",
                [
                    "All",
                    "Mitte",
                    "Friedrichshain-Kreuzberg",
                    "Pankow",
                    "Charlottenburg-Wilmersdorf",
                    "Spandau",
                    "Steglitz-Zehlendorf",
                    "Tempelhof-Schöneberg",
                    "Neukölln",
                    "Treptow-Köpenick",
                    "Marzahn-Hellersdorf",
                    "Lichtenberg",
                    "Reinickendorf",
                    "Other / Not specified",
                ],
            )

        col4, col5, col6 = st.columns(3)

        with col4:
            balcony_filter = st.selectbox(
                "Filter by balcony condition",
                [
                    "All",
                    "Full sun",
                    "Partial sun",
                    "Mostly shade",
                    "Indoor / windowsill",
                    "Flexible / easy-going",
                ],
            )

        with col5:
            suitable_filter = st.selectbox(
                "Filter by suitability",
                [
                    "All",
                    "Complete beginners",
                    "Balcony gardeners",
                    "Families / children",
                    "Pollinators / bees",
                    "Experienced gardeners",
                    "Small spaces",
                ],
            )

        with col6:
            status_filter = st.selectbox(
                "Filter by status",
                ["Available only", "Exchanged only", "All"],
            )

        filtered_listings = listings

        if search_text:
            search_lower = search_text.lower()

            filtered_listings = [
                listing for listing in filtered_listings
                if search_lower in str(listing.get("seed_name", "")).lower()
                or search_lower in str(listing.get("description", "")).lower()
                or search_lower in str(listing.get("owner_name", "")).lower()
                or search_lower in str(listing.get("contact", "")).lower()
            ]

        if category_filter != "All":
            filtered_listings = [
                listing for listing in filtered_listings
                if listing.get("category") == category_filter
            ]

        if district_filter != "All":
            filtered_listings = [
                listing for listing in filtered_listings
                if listing.get("berlin_district") == district_filter
            ]

        if balcony_filter != "All":
            filtered_listings = [
                listing for listing in filtered_listings
                if listing.get("best_balcony_condition") == balcony_filter
            ]

        if suitable_filter != "All":
            filtered_listings = [
                listing for listing in filtered_listings
                if listing.get("suitable_for") == suitable_filter
            ]

        if status_filter == "Available only":
            filtered_listings = [
                listing for listing in filtered_listings
                if listing.get("status", "Available") == "Available"
            ]

        elif status_filter == "Exchanged only":
            filtered_listings = [
                listing for listing in filtered_listings
                if listing.get("status", "Available") == "Exchanged"
            ]

        st.write(f"Showing **{len(filtered_listings)}** of **{len(listings)}** listings.")

        if not filtered_listings:
            st.warning("No listings match your search filters.")

        else:
            cols = st.columns(3)

            for index, listing in enumerate(filtered_listings):
                with cols[index % 3]:
                    listing_card(listing)

                    owner_id = listing.get("user_id")

                    if owner_id:
                        owner_rating = get_rating_summary(owner_id)

                        if owner_rating["count"] > 0:
                            st.caption(
                                f"Owner rating: ⭐ {owner_rating['average']}/5 from {owner_rating['count']} rating(s)"
                            )

                        if st.button("View owner profile", key=f"browse_owner_{listing.get('id')}"):
                            st.session_state.selected_profile_id = owner_id
                            st.info("Open the Community tab to view the selected profile.")


# -----------------------------
# Seed Map
# -----------------------------

if st.session_state.current_page == "Seed Map":
    render_navigation()
    page_header(
        "Seed Map",
        "Discover available seeds near you across Berlin. Markers use approximate district locations, not exact addresses.",
    )

    listings = get_all_listings()

    map_listings = [
        listing for listing in listings
        if listing.get("status", "Available") == "Available"
    ]

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Available Listings", len(map_listings))

    with c2:
        districts = len(set([listing.get("berlin_district", "Other") for listing in map_listings]))
        st.metric("Berlin Districts", districts)

    with c3:
        owners = len(set([listing.get("owner_name", "Unknown") for listing in map_listings]))
        st.metric("Seed Sharers", owners)

    if not map_listings:
        st.info("No available seed listings for the map yet.")

    else:
        seed_map = create_seed_map(map_listings)

        st_folium(
            seed_map,
            width=1000,
            height=600,
        )

        st.caption(
            "Privacy note: map markers show approximate Berlin district locations, not exact pickup addresses."
        )


# -----------------------------
# Add Listing
# -----------------------------

if st.session_state.current_page == "Add Listing":
    render_navigation()
    st.markdown('<div id="share-your-seeds"></div>', unsafe_allow_html=True)
    page_header(
        "Share Your Seeds",
        "Help another Berlin gardener start growing.",
    )

    if not is_logged_in():
        st.warning("Please log in to add a seed listing.")

    else:
        user = get_current_user()

        with st.form("add_listing_form"):
            st.markdown("### About the seed")

            seed_name = st.text_input(
                "Seed or seedling name",
                placeholder="e.g. Basil seedlings, tomato seeds, marigold seeds",
            )

            col1, col2 = st.columns(2)

            with col1:
                category = st.selectbox(
                    "Category",
                    [
                        "Herb",
                        "Vegetable",
                        "Flower",
                        "Fruit",
                        "Pollinator-friendly",
                        "Other",
                    ],
                )

                quantity = st.text_input(
                    "Quantity",
                    placeholder="e.g. 10 seeds, 3 seedlings, one small packet",
                )

                berlin_district = st.selectbox(
                    "Berlin District",
                    [
                        "Mitte",
                        "Friedrichshain-Kreuzberg",
                        "Pankow",
                        "Charlottenburg-Wilmersdorf",
                        "Spandau",
                        "Steglitz-Zehlendorf",
                        "Tempelhof-Schöneberg",
                        "Neukölln",
                        "Treptow-Köpenick",
                        "Marzahn-Hellersdorf",
                        "Lichtenberg",
                        "Reinickendorf",
                        "Other / Not specified",
                    ],
                )

            with col2:
                best_balcony_condition = st.selectbox(
                    "Best balcony condition",
                    [
                        "Full sun",
                        "Partial sun",
                        "Mostly shade",
                        "Indoor / windowsill",
                        "Flexible / easy-going",
                    ],
                )

                suitable_for = st.selectbox(
                    "Suitable for",
                    [
                        "Complete beginners",
                        "Balcony gardeners",
                        "Families / children",
                        "Pollinators / bees",
                        "Experienced gardeners",
                        "Small spaces",
                    ],
                )

                owner_name = st.text_input(
                    "Your name or nickname",
                    placeholder="e.g. Anna, GreenBalcony92",
                )

            contact = st.text_input(
                "Contact",
                placeholder="e.g. email, Telegram, phone, or preferred contact method",
            )

            description = st.text_area(
                "Short description / growing tip",
                placeholder="e.g. Easy basil seedlings, good for sunny balconies. Water regularly and harvest often.",
            )

            submitted_listing = st.form_submit_button("Publish Listing 🌱")

            if submitted_listing:
                if not seed_name:
                    st.error("Please enter a seed or seedling name.")
                elif not owner_name:
                    st.error("Please enter your name or nickname.")
                elif not contact:
                    st.error("Please enter a contact method.")
                else:
                    try:
                        create_listing(
                            seed_name=seed_name,
                            best_balcony_condition=best_balcony_condition,
                            category=category,
                            suitable_for=suitable_for,
                            berlin_district=berlin_district,
                            owner_name=owner_name,
                            quantity=quantity,
                            contact=contact,
                            description=description,
                            user_id=user.id,
                        )

                        st.success("Listing created successfully.")
                        st.rerun()

                    except Exception as e:
                        st.error("Could not create listing.")
                        st.caption(str(e))


# -----------------------------
# AI Gardening Assistant
# -----------------------------

if st.session_state.current_page == "AI Assistant":
    render_navigation()
    page_header(
        "AI Gardening Assistant",
        "Get personalized growing advice based on your balcony, season, sunlight, and gardening experience.",
    )

    col_left, col_right = st.columns([1.15, 0.85])

    with col_left:
        with st.form("ai_gardening_form"):
            ai_location = st.text_input(
                "Location",
                value="Berlin",
                placeholder="e.g. Berlin, Neukölln, Prenzlauer Berg",
            )

            col1, col2 = st.columns(2)

            with col1:
                balcony_size = st.selectbox(
                    "Balcony size",
                    [
                        "Small windowsill",
                        "Small balcony",
                        "Medium balcony",
                        "Large balcony",
                        "Shared courtyard",
                        "No balcony / indoor only",
                    ],
                )

                month_or_season = st.selectbox(
                    "Month or season",
                    [
                        "January / Winter",
                        "February / Winter",
                        "March / Early spring",
                        "April / Spring",
                        "May / Late spring",
                        "June / Early summer",
                        "July / Summer",
                        "August / Late summer",
                        "September / Early autumn",
                        "October / Autumn",
                        "November / Late autumn",
                        "December / Winter",
                    ],
                    index=4,
                )

            with col2:
                gardening_experience = st.selectbox(
                    "Gardening experience",
                    [
                        "Complete beginner",
                        "Beginner",
                        "Some experience",
                        "Experienced gardener",
                    ],
                )

                balcony_sunlight = st.selectbox(
                    "Balcony sunlight",
                    [
                        "Full sun, 6+ hours",
                        "Partial sun, 3–6 hours",
                        "Mostly shade, less than 3 hours",
                        "Not sure",
                    ],
                )

            main_interest = st.selectbox(
                "Main interest / seed type",
                [
                    "Herbs",
                    "Flowers",
                    "Vegetables",
                    "Balcony-friendly fruits",
                    "Pollinator-friendly plants",
                    "Easy beginner plants",
                    "Fast-growing seeds",
                    "Child-friendly gardening",
                    "Not sure, suggest for me",
                ],
            )

            submitted_ai = st.form_submit_button("Generate AI growing advice 🌱")

    with col_right:
        st.markdown(
            """
            <div class="section-card">
                <div class="big-emoji">🪴</div>
                <h2>Your balcony plant helper</h2>
                <p class="muted">
                    Sprouty can suggest beginner-friendly seeds, growing conditions,
                    and practical balcony tips for Berlin.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if submitted_ai:
        with st.spinner("Generating personalized gardening advice..."):
            result = generate_balcony_gardening_advice(
                location=ai_location,
                balcony_size=balcony_size,
                month_or_season=month_or_season,
                gardening_experience=gardening_experience,
                balcony_sunlight=balcony_sunlight,
                main_interest=main_interest,
            )

            advice = result["advice"]
            prompt = result["prompt"]

        with st.expander("Your gardening profile for this recommendation"):
            st.write(f"**Location:** {ai_location}")
            st.write(f"**Balcony size:** {balcony_size}")
            st.write(f"**Month or season:** {month_or_season}")
            st.write(f"**Experience:** {gardening_experience}")
            st.write(f"**Sunlight:** {balcony_sunlight}")
            st.write(f"**Main interest:** {main_interest}")

        st.markdown("### Personalized Growing Advice")
        st.markdown(
            f"""
            <div class="section-card">
                {advice}
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("View AI Prompt Used"):
            st.code(prompt, language="text")


# -----------------------------
# Community Profiles
# -----------------------------

if st.session_state.current_page == "Community":
    render_navigation()
    page_header(
        "Community Gardeners",
        "Browse Sprouty users, view public profiles, and rate community interactions.",
    )

    if not is_logged_in():
        st.warning("Please log in to view Community Profiles.")

    else:
        profiles = get_all_profiles()

        if not profiles:
            st.info("No community profiles yet.")

        else:
            search_profile = st.text_input(
                "Search profiles",
                placeholder="Search by name, username, neighbourhood, bio, or gardening level",
            )

            filtered_profiles = profiles

            if search_profile:
                search_lower = search_profile.lower()

                filtered_profiles = [
                    profile for profile in filtered_profiles
                    if search_lower in str(profile.get("display_name", "")).lower()
                    or search_lower in str(profile.get("username", "")).lower()
                    or search_lower in str(profile.get("neighbourhood", "")).lower()
                    or search_lower in str(profile.get("short_bio", "")).lower()
                    or search_lower in str(profile.get("gardening_level", "")).lower()
                    or search_lower in str(profile.get("looking_for", "")).lower()
                    or search_lower in str(profile.get("offering", "")).lower()
                ]

            st.write(f"Showing **{len(filtered_profiles)}** profile(s).")

            cols = st.columns(3)

            for index, profile in enumerate(filtered_profiles):
                profile_id = profile.get("id")
                rating_summary = get_rating_summary(profile_id)

                with cols[index % 3]:
                    profile_card(profile, rating_summary)

                    if st.button("View profile", key=f"view_profile_{profile_id}"):
                        st.session_state.selected_profile_id = profile_id
                        st.rerun()

            selected_profile = None

            if st.session_state.selected_profile_id:
                for profile in profiles:
                    if profile.get("id") == st.session_state.selected_profile_id:
                        selected_profile = profile
                        break

            if selected_profile:
                st.markdown("---")
                st.markdown("## Selected User Profile")

                selected_id = selected_profile.get("id")
                selected_name = selected_profile.get("display_name") or selected_profile.get("username", "Unnamed user")

                st.markdown(
                    f"""
                    <div class="section-card">
                        <h2>{selected_name}</h2>
                        <p><b>Username:</b> {selected_profile.get('username', 'Not specified')}</p>
                        <p><b>Neighbourhood:</b> {selected_profile.get('neighbourhood', 'Not specified')}</p>
                        <p><b>City:</b> {selected_profile.get('location', 'Not specified')}</p>
                        <p><b>Gardening level:</b> {selected_profile.get('gardening_level', 'Not specified')}</p>
                        <p><b>Bio:</b> {selected_profile.get('short_bio', '')}</p>
                        <p><b>Looking for:</b> {selected_profile.get('looking_for', 'Not specified')}</p>
                        <p><b>Offering:</b> {selected_profile.get('offering', 'Not specified')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                selected_user_listings = [
                    listing for listing in get_all_listings()
                    if listing.get("user_id") == selected_id
                    and listing.get("status", "Available") == "Available"
                ]

                if selected_user_listings:
                    st.markdown("### Available Seed Listings")
                    for listing in selected_user_listings:
                        listing_card(listing)
                else:
                    st.info("This user has no available listings right now.")

                current_user = get_current_user()

                if current_user.id == selected_id:
                    st.caption("You cannot rate your own profile.")

                else:
                    existing_rating = get_my_rating_for_user(
                        rated_user_id=selected_id,
                        rater_user_id=current_user.id,
                    )

                    default_rating = existing_rating.get("rating", 5) if existing_rating else 5
                    default_comment = existing_rating.get("comment", "") if existing_rating else ""

                    with st.form(f"rating_form_{selected_id}"):
                        rating = st.slider(
                            "Your rating",
                            min_value=1,
                            max_value=5,
                            value=default_rating,
                            key=f"rating_slider_{selected_id}",
                        )

                        comment = st.text_area(
                            "Optional comment",
                            value=default_comment,
                            placeholder="e.g. Friendly exchange, healthy seedlings, good communication.",
                            key=f"rating_comment_{selected_id}",
                        )

                        submitted_rating = st.form_submit_button("Save rating")

                        if submitted_rating:
                            try:
                                upsert_profile_rating(
                                    rated_user_id=selected_id,
                                    rater_user_id=current_user.id,
                                    rating=rating,
                                    comment=comment,
                                )

                                st.success("Rating saved.")
                                st.rerun()

                            except Exception as e:
                                st.error("Could not save rating.")
                                st.caption(str(e))


# -----------------------------
# My Profile
# -----------------------------

if st.session_state.current_page == "My Profile":
    render_navigation()
    page_header(
        "My Profile",
        "Manage your gardener profile, seed matching preferences, and community identity.",
    )

    if not is_logged_in():
        st.warning("Please log in to create or edit your profile.")

    else:
        user = get_current_user()
        profile = get_profile(user.id)

        default_username = profile.get("username", "") if profile else ""
        default_location = profile.get("location", "Berlin") if profile else "Berlin"
        default_level = profile.get("gardening_level", "Beginner") if profile else "Beginner"
        default_display_name = profile.get("display_name", "") if profile else ""
        default_neighbourhood = profile.get("neighbourhood", "") if profile else ""
        default_bio = profile.get("short_bio", "") if profile else ""
        default_looking_for = profile.get("looking_for", "") if profile else ""
        default_offering = profile.get("offering", "") if profile else ""

        profile_name = default_display_name or default_username or "Sprouty Gardener"
        initials = "".join([part[0] for part in profile_name.split()[:2]]).upper() or "🌱"

        st.markdown(
            f"""
            <div class="section-card">
                <div class="avatar">{initials}</div>
                <h2>{profile_name}</h2>
                <p class="muted">{default_level} · {default_neighbourhood or default_location}</p>
                <div class="badge-row">
                    <span class="badge">🌱 Seed sharer</span>
                    <span class="badge">🌿 Berlin gardener</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("profile_form"):
            st.markdown("### Registration / Public Profile")

            display_name = st.text_input(
                "Name",
                value=default_display_name,
                placeholder="e.g. Anna Müller",
            )

            username = st.text_input(
                "Username / nickname",
                value=default_username,
                placeholder="e.g. GreenBalcony92",
            )

            neighbourhood = st.text_input(
                "Neighbourhood",
                value=default_neighbourhood,
                placeholder="e.g. Neukölln, Wedding, Prenzlauer Berg",
            )

            location = st.text_input(
                "City",
                value=default_location,
            )

            gardening_level = st.selectbox(
                "Gardening level",
                ["Beginner", "Intermediate", "Advanced"],
                index=["Beginner", "Intermediate", "Advanced"].index(default_level)
                if default_level in ["Beginner", "Intermediate", "Advanced"]
                else 0,
            )

            short_bio = st.text_area(
                "Short bio",
                value=default_bio,
                placeholder="Tell the community a little about your balcony, garden, or seed interests.",
            )

            st.markdown("### Seed Matching Preferences")

            looking_for = st.text_area(
                "What are you looking for?",
                value=default_looking_for,
                placeholder="e.g. basil, mint, tomato seedlings, pollinator-friendly flowers",
            )

            offering = st.text_area(
                "What can you offer?",
                value=default_offering,
                placeholder="e.g. herb seeds, marigold seeds, beginner gardening advice",
            )

            submitted_profile = st.form_submit_button("Save profile")

            if submitted_profile:
                if not display_name:
                    st.error("Please enter your name.")
                elif not username:
                    st.error("Please enter a username or nickname.")
                elif not neighbourhood:
                    st.error("Please enter your neighbourhood.")
                elif not looking_for:
                    st.error("Please enter what you are looking for. This is needed for matching.")
                elif not offering:
                    st.error("Please enter what you can offer. This helps other users match with you.")
                else:
                    try:
                        upsert_profile(
                            user_id=user.id,
                            username=username,
                            location=location,
                            gardening_level=gardening_level,
                            display_name=display_name,
                            neighbourhood=neighbourhood,
                            short_bio=short_bio,
                            looking_for=looking_for,
                            offering=offering,
                        )

                        st.success("Profile saved.")
                        st.rerun()

                    except Exception as e:
                        st.error("Could not save profile.")
                        st.caption(str(e))

        st.markdown("---")
        st.markdown("### Suggested Matches")

        current_profile = get_profile(user.id)
        current_looking_for = current_profile.get("looking_for", "") if current_profile else ""

        if not current_looking_for:
            st.info("Add what you are looking for to see suggested matches.")

        else:
            matches = find_profile_matches(
                current_user_id=user.id,
                looking_for=current_looking_for,
            )

            if not matches:
                st.info(
                    "No matches found yet. Try using broader keywords like herbs, flowers, tomato, mint, or balcony."
                )

            else:
                st.write(f"Found **{len(matches)}** possible match(es).")

                for match in matches:
                    matched_profile = match["profile"]
                    matched_listings = match["matching_listings"]

                    with st.container(border=True):
                        matched_name = matched_profile.get("display_name") or matched_profile.get("username", "Community member")

                        st.markdown(f"### {matched_name}")
                        st.write(f"**Neighbourhood:** {matched_profile.get('neighbourhood', 'Not specified')}")
                        st.write(f"**Gardening level:** {matched_profile.get('gardening_level', 'Not specified')}")
                        st.write(f"**Offers:** {matched_profile.get('offering', 'Not specified')}")
                        st.write(f"**Bio:** {matched_profile.get('short_bio', '')}")
                        st.write(f"**Match type:** {match.get('match_type', 'Match')}")
                        st.write(f"**Match score:** {match.get('match_score', 0)}/100")
                        st.write(f"**Why this match:** {match.get('match_reason', '')}")

                        if matched_listings:
                            st.markdown("**Available listings:**")
                            for listing in matched_listings:
                                st.write(
                                    f"- {listing.get('seed_name', 'Unnamed seed')} "
                                    f"({listing.get('category', 'Not specified')})"
                                )

                        if st.button("View full profile", key=f"match_profile_{matched_profile.get('id')}"):
                            st.session_state.selected_profile_id = matched_profile.get("id")
                            st.info("Open the Community tab to view the selected profile.")


# -----------------------------
# My Listings
# -----------------------------

if st.session_state.current_page == "My Listings":
    render_navigation()
    page_header(
        "My Listings",
        "Manage the seeds and seedlings you have shared with the community.",
    )

    if not is_logged_in():
        st.warning("Please log in to view your listings.")

    else:
        user = get_current_user()
        my_listings = get_my_listings(user.id)

        if not my_listings:
            st.markdown(
                """
                <div class="empty-state">
                    <div class="big-emoji">🌱</div>
                    <h2>You haven't shared any seeds yet</h2>
                    <p class="muted">Help another Berlin gardener start growing by creating your first listing.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:
            for listing in my_listings:
                listing_card(listing)

                current_status = listing.get("status", "Available")
                st.write(f"**Current status:** {current_status}")

                col1, col2 = st.columns(2)

                with col1:
                    if current_status == "Available":
                        if st.button("Mark as exchanged", key=f"exchange_{listing.get('id')}"):
                            try:
                                update_listing_status(listing.get("id"), "Exchanged")
                                st.success("Listing marked as exchanged.")
                                st.rerun()
                            except Exception as e:
                                st.error("Could not update listing status.")
                                st.caption(str(e))
                    else:
                        if st.button("Mark as available again", key=f"available_{listing.get('id')}"):
                            try:
                                update_listing_status(listing.get("id"), "Available")
                                st.success("Listing marked as available again.")
                                st.rerun()
                            except Exception as e:
                                st.error("Could not update listing status.")
                                st.caption(str(e))

                with col2:
                    if st.button(
                        "Delete listing",
                        key=f"delete_{listing.get('id')}",
                    ):
                        try:
                            delete_listing(listing.get("id"))
                            st.success("Listing deleted.")
                            st.rerun()

                        except Exception as e:
                            st.error("Could not delete listing.")
                            st.caption(str(e))
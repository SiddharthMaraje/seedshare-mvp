# app.py

import streamlit as st

from streamlit_folium import st_folium
from map_utils import create_seed_map

from rating_utils import (
    get_all_profiles,
    get_rating_summary,
    get_my_rating_for_user,
    upsert_profile_rating,
)

from auth_utils import (
    init_auth_state,
    sign_up,
    sign_in,
    sign_out,
    get_current_user,
    is_logged_in,
)

from profile_utils import get_profile, upsert_profile

from listing_utils import (
    get_all_listings,
    get_my_listings,
    create_listing,
    delete_listing,
)

from ai_utils import generate_balcony_gardening_advice


st.set_page_config(
    page_title="SeedShare Berlin",
    page_icon="🌱",
    layout="wide",
)


init_auth_state()


# -----------------------------
# Header
# -----------------------------

st.title("🌱 SeedShare Berlin")
st.caption("Community seed sharing and AI gardening help for Berlin urban gardeners")


# -----------------------------
# Sidebar authentication
# -----------------------------

st.sidebar.header("Account")

if is_logged_in():
    user = get_current_user()
    st.sidebar.success(f"Logged in as {user.email}")

    if st.sidebar.button("Log out"):
        sign_out()
        st.rerun()

else:
    auth_tab = st.sidebar.radio(
        "Choose action",
        ["Login", "Sign up"],
    )

    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    if auth_tab == "Login":
        if st.sidebar.button("Login"):
            try:
                response = sign_in(email, password)

                if response.user:
                    st.sidebar.success("Login successful.")
                    st.rerun()
                else:
                    st.sidebar.error("Login failed.")

            except Exception as e:
                st.sidebar.error("Login failed.")
                st.sidebar.caption(str(e))

    if auth_tab == "Sign up":
        if st.sidebar.button("Create account"):
            try:
                response = sign_up(email, password)

                if response.user:
                    st.sidebar.success(
                        "Account created. Please log in. If email confirmation is enabled, check your inbox."
                    )
                else:
                    st.sidebar.error("Sign-up failed.")

            except Exception as e:
                st.sidebar.error("Sign-up failed.")
                st.sidebar.caption(str(e))


# -----------------------------
# Page tabs
# -----------------------------

home_tab, browse_tab, map_tab, add_tab, ai_tab, community_tab, profile_tab, my_listings_tab = st.tabs(
    [
        "SeedShare Home",
        "Browse Seeds",
        "Seed Map",
        "Add Listing",
        "AI Gardening Assistant",
        "Community Profiles",
        "My Profile",
        "My Listings",
    ]
)


# -----------------------------
# SeedShare Home
# -----------------------------

with home_tab:
    st.subheader("Welcome to SeedShare Berlin")

    listings = get_all_listings()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Available Listings", len(listings))

    with col2:
        st.metric("City Focus", "Berlin")

    with col3:
        st.metric("MVP Features", "Seed Sharing + AI")

    st.markdown("---")

    st.markdown(
        """
        SeedShare Berlin is a small community MVP for people who want to share, discover,
        and grow seeds in Berlin.

        With this app, users can:

        - browse available seed listings
        - create their own seed listings after login
        - build a simple gardening profile
        - manage their own listings
        - use an AI assistant for beginner-friendly gardening advice
        """
    )

    st.info(
        "This MVP focuses on simple community exchange, urban gardening, and AI-supported recommendations."
    )

# -----------------------------
# Browse Seeds
# -----------------------------

with browse_tab:
    st.subheader("Available Seed Listings")

    listings = get_all_listings()

    if not listings:
        st.info("No seed listings yet.")

    else:
        st.markdown("### Search and Filter")

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

        col4, col5 = st.columns(2)

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

        st.markdown("---")
        st.write(f"Showing **{len(filtered_listings)}** of **{len(listings)}** listings.")

        if not filtered_listings:
            st.warning("No listings match your search filters.")

        else:
            for listing in filtered_listings:
                with st.container(border=True):
                    st.markdown(f"### {listing.get('seed_name', 'Unnamed seed or seedling')}")
                    st.write(f"**Category:** {listing.get('category', 'Not specified')}")
                    st.write(f"**Best balcony condition:** {listing.get('best_balcony_condition', 'Not specified')}")
                    st.write(f"**Suitable for:** {listing.get('suitable_for', 'Not specified')}")
                    st.write(f"**Berlin district:** {listing.get('berlin_district', 'Not specified')}")
                    st.write(f"**Quantity:** {listing.get('quantity', 'Not specified')}")
                    st.write(f"**Shared by:** {listing.get('owner_name', 'Not specified')}")
                    st.write(f"**Contact:** {listing.get('contact', 'Not specified')}")
                    st.write(f"**Growing tip:** {listing.get('description', '')}")


# -----------------------------
# Seed Map
# -----------------------------

with map_tab:
    st.subheader("Seed Map of Berlin")
    st.write(
        "Explore available seed and seedling listings by Berlin district. "
        "Markers use approximate district locations, not exact addresses."
    )

    listings = get_all_listings()

    if not listings:
        st.info("No seed listings available for the map yet.")

    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            map_category_filter = st.selectbox(
                "Map category filter",
                [
                    "All",
                    "Herb",
                    "Vegetable",
                    "Flower",
                    "Fruit",
                    "Pollinator-friendly",
                    "Other",
                ],
                key="map_category_filter",
            )

        with col2:
            map_district_filter = st.selectbox(
                "Map district filter",
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
                key="map_district_filter",
            )

        with col3:
            map_balcony_filter = st.selectbox(
                "Map balcony condition filter",
                [
                    "All",
                    "Full sun",
                    "Partial sun",
                    "Mostly shade",
                    "Indoor / windowsill",
                    "Flexible / easy-going",
                ],
                key="map_balcony_filter",
            )

        map_listings = listings

        if map_category_filter != "All":
            map_listings = [
                listing for listing in map_listings
                if listing.get("category") == map_category_filter
            ]

        if map_district_filter != "All":
            map_listings = [
                listing for listing in map_listings
                if listing.get("berlin_district") == map_district_filter
            ]

        if map_balcony_filter != "All":
            map_listings = [
                listing for listing in map_listings
                if listing.get("best_balcony_condition") == map_balcony_filter
            ]

        st.write(f"Showing **{len(map_listings)}** listing marker(s) on the map.")

        if not map_listings:
            st.warning("No listings match the selected map filters.")

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

with add_tab:
    st.subheader("Add a Seed or Seedling Listing")

    if not is_logged_in():
        st.warning("Please log in to add a seed listing.")

    else:
        user = get_current_user()

        with st.form("add_listing_form"):
            seed_name = st.text_input(
                "Seed or seedling name",
                placeholder="e.g. Basil seedlings, tomato seeds, marigold seeds",
            )

            col1, col2 = st.columns(2)

            with col1:
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
                owner_name = st.text_input(
                    "Your name or nickname",
                    placeholder="e.g. Anna, GreenBalcony92",
                )

                quantity = st.text_input(
                    "Quantity",
                    placeholder="e.g. 10 seeds, 3 seedlings, one small packet",
                )

                contact = st.text_input(
                    "Contact",
                    placeholder="e.g. email, Telegram, phone, or preferred contact method",
                )

            description = st.text_area(
                "Short description / growing tip",
                placeholder="e.g. Easy basil seedlings, good for sunny balconies. Water regularly and harvest often.",
            )

            submitted_listing = st.form_submit_button("Create listing")

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

with ai_tab:
    st.subheader("AI Gardening Assistant")
    st.write(
        "Get personalized growing advice based on your balcony, season, sunlight, and gardening experience."
    )

    with st.form("ai_gardening_form"):
        col1, col2 = st.columns(2)

        with col1:
            ai_location = st.text_input(
                "Location",
                value="Berlin",
                placeholder="e.g. Berlin, Neukölln, Prenzlauer Berg",
            )

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

        submitted_ai = st.form_submit_button("Generate AI growing advice")

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
        st.write(advice)

        st.markdown("---")

        with st.expander("View AI Prompt Used"):
            st.code(prompt, language="text")

# -----------------------------
# Community Profiles
# -----------------------------

with community_tab:
    st.subheader("Community Profiles")
    st.write("Browse SeedShare Berlin users and rate community interactions.")

    if not is_logged_in():
        st.warning("Please log in to view Community Profiles.")

    else:
        profiles = get_all_profiles()

        if not profiles:
            st.info("No community profiles yet.")

        else:
            search_profile = st.text_input(
                "Search profiles",
                placeholder="Search by username, location, or gardening level",
            )

            filtered_profiles = profiles

            if search_profile:
                search_lower = search_profile.lower()

                filtered_profiles = [
                    profile for profile in filtered_profiles
                    if search_lower in str(profile.get("username", "")).lower()
                    or search_lower in str(profile.get("location", "")).lower()
                    or search_lower in str(profile.get("gardening_level", "")).lower()
                ]

            st.write(f"Showing **{len(filtered_profiles)}** profile(s).")

            for profile in filtered_profiles:
                profile_id = profile.get("id")
                username = profile.get("username", "Unnamed user")
                location = profile.get("location", "Not specified")
                gardening_level = profile.get("gardening_level", "Not specified")

                rating_summary = get_rating_summary(profile_id)
                average_rating = rating_summary["average"]
                rating_count = rating_summary["count"]

                with st.container(border=True):
                    st.markdown(f"### {username}")
                    st.write(f"**Location:** {location}")
                    st.write(f"**Gardening level:** {gardening_level}")

                    if rating_count == 0:
                        st.write("**Rating:** No ratings yet")
                    else:
                        st.write(
                            f"**Rating:** ⭐ {average_rating}/5 from {rating_count} rating(s)"
                        )

                    current_user = get_current_user()

                    if current_user.id == profile_id:
                        st.caption("You cannot rate your own profile.")

                    else:
                        existing_rating = get_my_rating_for_user(
                            rated_user_id=profile_id,
                            rater_user_id=current_user.id,
                        )

                        default_rating = (
                            existing_rating.get("rating", 5)
                            if existing_rating
                            else 5
                        )

                        default_comment = (
                            existing_rating.get("comment", "")
                            if existing_rating
                            else ""
                        )

                        with st.form(f"rating_form_{profile_id}"):
                            rating = st.slider(
                                "Your rating",
                                min_value=1,
                                max_value=5,
                                value=default_rating,
                                key=f"rating_slider_{profile_id}",
                            )

                            comment = st.text_area(
                                "Optional comment",
                                value=default_comment,
                                placeholder="e.g. Friendly exchange, healthy seedlings, good communication.",
                                key=f"rating_comment_{profile_id}",
                            )

                            submitted_rating = st.form_submit_button("Save rating")

                            if submitted_rating:
                                try:
                                    upsert_profile_rating(
                                        rated_user_id=profile_id,
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

with profile_tab:
    st.subheader("My Profile")

    if not is_logged_in():
        st.warning("Please log in to create or edit your profile.")

    else:
        user = get_current_user()
        profile = get_profile(user.id)

        default_username = profile.get("username", "") if profile else ""
        default_location = profile.get("location", "Berlin") if profile else "Berlin"
        default_level = profile.get("gardening_level", "Beginner") if profile else "Beginner"

        with st.form("profile_form"):
            username = st.text_input("Username", value=default_username)
            profile_location = st.text_input("Location", value=default_location)

            gardening_level = st.selectbox(
                "Gardening level",
                ["Beginner", "Intermediate", "Advanced"],
                index=["Beginner", "Intermediate", "Advanced"].index(default_level)
                if default_level in ["Beginner", "Intermediate", "Advanced"]
                else 0,
            )

            submitted_profile = st.form_submit_button("Save profile")

            if submitted_profile:
                try:
                    upsert_profile(
                        user_id=user.id,
                        username=username,
                        location=profile_location,
                        gardening_level=gardening_level,
                    )

                    st.success("Profile saved.")
                    st.rerun()

                except Exception as e:
                    st.error("Could not save profile.")
                    st.caption(str(e))


# -----------------------------
# My Listings
# -----------------------------

with my_listings_tab:
    st.subheader("My Listings")

    if not is_logged_in():
        st.warning("Please log in to view your listings.")

    else:
        user = get_current_user()
        my_listings = get_my_listings(user.id)

        if not my_listings:
            st.info("You have not created any listings yet.")

        else:
            for listing in my_listings:
                with st.container(border=True):
                    st.markdown(f"### {listing.get('seed_name', 'Unnamed seed or seedling')}")
                    st.write(f"**Category:** {listing.get('category', 'Not specified')}")
                    st.write(f"**Best balcony condition:** {listing.get('best_balcony_condition', 'Not specified')}")
                    st.write(f"**Suitable for:** {listing.get('suitable_for', 'Not specified')}")
                    st.write(f"**Berlin district:** {listing.get('berlin_district', 'Not specified')}")
                    st.write(f"**Quantity:** {listing.get('quantity', 'Not specified')}")
                    st.write(f"**Contact:** {listing.get('contact', 'Not specified')}")
                    st.write(f"**Growing tip:** {listing.get('description', '')}")

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
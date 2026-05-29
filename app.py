# app.py

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
# Session state
# -----------------------------

if "selected_profile_id" not in st.session_state:
    st.session_state.selected_profile_id = None


# -----------------------------
# Tabs
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
    available_count = len(
        [listing for listing in listings if listing.get("status", "Available") == "Available"]
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Listings", len(listings))

    with col2:
        st.metric("Available Seeds", available_count)

    with col3:
        st.metric("City Focus", "Berlin")

    st.markdown("---")

    st.markdown(
        """
        SeedShare Berlin is a community MVP for people who want to share, discover,
        and grow seeds in Berlin.

        With this app, users can:

        - browse and filter seed listings
        - view listings on a Berlin district seed map
        - create seed or seedling listings after login
        - mark seeds as exchanged
        - create richer community profiles
        - browse and rate community profiles
        - find profile matches based on what users are looking for
        - use an AI gardening assistant
        """
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

        st.markdown("---")
        st.write(f"Showing **{len(filtered_listings)}** of **{len(listings)}** listings.")

        if not filtered_listings:
            st.warning("No listings match your search filters.")

        else:
            for listing in filtered_listings:
                with st.container(border=True):
                    st.markdown(f"### {listing.get('seed_name', 'Unnamed seed or seedling')}")

                    status = listing.get("status", "Available")

                    if status == "Exchanged":
                        st.warning("Status: Exchanged")
                    else:
                        st.success("Status: Available")

                    st.write(f"**Category:** {listing.get('category', 'Not specified')}")
                    st.write(f"**Best balcony condition:** {listing.get('best_balcony_condition', 'Not specified')}")
                    st.write(f"**Suitable for:** {listing.get('suitable_for', 'Not specified')}")
                    st.write(f"**Berlin district:** {listing.get('berlin_district', 'Not specified')}")
                    st.write(f"**Quantity:** {listing.get('quantity', 'Not specified')}")
                    st.write(f"**Shared by:** {listing.get('owner_name', 'Not specified')}")
                    st.write(f"**Contact:** {listing.get('contact', 'Not specified')}")
                    st.write(f"**Growing tip:** {listing.get('description', '')}")

                    owner_id = listing.get("user_id")

                    if owner_id:
                        owner_rating = get_rating_summary(owner_id)

                        if owner_rating["count"] > 0:
                            st.write(
                                f"**Owner rating:** ⭐ {owner_rating['average']}/5 from {owner_rating['count']} rating(s)"
                            )

                        if st.button("View owner profile", key=f"browse_owner_{listing.get('id')}"):
                            st.session_state.selected_profile_id = owner_id
                            st.info("Open the Community Profiles tab to view the selected profile.")


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

    map_listings = [
        listing for listing in listings
        if listing.get("status", "Available") == "Available"
    ]

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
    st.write("Browse SeedShare Berlin users, view public profiles, and rate community interactions.")

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

            for profile in filtered_profiles:
                profile_id = profile.get("id")
                display_name = profile.get("display_name") or profile.get("username", "Unnamed user")
                username = profile.get("username", "Not specified")
                neighbourhood = profile.get("neighbourhood", "Not specified")
                gardening_level = profile.get("gardening_level", "Not specified")

                rating_summary = get_rating_summary(profile_id)
                average_rating = rating_summary["average"]
                rating_count = rating_summary["count"]

                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f"### {display_name}")
                        st.write(f"**Username:** {username}")
                        st.write(f"**Neighbourhood:** {neighbourhood}")
                        st.write(f"**Gardening level:** {gardening_level}")

                        if rating_count == 0:
                            st.write("**Rating:** No ratings yet")
                        else:
                            st.write(
                                f"**Rating:** ⭐ {average_rating}/5 from {rating_count} rating(s)"
                            )

                    with col2:
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

                st.markdown(f"### {selected_name}")
                st.write(f"**Username:** {selected_profile.get('username', 'Not specified')}")
                st.write(f"**Neighbourhood:** {selected_profile.get('neighbourhood', 'Not specified')}")
                st.write(f"**City:** {selected_profile.get('location', 'Not specified')}")
                st.write(f"**Gardening level:** {selected_profile.get('gardening_level', 'Not specified')}")
                st.write(f"**Bio:** {selected_profile.get('short_bio', '')}")
                st.write(f"**Looking for:** {selected_profile.get('looking_for', 'Not specified')}")
                st.write(f"**Offering:** {selected_profile.get('offering', 'Not specified')}")

                selected_user_listings = [
                    listing for listing in get_all_listings()
                    if listing.get("user_id") == selected_id
                    and listing.get("status", "Available") == "Available"
                ]

                if selected_user_listings:
                    st.markdown("### Available Seed Listings")
                    for listing in selected_user_listings:
                        st.write(
                            f"- **{listing.get('seed_name', 'Unnamed seed')}** "
                            f"({listing.get('category', 'Not specified')})"
                        )
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
        default_display_name = profile.get("display_name", "") if profile else ""
        default_neighbourhood = profile.get("neighbourhood", "") if profile else ""
        default_bio = profile.get("short_bio", "") if profile else ""
        default_looking_for = profile.get("looking_for", "") if profile else ""
        default_offering = profile.get("offering", "") if profile else ""

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

                        if matched_listings:
                            st.markdown("**Available listings:**")
                            for listing in matched_listings:
                                st.write(
                                    f"- {listing.get('seed_name', 'Unnamed seed')} "
                                    f"({listing.get('category', 'Not specified')})"
                                )

                        if st.button("View full profile", key=f"match_profile_{matched_profile.get('id')}"):
                            st.session_state.selected_profile_id = matched_profile.get("id")
                            st.info("Open the Community Profiles tab to view the selected profile.")


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

                    current_status = listing.get("status", "Available")
                    st.write(f"**Status:** {current_status}")

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
# match_utils.py

from profile_utils import get_all_profiles
from listing_utils import get_available_listings


def text_contains_match(search_text: str, target_text: str):
    if not search_text or not target_text:
        return False

    search_words = [
        word.strip().lower()
        for word in search_text.replace(",", " ").split()
        if len(word.strip()) > 2
    ]

    target_lower = target_text.lower()

    return any(word in target_lower for word in search_words)


def find_profile_matches(current_user_id: str, looking_for: str):
    profiles = get_all_profiles()
    listings = get_available_listings()

    matches = []

    for profile in profiles:
        profile_id = profile.get("id")

        if profile_id == current_user_id:
            continue

        profile_match_text = " ".join(
            [
                str(profile.get("offering", "")),
                str(profile.get("short_bio", "")),
                str(profile.get("gardening_level", "")),
                str(profile.get("neighbourhood", "")),
            ]
        )

        profile_matches = text_contains_match(looking_for, profile_match_text)

        user_listings = [
            listing for listing in listings
            if listing.get("user_id") == profile_id
        ]

        listing_match = False

        for listing in user_listings:
            listing_text = " ".join(
                [
                    str(listing.get("seed_name", "")),
                    str(listing.get("category", "")),
                    str(listing.get("description", "")),
                    str(listing.get("suitable_for", "")),
                ]
            )

            if text_contains_match(looking_for, listing_text):
                listing_match = True
                break

        if profile_matches or listing_match:
            matches.append(
                {
                    "profile": profile,
                    "matching_listings": user_listings,
                    "match_reason": "Profile offering or available seed listings match your looking-for text.",
                }
            )

    return matches
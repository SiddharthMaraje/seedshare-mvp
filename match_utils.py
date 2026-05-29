# match_utils.py

from profile_utils import get_all_profiles
from listing_utils import get_available_listings
from ai_utils import semantic_profile_matching


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

    candidate_profiles = []

    for profile in profiles:
        profile_id = profile.get("id")

        if profile_id == current_user_id:
            continue

        user_listings = [
            listing for listing in listings
            if listing.get("user_id") == profile_id
        ]

        candidate_profiles.append(
            {
                "profile_id": profile_id,
                "display_name": profile.get("display_name", ""),
                "username": profile.get("username", ""),
                "neighbourhood": profile.get("neighbourhood", ""),
                "gardening_level": profile.get("gardening_level", ""),
                "short_bio": profile.get("short_bio", ""),
                "offering": profile.get("offering", ""),
                "available_listings": [
                    {
                        "seed_name": listing.get("seed_name", ""),
                        "category": listing.get("category", ""),
                        "suitable_for": listing.get("suitable_for", ""),
                        "description": listing.get("description", ""),
                    }
                    for listing in user_listings
                ],
            }
        )

    ai_matches = semantic_profile_matching(
        looking_for=looking_for,
        candidate_profiles=candidate_profiles,
    )

    matches = []

    if ai_matches:
        for ai_match in ai_matches:
            matched_profile_id = ai_match.get("profile_id")

            matched_profile = next(
                (profile for profile in profiles if profile.get("id") == matched_profile_id),
                None,
            )

            if not matched_profile:
                continue

            matched_listings = [
                listing for listing in listings
                if listing.get("user_id") == matched_profile_id
            ]

            matches.append(
                {
                    "profile": matched_profile,
                    "matching_listings": matched_listings,
                    "match_reason": ai_match.get("reason", "AI semantic match"),
                    "match_score": ai_match.get("score", 0),
                    "match_type": "AI semantic match",
                }
            )

        return sorted(matches, key=lambda item: item["match_score"], reverse=True)

    # Fallback keyword matching if AI fails
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
                    "match_reason": "Keyword match based on profile offering or available listings.",
                    "match_score": 60,
                    "match_type": "Keyword fallback match",
                }
            )

    return matches
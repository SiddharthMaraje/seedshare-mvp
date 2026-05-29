# profile_utils.py

from supabase_client import get_supabase_client


def get_profile(user_id: str):
    supabase = get_supabase_client()

    response = (
        supabase.table("profiles")
        .select("*")
        .eq("id", user_id)
        .execute()
    )

    if response.data:
        return response.data[0]

    return None


def get_all_profiles():
    supabase = get_supabase_client()

    response = (
        supabase.table("profiles")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    return response.data or []


def upsert_profile(
    user_id: str,
    username: str,
    location: str,
    gardening_level: str,
    display_name: str,
    neighbourhood: str,
    short_bio: str,
    looking_for: str,
    offering: str,
):
    supabase = get_supabase_client()

    profile_data = {
        "id": user_id,
        "username": username,
        "location": location,
        "gardening_level": gardening_level,
        "display_name": display_name,
        "neighbourhood": neighbourhood,
        "short_bio": short_bio,
        "looking_for": looking_for,
        "offering": offering,
    }

    response = (
        supabase.table("profiles")
        .upsert(profile_data)
        .execute()
    )

    return response
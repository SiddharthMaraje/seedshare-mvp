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


def upsert_profile(user_id: str, username: str, location: str, gardening_level: str):
    supabase = get_supabase_client()

    profile_data = {
        "id": user_id,
        "username": username,
        "location": location,
        "gardening_level": gardening_level,
    }

    response = (
        supabase.table("profiles")
        .upsert(profile_data)
        .execute()
    )

    return response
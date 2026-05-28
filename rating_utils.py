# rating_utils.py

from supabase_client import get_supabase_client


def get_all_profiles():
    supabase = get_supabase_client()

    response = (
        supabase.table("profiles")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    return response.data or []


def get_all_profile_ratings():
    supabase = get_supabase_client()

    response = (
        supabase.table("profile_ratings")
        .select("*")
        .execute()
    )

    return response.data or []


def get_rating_summary(rated_user_id: str):
    ratings = get_all_profile_ratings()

    user_ratings = [
        rating for rating in ratings
        if rating.get("rated_user_id") == rated_user_id
    ]

    if not user_ratings:
        return {
            "average": 0,
            "count": 0,
        }

    total = sum(rating.get("rating", 0) for rating in user_ratings)
    count = len(user_ratings)

    return {
        "average": round(total / count, 1),
        "count": count,
    }


def get_my_rating_for_user(rated_user_id: str, rater_user_id: str):
    supabase = get_supabase_client()

    response = (
        supabase.table("profile_ratings")
        .select("*")
        .eq("rated_user_id", rated_user_id)
        .eq("rater_user_id", rater_user_id)
        .execute()
    )

    if response.data:
        return response.data[0]

    return None


def upsert_profile_rating(
    rated_user_id: str,
    rater_user_id: str,
    rating: int,
    comment: str,
):
    supabase = get_supabase_client()

    rating_data = {
        "rated_user_id": rated_user_id,
        "rater_user_id": rater_user_id,
        "rating": rating,
        "comment": comment,
    }

    response = (
        supabase.table("profile_ratings")
        .upsert(
            rating_data,
            on_conflict="rated_user_id,rater_user_id",
        )
        .execute()
    )

    return response
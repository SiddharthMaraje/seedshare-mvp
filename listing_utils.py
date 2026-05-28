# listing_utils.py

from supabase_client import get_supabase_client


def get_all_listings():
    supabase = get_supabase_client()

    response = (
        supabase.table("seed_listings")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    return response.data or []


def get_my_listings(user_id: str):
    supabase = get_supabase_client()

    response = (
        supabase.table("seed_listings")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )

    return response.data or []


def create_listing(
    seed_name: str,
    best_balcony_condition: str,
    category: str,
    suitable_for: str,
    berlin_district: str,
    owner_name: str,
    quantity: str,
    contact: str,
    description: str,
    user_id: str,
):
    supabase = get_supabase_client()

    listing_data = {
        "seed_name": seed_name,
        "best_balcony_condition": best_balcony_condition,
        "category": category,
        "suitable_for": suitable_for,
        "berlin_district": berlin_district,
        "owner_name": owner_name,
        "quantity": quantity,
        "contact": contact,
        "description": description,
        "user_id": user_id,
    }

    response = (
        supabase.table("seed_listings")
        .insert(listing_data)
        .execute()
    )

    return response


def delete_listing(listing_id: int):
    supabase = get_supabase_client()

    response = (
        supabase.table("seed_listings")
        .delete()
        .eq("id", listing_id)
        .execute()
    )

    return response
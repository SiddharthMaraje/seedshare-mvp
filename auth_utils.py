# auth_utils.py

import streamlit as st
from supabase_client import get_supabase_client


def init_auth_state():
    if "user" not in st.session_state:
        st.session_state.user = None
    if "access_token" not in st.session_state:
        st.session_state.access_token = None
    if "refresh_token" not in st.session_state:
        st.session_state.refresh_token = None


def sign_up(email: str, password: str):
    supabase = get_supabase_client()

    response = supabase.auth.sign_up({
        "email": email,
        "password": password,
    })

    return response


def sign_in(email: str, password: str):
    supabase = get_supabase_client()

    response = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password,
    })

    if response.session:
        st.session_state.user = response.user
        st.session_state.access_token = response.session.access_token
        st.session_state.refresh_token = response.session.refresh_token

    return response


def sign_out():
    supabase = get_supabase_client()

    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    st.session_state.user = None
    st.session_state.access_token = None
    st.session_state.refresh_token = None


def get_current_user():
    return st.session_state.get("user")


def is_logged_in():
    return st.session_state.get("user") is not None
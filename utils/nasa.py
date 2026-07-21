import os
import requests
import streamlit as st

# Default (fallback) API key; can be overridden by env var or Streamlit secrets
_env_key = os.environ.get("NASA_API_KEY")
_secrets_key = None
try:
    _secrets_key = st.secrets.get("NASA_API_KEY")
except Exception:
    _secrets_key = None

API_KEY = _env_key or _secrets_key or "DEMO_KEY"


def _mask_key(key: str) -> str:
    if not key:
        return "(none)"
    if len(key) <= 6:
        return "****"
    return key[:3] + "..." + key[-3:]


def get_apod(selected_date):
    url = "https://api.nasa.gov/planetary/apod"

    params = {
        "api_key": API_KEY,
        "date": selected_date.isoformat()
    }

    try:
        print(f"[DEBUG] NASA APOD request -> url={url} params={params}")
        response = requests.get(url, params=params, timeout=15)
        print(f"[DEBUG] NASA response status: {response.status_code}")

        if response.ok:
            print("[DEBUG] NASA response OK; returning JSON")
            return response.json()

        # Log full response body for debugging
        print("[DEBUG] NASA response failed:", response.text)
        return None

    except Exception as e:
        print(f"[ERROR] NASA request exception: {e}")
        return None
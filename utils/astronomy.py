import os
import base64
from typing import Optional, List, Dict, Any

import requests
import streamlit as st


def _get_credentials() -> Optional[Dict[str, str]]:
    # Try common environment variable names first
    env_pairs = [
        ("ASTRONOMY_API_APP_ID", "ASTRONOMY_API_APP_SECRET"),
        ("ASTRONOMYAPI_APP_ID", "ASTRONOMYAPI_APP_SECRET"),
        ("ASTRONOMY_API_ID", "ASTRONOMY_API_SECRET"),
        ("ASTRONOMY_APP_ID", "ASTRONOMY_APP_SECRET"),
    ]

    for id_key, secret_key in env_pairs:
        app_id = os.environ.get(id_key)
        app_secret = os.environ.get(secret_key)
        if app_id and app_secret:
            return {"app_id": app_id, "app_secret": app_secret}

    # Fallback to Streamlit secrets if provided
    try:
        secrets = st.secrets
    except Exception:
        secrets = {}

    # try a few shapes in secrets
    if isinstance(secrets, dict):
        # flat keys
        for id_key, secret_key in env_pairs:
            app_id = secrets.get(id_key)
            app_secret = secrets.get(secret_key)
            if app_id and app_secret:
                return {"app_id": app_id, "app_secret": app_secret}

        # nested under 'astronomy' or 'astronomy_api'
        for container in ("astronomy", "astronomy_api", "astronomyapi"):
            c = secrets.get(container, {})
            if isinstance(c, dict):
                app_id = c.get("app_id") or c.get("id") or c.get("key")
                app_secret = c.get("app_secret") or c.get("secret") or c.get("app_secret")
                if app_id and app_secret:
                    return {"app_id": app_id, "app_secret": app_secret}

    return None


def _build_headers(creds: Dict[str, str]) -> Dict[str, str]:
    # AstronomyAPI supports app id/secret headers
    headers = {
        "x-astronomyapi-app-id": creds["app_id"],
        "x-astronomyapi-app-secret": creds["app_secret"],
        "Content-Type": "application/json",
    }
    return headers


def _safe_get(data: Dict[str, Any], path: List[Any]):
    try:
        cur = data
        for p in path:
            cur = cur[p]
        return cur
    except Exception:
        return None


def get_moon_data(lat: float, lon: float, selected_date) -> Optional[Dict[str, Any]]:
    """Return {'phase': str, 'illumination': float} or None on failure."""
    creds = _get_credentials()
    if not creds:
        print("[DEBUG][astronomy] No AstronomyAPI credentials found; falling back to local moon calculation")
        try:
            # fallback to existing local moon helper if available
            from utils.moon import get_moon_phase as _local_moon
            return _local_moon(selected_date)
        except Exception as e:
            print(f"[DEBUG][astronomy] Local moon fallback failed: {e}")
            return None

    url = "https://api.astronomyapi.com/api/v2/bodies/positions"

    payload = {
        "observer": {
            "latitude": float(lat),
            "longitude": float(lon),
            "date": selected_date.isoformat()
        },
        "bodies": ["moon"]
    }

    try:
        headers = _build_headers(creds)
        # avoid printing secrets; show masked
        print(f"[DEBUG][astronomy] Moon request payload={payload}")
        print(f"[DEBUG][astronomy] Using headers x-astronomyapi-app-id={creds.get('app_id')} (secret hidden)")
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        print(f"[DEBUG][astronomy] Moon response status: {resp.status_code}")
        data = resp.json()
        print(f"[DEBUG][astronomy] Moon raw response: {data}")

        # Try to extract phase and illumination from known locations
        phase = _safe_get(data, ["data", "table", "rows", 0, "cells", 0, "extra", "phase", "name"])
        if not phase:
            phase = _safe_get(data, ["data", "table", "rows", 0, "cells", 0, "extra", "phase"])

        illum = _safe_get(data, ["data", "table", "rows", 0, "cells", 0, "extra", "phase", "illumination"])
        if illum is None:
            illum = _safe_get(data, ["data", "table", "rows", 0, "cells", 0, "extra", "illumination"])

        # Normalize illumination to percentage if possible
        if isinstance(illum, (int, float)):
            # If fraction (0-1) convert to percent
            if 0 <= illum <= 1:
                illumination_pct = round(illum * 100, 1)
            else:
                illumination_pct = round(float(illum), 1)
        else:
            illumination_pct = None

        result = {
            "phase": phase if phase else "unknown",
            "illumination": illumination_pct
        }

        return result

    except Exception as e:
        print(f"[ERROR][astronomy] Moon request error: {e}")
        try:
            print("[DEBUG][astronomy] Response text:", resp.text)
        except Exception:
            pass
        return None


def get_visible_planets(lat: float, lon: float, selected_date) -> Optional[List[str]]:
    """Return list of visible planet names or None on failure."""
    creds = _get_credentials()
    if not creds:
        print("[DEBUG][astronomy] No AstronomyAPI credentials found; falling back to local planets placeholder")
        try:
            from utils.planets import get_visible_planets as _local_planets
            return _local_planets(selected_date)
        except Exception as e:
            print(f"[DEBUG][astronomy] Local planets fallback failed: {e}")
            return None

    url = "https://api.astronomyapi.com/api/v2/bodies/positions"

    PLANETS = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]

    visible = []

    try:
        headers = _build_headers(creds)
        print(f"[DEBUG][astronomy] Planets request start for date={selected_date.isoformat()} lat={lat} lon={lon}")

        for body in PLANETS:
            payload = {
                "observer": {
                    "latitude": float(lat),
                    "longitude": float(lon),
                    "date": selected_date.isoformat()
                },
                "bodies": [body]
            }

            print(f"[DEBUG][astronomy] Requesting body={body} payload={payload}")
            resp = requests.post(url, json=payload, headers=headers, timeout=15)
            print(f"[DEBUG][astronomy] body={body} status={resp.status_code}")
            try:
                data = resp.json()
            except Exception:
                print(f"[DEBUG][astronomy] body={body} response not JSON: {resp.text}")
                continue

            print(f"[DEBUG][astronomy] body={body} raw response: {data}")

            alt = _safe_get(data, ["data", "table", "rows", 0, "cells", 0, "position", "horizontal", "altitude", "degrees"])
            print(f"[DEBUG][astronomy] body={body} altitude={alt}")

            try:
                if alt is not None and float(alt) > 0:
                    visible.append(body)
            except Exception as e:
                print(f"[DEBUG][astronomy] body={body} parse error: {e}")
                continue

        print(f"[DEBUG][astronomy] Visible planets: {visible}")
        return visible

    except Exception as e:
        print(f"[ERROR][astronomy] Planets request error: {e}")
        try:
            print("[DEBUG][astronomy] Response text:", resp.text)
        except Exception:
            pass
        return None
from datetime import datetime
from skyfield.api import load

def moon_phase():

    ts = load.timescale()
    t = ts.now()
    eph = load(
        "de421.bsp"
    )

    moon = eph["moon"]
    earth = eph["earth"]

    astrometric = earth.at(t).observe(moon)
    return "moon data loaded!"
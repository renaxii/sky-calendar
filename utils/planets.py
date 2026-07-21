from datetime import datetime
from typing import List, Optional

from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo
from skyfield.api import load, wgs84


PLANETS = [
    ("Mercury", "mercury"),
    ("Venus", "venus"),
    ("Mars", "mars"),
    ("Jupiter", "jupiter barycenter"),
    ("Saturn", "saturn barycenter"),
    ("Uranus", "uranus barycenter"),
    ("Neptune", "neptune barycenter"),
]


def get_visible_planets(lat: float, lon: float, selected_date) -> Optional[List[str]]:
    """Return a list of planet names visible at the given location and date (local 22:00).

    If no planets are visible, return a list containing a single explanatory string.
    On error, return None.
    """
    try:
        tf = TimezoneFinder()
        tz_name = tf.timezone_at(lat=lat, lng=lon) or "UTC"
        tz = ZoneInfo(tz_name)

        # choose an observing time: local 22:00
        dt_local = datetime(selected_date.year, selected_date.month, selected_date.day, 22, 0, tzinfo=tz)

        ts = load.timescale()
        t = ts.from_datetime(dt_local)
        eph = load("de421.bsp")

        observer = wgs84.latlon(lat, lon)

        visible = []

        for display_name, body_name in PLANETS:
            try:
                body = eph[body_name]
            except Exception:
                body = eph[body_name]

            # build a topocentric observer by adding the geographic position to Earth
            top = (eph["earth"] + wgs84.latlon(lat, lon)).at(t)
            astrometric = top.observe(body).apparent()
            alt, az, distance = astrometric.altaz()
            alt_deg = alt.degrees

            if alt_deg is not None and alt_deg > 0:
                visible.append(display_name)

        if visible:
            return visible
        else:
            explanation = (
                "No major planets are above the horizon at local 22:00 for the selected date and location. "
                "This can be due to daylight, seasonal geometry, or local horizon limits."
            )
            return [explanation]

    except Exception as e:
        print(f"[ERROR][planets] failed to compute visible planets: {e}")
        return None
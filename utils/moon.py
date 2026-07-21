from datetime import timedelta
from math import cos, radians

from skyfield.api import load


def get_moon_phase(selected_date):
    """Return {'phase': str, 'illumination': float} using Skyfield.

    Illumination is returned as a percentage (0-100).
    Phase name is one of: new moon, waxing crescent, first quarter,
    waxing gibbous, full moon, waning gibbous, last quarter, waning crescent.
    """
    try:
        ts = load.timescale()
        eph = load("de421.bsp")

        # compute at UTC midday for the selected date to get a stable phase
        t0 = ts.utc(selected_date.year, selected_date.month, selected_date.day, 12)

        sun = eph["sun"]
        moon = eph["moon"]
        earth = eph["earth"]

        # elongation: angular separation between Moon and Sun as seen from Earth
        sun_apparent = earth.at(t0).observe(sun).apparent()
        moon_apparent = earth.at(t0).observe(moon).apparent()
        elongation = moon_apparent.separation_from(sun_apparent).degrees

        # illuminated fraction (0-100)
        illum_frac = (1 - cos(radians(elongation))) / 2.0
        illumination_pct = round(illum_frac * 100, 1)

        # determine waxing vs waning by comparing elongation tomorrow
        t1 = ts.utc((selected_date + timedelta(days=1)).year,
                    (selected_date + timedelta(days=1)).month,
                    (selected_date + timedelta(days=1)).day, 12)
        moon_app_next = earth.at(t1).observe(moon).apparent()
        sun_app_next = earth.at(t1).observe(sun).apparent()
        elong_next = moon_app_next.separation_from(sun_app_next).degrees

        waxing = elong_next > elongation

        # map to phase name
        if illumination_pct < 1.0:
            phase_name = "new moon"
        elif illumination_pct < 49.0:
            phase_name = "waxing crescent" if waxing else "waning crescent"
        elif 49.0 <= illumination_pct <= 51.0:
            phase_name = "first quarter" if waxing else "last quarter"
        elif illumination_pct < 98.0:
            phase_name = "waxing gibbous" if waxing else "waning gibbous"
        else:
            phase_name = "full moon"

        return {"phase": phase_name, "illumination": illumination_pct}

    except Exception as e:
        print(f"[ERROR][moon] failed to compute moon phase: {e}")
        return {"phase": "unknown", "illumination": None}
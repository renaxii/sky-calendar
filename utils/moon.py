from skyfield.api import load

ts = load.timescale()

def get_moon_phase(selected_date):

    eph = load("de421.bsp")

    t = ts.utc(
        selected_date.year,
        selected_date.month,
        selected_date.day
    )

    phase = eph["earth"].at(t).observe(eph["moon"]).apparent()

    # placeholder until illumination calculation added
    return {
        "phase": "coming soon",
        "illumination": 0
    }
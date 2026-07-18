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
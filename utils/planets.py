from skyfield.api import load

ts = load.timescale()

PLANETS = [
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter barycenter",
    "Saturn barycenter"
]

def get_visible_planets(selected_date):

    # placeholder
    return [
        "Venus",
        "Mars"
    ]
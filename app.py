import streamlit as st
from streamlit_searchbox import st_searchbox
from datetime import date

from utils.location import search_locations
from utils.weather import get_weather
from utils.sun import get_sun_times
from utils.score import calculate_score
from utils.nasa import get_apod
from utils.moon import get_moon_phase
from utils.planets import get_visible_planets

st.set_page_config(
    page_title="sky calendar",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>

.block-container{
    padding-top:2rem;
    max-width:1200px;
}

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}

[data-testid="stHeader"] {
    background: transparent;
}

div[data-testid="stMetric"]{
    background:#15243D;
    border-radius:18px;
    padding:15px;
}

div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stMarkdownContainer"]){
    border-radius:18px;
}

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: "Inter", sans-serif;
}

h1 {
    font-size: 3rem;
    letter-spacing: -0.03em;
    font-weight: 500;
}

h2, h3, h4, h5, h6,
.stTitle,
.stHeading {
    font-family: "Outfit", sans-serif;
    color:white;
    font-weight:600;
}

p, span, div {
    font-family: "Inter", sans-serif;
}

</style>
""", unsafe_allow_html=True)

# store location between reruns
if "lat" not in st.session_state:
    st.session_state.lat = None

if "lon" not in st.session_state:
    st.session_state.lon = None

if "location_name" not in st.session_state:
    st.session_state.location_name = None


with st.sidebar:

    st.title("settings")
    def location_search(query):
        if not query:
            return []

        locations = search_locations(query)

        return [
            (
                f"{x.get('name', '')}, {x.get('state', '')}, {x.get('country', '')}",
                x
            )
            for x in locations
        ]


    selected_location = st_searchbox(
        location_search,
        placeholder="search location",
        key="location_search"
    )

    selected_date = st.date_input(
        "choose a date",
        value=date.today()
    )

    units = st.selectbox(
        "units",
        ["metric", "imperial"]
    )

if selected_location:

    st.session_state.lat = selected_location["latitude"]
    st.session_state.lon = selected_location["longitude"]

    st.session_state.location_name = (
        f"{selected_location.get('name', '')}, "
        f"{selected_location.get('state', '')}, "
        f"{selected_location.get('country', '')}"
    )

# prepare variables
weather = None
sun = None
score = None
apod = None
moon = None
planets = []

# always load APOD and moon phase (APOD does not depend on location)
try:
    selected_date
except NameError:
    selected_date = date.today()

try:
    units
except NameError:
    units = "metric"

apod = get_apod(selected_date)
moon = get_moon_phase(selected_date)

# if we have a location, load weather, sun, score, planets
if st.session_state.lat is not None and st.session_state.lon is not None:
    print(f"[DEBUG][app] selected location: {st.session_state.location_name}")
    print(f"[DEBUG][app] lat={st.session_state.lat} lon={st.session_state.lon} date={selected_date.isoformat()}")

    weather = get_weather(
        st.session_state.lat,
        st.session_state.lon,
        units
    )

    sun = get_sun_times(
        st.session_state.location_name,
        st.session_state.lat,
        st.session_state.lon,
        selected_date
    )

    score = calculate_score(
        weather.get("clouds", 0),
        weather.get("humidity", 0)
    )

    planets = get_visible_planets(
        st.session_state.lat,
        st.session_state.lon,
        selected_date
    )

st.title("sky calendar")
st.caption("a dashboard for stargazers")

st.divider()

# top summary cards
col1, col2, col3, col4 = st.columns(4)

card_style = """
background:#15243D;
border-radius:18px;
padding:16px;
text-align:center;
color:white;
display:flex;
align-items:center;
justify-content:center;
"""


def load_icon(name: str) -> str:
    path = f"assets/icons/{name}.svg"
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

with col1:
    with st.container():
        title = "moon"
        phase = moon.get("phase") if moon else None
        svg = load_icon("moon")
        value = phase or "--"
        st.markdown(
            f"<div style='{card_style} height:105px; display:flex; flex-direction:column; align-items:center; justify-content:center;'><div style='font-size:11px;text-transform:lowercase;margin-bottom:6px'>{title}</div><div style='color:inherit'>{svg}</div><div style='font-size:12px;margin-top:6px;white-space:normal;max-width:120px'>{value}</div></div>",
            unsafe_allow_html=True,
        )

with col2:
    with st.container():
        title = "cloud cover"
        value = f"{weather['clouds']}%" if weather else "--"
        svg = load_icon("cloud")
        st.markdown(
            f"<div style='{card_style} height:105px; display:flex; flex-direction:column; align-items:center; justify-content:center; color:white;'><div style='font-size:11px;text-transform:lowercase;margin-bottom:6px'>{title}</div><div style='color:inherit'>{svg}</div><div style='font-size:14px;margin-top:6px'>{value}</div></div>",
            unsafe_allow_html=True,
        )

with col3:
    with st.container():
        title = "observing score"
        value = f"{score}/100" if score is not None else "--"
        svg = load_icon("telescope")
        st.markdown(
            f"<div style='{card_style} height:105px; display:flex; flex-direction:column; align-items:center; justify-content:center; color:white;'><div style='font-size:11px;text-transform:lowercase;margin-bottom:6px'>{title}</div><div style='color:inherit'>{svg}</div><div style='font-size:14px;margin-top:6px'>{value}</div></div>",
            unsafe_allow_html=True,
        )

with col4:
    with st.container():
        title = "iss pass"
        value = "--"
        svg = load_icon("drone")
        st.markdown(
            f"<div style='{card_style} height:105px; display:flex; flex-direction:column; align-items:center; justify-content:center; color:white;'><div style='font-size:11px;text-transform:lowercase;margin-bottom:6px'>{title}</div><div style='color:inherit'>{svg}</div><div style='font-size:12px;margin-top:6px'>{value}</div></div>",
            unsafe_allow_html=True,
        )

st.divider()

# main layout
left, right = st.columns([2,1])

with left:

    with st.container(border=True):
        st.subheader("selected date")
        st.write(
            selected_date
        )

    st.write("")

    with st.container(border=True):
        st.subheader("planets visible tonight")
        if planets:
            if isinstance(planets, list) and planets:
                for planet in planets:
                    st.write(f"• {planet}")
            else:
                st.write("no planets visible")
        else:
            st.write("no planets visible")

    st.write("")

    with st.container(border=True):
        st.subheader("NASA astronomy picture")
        if apod:
            if apod.get("media_type") == "image":

                st.image(
                    apod["url"],
                    use_container_width=True
                )
            elif apod.get("media_type") == "video":

                st.video(
                    apod["url"]
                )
            st.markdown(
                f"**{apod['title']}**"
            )
            st.caption(
                apod["date"]
            )
            with st.expander("description"):

                st.write(
                    apod["explanation"]
                )
        else:
            st.write(
                "unable to load NASA astronomy picture"
            )

with right:

    with st.container(border=True):

        st.subheader("sun")

        if sun:
            st.write(
                f"sunrise: {sun['sunrise'].strftime('%I:%M %p')}"
            )
            st.write(
                f"sunset: {sun['sunset'].strftime('%I:%M %p')}"
            )

        else:
            st.write(
                "sunrise: --"
            )
            st.write(
                "sunset: --"
            )

    st.write("")

    with st.container(border=True):
        st.subheader("weather")
        if weather:
            unit = "F" if units == "imperial" else "C"
            st.write(
                f"temperature: {weather['temperature']}° {unit}"
            )
            st.write(
                f"cloud cover: {weather['clouds']}%"
            )
            st.write(
                f"humidity: {weather['humidity']}%"
            )

        else:
            st.write(
                "temperature: --"
            )
            st.write(
                "cloud cover: --"
            )
            st.write(
                "humidity: --"
            )

    st.write("")

    with st.container(border=True):
        st.subheader("events")
        st.write(
            "meteor showers"
        )
        st.write(
            "ISS flyovers"
        )
        st.write(
            "rocket launches"
        )

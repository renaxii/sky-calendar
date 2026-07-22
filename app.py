import streamlit as st
from streamlit_searchbox import st_searchbox
from datetime import date
from urllib.parse import quote_plus

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

/* Micro-interactions and link-card styles */
.card-hoverable {
    transition: transform 200ms ease-out, filter 200ms ease-out, box-shadow 200ms ease-out;
}
.card-hoverable:hover {
    transform: translateY(-3px);
    filter: brightness(1.06);
    box-shadow: 0 8px 20px rgba(0,0,0,0.35);
}
.link-card {
    display:inline-flex;
    gap:6px;
    align-items:center;
    justify-content:center;
    background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
    border-radius:18px;
    padding:8px 12px;
    font-size:13px;
    text-transform:lowercase;
    color:inherit;
    text-decoration:none;
    border: 1px solid rgba(255,255,255,0.06);
    box-shadow: 0 2px 6px rgba(0,0,0,0.20);
}
.link-card:link, .link-card:visited { color: inherit; text-decoration: none; }
.link-card .link-icon {
    display:inline-flex;
    width:16px;height:16px;
    align-items:center;justify-content:center;
    margin-left:6px;
    transition: transform 180ms ease-out, filter 180ms ease-out;
}

.link-card .link-text {
    display:inline-block;
    text-align:center;
    line-height:1;
}
.link-card:hover {
    transform: translateY(-3px) scale(1.01);
    filter: brightness(1.08);
    box-shadow: 0 10px 24px rgba(0,0,0,0.35);
}
.link-card:hover .link-icon { transform: translateX(2px); }
.apod-image {
    width:100%;
    border-radius:8px;
    transition: transform 220ms ease-out, filter 220ms ease-out;
}
.apod-image:hover { transform: scale(1.01); filter: brightness(1.02); }

@media (prefers-reduced-motion: reduce) {
    .card-hoverable, .link-card, .apod-image { transition: none !important; transform: none !important; }
}

</style>
""", unsafe_allow_html=True)



# cached geocoding helper: used by the sidebar search suggestions
@st.cache_data(ttl=600)
def geocode_cached(query: str, limit: int = 8):
    try:
        results = search_locations(query)
        if not results:
            return []
        return results[:limit]
    except Exception:
        return []

# helper: load Lucide SVGs from assets

# store location between reruns
if "lat" not in st.session_state:
    st.session_state.lat = None

if "lon" not in st.session_state:
    st.session_state.lon = None

if "location_name" not in st.session_state:
    st.session_state.location_name = None


with st.sidebar:

    st.title("settings")
    # location search: show suggestions as the user types using st_searchbox
    def location_search(query):
        if not query or len(query.strip()) < 2:
            return []
        results = geocode_cached(query, limit=8)
        return [
            (
                f"{x.get('name', '')}, {x.get('state', '')}, {x.get('country', '')}",
                x
            )
            for x in results
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
# ensure defaults without evaluating bare variables that can render
if 'selected_date' not in globals() and 'selected_date' not in locals():
    selected_date = date.today()

if 'units' not in globals() and 'units' not in locals():
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
def render_link_card(text: str, url: str, icon_name: str = "external-link", extra_classes: str = ""):
    svg = load_icon(icon_name)
    safe_text = text
    icon_html = f"<span class='link-icon'>{svg}</span>" if svg else ""
    return st.markdown(
        f"<a class='link-card card-hoverable {extra_classes}' href='{url}' target='_blank' rel='noopener noreferrer' aria-label='{safe_text}'><span class='link-text'>{safe_text}</span>{icon_html}</a>",
        unsafe_allow_html=True,
    )

# (no pending search processing needed when using st_searchbox)

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

        # small secondary link card for exploring visible planets
        ext_svg = load_icon("external-link")
        if st.session_state.lat is not None and st.session_state.lon is not None:
            planets_url = f"https://in-the-sky.org/skymap.php?lat={st.session_state.lat}&lon={st.session_state.lon}&day={selected_date.isoformat()}"
        else:
            planets_url = "https://in-the-sky.org/"

        render_link_card("explore visible planets", planets_url)

    st.write("")

    with st.container(border=True):
        st.subheader("NASA astronomy picture")
        if apod:
            if apod.get("media_type") == "image":
                # render inline so we can apply hover effect and rounded corners
                st.markdown(f"<img src='{apod['url']}' class='apod-image' alt='apod'>", unsafe_allow_html=True)
            elif apod.get("media_type") == "video":
                st.video(apod["url"])

            st.markdown(f"**{apod['title']}**")
            st.caption(apod["date"])

            with st.expander("description"):
                st.write(apod["explanation"])

            # small secondary link card to official APOD page
            try:
                apod_suffix = selected_date.strftime('%y%m%d')
                apod_url = f"https://apod.nasa.gov/apod/ap{apod_suffix}.html"
            except Exception:
                apod_url = "https://apod.nasa.gov/"

            render_link_card("view on NASA", apod_url)
        else:
            st.write("unable to load NASA astronomy picture")

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

            # small secondary link to detailed forecast (opens externally)
            location_for_search = st.session_state.location_name.split(',')[0].strip() if st.session_state.location_name else ''
            if st.session_state.lat is not None and st.session_state.lon is not None:
                # Weather.com supports lat,lon in the URL
                forecast_url = f"https://weather.com/weather/today/l/{st.session_state.lat},{st.session_state.lon}"
            elif location_for_search:
                forecast_url = f"https://weather.com/search/enhancedlocalsearch?where={quote_plus(location_for_search)}"
            else:
                forecast_url = "https://weather.com/"

            render_link_card("view detailed forecast", forecast_url)

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

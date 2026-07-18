import streamlit as st
from datetime import date

from utils.location import search_locations
from utils.weather import get_weather
from utils.sun import get_sun_times
from utils.score import calculate_score


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

h1{
    color:white;
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
    city = st.text_input(
        "search location",
        placeholder="city name"
    )

    selected_location = None

    if city:

        locations = search_locations(city)

        if locations:

            selected_location = st.selectbox(
                "choose location",
                locations,
                format_func=lambda x:
                    f"{x.get('name', '')}, {x.get('state', '')}, {x.get('country', '')}"
            )

            if selected_location:

                st.session_state.lat = selected_location["latitude"]
                st.session_state.lon = selected_location["longitude"]

                st.session_state.location_name = (
                    f"{selected_location.get('name', '')}, "
                    f"{selected_location.get('state', '')}, "
                    f"{selected_location.get('country', '')}"
                )

    if st.session_state.location_name:
        st.write(
            f"using: {st.session_state.location_name}"
        )

    selected_date = st.date_input(
        "choose a date",
        value=date.today()
    )

    units = st.selectbox(
        "units",
        ["metric", "imperial"]
    )

weather = None
sun = None
score = None

if (
    st.session_state.lat is not None
    and st.session_state.lon is not None
):

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
        weather["clouds"],
        weather["humidity"]
    )

st.title("sky calendar")
st.caption("a dashboard for stargazers")

st.divider()

# top metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "moon",
        "--"
    )


with col2:

    if weather:
        st.metric(
            "cloud cover",
            f"{weather['clouds']}%"
        )
    else:
        st.metric(
            "cloud cover",
            "--"
        )


with col3:

    if score is not None:
        st.metric(
            "observing score",
            f"{score}"
        )

    else:
        st.metric(
            "observing score",
            "--"
        )


with col4:
    st.metric(
        "ISS pass",
        "--"
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
        st.write(
            "coming soon..."
        )

    st.write("")

    with st.container(border=True):
        st.subheader("NASA astronomy picture")
        st.write(
            "coming soon..."
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
                f"temperature: {weather['temperature']}{unit}"
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
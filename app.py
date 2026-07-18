import streamlit as st
from datetime import date

from utils.location import get_coordinates
from utils.weather import get_weather
from utils.sun import get_sun_times
from utils.score import calculate_score

st.set_page_config(
    page_title="sky calendar",
    page_icon="🌌",
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

with st.sidebar:

    st.title("Settings")

    city = st.text_input(
        "location",
        placeholder="city"
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

if city:

    lat, lon = get_coordinates(city)

    weather = get_weather(
        lat,
        lon,
        units
    )

    sun = get_sun_times(
        city,
        lat,
        lon
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
    st.metric("moon", "--")

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
        st.metric("observing score", f"{score}")
    else:
        st.metric("observing score", "--")

with col4:
    st.metric("ISS pass", "--")
st.divider()

# main layout
left, right = st.columns([2,1])

with left:

    with st.container(border=True):
        st.subheader("selected date")
        st.write(selected_date)

    st.write("")

    with st.container(border=True):
        st.subheader("planets visible tonight")
        st.write("coming soon...")

    st.write("")

    with st.container(border=True):
        st.subheader("NASA astronomy picture")
        st.write("coming soon...")

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
            st.write("sunrise: --")
            st.write("sunset: --")

    st.write("")

    with st.container(border=True):
        st.subheader("weather")
        if weather:
            unit = "F" if units == "imperial" else "C"

            st.write(f"temperature: {weather['temperature']}{unit}")
            st.write(f"cloud cover: {weather['clouds']}%")
            st.write(f"humidity: {weather['humidity']}%")
        else:
            st.write("temperature: --")
            st.write("cloud cover: --")
            st.write("humidity: --")

    st.write("")

    with st.container(border=True):
        st.subheader("events")
        st.write("meteor showers")
        st.write("ISS flyovers")
        st.write("rocket launches")
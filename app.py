import streamlit as st
from datetime import date

st.set_page_config(
    page_title="sky calendar",
    page_icon="🌌",
    layout="wide"
)

st.markdown("""
<style>

.block-container{
    padding-top:2rem;
    max-width:1200px;
}

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

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
        "Location",
        placeholder="City"
    )

    selected_date = st.date_input(
        "Choose a date",
        value=date.today()
    )

    units = st.selectbox(
        "Units",
        ["Metric", "Imperial"]
    )

st.title("Sky Calendar")
st.caption("a dashboard for stargazers")

st.divider()

# top metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Moon", "--")

with col2:
    st.metric("Cloud Cover", "--")

with col3:
    st.metric("Observing Score", "--")

with col4:
    st.metric("ISS Pass", "--")
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
        st.write("sunrise: --")
        st.write("sunset: --")

    st.write("")

    with st.container(border=True):
        st.subheader("weather")
        st.write("temperature: --")
        st.write("cloud cover: --")
        st.write("humidity: --")

    st.write("")

    with st.container(border=True):
        st.subheader("events")
        st.write("meteor showers")
        st.write("ISS flyovers")
        st.write("rocket launches")
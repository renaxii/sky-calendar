import streamlit as st
from datetime import date

st.set_page_config(
    page_title="Stargaze",
    page_icon="🌌",
    layout="wide"
)

st.title("Sky Calendar")
st.subheader("a dashboard for stargazers")

# Today's date
st.write(f"**Today:** {date.today().strftime('%B %d, %Y')}")

st.divider()

st.write(
    "Welcome! This app will help you explore tonight's sky, "
    "including moon phases, visible planets, weather conditions, "
    "and NASA's Astronomy Picture of the Day."
)
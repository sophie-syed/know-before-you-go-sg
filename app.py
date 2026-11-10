import streamlit as st

from kbyg.core import load_places
from kbyg.ui import hero, required_disclaimer, require_password, setup_page


setup_page("Home")
require_password()
places = load_places()

hero(
    "Know Before You Go SG",
    "Turn official Singapore heritage data into a short outing that fits your time, interests and walking comfort.",
)

required_disclaimer()

left, right = st.columns([3, 2])
with left:
    st.subheader("Your next Singapore story starts here")
    st.write(
        "The app simplifies the process of planning a self-guided visit to Singapore’s "
        "official heritage places. Tell it where you want to start, how much time you have "
        "and what you want to learn. It will suggest a manageable sequence of national "
        "monuments and marked historic sites, then explain the stories connecting them."
    )
    st.page_link("pages/1_Plan_My_Outing.py", label="Plan my outing", icon="🗺️")
    st.page_link("pages/2_Explore_a_Place.py", label="Explore a place", icon="🔎")

with right:
    st.markdown("### Passport collection")
    st.metric("Official heritage places", f"{len(places)}")
    st.metric("National monuments", sum(place.place_type == "National monument" for place in places))
    st.metric("Historic sites", sum(place.place_type == "Historic site" for place in places))

st.divider()
st.subheader("Try your first passport trail")
st.info(
    "I have two hours around Telok Ayer, prefer walking, and want to learn about "
    "Singapore’s multicultural history and architecture."
)

st.subheader("Built from public information")
st.write(
    "The prototype combines National Heritage Board datasets published on data.gov.sg, "
    "official Roots.gov.sg entries and optional walking-route estimates from Singapore "
    "Land Authority’s OneMap service."
)
st.caption(
    "This is a planning and learning tool. Check official websites before travelling for "
    "current access, opening hours, admission charges and accessibility information."
)


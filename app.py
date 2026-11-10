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

st.subheader("Start here")
st.write("Choose the journey that matches what you want to do today.")

journey_one, journey_two = st.columns(2)
with journey_one:
    with st.container(border=True):
        st.markdown("### 🗺️ I want a ready-made outing")
        st.write(
            "Use **Plan My Outing**. Choose a neighbourhood, time, walking distance and "
            "interests. You’ll receive a route, photographs, a cultural story and links for navigation."
        )
        st.page_link(
            "pages/1_Plan_My_Outing.py",
            label="Create my heritage trail",
            icon="🧭",
        )

with journey_two:
    with st.container(border=True):
        st.markdown("### 🔎 I want to discover a particular place")
        st.write(
            "Use **Explore Heritage Places**. Search or filter the national map, select a site, "
            "read its official information and ask the cultural guide follow-up questions."
        )
        st.page_link(
            "pages/2_Explore_Heritage_Places.py",
            label="Explore heritage places",
            icon="🌺",
        )

with st.expander("What is each page for?"):
    st.markdown(
        """
- **app:** The homepage you are viewing now, with orientation and the required prototype notice.
- **Plan My Outing:** Generates a personalised, downloadable heritage trail.
- **Explore Heritage Places:** Combines the national cultural map, place photographs and grounded cultural-guide questions.
- **About Us:** Explains the problem, project objectives, features, official data sources and limitations.
- **Methodology:** Shows how the data, route logic and LLM work, including a flowchart for each use case.
"""
    )

left, right = st.columns([3, 2])
with left:
    st.subheader("Your next Singapore story starts here")
    st.write(
        "The app simplifies the process of planning a self-guided visit to Singapore’s "
        "official heritage places. Tell it where you want to start, how much time you have "
        "and what you want to learn. It will suggest a manageable sequence of national "
        "monuments and marked historic sites, then explain the stories connecting them."
    )

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


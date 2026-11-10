import streamlit as st

from kbyg.core import load_places
from kbyg.ui import hero, required_disclaimer, require_password, setup_page


setup_page("Start Here")
require_password()
places = load_places()

hero(
    "Know Before You Go SG",
    "Turn official Singapore heritage data into a short outing that fits your time, interests and walking comfort.",
)

required_disclaimer()

st.subheader("What would you like to do?")
st.write("Choose either card—the whole card is clickable.")

journey_one, journey_two = st.columns(2)
with journey_one:
    st.markdown(
        """
        <a class="journey-card" href="./plan-my-outing" target="_self">
          <strong>🗺️ I want a ready-made outing</strong>
          <span>Choose your area, available time, walking distance and interests. Get a suggested route with photographs, stories and navigation links.</span>
          <em>Plan my outing →</em>
        </a>
        """,
        unsafe_allow_html=True,
    )

with journey_two:
    st.markdown(
        """
        <a class="journey-card" href="./explore-heritage-places" target="_self">
          <strong>🔎 I want to discover a particular place</strong>
          <span>Search the heritage map, open a place card, view photographs and ask the cultural guide follow-up questions.</span>
          <em>Explore heritage places →</em>
        </a>
        """,
        unsafe_allow_html=True,
    )

with st.expander("What is each page for?"):
    st.markdown(
        """
- **Start Here:** A quick guide to choosing the right part of the app.
- **Plan My Outing:** Creates a personalised, downloadable heritage trail.
- **Explore Heritage Places:** Lets you browse the national map, view place photographs and ask grounded cultural-guide questions.
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
st.subheader("Need inspiration for your first outing?")
st.write(
    "A good first route is **Telok Ayer**, with about **two hours**, interests in "
    "**multicultural history** and **architecture**, and a comfortable walking distance. "
    "Open the planner and select those options to create your own version."
)
st.page_link(
    "pages/1_Plan_My_Outing.py",
    label="Open the outing planner",
    icon="🧭",
    use_container_width=True,
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

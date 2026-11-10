import streamlit as st

from kbyg.core import load_places
from kbyg.ui import hero, required_disclaimer, setup_page


setup_page("Start Here")
places = load_places()

hero(
    "Know Before You Go SG",
    "Choose whether to plan a complete outing or explore one place, using official Singapore heritage information.",
)

required_disclaimer()

st.subheader("What would you like to do?")
st.write("Choose either card—the whole card is clickable.")

journey_one, journey_two = st.columns(2)
with journey_one:
    with st.container(key="journey_plan"):
        if st.button(
            "🗺️  I want a ready-made outing\n\nChoose your area, available time, walking distance "
            "and interests. Get a suggested route with photographs, stories and navigation links.\n\nPlan my outing →",
            width="stretch",
        ):
            st.switch_page("pages/1_Plan_My_Outing.py")

with journey_two:
    with st.container(key="journey_explore"):
        if st.button(
            "🔎  I want to discover a particular place\n\nSearch the heritage map, open a place card, view "
            "photographs and ask the cultural guide follow-up questions.\n\nExplore heritage places →",
            width="stretch",
        ):
            st.switch_page("pages/2_Explore_Heritage_Places.py")

with st.expander("What is each page for?"):
    st.markdown(
        """
- **Start Here:** A quick guide to choosing the right part of the app.
- **Plan My Outing:** Creates a personalised, downloadable heritage trail.
- **Explore Heritage Places:** Lets you browse the national map, view place photographs and ask grounded cultural-guide questions.
- **About Us:** Explains the problem, project objectives, features, official data sources and limitations.
- **Methodology:** Shows how the website was built, how the route logic and LLM work, and what the prototype cannot yet do.
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
    st.markdown("### Heritage places available")
    st.caption("Official places the app can search and recommend in your outing.")
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

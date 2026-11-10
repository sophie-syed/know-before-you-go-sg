import random

import pandas as pd
import streamlit as st

from kbyg.ai import ai_available, ask_grounded_guide
from kbyg.core import load_places, place_context
from kbyg.ui import hero, place_card, place_map, setup_page


# A deliberately varied discovery set: faiths, communities, civic life, arts,
# hospitality and public service. Session history prevents repetitive surprises.
FEATURED_DISCOVERY_NAMES = {
    "38 Oxley Road",
    "Al-Abrar Mosque",
    "Former Nagore Dargah",
    "Jamae Mosque",
    "Pondok Peranakan Gelam Club",
    "Sri Mariamman Temple",
    "Sultan Mosque",
    "Thian Hock Keng",
}


setup_page("Explore Heritage Places", "🔎")
hero(
    "Ask our heritage guide",
    "Choose a Singapore heritage place, discover its story and ask the questions you are curious about.",
)

places = load_places()
st.markdown(
    """
    <div class="passport-panel">
    <b>How to use this page</b><br>
    Find a place by searching—or let us surprise you with one.<br>
    Ask a suggested question or type one naturally in your own words.<br>
    Then read the answer alongside its official description, photograph and source link.
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Step 1 · Find a place you’d like to know about")
types = st.multiselect(
    "Place type",
    ["National monument", "Historic site"],
    default=["National monument", "Historic site"],
)
search = st.text_input(
    "Filter by name, description or address",
    placeholder="Try: mosque, Fort Canning, Telok Ayer...",
)
filtered = [place for place in places if place.place_type in types]
if search:
    needle = search.casefold()
    filtered = [
        place
        for place in filtered
        if needle in f"{place.name} {place.description} {place.address}".casefold()
    ]

if not filtered:
    st.warning("No official heritage places matched those filters.")
    st.stop()

st.write(f"Showing **{len(filtered)}** official heritage places.")

discovery_places = [place for place in filtered if place.name in FEATURED_DISCOVERY_NAMES]
if st.button(
    "✨ Surprise me — spark my curiosity",
    type="primary",
    help="Choose a varied Singapore heritage story, then ask the guide whatever it makes you wonder.",
    disabled=not discovery_places,
):
    history = st.session_state.get("surprise_history", [])
    available_names = {place.name for place in discovery_places}
    history = [name for name in history if name in available_names]
    remaining = [place for place in discovery_places if place.name not in history]
    if not remaining:
        history = []
        remaining = discovery_places
    surprise = random.choice(remaining)
    st.session_state["surprise_history"] = history + [surprise.name]
    st.session_state["explore_selected_name"] = surprise.name
    st.session_state["last_surprise_name"] = surprise.name

st.caption(
    "Not sure where to begin? Surprise Me rotates through a varied collection of Singapore "
    "stories without repeating one until you have explored the full set."
)

preferred_name = st.session_state.get("explore_selected_name")
default_index = next(
    (index for index, item in enumerate(filtered) if item.name == preferred_name),
    0,
)
selected_name = st.selectbox(
    "Choose a place to explore",
    [place.name for place in filtered],
    index=default_index,
    help="The map helps you see where the filtered places are; use this list to open one.",
)
st.session_state["explore_selected_name"] = selected_name
place = next(place for place in filtered if place.name == selected_name)
if st.session_state.get("last_surprise_name") == place.name:
    st.info(
        f"✨ Your surprise is **{place.name}**. Start with ‘Why does this place matter?’ "
        "or ask the guide whatever this place makes you curious about."
    )

with st.expander("Browse these places on the map", expanded=False):
    st.caption("Use the filters above to narrow the map, then choose a place from the list.")
    place_map(filtered)

st.subheader(f"Step 2 · Ask the cultural guide about {place.name}")
st.write(
    "Ask what makes it significant, what to notice when you visit, or how it connects "
    "to Singapore’s communities."
)
st.caption("Answers are grounded in the official government heritage sources linked on this page.")
suggestions = [
    "Why does this place matter?",
    "Explain this to a 10-year-old.",
    "What should I pay attention to when I arrive?",
    "How does this place connect to Singapore’s communities?",
]
suggested_question = st.selectbox("Start with a suggested question", suggestions)
own_question = st.text_area(
    "Or ask in your own words",
    placeholder="For example: Why are Jamae Mosque and Sri Mariamman Temple so close together?",
    help="If you type here, this question will be used instead of the suggested one.",
)
question = own_question.strip() or suggested_question
audience = st.selectbox(
    "Explanation for",
    ["General public", "A child", "A new resident", "A history enthusiast"],
)

if st.button("Ask the cultural guide", type="primary", disabled=not question):
    if not ai_available():
        st.info(
            "The official record below is available now. Configure the OpenAI key in "
            "Streamlit secrets to activate grounded follow-up answers."
        )
    else:
        with st.spinner("Reading the official information..."):
            try:
                st.session_state["place_answer"] = ask_grounded_guide(
                    question, place_context(place), audience
                )
                st.session_state["place_answer_for"] = place.place_id
            except Exception as exc:
                st.error(f"The AI guide could not respond: {exc}")

if (
    st.session_state.get("place_answer")
    and st.session_state.get("place_answer_for") == place.place_id
):
    st.success(st.session_state["place_answer"])

st.subheader(f"Step 3 · Discover {place.name}")
st.caption("See the government dataset summary, verified photograph where available, visit prompt and official source.")
place_card(place)

with st.expander("View the filtered government dataset"):
    table = pd.DataFrame(
        [
            {
                "Name": item.name,
                "Type": item.place_type,
                "Address": item.address,
                "Official source": item.official_url,
            }
            for item in filtered
        ]
    )
    st.dataframe(
        table,
        hide_index=True,
        width="stretch",
        column_config={
            "Official source": st.column_config.LinkColumn(
                display_text="View official heritage information"
            )
        },
    )

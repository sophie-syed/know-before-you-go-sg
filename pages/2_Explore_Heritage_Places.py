import pandas as pd
import streamlit as st

from kbyg.ai import ai_available, ask_grounded_guide
from kbyg.core import load_places, place_context
from kbyg.ui import hero, place_card, place_map, setup_page


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
    <b>1.</b> Search by a place, neighbourhood or theme and choose a heritage site.<br>
    <b>2.</b> Ask a suggested question or type one naturally in your own words.<br>
    <b>3.</b> Read the answer alongside the official description, photograph and source link.
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("1. Find a heritage place")
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
selected_name = st.selectbox(
    "Choose a place to explore",
    [place.name for place in filtered],
    help="The map helps you see where the filtered places are; use this list to open one.",
)
place = next(place for place in filtered if place.name == selected_name)

with st.expander("Browse these places on the map", expanded=False):
    st.caption("Use the filters above to narrow the map, then choose a place from the list.")
    place_map(filtered)

st.subheader(f"2. Ask the cultural guide about {place.name}")
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

st.subheader(f"3. Explore the official record for {place.name}")
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

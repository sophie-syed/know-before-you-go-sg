import pandas as pd
import streamlit as st

from kbyg.ai import ai_available, ask_grounded_guide
from kbyg.core import load_places, place_context
from kbyg.ui import hero, place_card, place_map, setup_page


setup_page("Explore Heritage Places", "🔎")
hero(
    "Explore Singapore’s heritage places",
    "Search or browse the national map, choose a place that catches your eye, then view its photograph and ask the cultural guide why it matters.",
)

places = load_places()
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
place_map(filtered)

st.divider()
st.subheader("Choose a place to explore")
selected_name = st.selectbox("Heritage place", [place.name for place in filtered])
place = next(place for place in filtered if place.name == selected_name)
place_card(place)

st.subheader("Ask the cultural guide")
suggestions = [
    "Why does this place matter?",
    "Explain this to a 10-year-old.",
    "What should I pay attention to when I arrive?",
    "What does the official information not tell me?",
]
question = st.selectbox("Start with a question", suggestions + ["Write my own question"])
if question == "Write my own question":
    question = st.text_area("Your question")
audience = st.selectbox(
    "Explanation for",
    ["General public", "A child", "A new resident", "A history enthusiast"],
)

if st.button("Ask", type="primary", disabled=not question):
    if not ai_available():
        st.info(
            "The official description above is available now. Configure the OpenAI key in "
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

with st.expander("View the filtered official dataset"):
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

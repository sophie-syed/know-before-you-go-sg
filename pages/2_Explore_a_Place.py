import streamlit as st

from kbyg.ai import ai_available, ask_grounded_guide
from kbyg.core import load_places, place_context
from kbyg.ui import hero, place_card, place_map, require_password, setup_page


setup_page("Explore a Place", "🔎")
require_password()
hero(
    "Explore a place",
    "Search official NHB places, read the source description, and ask a grounded cultural guide for a clearer explanation.",
)

places = load_places()
place_by_name = {place.name: place for place in places}
query = st.text_input("Search by name or address", placeholder="Try: mosque, Fort Canning, Telok Ayer...")

if query:
    needle = query.casefold()
    matches = [
        place for place in places
        if needle in f"{place.name} {place.address} {place.description}".casefold()
    ][:30]
else:
    matches = places

selected_name = st.selectbox("Choose a place", [place.name for place in matches]) if matches else None
if not selected_name:
    st.warning("No places matched that search.")
    st.stop()

place = place_by_name[selected_name]
place_map([place], height=320)
place_card(place)

st.divider()
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
audience = st.selectbox("Explanation for", ["General public", "A child", "A new resident", "A history enthusiast"])

if st.button("Ask", type="primary", disabled=not question):
    if not ai_available():
        st.info(
            "The official description above is available now. Add an OpenAI API key to Streamlit "
            "secrets to activate grounded follow-up answers."
        )
    else:
        with st.spinner("Reading the official description..."):
            try:
                st.session_state["place_answer"] = ask_grounded_guide(
                    question, place_context(place), audience
                )
            except Exception as exc:
                st.error(f"The AI guide could not respond: {exc}")

if st.session_state.get("place_answer"):
    st.success(st.session_state["place_answer"])


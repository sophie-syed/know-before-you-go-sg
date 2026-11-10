import pandas as pd
import streamlit as st

from kbyg.core import load_places
from kbyg.ui import hero, place_map, require_password, setup_page


setup_page("Cultural Map", "📍")
require_password()
hero(
    "Singapore’s cultural map",
    "Explore national monuments and marked historic sites published by the National Heritage Board.",
)

places = load_places()
types = st.multiselect(
    "Place type",
    ["National monument", "Historic site"],
    default=["National monument", "Historic site"],
)
search = st.text_input("Filter by name, description or address")
filtered = [place for place in places if place.place_type in types]
if search:
    needle = search.casefold()
    filtered = [
        place for place in filtered
        if needle in f"{place.name} {place.description} {place.address}".casefold()
    ]

st.write(f"Showing **{len(filtered)}** official heritage places.")
place_map(filtered)

table = pd.DataFrame(
    [
        {
            "Name": place.name,
            "Type": place.place_type,
            "Address": place.address,
            "Official source": place.official_url,
        }
        for place in filtered
    ]
)
st.dataframe(
    table,
    hide_index=True,
    width="stretch",
    column_config={"Official source": st.column_config.LinkColumn(display_text="Open Roots entry")},
)

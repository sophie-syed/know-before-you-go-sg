import streamlit as st

from kbyg.core import load_places
from kbyg.ui import hero, require_password, setup_page


setup_page("About Us", "ℹ️")
require_password()
hero(
    "About Know Before You Go SG",
    "A capstone prototype that helps residents turn official heritage data into manageable, meaningful outings.",
)

places = load_places()

st.subheader("Project scope")
st.write(
    "This prototype supports the citizen process of discovering official heritage information "
    "and planning a self-guided visit to Singapore’s officially recognised heritage places. "
    "Residents currently need to search, "
    "compare locations and decide what fits into a short outing. The application combines official "
    "geospatial data with transparent route selection and grounded LLM explanations."
)

st.subheader("Objectives")
st.markdown(
    """
- Help residents discover official heritage places near a chosen district.
- Personalise an outing by time, walking comfort and interests.
- Explain why each place matters using official source material.
- Preserve a clear path back to the authoritative government resource.
"""
)

st.subheader("Features")
st.markdown(
    """
1. **Personalised heritage planner:** selects and orders a manageable set of nearby stops.
2. **Grounded cultural guide:** explains a selected place or route using only supplied NHB context.
3. **Cultural map:** lets users search and inspect the source dataset directly.
"""
)

st.subheader("Official data sources")
st.markdown(
    f"""
- [National Monuments (GEOJSON)](https://data.gov.sg/collections/1461/datasets/d_b29c230ec6b609e29ed42f71ca9a8767/view) — National Heritage Board; {sum(p.place_type == 'National monument' for p in places)} records in this snapshot.
- [Historic Sites (GEOJSON)](https://data.gov.sg/collections/1460/datasets/d_31e16b12809e66673e90d8b04fdee1b2/view) — National Heritage Board; {sum(p.place_type == 'Historic site' for p in places)} records in this snapshot.
- Individual place descriptions and images link to [Roots.gov.sg](https://www.roots.gov.sg/).
- [OneMap Routing API](https://www.onemap.gov.sg/apidocs/routing) — Singapore Land Authority; used for official walking distance and time when configured.
"""
)

st.subheader("Limitations")
st.warning(
    "The prototype does not verify live access, opening hours, admission charges, closures or "
    "wheelchair accessibility. Straight-line estimates are not turn-by-turn navigation. Some "
    "historic-site markers commemorate places whose original buildings no longer exist. Users "
    "should check the linked official page before travelling."
)


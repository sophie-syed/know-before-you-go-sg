import streamlit as st

from kbyg.ui import hero, require_password, setup_page


setup_page("How It Works", "🧪")
require_password()
hero(
    "How this website works",
    "How official data becomes a personalised outing, how the AI guide is kept grounded, and what the prototype cannot yet do.",
)

st.subheader("How it was built")
st.write(
    "Know Before You Go SG is a Streamlit prototype built with Python. It combines National "
    "Heritage Board place records, deterministic route-planning logic, optional SLA OneMap "
    "walking estimates and an OpenAI-generated cultural explanation grounded in selected "
    "official records."
)

st.subheader("Data flow")
st.code(
    """NHB monuments + historic sites (GeoJSON) + SLA OneMap
                 ↓
Validate points and normalise common fields
                 ↓
Distance filter + interest matching
                 ↓
Time and walking constraints
                 ↓
Nearest-stop route ordering
                 ↓
Map, itinerary, walking estimates and official source links
                 ↓
LLM explanation using selected source records only""",
    language="text",
)

st.subheader("Use case 1: Personalised outing planner")
st.graphviz_chart(
    """
    digraph Planner {
      rankdir=TB;
      node [shape=box, style="rounded,filled", fillcolor="#F4EBDD", color="#99643D"];
      input [label="Choose area, time, walking limit and interests"];
      nearby [label="Find official places within a bounded radius"];
      score [label="Score interest matches in official text"];
      route [label="Order nearby stops and enforce limits"];
      result [label="Show map, itinerary, estimates and source links"];
      input -> nearby -> score -> route -> result;
    }
    """,
    width="stretch",
)

st.subheader("Use case 2: Grounded cultural guide")
st.graphviz_chart(
    """
    digraph Guide {
      rankdir=TB;
      node [shape=box, style="rounded,filled", fillcolor="#E8F0EC", color="#24483F"];
      select [label="Select a place or generated route"];
      retrieve [label="Retrieve matching official descriptions and URLs"];
      ask [label="Send bounded context and question to the LLM"];
      guard [label="Require unknowns to be stated, not invented"];
      answer [label="Return a clear answer with an official source link"];
      select -> retrieve -> ask -> guard -> answer;
    }
    """,
    width="stretch",
)

st.subheader("Recommendation logic")
st.write(
    "The app—not the LLM—selects route stops. It calculates straight-line distance using the "
    "Haversine formula, counts declared interest-keyword matches in official text, and orders a "
    "short candidate list using a nearest-neighbour heuristic. Every stop adds an assumed "
    "15-minute visit. Candidates that would exceed the user’s time or walking limit are removed."
)

st.subheader("LLM implementation")
st.write(
    "The OpenAI Responses API receives only the selected NHB records, the user’s general audience "
    "preference and the question. The developer instruction prohibits unsupported historical facts, "
    "opening hours, prices, accessibility claims and events. If no API key is configured, the app "
    "continues to provide deterministic routes and official descriptions without pretending that an "
    "LLM response was generated."
)

st.subheader("Privacy and safeguards")
st.markdown(
    """
- The app requests no name, NRIC, address, account or precise live location.
- User preferences are held only in the current Streamlit session.
- Every place card preserves the official Roots.gov.sg link.
- Estimates are labelled as estimates.
- Changing operational information is deliberately excluded from generated answers.
"""
)

st.subheader("Limitations and future improvements")
st.markdown(
    """
- **Accessibility information:** The NHB geospatial datasets do not consistently state whether entrances, paths, parking, seating or toilets are wheelchair accessible. The prototype therefore does not guess or label a missing value as “not accessible”. Future work could use verified venue information or Google Places accessibility fields, while clearly distinguishing **reported accessible**, **reported not accessible** and **information unavailable**.
- **Opening hours:** Historic markers and outdoor sites may not have opening hours, while operating venues can change their hours for holidays, events or renovations. Google Places could supply current hours, but requires a separately managed API key, billing and attribution. Users are directed to official sources and Google Maps to verify before travelling.
- **Walking routes:** Without a configured OneMap token, distance and time use straight-line estimates rather than turn-by-turn, step-free routing. Even OneMap walking estimates do not guarantee a wheelchair-accessible path.
- **Heritage photographs:** The NHB dataset generally supplies one photograph per place. Additional gallery images would require separate licensing and place-by-place verification.
- **Coverage and freshness:** The app reflects the included government-data snapshot. A place may be temporarily closed, under renovation or otherwise inaccessible after the dataset was published.
- **AI explanations:** The cultural guide is instructed to use only supplied official context, but generated wording can still be incomplete or inaccurate. Official source links remain the authority.
- **Prototype scope:** Accounts, saved outings, visited-place collections, real-time crowd information and live location tracking are deliberately excluded.
"""
)

st.info(
    "Future priority: add verified visit-planning information only when its source, update date "
    "and unknown values can be shown transparently."
)

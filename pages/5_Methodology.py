import streamlit as st

from kbyg.ui import hero, setup_page


setup_page("Methodology", "🧪")
hero(
    "How this website works",
    "Follow how official data becomes a personalised outing, how the AI guide is kept grounded, and what the prototype cannot yet do.",
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
      rankdir=LR;
      graph [pad="0.1", nodesep="0.22", ranksep="0.32", bgcolor="transparent"];
      node [shape=box, style="rounded,filled", fillcolor="#F4EBDD", color="#99643D", fontsize=10, margin="0.10,0.07"];
      edge [color="#99643D", arrowsize=0.65];
      input [label="Choose area, time,\nwalking limit and interests"];
      match [label="Match nearby places\nusing official NHB text"];
      route [label="Order stops within\ntime and distance limits"];
      result [label="Show story, itinerary,\nstops and route map"];
      input -> match -> route -> result;
    }
    """,
    width="stretch",
)

st.subheader("Use case 2: Grounded cultural guide")
st.graphviz_chart(
    """
    digraph Guide {
      rankdir=LR;
      graph [pad="0.1", nodesep="0.22", ranksep="0.32", bgcolor="transparent"];
      node [shape=box, style="rounded,filled", fillcolor="#E8F0EC", color="#24483F", fontsize=10, margin="0.10,0.07"];
      edge [color="#24483F", arrowsize=0.65];
      select [label="Select a place\nor generated route"];
      retrieve [label="Retrieve matching\nofficial context"];
      ask [label="Ask LLM with\ngrounding guardrails"];
      answer [label="Return explanation\nand official link"];
      select -> retrieve -> ask -> answer;
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
- **Walking routes:** Without a configured OneMap token, distance and time use straight-line estimates rather than turn-by-turn, step-free routing. A OneMap access token currently expires after three days and would need regular regeneration; this educational deployment deliberately avoids depending on that short-lived credential so the live demonstration remains stable. Even OneMap walking estimates do not guarantee a wheelchair-accessible path.
- **Heritage photographs:** The NHB dataset generally supplies one photograph per place. Additional gallery images would require separate licensing and place-by-place verification.
- **Coverage and freshness:** The app reflects the included government-data snapshot. A place may be temporarily closed, under renovation or otherwise inaccessible after the dataset was published.
- **Curated evidence, not open-web browsing:** The LLM receives only selected NHB datasets and verified context from Roots.gov.sg, NHB heritage resources and other named public-sector sources. It cannot roam the open internet. This reduces unsupported claims, but also means some places have less detail than others.
- **AI explanations:** The cultural guide is instructed to use only the curated evidence supplied with the request, but generated wording can still be incomplete or inaccurate. Official source links remain the authority.
- **Prototype scope:** Accounts, saved outings, visited-place collections, real-time crowd information and live location tracking are deliberately excluded.
"""
)

st.info(
    "Future priority: add verified visit-planning information only when its source, update date "
    "and unknown values can be shown transparently."
)

st.subheader("Assignment requirements demonstrated")
st.caption("Use this table as a quick guide to where each capstone requirement is demonstrated.")
st.dataframe(
    [
        {
            "Requirement": "Two complete use cases",
            "How this app demonstrates it": "Personalised outing planning and grounded exploration of an individual heritage place.",
            "Where to see it": "Plan My Outing; Explore Heritage Places",
        },
        {
            "Requirement": "Official, publicly accessible information",
            "How this app demonstrates it": "Uses NHB National Monuments and Historic Sites datasets, Roots.gov.sg records and optional SLA OneMap routing.",
            "Where to see it": "Place cards, source links, About Us",
        },
        {
            "Requirement": "Non-identifying personalisation",
            "How this app demonstrates it": "Adapts routes using area, time, walking comfort, interests, audience and guide style without requesting names or sensitive data.",
            "Where to see it": "Plan My Outing form",
        },
        {
            "Requirement": "Interactive explanations and follow-ups",
            "How this app demonstrates it": "Creates route stories and answers suggested or natural-language cultural questions using curated official evidence.",
            "Where to see it": "Route Story tab; Ask the Cultural Guide",
        },
        {
            "Requirement": "Effective presentation formats",
            "How this app demonstrates it": "Uses forms, summary metrics, itinerary tables, maps, photographs, stop cards, downloadable guides and Google Maps hand-off.",
            "Where to see it": "Generated outing; heritage place records",
        },
        {
            "Requirement": "About Us and Methodology documentation",
            "How this app demonstrates it": "Documents scope, objectives, features, data sources, implementation, limitations and one process diagram per use case.",
            "Where to see it": "About Us; Methodology",
        },
        {
            "Requirement": "Deployment and safeguards",
            "How this app demonstrates it": "Runs on Streamlit Community Cloud with password protection and the required educational-prototype disclaimer.",
            "Where to see it": "Live app entry page",
        },
    ],
    hide_index=True,
    width="stretch",
    column_config={
        "Requirement": st.column_config.TextColumn(width="medium"),
        "How this app demonstrates it": st.column_config.TextColumn(width="large"),
        "Where to see it": st.column_config.TextColumn(width="medium"),
    },
)

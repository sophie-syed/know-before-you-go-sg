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

with st.expander("Exact rules used by this prototype"):
    st.markdown(
        """
| Stage | Rule used |
|---|---|
| Starting point | Uses a fixed coordinate for the selected neighbourhood, not the visitor’s live location. |
| Nearby places | Searches within the selected walking limit × 0.8 + 0.5 km, capped at 4.5 km. |
| Interest matching | Searches each place’s official name, description and address for predefined keywords. |
| Interest score | Each matched keyword adds 2 points, up to 3 matches for each selected interest. |
| Record bonus | Adds 1 point when the government record contains a description. |
| Monument bonus | Adds 1 point for a national monument. |
| Candidate shortlist | Sorts by interest match, then proximity and name; the first 24 places form the candidate pool. |
| Stop ordering | Selects a nearby next stop, with a small preference for stronger interest matches. |
| Number of stops | Allows 2–6 stops depending on the time available. |
| Visit time | Assumes 15 minutes at every stop. |
| Walking pace | Assumes 4.5 km per hour when OneMap is not configured. |
| Route limits | Skips an additional stop when it would exceed the selected time or walking-distance limit. |
| Distance estimate | Adds straight-line distances from the starting point through successive stops; it does not include a return journey. |
| Try different stops | Excludes the current places and runs the same selection rules again. |

**What influences the route?** Starting area, available time, maximum walking distance and interests.

**What influences only the AI explanation?** The selected audience and guide style. The LLM does not choose stops or calculate distances.
        """
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
st.markdown(
    """
    <style>
    .requirements-wrap {overflow-x:auto; margin:.75rem 0 1.5rem; border:1.5px solid #B8D5C6; border-radius:18px;}
    .requirements-table {width:100%; border-collapse:collapse; table-layout:fixed; background:rgba(255,255,255,.45);}
    .requirements-table th,.requirements-table td {padding:.85rem .9rem; border-bottom:1px solid #D7E1DA; border-right:1px solid #D7E1DA; vertical-align:top; text-align:left; white-space:normal; overflow-wrap:anywhere; line-height:1.45;}
    .requirements-table th {background:#F1F5EC; color:#58716B; font-weight:800;}
    .requirements-table th:nth-child(1) {width:25%;}
    .requirements-table th:nth-child(2) {width:48%;}
    .requirements-table th:nth-child(3) {width:27%;}
    .requirements-table td:first-child {font-weight:750; color:#183F3A;}
    .requirements-table tr:last-child td {border-bottom:0;}
    .requirements-table th:last-child,.requirements-table td:last-child {border-right:0;}
    @media (max-width:720px) {
      .requirements-table {min-width:720px; font-size:.92rem;}
      .requirements-table th,.requirements-table td {padding:.7rem;}
    }
    </style>
    <div class="requirements-wrap"><table class="requirements-table">
      <thead><tr><th>Requirement</th><th>How this app demonstrates it</th><th>Where to see it</th></tr></thead>
      <tbody>
        <tr><td>Two complete use cases</td><td>Personalised outing planning and grounded exploration of an individual heritage place.</td><td>Plan My Outing; Explore Heritage Places</td></tr>
        <tr><td>Official, publicly accessible information</td><td>Uses NHB National Monuments and Historic Sites datasets, Roots.gov.sg records and optional SLA OneMap routing.</td><td>Place cards, source links, About Us</td></tr>
        <tr><td>Non-identifying personalisation</td><td>Adapts routes using area, time, walking comfort, interests, audience and guide style without requesting names or sensitive data.</td><td>Plan My Outing form</td></tr>
        <tr><td>Interactive explanations and follow-ups</td><td>Creates route stories and answers suggested or natural-language cultural questions using curated official evidence.</td><td>Route Story tab; Ask the Cultural Guide</td></tr>
        <tr><td>Effective presentation formats</td><td>Uses forms, summary metrics, itinerary tables, maps, photographs, stop cards, downloadable guides and Google Maps hand-off.</td><td>Generated outing; heritage place records</td></tr>
        <tr><td>About Us and Methodology documentation</td><td>Documents scope, objectives, features, data sources, implementation, limitations and one process diagram per use case.</td><td>About Us; Methodology</td></tr>
        <tr><td>Deployment and safeguards</td><td>Runs on Streamlit Community Cloud with password protection and the required educational-prototype disclaimer.</td><td>Live app entry page</td></tr>
      </tbody>
    </table></div>
    """,
    unsafe_allow_html=True,
)

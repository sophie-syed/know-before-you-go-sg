# Know Before You Go SG 🌺

![Know Before You Go SG illustrated heritage streetscape](static/heritage-shophouses-hero.png)

**Know Before You Go SG** is an interactive prototype that turns official Singapore heritage data into personalised, self-guided outings. A visitor chooses a neighbourhood, available time, maximum walking distance and interests, then receives a practical route with photographs, historical context, an itinerary, official sources and a Google Maps hand-off.

This was developed as an individual capstone project for the **AI Champions Bootcamp**.

> **Educational prototype:** This application is a learning exercise, not a public service or a source of current visitor advice. Generated explanations may be incomplete or inaccurate. Opening hours, access, closures, prices and accessibility should be checked with the relevant official source.

## Why this project

The capstone brief was to use publicly accessible, official or trustworthy government information to build a citizen-facing, multi-page application that:

- consolidates information;
- personalises guidance using non-identifying inputs;
- supports explanations and follow-up questions;
- combines effective formats such as forms, maps, tables and visual content;
- implements at least two complete use cases; and
- is deployed as a working web prototype.

Singapore's official heritage information is distributed across geospatial datasets and individual agency pages. This prototype explores how those records could become an approachable outing rather than remaining a directory that residents must research and organise themselves.

## The two use cases

### 1. Personalised heritage outing planner

The visitor selects a starting neighbourhood, available time, maximum walking distance, up to three cultural interests, an intended audience and a preferred guide style.

The app returns route metrics, an itinerary, a story explaining why the places connect, expanded stop cards, photographs, official links, a route map, a Google Maps directions link and a downloadable reference guide. **Try different stops** runs the same constraints again while excluding the current places.

### 2. Grounded cultural guide

The visitor can search or browse all 177 included heritage places, or use **Surprise me** to discover one without repetition during the current session. After choosing a place, the visitor can ask a suggested or natural-language question, read its official record and inspect its photograph and source.

## What the LLM does—and does not do

The LLM does **not** select stops, calculate distance or decide whether a route fits. Those tasks use deterministic Python rules so that the practical recommendation remains repeatable and explainable.

The LLM receives only the selected official-source context and is used to:

- explain why the places and route are historically interesting;
- adapt the writing for the selected audience and guide style; and
- answer follow-up cultural questions.

Its instructions prohibit unsupported claims about history, architecture, opening hours, prices, accessibility and events. If an OpenAI API key is unavailable, the route planner still works and displays deterministic fallback text and official records.

This is a bounded, RAG-style grounding pattern: relevant records are retrieved and supplied as context at response time. It is not an open-web agent or a vector-database implementation.

## How a route is selected

1. The selected neighbourhood supplies a fixed starting coordinate; the app does not request live location.
2. Nearby places are found using straight-line Haversine distance.
3. Official names, descriptions and addresses are matched against declared interest keywords.
4. Candidates receive small bonuses for an available description and for national-monument status.
5. The first 24 ranked places form the candidate pool.
6. A nearest-neighbour heuristic orders 2–6 stops, with a small preference for stronger interest matches.
7. The prototype assumes a walking pace of 4.5 km/h and 15 minutes at each stop.
8. Additional stops are skipped when they would exceed the selected time or distance limit.

Without OneMap, distances are straight-line estimates through successive stops and do not include a return journey. The complete rule table is shown in the app's **Methodology** page.

## Information and media sources

- [National Heritage Board — National Monuments](https://data.gov.sg/collections/1461/datasets/d_b29c230ec6b609e29ed42f71ca9a8767/view)
- [National Heritage Board — Historic Sites](https://data.gov.sg/collections/1460/datasets/d_31e16b12809e66673e90d8b04fdee1b2/view)
- [Roots.gov.sg](https://www.roots.gov.sg/) place records, stories and photographs
- [Singapore Land Authority OneMap](https://www.onemap.gov.sg/apidocs/routing) routing service when configured
- Reusable photographs from Wikimedia Commons where an official image cannot be displayed, with the creator, licence and source shown beside the image

Local dataset snapshots are included so the educational prototype remains available if a download service is temporarily unavailable.

## Tools used

- **Python** for data processing and deterministic route logic
- **Streamlit** for the multi-page interface
- **OpenAI Responses API** for grounded explanations and Q&A
- **pandas** for itinerary presentation
- **Graphviz** for the two use-case process diagrams
- **Google Maps URLs** for connected route navigation
- **GitHub** for version control and source hosting
- **Streamlit Community Cloud** for deployment

## Application structure

```text
app.py                         Authentication and Start Here entry point
pages/0_Start_Here.py          Orientation and use-case selection
pages/1_Plan_My_Outing.py      Planner, story, itinerary, stops and map
pages/2_Explore_Heritage_Places.py  Heritage search, Surprise Me and cultural guide
pages/4_About_Us.py            Scope, objectives, sources and limitations
pages/5_Methodology.py         Data flows, exact rules, safeguards and rubric map
kbyg/core.py                   Dataset loading, scoring and route selection
kbyg/ai.py                     Grounded OpenAI request and guardrails
kbyg/onemap.py                 Optional OneMap walking-route integration
kbyg/ui.py                     Shared interface, maps and photo resolution
tests/test_core.py             Automated core-logic tests
```

## Privacy and safeguards

- No name, NRIC, account, home address or precise live location is requested.
- Preferences are held only in the current Streamlit session.
- The live educational deployment is password protected.
- Every place retains its official Roots.gov.sg link.
- Estimates and unknown visitor information are labelled rather than guessed.
- Photographs use layered validation and visible source/licence attribution.
- Historic markers known to represent a former location or a structure that no longer exists are identified where supported by the official record.

## Current limitations

- Without a OneMap token, distance and time use straight-line estimates rather than actual walking paths.
- The app does not verify current hours, admission, closures, events or wheelchair accessibility.
- Interest matching uses an explainable keyword method rather than semantic ranking.
- Some official records contain much more historical detail than others.
- Photo coverage depends on available official media or a verified reusable image.
- The included government-data snapshot may not reflect later changes.

## Run locally

1. Create and activate a Python virtual environment.
2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and add:

   ```toml
   OPENAI_API_KEY = "your-project-key"
   OPENAI_MODEL = "your-model"
   APP_PASSWORD = "your-test-password"
   # Optional:
   ONEMAP_API_TOKEN = "your-token"
   ```

4. Start the app:

   ```bash
   streamlit run app.py
   ```

Never commit `.streamlit/secrets.toml` or any real secret key.

## Test the core logic

```bash
python -m unittest discover -s tests -v
```

The tests cover dataset loading, route repeatability, time and distance constraints, status labels, text repair, the required disclaimer and OneMap leg aggregation.

## Photo attribution

Most place photographs are supplied through the linked National Heritage Board record. Locally stored Wikimedia Commons fallbacks include:

- Former Nagore Dargah — Philip Nalangan, CC BY 4.0
- Former Kandang Kerbau Hospital — Aranho, public domain
- 38 Oxley Road — Bahnfrend, CC BY-SA 4.0
- Sri Mariamman Temple — -jkb-, CC BY-SA 3.0
- Jamae Mosque — Bjoertvedt, CC BY-SA 4.0
- Thian Hock Keng — Basile Morin, CC BY-SA 4.0

The decorative Singapore heritage map is original AI-generated artwork created for this educational prototype. Its landmark positions are illustrative rather than navigational.

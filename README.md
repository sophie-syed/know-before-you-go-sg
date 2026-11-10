# Know Before You Go SG 🌺

**Know Before You Go SG** is an interactive Streamlit prototype that turns official Singapore heritage data into personalised, self-guided outings. Residents choose a neighbourhood, available time, walking comfort and interests, then receive a practical heritage trail with official sources, photographs, maps and grounded cultural explanations.

This application was developed as an individual capstone project for the AI Champions Bootcamp.

> **Educational prototype:** This project is not intended for real-world decision-making or public distribution. Generated explanations may contain inaccuracies. Always verify information using the linked official sources.

## What the app demonstrates

- Multi-page Streamlit interface
- Two user-centred use cases: outing planning and grounded cultural Q&A
- Personalisation using non-identifying inputs
- Deterministic route logic with stated assumptions
- Maps, itinerary tables, source cards and official links
- Optional OpenAI Responses API integration
- About Us and Methodology pages with one process flow per use case

## Main use cases

### 1. Personalised heritage outing planner

Users provide generic, non-identifying preferences such as starting area, available time, maximum walking distance and cultural interests. Explainable route logic recommends a manageable sequence of official heritage places.

### 2. Grounded cultural guide

Users can explore an individual place, request a personalised route introduction and ask follow-up questions. The LLM receives bounded official-source context and is instructed not to invent unsupported facts.

## Official information sources

- National Heritage Board — National Monuments dataset on data.gov.sg
- National Heritage Board — Historic Sites dataset on data.gov.sg
- National Heritage Board — Roots.gov.sg place information and photographs
- Singapore Land Authority — OneMap routing service when configured

## Run locally

1. Create and activate a Python virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`. Add an OpenAI API key, a prototype password and, if available, a OneMap token.
4. Start the app:

   ```bash
   streamlit run app.py
   ```

The route planner and maps work without external keys. The OpenAI key enables personalised storytelling and follow-up Q&A. The OneMap token enables official walking-route estimates.

## Deploy on Streamlit Community Cloud

1. Put this folder in a GitHub repository.
2. Create a Streamlit Community Cloud app using `app.py` as the entry point.
3. Add `OPENAI_API_KEY`, `OPENAI_MODEL`, `APP_PASSWORD` and optionally `ONEMAP_API_TOKEN` under the app's Secrets settings.
4. Deploy and test every page from the public URL.

Do not commit `.streamlit/secrets.toml`.

Local dataset snapshots are included so the educational prototype remains available if a download service is temporarily unavailable.

## Photo attribution

Most place photographs are supplied through the linked National Heritage Board record. The following locally stored fallbacks are openly licensed Wikimedia Commons photographs; the app displays the creator, licence and source link beside each image:

- Former Nagore Dargah — Philip Nalangan, CC BY 4.0
- Sri Mariamman Temple — -jkb-, CC BY-SA 3.0
- Jamae Mosque — Bjoertvedt, CC BY-SA 4.0
- Thian Hock Keng — Basile Morin, CC BY-SA 4.0

## Current limitations

- Without a OneMap token, distance uses straight-line estimates rather than turn-by-turn routing.
- The app does not verify current access, hours, prices, closures or accessibility.
- Interest matching uses an explainable keyword method rather than opaque model scoring.
- The OpenAI integration cannot be exercised without a project API key.

## Test the core logic

```bash
python -m unittest discover -s tests -v
```

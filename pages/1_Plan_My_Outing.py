from urllib.parse import quote_plus

import streamlit as st

from kbyg.ai import ai_available, ask_grounded_guide
from kbyg.core import (
    INTEREST_KEYWORDS,
    STARTING_AREAS,
    fallback_route_story,
    load_places,
    plan_route,
    route_context,
)
from kbyg.onemap import onemap_available, walking_route
from kbyg.ui import hero, place_card, place_map, require_password, route_table, setup_page


setup_page("Plan My Outing", "🗺️")
require_password()
hero(
    "Create my heritage trail",
    "Choose your neighbourhood, available time and curiosities. We’ll turn them into a pocket-sized Singapore adventure.",
)

places = load_places()


def generate_route_story(route, audience: str, style: str) -> str:
    return ask_grounded_guide(
        "Make this route feel genuinely worth taking, not like a directory listing. Open with "
        "a compelling but factual hook. Explain why these places matter, what is surprising or "
        "human about their official stories, and what their proximity reveals about Singapore. "
        "Give each stop a different, specific reason to care and one concrete thing to notice. "
        "For every stop, write two or three complete sentences: first explain its human or historical "
        "significance, then give a specific visual detail to seek out. Do not use vague phrases such "
        "as 'take a moment to appreciate' or merely list nearby buildings. "
        f"Use short paragraphs and vivid plain language. Style: {style}.",
        route_context(route),
        audience,
    )


def route_markdown(route) -> str:
    lines = [
        f"# My {route.start_name} heritage walk",
        "",
        f"Estimated time: {route.estimated_minutes} minutes  ",
        f"Estimated walking: {route.total_distance_km:.1f} km",
        "",
    ]
    story = st.session_state.get("route_story")
    if story:
        lines.extend(["## Why this route is worth exploring", "", story, ""])
    lines.extend(["## Stops", ""])
    for number, stop in enumerate(route.stops, start=1):
        place = stop.place
        lines.extend(
            [
                f"### {number}. {place.name}",
                "",
                place.description or "See the official source for the full heritage story.",
                "",
                f"Address: {place.address or 'Not supplied'}  ",
                f"Official heritage information: {place.official_url}",
                "",
            ]
        )
    lines.append("Information source: National Heritage Board datasets and Roots.gov.sg.")
    return "\n".join(lines)


def google_maps_route_url(route) -> str:
    points = list(route.stops)
    origin_lat, origin_lon = STARTING_AREAS[route.start_name]
    origin = f"{origin_lat},{origin_lon}"
    destination = f"{points[-1].place.latitude},{points[-1].place.longitude}"
    url = (
        "https://www.google.com/maps/dir/?api=1"
        f"&origin={quote_plus(origin)}&destination={quote_plus(destination)}&travelmode=walking"
    )
    if len(points) > 1:
        waypoints = "|".join(
            f"{stop.place.latitude},{stop.place.longitude}" for stop in points[:-1]
        )
        url += f"&waypoints={quote_plus(waypoints)}"
    return url

with st.form("planner"):
    col1, col2 = st.columns(2)
    with col1:
        start_name = st.selectbox("Starting area", list(STARTING_AREAS), index=0)
        available_minutes = st.select_slider(
            "Time available", options=[45, 60, 90, 120, 180], value=120,
            format_func=lambda value: f"{value // 60}h {value % 60:02d}m" if value >= 60 else f"{value} min",
        )
        max_walking_km = st.slider("Maximum walking distance", 0.8, 5.0, 2.5, 0.2)
    with col2:
        interests = st.multiselect(
            "What interests you?",
            list(INTEREST_KEYWORDS),
            default=["Multicultural history", "Architecture"],
            max_selections=3,
        )
        audience = st.selectbox(
            "Who is this for?",
            ["Curious adults", "A family with children", "Teenagers", "Visitors new to Singapore", "Older adults"],
        )
        explanation_style = st.selectbox(
            "Guide style", ["Warm and conversational", "Concise and factual", "Child-friendly", "Reflective and curious"]
        )
    submitted = st.form_submit_button("Create my outing", type="primary", width="stretch")

if submitted:
    route = plan_route(
        places=places,
        start_name=start_name,
        available_minutes=available_minutes,
        max_walking_km=max_walking_km,
        interests=interests,
    )
    st.session_state["planned_route"] = route
    st.session_state["route_audience"] = audience
    st.session_state["route_style"] = explanation_style
    st.session_state["route_settings"] = {
        "start_name": start_name,
        "available_minutes": available_minutes,
        "max_walking_km": max_walking_km,
        "interests": interests,
    }
    st.session_state.pop("route_story", None)
    st.session_state.pop("route_story_error", None)

route = st.session_state.get("planned_route")
if route:
    st.divider()
    st.subheader(f"Your {route.start_name} heritage walk")
    official_walking = None
    if onemap_available() and route.stops:
        official_walking = walking_route(
            STARTING_AREAS[route.start_name], [stop.place for stop in route.stops]
        )
    metric_cols = st.columns(3)
    metric_cols[0].metric("Stops", len(route.stops))
    if official_walking:
        visit_minutes = len(route.stops) * 15
        metric_cols[1].metric(
            "Estimated time", f"{official_walking.duration_minutes + visit_minutes} min"
        )
        metric_cols[2].metric("OneMap walking route", f"{official_walking.distance_km:.1f} km")
        st.caption(
            "Walking distance and travel time supplied by SLA OneMap; visit time assumes 15 minutes per stop."
        )
    else:
        metric_cols[1].metric("Estimated time", f"{route.estimated_minutes} min")
        metric_cols[2].metric("Estimated walking", f"{route.total_distance_km:.1f} km")

    if not route.stops:
        st.warning("No route fits those limits. Increase the time or walking distance and try again.")
        st.stop()

    audience = st.session_state.get("route_audience", "Curious adults")
    style = st.session_state.get("route_style", "Warm and conversational")
    if ai_available() and not st.session_state.get("route_story") and not st.session_state.get("route_story_error"):
        with st.spinner("Connecting the stories behind your route..."):
            try:
                st.session_state["route_story"] = generate_route_story(route, audience, style)
            except Exception as exc:
                st.session_state["route_story_error"] = str(exc)

    action_cols = st.columns(3)
    with action_cols[0]:
        settings = st.session_state.get("route_settings", {})
        if st.button("🔀 Try different stops", width="stretch") and settings:
            alternative = plan_route(
                places=places,
                excluded_place_ids=[stop.place.place_id for stop in route.stops],
                **settings,
            )
            if alternative.stops:
                st.session_state["planned_route"] = alternative
                st.session_state.pop("route_story", None)
                st.session_state.pop("route_story_error", None)
                st.rerun()
            else:
                st.info("No different route fits these limits. Try allowing more time or walking distance.")
    with action_cols[1]:
        st.link_button("🗺️ Open in Google Maps", google_maps_route_url(route), width="stretch")
    with action_cols[2]:
        st.download_button(
            "⬇️ Download my outing",
            data=route_markdown(route),
            file_name=f"{route.start_name.lower().replace(' ', '-')}-heritage-walk.txt",
            mime="text/plain",
            width="stretch",
        )

    place_map([stop.place for stop in route.stops])
    st.dataframe(route_table(route), hide_index=True, width="stretch")

    st.subheader("Your route story")
    if ai_available():
        if st.session_state.get("route_story_error"):
            st.warning("The personalised story could not load, so a shorter data-based summary is shown instead.")
        st.write(st.session_state.get("route_story", fallback_route_story(route, audience)))
    else:
        st.write(fallback_route_story(route, audience))
        st.info(
            "The route planner is working. Add an OpenAI API key to Streamlit secrets to activate "
            "the personalised LLM introduction and cultural-guide Q&A."
        )

    if not official_walking:
        st.caption(
            "Times use straight-line distance as a prototype estimate and include 15 minutes at each stop. "
            "They are not turn-by-turn directions. Configure OneMap to enable official walking estimates."
        )

    st.subheader("Stops")
    for number, stop in enumerate(route.stops, start=1):
        with st.expander(f"{number}. {stop.place.name}", expanded=True):
            place_card(stop.place, number)

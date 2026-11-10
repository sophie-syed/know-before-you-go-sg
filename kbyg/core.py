from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DATA_DIR = Path(__file__).resolve().parent.parent / "data"

STARTING_AREAS = {
    "Telok Ayer": (1.2821, 103.8481),
    "Chinatown": (1.2838, 103.8439),
    "Civic District": (1.2906, 103.8510),
    "Bras Basah–Bugis": (1.2992, 103.8514),
    "Kampong Gelam": (1.3029, 103.8593),
    "Little India": (1.3067, 103.8494),
    "Tanjong Pagar": (1.2764, 103.8459),
}

INTEREST_KEYWORDS = {
    "Multicultural history": [
        "community", "migrant", "immigrant", "mosque", "temple", "church",
        "synagogue", "religion", "clan", "ethnic", "indian", "chinese",
        "malay", "eurasian", "arab", "jewish", "peranakan",
    ],
    "Architecture": [
        "architecture", "architectural", "building", "designed", "constructed",
        "style", "facade", "tower", "hall", "cathedral", "shophouse",
    ],
    "Migration and community": [
        "migrant", "immigrant", "community", "settlement", "clan", "self-help",
        "trade", "trader", "diaspora", "guild", "association",
    ],
    "Wartime history": [
        "war", "wartime", "japanese", "surrender", "occupation", "battle",
        "defence", "military", "memorial", "prisoner",
    ],
    "Religion and worship": [
        "mosque", "temple", "church", "cathedral", "synagogue", "shrine",
        "religion", "worship", "chapel", "monastery",
    ],
    "Civic and political history": [
        "government", "parliament", "court", "civic", "political", "president",
        "municipal", "independence", "union", "administration",
    ],
    "Arts and performance": [
        "arts", "theatre", "music", "concert", "performance", "museum",
        "gallery", "cinema", "opera", "literary",
    ],
}


# Supplemental facts from official Roots.gov.sg stories and monument features. The
# geospatial datasets deliberately contain short summaries; these notes give the LLM
# enough official context to explain significance without inventing details.
OFFICIAL_PLACE_CONTEXT = {
    "Former Nagore Dargah": (
        "Official NHB context: Chulia immigrants from the Coromandel Coast of southern "
        "India built the shrine between 1828 and 1830 in honour of the Sufi saint Shahul "
        "Hamid, whom seafarers visited before long voyages to pray for safe passage. Many "
        "Chulias in early Singapore worked as traders and moneychangers. The Singapore "
        "building is a smaller, eclectic counterpart to the shrine in Nagore, Tamil Nadu; "
        "its design combines minaret-like towers and Islamic motifs with classical columns, "
        "arches and French-style windows. It now houses the Indian Muslim Heritage Centre. "
        "Official sources: https://www.roots.gov.sg/MUSE/articles/Former-Nagore-Dargah and "
        "https://www.roots.gov.sg/stories-landing/stories/telok-ayer/story"
    ),
    "Al-Abrar Mosque": (
        "Official NHB context: Al-Abrar Mosque was founded in 1827 for Chulia Tamil Muslim "
        "traders and moneychangers from southern India's Coromandel Coast. It began as a "
        "thatched hut, giving it the Tamil nickname Kuchu Palli, or Hut Mosque; the present "
        "brick building dates from 1850 to 1855. It was both a spiritual refuge and a place "
        "for the migrant community to meet. Its Indo-Islamic minarets stand out from the "
        "shophouse row, while its interior also contains European Neoclassical elements. "
        "Official source: https://www.roots.gov.sg/places/places-landing/Places/national-monuments/al-abrar-mosque"
    ),
    "Sultan Mosque": (
        "Official NHB context: Sultan Mosque began as the royal mosque of Sultan Hussein Shah "
        "of Johor. After the 1824 agreement that enabled the British trading port, land near "
        "Istana Kampong Gelam was reserved for the mosque and the East India Company contributed "
        "3,000 Spanish dollars to its building fund. The original mosque was a single-storey "
        "brick structure with a traditional two-tiered roof. The present larger mosque was "
        "designed by Denis Santry of Swan & Maclaren and built through fundraising supported by "
        "Muslims from different ethnic communities. A striking detail is the belt of glass "
        "bottles around the base of each golden dome: these were donated by poorer members of "
        "the community so they too could contribute. The mosque also historically served as a "
        "stopover for regional pilgrims travelling to Mecca. Official source: "
        "https://www.roots.gov.sg/places/places-landing/Places/national-monuments/sultan-mosque"
    ),
    "Jamae Mosque": (
        "Official NHB context: Chulia Muslim immigrants from southern India's Coromandel Coast "
        "established a mosque here around 1826; the present building dates from 1830 to 1835. "
        "Its prominent octagonal minarets, Indo-Islamic design, Tuscan columns, ventilating "
        "verandahs and Chinese green-glazed tiles reflect several architectural traditions. "
        "It remains a place of worship and is one of the few Singapore mosques offering religious "
        "classes in Tamil. Official source: https://www.roots.gov.sg/places/places-landing/Places/"
        "national-monuments/jamae-mosque"
    ),
    "Sri Mariamman Temple": (
        "Official NHB context: Founded by Tamil pioneer Naraina Pillai, Sri Mariamman Temple is "
        "Singapore's oldest Hindu temple. Its early role went beyond worship: it sheltered newly "
        "arrived Indian immigrants and provided a social meeting place. The present five-tiered "
        "gopuram dates from 1925 and is covered with brightly painted sculptures. The temple "
        "continues to host Theemithi, the annual fire-walking festival. Official source: "
        "https://www.roots.gov.sg/places/places-landing/Places/national-monuments/sri-mariamman-temple"
    ),
    "Pondok Peranakan Gelam Club": (
        "Official NHB context: Registered in 1932, this communal lodging club was founded by "
        "Baweanese migrants to support newcomers from the Gelam area of Bawean Island, Indonesia. "
        "During the racial riots of 1945 and 1964, Chinese neighbours sheltered Baweanese residents, "
        "making the site a story of mutual aid across communities. The lodging house no longer "
        "operates here; the marker commemorates the former location. Official source: "
        "https://www.roots.gov.sg/places/places-landing/Places/historic-sites/pondok-peranakan-gelam-club"
    ),
}

OFFICIAL_AREA_CONTEXT = {
    "Telok Ayer": (
        "Official NHB area context: Telok Ayer was once the shoreline where many early "
        "immigrants first arrived. Nearby shrines, temples, mosques and later a church were "
        "not merely landmarks: they offered thanks for safe passage, worship, community "
        "support and a sense of home to different migrant groups. Land reclamation later "
        "moved the street several blocks inland. The surviving places of worship now make "
        "the former waterfront and the fears, hopes and contributions of early immigrants "
        "visible within today's business district. Official source: "
        "https://www.roots.gov.sg/stories-landing/stories/telok-ayer/story"
    )
}


@dataclass(frozen=True)
class Place:
    place_id: str
    name: str
    place_type: str
    latitude: float
    longitude: float
    address: str
    description: str
    official_url: str
    photo_url: str

    def as_dict(self) -> dict:
        return {
            "place_id": self.place_id,
            "name": self.name,
            "place_type": self.place_type,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "description": self.description,
            "official_url": self.official_url,
            "photo_url": self.photo_url,
        }


NO_LONGER_PRESENT_PLACES = {
    "National Theatre",
    "Syonan Jinja",
}

FORMER_LOCATION_PLACES = {
    "Central Sikh Temple",
    "Pondok Peranakan Gelam Club",
    "Raffles Girls' School",
    "Singapore Chinese Girls' School",
}


def visit_status(place: Place) -> str:
    """Return a visit expectation only when the official record is explicit."""
    if place.name in NO_LONGER_PRESENT_PLACES:
        return (
            "Commemorative site — original structure no longer present. "
            "The official NHB description states that it was demolished or destroyed."
        )
    if place.name in FORMER_LOCATION_PLACES:
        return (
            "Former location or use. The official NHB record describes an organisation or "
            "activity that has moved or ended here; it does not confirm which original structures remain."
        )
    return "No separate present-day physical-status statement is supplied in the dataset."


@dataclass(frozen=True)
class RouteStop:
    place: Place
    distance_from_previous_km: float
    cumulative_km: float
    arrival_minute: int
    depart_minute: int
    interest_score: int


@dataclass(frozen=True)
class PlannedRoute:
    stops: tuple[RouteStop, ...]
    total_distance_km: float
    estimated_minutes: int
    start_name: str
    interests: tuple[str, ...]


def _clean(value: object) -> str:
    if value is None:
        return ""
    # The government snapshots contain a small number of damaged curly apostrophes
    # represented by the Unicode replacement character (for example, Singapore�s).
    repaired = str(value).replace("\ufffd", "’")
    return re.sub(r"\s+", " ", repaired).strip()


def _address(properties: dict) -> str:
    pieces = [
        properties.get("ADDRESSBLOCKHOUSENUMBER"),
        properties.get("ADDRESSSTREETNAME"),
        properties.get("ADDRESSBUILDINGNAME"),
        properties.get("ADDRESSPOSTALCODE"),
    ]
    return ", ".join(_clean(piece) for piece in pieces if _clean(piece))


def _load_geojson(path: Path, place_type: str) -> list[Place]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    places: list[Place] = []
    for feature in payload.get("features", []):
        geometry = feature.get("geometry") or {}
        coordinates = geometry.get("coordinates") or []
        properties = feature.get("properties") or {}
        if geometry.get("type") != "Point" or len(coordinates) < 2:
            continue
        longitude, latitude = coordinates[:2]
        name = _clean(properties.get("NAME"))
        if not name:
            continue
        object_id = properties.get("OBJECTID") or properties.get("OBJECTID_1") or name
        places.append(
            Place(
                place_id=f"{place_type}-{object_id}",
                name=name,
                place_type=place_type,
                latitude=float(latitude),
                longitude=float(longitude),
                address=_address(properties),
                description=_clean(properties.get("DESCRIPTION")),
                official_url=_clean(properties.get("HYPERLINK")),
                photo_url=_clean(properties.get("PHOTOURL")),
            )
        )
    return places


def load_places(data_dir: Path = DATA_DIR) -> list[Place]:
    places = _load_geojson(data_dir / "monuments.geojson", "National monument")
    places.extend(_load_geojson(data_dir / "historic_sites.geojson", "Historic site"))
    return sorted(places, key=lambda place: place.name.casefold())


def haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    d_lat = lat2 - lat1
    d_lon = lon2 - lon1
    value = (
        math.sin(d_lat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2) ** 2
    )
    return 2 * 6371.0088 * math.asin(math.sqrt(value))


def interest_score(place: Place, interests: Iterable[str]) -> int:
    text = f"{place.name} {place.description} {place.address}".casefold()
    score = 0
    for interest in interests:
        keywords = INTEREST_KEYWORDS.get(interest, [])
        matched = sum(1 for keyword in keywords if keyword in text)
        score += min(matched, 3) * 2
    if place.description:
        score += 1
    if place.place_type == "National monument":
        score += 1
    return score


def _nearest_order(
    start: tuple[float, float], candidates: list[tuple[Place, int]], limit: int
) -> list[tuple[Place, int, float]]:
    remaining = candidates.copy()
    current = start
    ordered: list[tuple[Place, int, float]] = []
    while remaining and len(ordered) < limit:
        place, score = min(
            remaining,
            key=lambda item: (
                haversine_km(current, (item[0].latitude, item[0].longitude))
                - min(item[1], 6) * 0.025
            ),
        )
        distance = haversine_km(current, (place.latitude, place.longitude))
        ordered.append((place, score, distance))
        remaining.remove((place, score))
        current = (place.latitude, place.longitude)
    return ordered


def plan_route(
    places: list[Place],
    start_name: str,
    available_minutes: int,
    max_walking_km: float,
    interests: Iterable[str],
    minutes_per_stop: int = 15,
    excluded_place_ids: Iterable[str] = (),
) -> PlannedRoute:
    if start_name not in STARTING_AREAS:
        raise ValueError(f"Unknown starting area: {start_name}")
    if available_minutes < 30:
        raise ValueError("At least 30 minutes is required")
    if max_walking_km <= 0:
        raise ValueError("Walking distance must be positive")

    chosen_interests = tuple(interests)
    excluded = set(excluded_place_ids)
    start = STARTING_AREAS[start_name]
    search_radius = min(max_walking_km * 0.8 + 0.5, 4.5)
    scored: list[tuple[Place, int]] = []
    for place in places:
        if place.place_id in excluded:
            continue
        distance = haversine_km(start, (place.latitude, place.longitude))
        if distance <= search_radius:
            scored.append((place, interest_score(place, chosen_interests)))

    scored.sort(
        key=lambda item: (
            -item[1],
            haversine_km(start, (item[0].latitude, item[0].longitude)),
            item[0].name,
        )
    )
    candidate_pool = scored[:24]
    maximum_stops = max(2, min(6, available_minutes // (minutes_per_stop + 8)))
    ordered = _nearest_order(start, candidate_pool, maximum_stops)

    walking_speed_km_per_minute = 4.5 / 60
    route_stops: list[RouteStop] = []
    cumulative_km = 0.0
    elapsed = 0.0
    for place, score, leg_km in ordered:
        proposed_distance = cumulative_km + leg_km
        proposed_elapsed = elapsed + leg_km / walking_speed_km_per_minute + minutes_per_stop
        if route_stops and (
            proposed_distance > max_walking_km or proposed_elapsed > available_minutes
        ):
            continue
        arrival = round(elapsed + leg_km / walking_speed_km_per_minute)
        depart = arrival + minutes_per_stop
        cumulative_km = proposed_distance
        elapsed = proposed_elapsed
        route_stops.append(
            RouteStop(
                place=place,
                distance_from_previous_km=leg_km,
                cumulative_km=cumulative_km,
                arrival_minute=arrival,
                depart_minute=depart,
                interest_score=score,
            )
        )

    return PlannedRoute(
        stops=tuple(route_stops),
        total_distance_km=cumulative_km,
        estimated_minutes=round(elapsed),
        start_name=start_name,
        interests=chosen_interests,
    )


def fallback_route_story(route: PlannedRoute, audience: str) -> str:
    names = [stop.place.name for stop in route.stops]
    interests = ", ".join(route.interests).lower() or "Singapore history"
    if not names:
        return "No suitable stops were found within those limits. Try a longer outing or distance."
    joined = ", ".join(names[:-1]) + (f", and {names[-1]}" if len(names) > 1 else names[0])
    details = [stop.place.description for stop in route.stops if stop.place.description]
    hook = details[0] if details else "These places reveal how history remains embedded in an everyday neighbourhood."
    return (
        f"Why take this walk? {hook} "
        f"Over about {route.estimated_minutes} minutes, you’ll connect {joined} and explore {interests}. "
        "Rather than treating them as isolated landmarks, notice how closely different communities and stories sit beside one another."
    )


def route_context(route: PlannedRoute) -> str:
    sections = []
    area_context = OFFICIAL_AREA_CONTEXT.get(route.start_name)
    if area_context:
        sections.append(f"ROUTE AREA\n{area_context}")
    for index, stop in enumerate(route.stops, start=1):
        place = stop.place
        supplemental = OFFICIAL_PLACE_CONTEXT.get(place.name, "No supplemental official context supplied")
        sections.append(
            f"STOP {index}\n"
            f"Name: {place.name}\n"
            f"Type: {place.place_type}\n"
            f"Address: {place.address or 'Not supplied'}\n"
            f"Official description: {place.description or 'No description supplied'}\n"
            f"Visit status: {visit_status(place)}\n"
            f"Official source: {place.official_url}\n"
            f"Supplemental official context: {supplemental}"
        )
    return "\n\n".join(sections)


def place_context(place: Place) -> str:
    supplemental = OFFICIAL_PLACE_CONTEXT.get(
        place.name, "No supplemental official context supplied for this place."
    )
    return (
        f"Name: {place.name}\n"
        f"Type: {place.place_type}\n"
        f"Address: {place.address or 'Not supplied'}\n"
        f"Official description: {place.description or 'No description supplied'}\n"
        f"Visit status: {visit_status(place)}\n"
        f"Official source: {place.official_url}\n"
        f"Supplemental official context: {supplemental}"
    )


from __future__ import annotations

import html
import re
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
import requests
import streamlit as st

from kbyg.core import Place, PlannedRoute, visit_status


STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
CURATED_PHOTOS = {
    "38 Oxley Road": {
        "path": STATIC_DIR / "38-oxley-road.jpg",
        "caption": "38 Oxley Road · Photo: Bahnfrend (CC BY-SA 4.0)",
        "source": "https://commons.wikimedia.org/wiki/File:38_Oxley_Road,_2023_(01).jpg",
    },
    "Former Nagore Dargah": {
        "path": STATIC_DIR / "former-nagore-dargah.jpg",
        "caption": "Former Nagore Dargah · Photo: Philip Nalangan (CC BY 4.0)",
        "source": "https://commons.wikimedia.org/wiki/File:Nagore_Dargah_Singapore.jpg",
    },
    "Sri Mariamman Temple": {
        "path": STATIC_DIR / "sri-mariamman-temple.jpg",
        "caption": "Sri Mariamman Temple · Photo: -jkb- (CC BY-SA 3.0)",
        "source": "https://commons.wikimedia.org/wiki/File:Singapore_Sri_Mariamman_temple.jpg",
    },
    "Jamae Mosque": {
        "path": STATIC_DIR / "jamae-mosque.jpg",
        "caption": "Jamae Mosque · Photo: Bjoertvedt (CC BY-SA 4.0)",
        "source": "https://commons.wikimedia.org/wiki/File:Singapore_-_Temple_Street_-_Jamae_Chulia_Mosque_IMG_9236.jpg",
    },
    "Thian Hock Keng": {
        "path": STATIC_DIR / "thian-hock-keng.jpg",
        "caption": "Thian Hock Keng · Photo: Basile Morin (CC BY-SA 4.0)",
        "source": "https://commons.wikimedia.org/wiki/File:Thian_Hock_Keng_Temple_Singapore.jpg",
    },
}
OFFICIAL_PHOTO_OVERRIDES = {
    "Pondok Peranakan Gelam Club": (
        "https://www.roots.gov.sg/api/media/313a34ad-8075-41a6-bb1b-bfb860bd4751/"
        "063-pondok-perankan-club.png"
    )
}


def place_photo(place: Place) -> tuple[str | bytes | None, str, str]:
    """Return one verified place photograph, its caption and its source page."""
    curated = CURATED_PHOTOS.get(place.name)
    if curated:
        return str(curated["path"]), str(curated["caption"]), str(curated["source"])

    official_override = OFFICIAL_PHOTO_OVERRIDES.get(place.name)
    dataset_url_is_current = place.photo_url and "~/media/" not in place.photo_url
    official_photo_url = official_override or (place.photo_url if dataset_url_is_current else "")
    photo = _download_photo(official_photo_url) if official_photo_url else None
    if photo:
        return photo, f"{place.name} · National Heritage Board", place.official_url
    photo, licence, source = _commons_photo(place.name)
    if photo:
        licence_note = f" ({licence})" if licence else ""
        return photo, f"{place.name} · Wikimedia Commons{licence_note}", source
    photo, licence, source = _wikipedia_photo(place.name)
    if photo:
        licence_note = f" ({licence})" if licence else ""
        return photo, f"{place.name} · Wikimedia Commons{licence_note}", source
    # Last attempt for places without a matching encyclopaedia article: inspect
    # the official page for a migrated media address.
    photo = _official_page_photo(place.official_url, place.photo_url)
    if photo:
        return photo, f"{place.name} · National Heritage Board", place.official_url
    return None, "", place.official_url


REQUIRED_DISCLAIMER = """IMPORTANT NOTICE: This web application is a prototype developed for educational purposes only. The information provided here is NOT intended for real-world usage and should not be relied upon for making any decisions, especially those related to financial, legal, or healthcare matters.

Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. You assume full responsibility for how you use any generated output.

Always consult with qualified professionals for accurate and personalised advice."""


def setup_page(title: str, icon: str = "🧭") -> None:
    st.markdown(
        """
        <style>
        :root {
            --kbyg-ink:#183F3A;
            --kbyg-coral:#E85D4A;
            --kbyg-pink:#F3A6A0;
            --kbyg-mint:#BFE3D0;
            --kbyg-jade:#218C7E;
            --kbyg-sun:#F5C451;
            --kbyg-blue:#4F7FBB;
            --kbyg-cream:#FFF9ED;
        }
        html, body, [class*="css"] {font-family:"Avenir Next", Avenir, "Trebuchet MS", sans-serif; color:var(--kbyg-ink);}
        .stApp {background:
            radial-gradient(circle at 7% 12%, rgba(243,166,160,.16) 0 38px, transparent 39px),
            radial-gradient(circle at 94% 34%, rgba(191,227,208,.22) 0 58px, transparent 59px),
            var(--kbyg-cream);}
        h1, h2, h3 {font-family:"Avenir Next Rounded", "Arial Rounded MT Bold", "Avenir Next", sans-serif; letter-spacing:-.025em; color:var(--kbyg-ink);}
        .block-container {padding-top:2rem; padding-bottom:4rem; max-width:1180px;}
        .hero {position:relative; overflow:hidden; box-sizing:border-box; min-height:260px; padding:2.4rem 2.2rem; border-radius:28px; background-color:#FFF3D9; background-image:url("app/static/heritage-shophouses-hero.png"); background-size:cover; background-position:center; color:var(--kbyg-ink); margin:.65rem 0 1.25rem; box-shadow:0 10px 0 #F5C451; border:2px solid #183F3A; display:flex; flex-direction:column; justify-content:center;}
        .hero:before {content:""; position:absolute; z-index:0; inset:0; background:linear-gradient(90deg,#FFF9ED 0%,#FFF9ED 52%,rgba(255,249,237,.97) 64%,rgba(255,249,237,.72) 77%,rgba(255,249,237,.08) 94%);}
        .hero-copy {position:relative; z-index:1; max-width:60%;}
        .hero h1 {margin:0 0 .45rem 0; color:var(--kbyg-ink); font-size:clamp(2.1rem,5vw,3.45rem); text-shadow:0 2px 0 white;}
        .hero p {margin:0; font-size:1.08rem; font-weight:650; line-height:1.55; color:var(--kbyg-ink); text-shadow:0 1px 0 white;}
        .hero-eyebrow {position:relative; z-index:1; width:max-content; margin-bottom:.7rem; padding:.34rem .7rem; border:1.5px solid var(--kbyg-ink); border-radius:999px; background:rgba(255,249,237,.9); color:#B43F32; font-size:.71rem; font-weight:850; letter-spacing:.13em; text-transform:uppercase; box-shadow:2px 2px 0 var(--kbyg-sun);}
        .orchid-rule {display:flex; align-items:center; gap:.55rem; color:var(--kbyg-coral); margin:.7rem 0 1.15rem; font-weight:800; letter-spacing:.08em;}
        .orchid-rule:before,.orchid-rule:after {content:""; height:2px; flex:1; background:linear-gradient(90deg,transparent,var(--kbyg-pink),var(--kbyg-jade));}
        .passport-panel {background:rgba(255,255,255,.78); border:2px solid var(--kbyg-ink); border-radius:22px; padding:1rem 1.2rem; box-shadow:6px 6px 0 var(--kbyg-mint); margin:.8rem 0 1.2rem;}
        .source-note {font-size:.84rem; color:#58716B;}
        .stop-card {border-left:7px solid var(--kbyg-coral); padding:.2rem 0 .2rem 1rem; margin:.8rem 0;}
        .passport-kicker {font-size:.75rem; letter-spacing:.14em; text-transform:uppercase; color:#B43F32; font-weight:800;}
        .passport-chip {display:inline-block; background:var(--kbyg-mint); color:var(--kbyg-ink); border:1.5px solid #77B7A2; border-radius:999px; padding:.28rem .68rem; margin:.12rem .18rem .12rem 0; font-size:.78rem; font-weight:750;}
        .passport-chip:nth-child(even) {background:#F7D67D; border-color:#E6B43D;}
        .notice-card {background:#FFF0C9; border:1.5px solid #E5B84F; border-radius:16px; padding:.9rem 1rem; margin:.9rem 0; color:var(--kbyg-ink); box-shadow:4px 4px 0 #F3A6A0;}
        .photo-fallback {min-height:210px; border-radius:20px; background:linear-gradient(145deg,#BFE3D0,#F7D67D); display:flex; align-items:center; justify-content:center; text-align:center; color:var(--kbyg-ink); padding:1.2rem; border:2px solid var(--kbyg-ink); box-shadow:6px 6px 0 #F3A6A0;}
        .photo-fallback .landmark {font-size:2.4rem; display:block; margin-bottom:.35rem;}
        div[data-testid="stForm"], div[data-testid="stExpander"] {background:rgba(255,255,255,.62); border:1.5px solid #CADBD1; border-radius:20px;}
        div[data-testid="stMetric"] {background:#FFFFFF; border:1.5px solid #B8D5C6; border-radius:18px; padding:1rem; box-shadow:4px 4px 0 #BFE3D0;}
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {color:var(--kbyg-jade); font-weight:800;}
        .stButton>button, .stDownloadButton>button, [data-testid="stLinkButton"] a {border-radius:999px !important; border:1.5px solid var(--kbyg-ink) !important; font-weight:750 !important; box-shadow:3px 3px 0 var(--kbyg-ink); transition:transform .12s ease, box-shadow .12s ease;}
        .stButton>button:hover, .stDownloadButton>button:hover, [data-testid="stLinkButton"] a:hover {transform:translate(2px,2px); box-shadow:1px 1px 0 var(--kbyg-ink);}
        .journey-card {display:block; min-height:190px; margin-bottom:1.35rem; padding:1.35rem 1.45rem; border:2px solid var(--kbyg-ink); border-radius:22px; background:rgba(255,255,255,.82); color:var(--kbyg-ink) !important; text-decoration:none !important; box-shadow:7px 7px 0 var(--kbyg-mint); transition:transform .12s ease, box-shadow .12s ease;}
        .journey-card:hover {transform:translate(3px,3px); box-shadow:4px 4px 0 var(--kbyg-sun); background:#fffdf7;}
        .journey-card strong {display:block; margin-bottom:.65rem; font-family:"Avenir Next Rounded", "Arial Rounded MT Bold", "Avenir Next", sans-serif; font-size:1.3rem; color:var(--kbyg-ink);}
        .journey-card span {display:block; line-height:1.55; color:var(--kbyg-ink);}
        .journey-card em {display:block; margin-top:1rem; color:#B43F32; font-style:normal; font-weight:800;}
        .st-key-choice_plan, .st-key-choice_explore {min-height:220px; background:rgba(255,255,255,.82); border-radius:22px; box-shadow:7px 7px 0 var(--kbyg-mint);}
        .st-key-choice_plan p, .st-key-choice_explore p {font-weight:400; line-height:1.55;}
        .st-key-choice_plan h3, .st-key-choice_explore h3 {font-size:1.2rem; margin-top:.2rem;}
        .choice-copy {min-height:5rem; margin:.25rem 0 .65rem; font-weight:400; line-height:1.55;}
        .st-key-outing_action_shuffle, .st-key-outing_action_maps, .st-key-outing_action_download {min-height:175px; background:rgba(255,255,255,.72); border-radius:18px; box-shadow:4px 4px 0 var(--kbyg-mint);}
        [class*="st-key-route_gallery_"] {min-height:340px; margin-bottom:1rem; background:rgba(255,255,255,.68); border-radius:18px;}
        [class*="st-key-route_gallery_"] img {width:100% !important; height:230px !important; object-fit:contain !important; object-position:center; background:#F4F1E8; border-radius:12px;}
        [class*="st-key-route_gallery_"] figcaption {min-height:2.8rem; line-height:1.35; text-align:left;}
        [class*="st-key-route_gallery_"] a {font-size:.86rem; font-weight:750; color:#B43F32;}
        button[kind="primary"] {background:var(--kbyg-coral) !important; color:white !important;}
        [data-testid="stDataFrame"] {border-radius:18px; overflow:hidden; border:1.5px solid #CADBD1;}
        hr {border-color:#B8D5C6 !important;}
        @media (max-width:720px) {
            .hero {min-height:360px; justify-content:flex-start; padding:1.5rem; background-position:63% bottom;}
            .hero:before {background:linear-gradient(180deg,rgba(255,249,237,.99) 0%,rgba(255,249,237,.94) 48%,rgba(255,249,237,.28) 78%,rgba(255,249,237,.05) 100%);}
            .hero-copy {max-width:100%;}
            .journey-card {min-height:auto; margin-bottom:1.5rem;}
            .st-key-choice_plan, .st-key-choice_explore {min-height:auto; margin-bottom:1rem;}
            .choice-copy {min-height:auto;}
            .st-key-outing_action_shuffle, .st-key-outing_action_maps, .st-key-outing_action_download {min-height:auto; margin-bottom:.8rem;}
            [class*="st-key-route_gallery_"] {min-height:auto;}
            [class*="st-key-route_gallery_"] img {height:210px !important;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def require_password() -> None:
    """Protect a deployed prototype when APP_PASSWORD is configured."""
    try:
        expected = str(st.secrets.get("APP_PASSWORD", "")).strip()
    except Exception:
        expected = ""
    if not expected or st.session_state.get("authenticated"):
        return

    st.title("Know Before You Go SG")
    st.write("Enter the prototype password supplied with the submission.")
    supplied = st.text_input("Password", type="password")
    if st.button("Enter", type="primary"):
        if supplied == expected:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()


def required_disclaimer() -> None:
    with st.expander("Important notice — educational prototype", expanded=True):
        st.warning(REQUIRED_DISCLAIMER)


def hero(title: str, subtitle: str) -> None:
    st.markdown(
        '<div class="hero">'
        '<div class="hero-copy"><div class="hero-eyebrow">Your Singapore heritage outing · ❀</div>'
        f'<h1>{html.escape(title)}</h1><p>{html.escape(subtitle)}</p></div>'
        '</div><div class="orchid-rule">❀ &nbsp; DISCOVER · UNDERSTAND · EXPLORE &nbsp; ❀</div>',
        unsafe_allow_html=True,
    )


def place_map(places: list[Place] | tuple[Place, ...], height: int = 430) -> None:
    if not places:
        st.info("No places to map yet.")
        return
    frame = pd.DataFrame(
        [
            {
                "lat": place.latitude,
                "lon": place.longitude,
                "name": place.name,
                "type": place.place_type,
                "stop": str(number),
            }
            for number, place in enumerate(places, start=1)
        ]
    )
    if len(frame) <= 12:
        route_colors = [
            "#D94F3D", "#167F73", "#4F6FB3", "#B46A12", "#8A4F9E", "#347A3E",
            "#C23D76", "#5B6670", "#A45628", "#376E8C", "#6D5A9C", "#7B6B12",
        ]
        frame["marker_color"] = route_colors[: len(frame)]
        legend = "".join(
            f'<span class="passport-chip"><b style="color:{row.marker_color};font-size:1.1rem">●</b> '
            f'{html.escape(row.stop)} · {html.escape(row.name)}</span>'
            for row in frame.itertuples(index=False)
        )
        st.markdown(f'<div style="margin:.25rem 0 .7rem">{legend}</div>', unsafe_allow_html=True)
        st.map(
            frame,
            latitude="lat",
            longitude="lon",
            size=10,
            color="marker_color",
            height=height,
        )
    else:
        st.map(
            frame,
            latitude="lat",
            longitude="lon",
            size=8,
            color="#E876A7",
            height=height,
        )


def route_table(route: PlannedRoute) -> pd.DataFrame:
    rows = []
    for number, stop in enumerate(route.stops, start=1):
        rows.append(
            {
                "Stop": number,
                "Place": stop.place.name,
                "Type": stop.place.place_type,
                "Arrive": f"+{stop.arrival_minute} min",
                "Leave": f"+{stop.depart_minute} min",
                "Walk from previous": f"{stop.distance_from_previous_km:.2f} km",
            }
        )
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False, ttl=86_400)
def _download_photo(url: str) -> bytes | None:
    """Fetch an official image server-side so failed hotlinks never become broken images."""
    if not url:
        return None
    candidates = [url]
    if "https://roots.sg/" in url:
        candidates.insert(0, url.replace("https://roots.sg/", "https://www.roots.gov.sg/"))
    for candidate in candidates:
        try:
            response = requests.get(
                candidate,
                timeout=8,
                headers={"User-Agent": "Know-Before-You-Go-SG/1.0"},
            )
            content_type = response.headers.get("content-type", "").lower()
            if response.ok and content_type.startswith("image/"):
                return response.content
        except requests.RequestException:
            continue
    return None


@st.cache_data(show_spinner=False, ttl=604_800)
def _official_page_photo(page_url: str, legacy_photo_url: str = "") -> bytes | None:
    """Use the image declared by the official Roots page when an old dataset URL fails."""
    if not page_url:
        return None
    try:
        page = requests.get(
            page_url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0 (compatible; Know-Before-You-Go-SG/1.0)"},
        )
        page.raise_for_status()
        match = re.search(
            r'<meta[^>]+(?:property|name)=["\']og:image["\'][^>]+content=["\']([^"\']+)',
            page.text,
            flags=re.IGNORECASE,
        ) or re.search(
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']og:image["\']',
            page.text,
            flags=re.IGNORECASE,
        )
        candidates = [html.unescape(match.group(1))] if match else []
        candidates.extend(
            html.unescape(url)
            for url in re.findall(
                r'(?:https://www\.roots\.gov\.sg)?(/api/media/[^"\'<> ]+)',
                page.text,
                flags=re.IGNORECASE,
            )
        )
        candidates = [
            ("https://www.roots.gov.sg" + url) if url.startswith("/") else url
            for url in candidates
        ]
        legacy_filename = legacy_photo_url.rsplit("/", 1)[-1].lower()
        if legacy_filename:
            candidates.sort(key=lambda url: legacy_filename not in url.lower())
        for image_url in dict.fromkeys(candidates):
            photo = _download_photo(image_url)
            if photo:
                return photo
        return None
    except requests.RequestException:
        return None


@st.cache_data(show_spinner=False, ttl=604_800)
def _commons_photo(place_name: str) -> tuple[bytes | None, str, str]:
    """Find a reusable Commons thumbnail, keeping its source and licence visible."""
    try:
        response = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query",
                "generator": "search",
                "gsrsearch": f"{place_name} Singapore",
                "gsrnamespace": 6,
                "gsrlimit": 1,
                "prop": "imageinfo",
                "iiprop": "url|extmetadata",
                "iiurlwidth": 900,
                "format": "json",
            },
            headers={"User-Agent": "Know-Before-You-Go-SG/1.0 (educational prototype)"},
            timeout=8,
        )
        response.raise_for_status()
        pages = (response.json().get("query") or {}).get("pages") or {}
        if not pages:
            return None, "", ""
        result_page = next(iter(pages.values()))
        expected_tokens = _matching_name_tokens(place_name)
        result_tokens = _matching_name_tokens(result_page.get("title", ""))
        required_overlap = min(2, len(expected_tokens), len(result_tokens))
        if not required_overlap or len(expected_tokens & result_tokens) < required_overlap:
            return None, "", ""
        info = result_page.get("imageinfo", [{}])[0]
        image_url = info.get("thumburl") or info.get("url")
        if not image_url:
            return None, "", ""
        image_response = requests.get(image_url, timeout=8, headers={"User-Agent": "Know-Before-You-Go-SG/1.0"})
        if not image_response.ok or not image_response.headers.get("content-type", "").startswith("image/"):
            return None, "", ""
        metadata = info.get("extmetadata") or {}
        licence = re.sub(r"<[^>]+>", "", (metadata.get("LicenseShortName") or {}).get("value", ""))
        return image_response.content, licence, info.get("descriptionurl", "")
    except (requests.RequestException, ValueError, KeyError, IndexError):
        return None, "", ""


def _matching_name_tokens(value: str) -> set[str]:
    stop_words = {"the", "and", "of", "at", "former", "now", "building", "site", "singapore"}
    return {
        token for token in re.findall(r"[a-z0-9]+", value.casefold())
        if len(token) > 2 and token not in stop_words
    }


@st.cache_data(show_spinner=False, ttl=604_800)
def _wikipedia_photo(place_name: str) -> tuple[bytes | None, str, str]:
    """Return a validated, reusable Commons image from a matching Wikipedia article."""
    try:
        response = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "generator": "search",
                "gsrsearch": f"{place_name} Singapore",
                "gsrlimit": 1,
                "prop": "pageimages|info",
                "piprop": "name|thumbnail|original",
                "pithumbsize": 900,
                "inprop": "url",
                "format": "json",
            },
            headers={"User-Agent": "Know-Before-You-Go-SG/1.0 (educational prototype)"},
            timeout=8,
        )
        response.raise_for_status()
        pages = (response.json().get("query") or {}).get("pages") or {}
        if not pages:
            return None, "", ""
        page = next(iter(pages.values()))
        expected_tokens = _matching_name_tokens(place_name)
        page_tokens = _matching_name_tokens(page.get("title", ""))
        required_overlap = min(2, len(expected_tokens), len(page_tokens))
        if not required_overlap or len(expected_tokens & page_tokens) < required_overlap:
            return None, "", ""

        image_name = page.get("pageimage")
        if not image_name:
            return None, "", ""
        if any(word in image_name.casefold() for word in ("logo", "icon", "seal", "coat_of_arms", "map")):
            return None, "", ""
        commons_response = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query",
                "titles": f"File:{image_name}",
                "prop": "imageinfo",
                "iiprop": "url|extmetadata",
                "iiurlwidth": 900,
                "format": "json",
            },
            headers={"User-Agent": "Know-Before-You-Go-SG/1.0 (educational prototype)"},
            timeout=8,
        )
        commons_response.raise_for_status()
        commons_pages = (commons_response.json().get("query") or {}).get("pages") or {}
        if not commons_pages:
            return None, "", ""
        info = next(iter(commons_pages.values())).get("imageinfo", [{}])[0]
        metadata = info.get("extmetadata") or {}
        licence = re.sub(
            r"<[^>]+>", "", (metadata.get("LicenseShortName") or {}).get("value", "")
        ).strip()
        if not licence:
            return None, "", ""
        image_url = info.get("thumburl") or info.get("url")
        if not image_url:
            return None, "", ""
        image_response = requests.get(
            image_url, timeout=8, headers={"User-Agent": "Know-Before-You-Go-SG/1.0"}
        )
        if not image_response.ok or not image_response.headers.get("content-type", "").startswith("image/"):
            return None, "", ""
        return image_response.content, licence, info.get("descriptionurl", page.get("fullurl", ""))
    except (requests.RequestException, ValueError, KeyError, IndexError):
        return None, "", ""


def _heritage_badges(place: Place) -> list[str]:
    text = f"{place.name} {place.description}".lower()
    candidates = [
        ("Architecture", ("building", "architect", "house", "church", "mosque", "temple")),
        ("Living heritage", ("community", "communal", "welfare", "tradition")),
        ("Migration stories", ("immigrant", "migrant", "island", "province")),
        ("Faith & culture", ("mosque", "church", "temple", "shrine", "religious")),
        ("People & places", ("home", "resident", "people", "street")),
    ]
    matches = [label for label, words in candidates if any(word in text for word in words)]
    return matches[:2] or ["Singapore stories"]


def _notice_prompt(place: Place) -> str:
    text = f"{place.name} {place.description}".lower()
    if "oldest" in text:
        return f"Pause here: {place.name} is described as one of Singapore’s oldest of its kind. What has changed around it while it remained?"
    if "short distance" in text or "short walk" in text:
        return "Scan the street: several historic places sit unusually close together. What does that suggest about the communities that shared this neighbourhood?"
    if any(word in text for word in ("community", "communal", "immigrant", "home")):
        return f"Picture daily life here: who gathered at {place.name}, and what might this place have meant to them?"
    if any(word in text for word in ("mosque", "church", "temple", "building", "architect")):
        return f"Look closely at {place.name}: which feature catches your eye first, and what might it tell you about the building?"
    return f"Compare {place.name} with its modern surroundings. What feels preserved, and what feels changed?"


def google_maps_place_url(place: Place) -> str:
    query = " ".join(part for part in (place.name, place.address, "Singapore") if part)
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(query)}"


def google_street_view_url(place: Place) -> str:
    return (
        "https://www.google.com/maps/@?api=1&map_action=pano"
        f"&viewpoint={place.latitude},{place.longitude}"
    )


def place_card(place: Place, number: int | None = None) -> None:
    prefix = f"Stop {number}: " if number else ""
    st.markdown(
        f'<div class="passport-kicker">Your outing · {html.escape(prefix.rstrip(": "))}</div>'
        f'<div class="stop-card"><h3>{html.escape(place.name)}</h3></div>',
        unsafe_allow_html=True,
    )
    cols = st.columns([2, 1])
    with cols[0]:
        st.caption(place.place_type)
        status = visit_status(place)
        if status.startswith("Commemorative site"):
            st.warning(f"**Before you go:** {status}")
        elif status.startswith("Former location"):
            st.info(f"**Before you go:** {status}")
        st.markdown(
            "".join(f'<span class="passport-chip">{html.escape(badge)}</span>' for badge in _heritage_badges(place)),
            unsafe_allow_html=True,
        )
        if place.description:
            st.write(place.description)
        else:
            st.write("The dataset does not include a short description for this location.")
        if place.address:
            st.write(f"**Address:** {place.address}")
        st.markdown(f'<div class="notice-card"><b>While you’re here</b><br>{html.escape(_notice_prompt(place))}</div>', unsafe_allow_html=True)
        if place.official_url:
            st.link_button("View official heritage information ↗", place.official_url)
            st.caption("Official source: National Heritage Board · Roots.gov.sg")
        st.link_button("Find this stop in Google Maps ↗", google_maps_place_url(place))
        st.link_button("See the surroundings in Street View ↗", google_street_view_url(place))
    with cols[1]:
        photo, caption, photo_source = place_photo(place)
        if photo:
            st.image(photo, caption=caption, width="stretch")
            if photo_source:
                st.link_button("See photo source and gallery ↗", photo_source)
        else:
            if place.official_url:
                safe_url = html.escape(place.official_url, quote=True)
                st.markdown(
                    f'<a href="{safe_url}" target="_blank" style="text-decoration:none">'
                    '<div class="photo-fallback"><div><span class="landmark">📷</span>'
                    '<b>Photograph unavailable here</b><br>'
                    '<small>Open the official Roots page to view its gallery ↗</small>'
                    '</div></div></a>',
                    unsafe_allow_html=True,
                )

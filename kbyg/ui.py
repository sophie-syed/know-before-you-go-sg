from __future__ import annotations

import html
import re
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
import requests
import streamlit as st

from kbyg.core import Place, PlannedRoute


STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
CURATED_PHOTOS = {
    "Former Nagore Dargah": {
        "path": STATIC_DIR / "former-nagore-dargah.jpg",
        "caption": "Former Nagore Dargah · Photo: Philip Nalangan (CC BY 4.0)",
        "source": "https://commons.wikimedia.org/wiki/File:Nagore_Dargah_Singapore.jpg",
    }
}


REQUIRED_DISCLAIMER = """IMPORTANT NOTICE: This web application is a prototype developed for educational purposes only. The information provided here is NOT intended for real-world usage and should not be relied upon for making any decisions, especially those related to financial, legal, or healthcare matters.

Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. You assume full responsibility for how you use any generated output.

Always consult with qualified professionals for accurate and personalised advice."""


def setup_page(title: str, icon: str = "🧭") -> None:
    st.set_page_config(page_title=f"{title} | Know Before You Go SG", page_icon=icon, layout="wide")
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
        .hero {position:relative; overflow:hidden; min-height:260px; padding:2.4rem 2.2rem; border-radius:28px; background-color:#FFF3D9; background-image:url("app/static/heritage-shophouses-hero.png"); background-size:cover; background-position:center; color:var(--kbyg-ink); margin-bottom:1.25rem; box-shadow:0 10px 0 #F5C451; border:2px solid #183F3A; display:flex; flex-direction:column; justify-content:center;}
        .hero:before {content:""; position:absolute; z-index:0; inset:0; background:linear-gradient(90deg,#FFF9ED 0%,#FFF9ED 48%,rgba(255,249,237,.97) 61%,rgba(255,249,237,.72) 74%,rgba(255,249,237,.08) 92%);}
        .hero-copy {position:relative; z-index:1; max-width:50%;}
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
        button[kind="primary"] {background:var(--kbyg-coral) !important; color:white !important;}
        [data-testid="stDataFrame"] {border-radius:18px; overflow:hidden; border:1.5px solid #CADBD1;}
        hr {border-color:#B8D5C6 !important;}
        @media (max-width:720px) {
            .hero {min-height:360px; justify-content:flex-start; padding:1.5rem; background-position:63% bottom;}
            .hero:before {background:linear-gradient(180deg,rgba(255,249,237,.99) 0%,rgba(255,249,237,.94) 48%,rgba(255,249,237,.28) 78%,rgba(255,249,237,.05) 100%);}
            .hero-copy {max-width:100%;}
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
        '<div class="hero-copy"><div class="hero-eyebrow">Singapore Heritage Passport · ❀</div>'
        f'<h1>{html.escape(title)}</h1><p>{html.escape(subtitle)}</p></div>'
        '</div><div class="orchid-rule">❀ &nbsp; EXPLORE · NOTICE · COLLECT &nbsp; ❀</div>',
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
        legend = "".join(
            f'<span class="passport-chip">🌺 {html.escape(row.stop)} · {html.escape(row.name)}</span>'
            for row in frame.itertuples(index=False)
        )
        st.markdown(f'<div style="margin:.25rem 0 .7rem">{legend}</div>', unsafe_allow_html=True)
    st.map(
        frame,
        latitude="lat",
        longitude="lon",
        size=18 if len(frame) <= 12 else 8,
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
def _official_page_photo(page_url: str) -> bytes | None:
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
        if not match:
            return None
        image_url = html.unescape(match.group(1))
        if image_url.startswith("/"):
            image_url = "https://www.roots.gov.sg" + image_url
        return _download_photo(image_url)
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
        info = next(iter(pages.values())).get("imageinfo", [{}])[0]
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


@st.cache_data(show_spinner=False, ttl=604_800)
def _wikipedia_photo(place_name: str) -> tuple[bytes | None, str]:
    """Use a Wikipedia lead image only when the official and Commons searches fail."""
    try:
        response = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "generator": "search",
                "gsrsearch": f"{place_name} Singapore",
                "gsrlimit": 1,
                "prop": "pageimages|info",
                "piprop": "thumbnail|original",
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
            return None, ""
        page = next(iter(pages.values()))
        image_url = (page.get("thumbnail") or {}).get("source") or (page.get("original") or {}).get("source")
        if not image_url:
            return None, ""
        image_response = requests.get(image_url, timeout=8, headers={"User-Agent": "Know-Before-You-Go-SG/1.0"})
        if not image_response.ok or not image_response.headers.get("content-type", "").startswith("image/"):
            return None, ""
        return image_response.content, page.get("fullurl", "")
    except (requests.RequestException, ValueError, KeyError, IndexError):
        return None, ""


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
        f'<div class="passport-kicker">Heritage passport · {html.escape(prefix.rstrip(": "))}</div>'
        f'<div class="stop-card"><h3>{html.escape(place.name)}</h3></div>',
        unsafe_allow_html=True,
    )
    cols = st.columns([2, 1])
    with cols[0]:
        st.caption(place.place_type)
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
        curated = CURATED_PHOTOS.get(place.name)
        photo = None if curated else (_download_photo(place.photo_url) or _official_page_photo(place.official_url))
        if curated:
            st.image(str(curated["path"]), caption=str(curated["caption"]), width="stretch")
            st.link_button("Photo source and licence ↗", str(curated["source"]))
        elif photo:
            st.image(photo, caption=f"{place.name} · National Heritage Board", width="stretch")
        else:
            commons_photo, licence, commons_url = _commons_photo(place.name)
            if commons_photo:
                st.image(commons_photo, caption=f"{place.name} · Wikimedia Commons", width="stretch")
                source_text = f"Photo source and attribution ({licence or 'licence details'}) ↗"
                st.link_button(source_text, commons_url)
            else:
                wikipedia_photo, wikipedia_url = _wikipedia_photo(place.name)
                if wikipedia_photo:
                    st.image(wikipedia_photo, caption=f"{place.name} · Wikipedia/Wikimedia Commons", width="stretch")
                    if wikipedia_url:
                        st.link_button("View photograph source and attribution ↗", wikipedia_url)
                elif place.official_url:
                    safe_url = html.escape(place.official_url, quote=True)
                    st.markdown(
                        f'<a href="{safe_url}" target="_blank" style="text-decoration:none">'
                        '<div class="photo-fallback"><div><span class="landmark">🏛️</span>'
                        '<b>Open the official photo gallery ↗</b><br>'
                        '<small>National Heritage Board · Roots.gov.sg</small>'
                        '</div></div></a>',
                        unsafe_allow_html=True,
                    )

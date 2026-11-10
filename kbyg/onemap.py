from __future__ import annotations

import os
from dataclasses import dataclass

import requests

from kbyg.core import Place


ONEMAP_ROUTE_URL = "https://www.onemap.gov.sg/api/public/routingsvc/route"


@dataclass(frozen=True)
class WalkingRoute:
    distance_km: float
    duration_minutes: int
    source: str = "Singapore Land Authority OneMap"


def _secret(name: str) -> str:
    try:
        import streamlit as st

        value = st.secrets.get(name, "")
        if value:
            return str(value)
    except Exception:
        pass
    return os.getenv(name, "")


def onemap_available() -> bool:
    return bool(_secret("ONEMAP_API_TOKEN"))


def walking_route(start: tuple[float, float], stops: list[Place]) -> WalkingRoute | None:
    """Calculate successive walking legs with the official OneMap Routing API."""
    token = _secret("ONEMAP_API_TOKEN")
    if not token or not stops:
        return None

    total_distance_metres = 0.0
    total_seconds = 0.0
    current = start
    try:
        for stop in stops:
            response = requests.get(
                ONEMAP_ROUTE_URL,
                params={
                    "start": f"{current[0]},{current[1]}",
                    "end": f"{stop.latitude},{stop.longitude}",
                    "routeType": "walk",
                },
                headers={"Authorization": token},
                timeout=12,
            )
            response.raise_for_status()
            summary = (response.json().get("route_summary") or {})
            total_distance_metres += float(summary["total_distance"])
            total_seconds += float(summary["total_time"])
            current = (stop.latitude, stop.longitude)
    except (requests.RequestException, KeyError, TypeError, ValueError):
        return None

    return WalkingRoute(
        distance_km=total_distance_metres / 1000,
        duration_minutes=round(total_seconds / 60),
    )

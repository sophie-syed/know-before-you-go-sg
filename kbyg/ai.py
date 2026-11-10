from __future__ import annotations

import os


DEFAULT_MODEL = "gpt-6.1-terra"


def _secret(name: str) -> str:
    try:
        import streamlit as st

        value = st.secrets.get(name, "")
        if value:
            return str(value)
    except Exception:
        pass
    return os.getenv(name, "")


def ai_available() -> bool:
    return bool(_secret("OPENAI_API_KEY"))


def model_name() -> str:
    return _secret("OPENAI_MODEL") or DEFAULT_MODEL


def ask_grounded_guide(question: str, context: str, audience: str = "general public") -> str:
    """Answer using only supplied government-source context."""
    api_key = _secret("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    developer = (
        "You are the cultural guide for Know Before You Go SG. Use only the official "
        "government-source context supplied by the application. Do not invent dates, "
        "opening hours, admission charges, accessibility details, events, architecture, "
        "or historical claims. If the context cannot answer the question, say what is "
        "unknown and point the user to the official source link. Distinguish a national "
        "monument from a historic-site marker. Write warmly and clearly for the stated "
        "audience. Explain significance rather than merely repeating locations or saying that "
        "a building is old. Translate facts into a clear answer to 'why should I care?', while "
        "remaining within the supplied context. Use complete sentences and never end mid-sentence. "
        "Keep the answer under 300 words and end with a short 'Official source' "
        "line containing the most relevant supplied URL."
    )
    prompt = (
        f"Audience: {audience}\n\n"
        f"OFFICIAL CONTEXT\n{context}\n\n"
        f"USER REQUEST\n{question}"
    )
    response = client.responses.create(
        model=model_name(),
        instructions=developer,
        input=prompt,
        max_output_tokens=1800,
    )
    return response.output_text.strip()


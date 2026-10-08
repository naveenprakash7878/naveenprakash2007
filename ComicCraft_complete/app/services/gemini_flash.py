from google import genai
from google.genai import types

from app.config import get_settings
from app.models import ComicOutline, PromptRequest


def _client() -> genai.Client:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")
    return genai.Client(api_key=settings.gemini_api_key)


def generate_outline(request: PromptRequest) -> ComicOutline:
    settings = get_settings()
    prompt = f"""
Create a coherent 5-panel comic outline.

User story idea:
{request.story_prompt}

Main character:
{request.character_name}

Setting:
{request.setting}

Tone:
{request.tone}

Art style:
{request.art_style}

Requirements:
- Exactly 5 panels, numbered 1 through 5.
- Maintain the same protagonist and visual identity across every panel.
- Each panel needs a concise title.
- Each scene description should explain the action, environment, mood, and important visual continuity.
- Each image_prompt must be a production-ready text-to-image prompt.
- Do not put speech bubbles or readable text inside the generated artwork.
- The image prompts must explicitly preserve the character's appearance across panels.
- Build a clear beginning, escalation, turning point, and ending.
"""
    response = _client().models.generate_content(
        model=settings.gemini_outline_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.8,
            response_mime_type="application/json",
            response_schema=ComicOutline,
        ),
    )
    if not response.parsed:
        raise RuntimeError("Gemini returned no structured outline.")
    return response.parsed

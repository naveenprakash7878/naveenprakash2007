from google import genai
from google.genai import types

from app.config import get_settings
from app.models import ComicOutline, ComicStory, PromptRequest


def _client() -> genai.Client:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")
    return genai.Client(api_key=settings.gemini_api_key)


def generate_story(request: PromptRequest, outline: ComicOutline) -> ComicStory:
    settings = get_settings()
    outline_json = outline.model_dump_json(indent=2)

    prompt = f"""
Expand this 5-panel outline into a polished comic script.

Original story:
{request.story_prompt}

Character:
{request.character_name}

Setting:
{request.setting}

Tone:
{request.tone}

Art style:
{request.art_style}

Outline:
{outline_json}

Requirements:
- Return exactly 5 panels with matching panel numbers.
- Keep the story coherent from panel to panel.
- Caption: a short ambient/comic caption, suitable for a comic page.
- Narration: concise prose describing action, emotion, or context.
- Dialogue: natural spoken dialogue. It may be empty when unnecessary.
- Avoid excessive exposition.
- Do not introduce characters or locations that contradict the outline.
- Keep each panel readable and visually compatible with one comic illustration.
"""
    response = _client().models.generate_content(
        model=settings.gemini_story_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.9,
            response_mime_type="application/json",
            response_schema=ComicStory,
        ),
    )
    if not response.parsed:
        raise RuntimeError("Gemini returned no structured story.")
    return response.parsed

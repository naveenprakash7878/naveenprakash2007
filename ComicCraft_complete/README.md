# ComicCraft — AI Comic Story Creator

ComicCraft is a FastAPI + Jinja2 application that turns a user story idea into a five-panel comic:

1. Gemini creates a structured five-panel outline.
2. Gemini expands the outline into captions, narration and dialogue.
3. Hugging Face Diffusion inference (or local Diffusers) creates one image per panel.
4. The backend builds a comic layout.
5. FPDF exports the panels and story into a downloadable PDF.

The project follows the architecture described in the supplied ComicCraft project document, including `gemini_flash.py`, `gemini_pro.py`, `image_generator.py`, `layout_builder.py`, `exporters.py`, `routes.py`, and the three Jinja2 templates.

## Why the implementation differs from the document

The supplied document uses the older `google-generativeai` package and Gemini 1.5 model names. This implementation uses Google's current `google-genai` SDK and configurable current Gemini model IDs. The image layer remains diffusion-based, but defaults to Hugging Face hosted inference so a normal development PC does not have to download a large model locally.

For a fully local diffusion setup, use `requirements-local.txt` and set `IMAGE_BACKEND=local`.

## 1. Prerequisites

- Python 3.11 or newer
- VS Code
- A Gemini API key
- A Hugging Face token for hosted image generation

## 2. Create the virtual environment

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### macOS / Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Configure secrets

Copy `.env.example` to `.env`.

```text
GEMINI_API_KEY=...
HF_TOKEN=...
IMAGE_BACKEND=hf
```

Do not commit `.env`.

## 4. Run

```bash
uvicorn app.main:app --reload
```

Open:

- http://127.0.0.1:8000 — web app
- http://127.0.0.1:8000/docs — Swagger API docs
- http://127.0.0.1:8000/health — health check

## 5. Test

Run:

```bash
pip install pytest
pytest -q
```

You can also test the API from Swagger.

### JSON example

POST `/generate-comic/json`

```json
{
  "story_prompt": "A brave fox discovers a magical door in an enchanted forest.",
  "character_name": "Fenn",
  "setting": "Enchanted forest",
  "tone": "funny",
  "art_style": "comic book"
}
```

### Image-only test

POST `/test-image` as form data:

```text
prompt=Comic book illustration of a brave fox in an enchanted forest
```

## 6. Local Diffusers mode

If you have a suitable machine and want the diffusion model to run locally:

```bash
pip install -r requirements-local.txt
```

Set:

```text
IMAGE_BACKEND=local
LOCAL_DIFFUSION_MODEL=runwayml/stable-diffusion-v1-5
```

The first generation downloads model weights. GPU inference is strongly preferred.

## 7. Placeholder mode

To test the entire UI and PDF pipeline without any AI credentials:

```text
IMAGE_BACKEND=placeholder
```

Gemini keys are still required for actual story generation. For a completely offline UI-only smoke test, you can replace the Gemini service calls with fixtures; the included tests intentionally avoid making external AI calls.

## Project tree

```text
ComicCraft/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── routes.py
│   ├── config.py
│   ├── models.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── gemini_flash.py
│   │   ├── gemini_pro.py
│   │   ├── image_generator.py
│   │   ├── layout_builder.py
│   │   ├── exporters.py
│   │   └── pipeline.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── comic_preview.html
│   │   └── export_success.html
│   └── static/
│       ├── css/style.css
│       ├── panels/.gitkeep
│       └── exports/.gitkeep
├── tests/
│   ├── test_models.py
│   └── test_health.py
├── .env.example
├── .gitignore
├── requirements.txt
├── requirements-local.txt
└── README.md
```

from __future__ import annotations

import re
import uuid
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.config import get_settings


def _safe_name(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_-]+", "_", value).strip("_")
    return value[:80] or "panel"


def _placeholder(prompt: str, output: Path, panel_number: int) -> None:
    settings = get_settings()
    image = Image.new("RGB", (settings.image_width, settings.image_height), "#1b1b24")
    draw = ImageDraw.Draw(image)
    title = f"COMIC PANEL {panel_number}"
    subtitle = "Placeholder image mode"
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 42)
        small = ImageFont.truetype("DejaVuSans.ttf", 20)
    except OSError:
        font = ImageFont.load_default()
        small = ImageFont.load_default()

    draw.text((40, 40), title, fill="white", font=font)
    draw.text((40, 105), subtitle, fill="#c9c9d4", font=small)
    wrapped = prompt[:900]
    y = 160
    for line in [wrapped[i:i+65] for i in range(0, len(wrapped), 65)]:
        draw.text((40, y), line, fill="#eeeeee", font=small)
        y += 28
    image.save(output, format="PNG")


def _hf_generate(prompt: str, output: Path) -> None:
    from huggingface_hub import InferenceClient

    settings = get_settings()
    if not settings.hf_token:
        raise RuntimeError("HF_TOKEN is not configured for Hugging Face image generation.")

    client = InferenceClient(
        api_key=settings.hf_token,
        provider="auto",
    )
    image = client.text_to_image(
        prompt=prompt,
        model=settings.hf_image_model,
        width=settings.image_width,
        height=settings.image_height,
    )
    image.save(output)


_local_pipeline = None


def _local_generate(prompt: str, output: Path) -> None:
    global _local_pipeline
    import torch
    from diffusers import DiffusionPipeline

    settings = get_settings()
    if _local_pipeline is None:
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        kwargs = {"torch_dtype": dtype}
        if torch.cuda.is_available():
            kwargs["device_map"] = "cuda"
        _local_pipeline = DiffusionPipeline.from_pretrained(
            settings.local_diffusion_model,
            **kwargs,
        )
        if not torch.cuda.is_available():
            _local_pipeline.to("cpu")

    result = _local_pipeline(
        prompt,
        width=settings.image_width,
        height=settings.image_height,
        num_inference_steps=settings.image_steps,
    )
    result.images[0].save(output)


def generate_image(prompt: str, panel_number: int) -> str:
    settings = get_settings()
    filename = f"{uuid.uuid4().hex[:12]}_panel_{panel_number}_{_safe_name(prompt[:40])}.png"
    output = settings.panels_dir / filename

    enhanced_prompt = (
        f"{prompt}. High-quality sequential comic illustration, consistent character design, "
        "clear composition, expressive faces, cinematic lighting, detailed environment, "
        "no text, no watermark, no logo."
    )

    backend = settings.image_backend.lower()
    if backend == "placeholder":
        _placeholder(enhanced_prompt, output, panel_number)
    elif backend == "local":
        _local_generate(enhanced_prompt, output)
    elif backend == "hf":
        _hf_generate(enhanced_prompt, output)
    else:
        raise RuntimeError(
            f"Unsupported IMAGE_BACKEND='{settings.image_backend}'. "
            "Use hf, local, or placeholder."
        )

    return f"/static/panels/{filename}"

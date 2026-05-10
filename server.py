"""
Shoe-on-foot generator — v3 (gpt-image-2 via OpenAI).

Gebruik:
    export OPENAI_API_KEY="sk-..."
    pip install -r requirements.txt
    python server.py
"""

import base64
import io
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from openai import OpenAI
from PIL import Image

load_dotenv()

# --- Configuratie ---
API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable is niet gezet.")

MODEL = "gpt-image-2"

GENDER_FOOT_DESC = {
    "vrouw": (
        "a woman's foot with a natural skin tone, slim ankles, and a neat pedicure"
    ),
    "man": (
        "a man's foot with a natural skin tone, masculine proportions "
        "(wider, slightly larger), and clean unpainted toenails"
    ),
}

PROMPT_PRESETS = {
    "studio": (
        "{foot_desc} is wearing this exact shoe on both feet — both the left and right "
        "shoe are visible, both feet on the ground, shot from a slight front-side angle "
        "so both shoes are clearly seen. Both feet fully inside the shoes, "
        "heels in, toes forward, shoes worn naturally. "
        "White seamless studio background, soft even lighting, lower legs visible. "
        "Preserve every detail of the shoe: same color, materials, sole, laces, "
        "stitching, buckles. Photorealistic high-end e-commerce product photography."
    ),
    "lifestyle": (
        "{foot_desc} is wearing this exact shoe on both feet — both the left and right "
        "shoe are visible, both feet on the ground, slight front-side angle. "
        "Both feet fully inside the shoes, worn naturally. "
        "Mediterranean stone floor, soft afternoon sunlight, subtle plant shadows. "
        "Preserve every detail of the shoe: same color, materials, sole, laces, "
        "stitching, buckles. Photorealistic editorial fashion photography."
    ),
    "frontaal": (
        "{foot_desc} is wearing this exact shoe on both feet — both the left and right "
        "shoe are visible, photographed straight from the front. "
        "Both feet fully inside the shoes, worn naturally side by side. "
        "Clean light grey background, soft studio lighting, lower legs visible. "
        "Preserve every detail of the shoe: same color, materials, sole, laces, "
        "stitching, buckles. Photorealistic e-commerce style."
    ),
}


def build_prompt(preset: str, gender: str) -> str:
    if preset not in PROMPT_PRESETS:
        raise ValueError(f"Onbekende preset: {preset}")
    if gender not in GENDER_FOOT_DESC:
        raise ValueError(f"Onbekend geslacht: {gender}")
    return PROMPT_PRESETS[preset].format(foot_desc=GENDER_FOOT_DESC[gender])


# --- App ---
app = FastAPI(title="Shoe-on-Foot v3 (gpt-image-2)")
client = OpenAI(api_key=API_KEY)

OUTPUT_DIR = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = Path(__file__).parent / "index.html"
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


@app.post("/generate")
async def generate(
    file: UploadFile = File(...),
    preset: str = Form("studio"),
    gender: str = Form("vrouw"),
):
    if preset not in PROMPT_PRESETS:
        raise HTTPException(400, f"Onbekende preset: {preset}")
    if gender not in GENDER_FOOT_DESC:
        raise HTTPException(400, f"Onbekend geslacht: {gender}")

    raw = await file.read()
    try:
        img = Image.open(io.BytesIO(raw))
        img.verify()
        img = Image.open(io.BytesIO(raw))
    except Exception as e:
        raise HTTPException(400, f"Ongeldige afbeelding: {e}")

    orig_width, orig_height = img.size

    max_dim = 1536
    if max(img.size) > max_dim:
        img.thumbnail((max_dim, max_dim), Image.LANCZOS)
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")

    png_buffer = io.BytesIO()
    img.save(png_buffer, format="PNG")
    png_buffer.seek(0)
    png_buffer.name = "shoe.png"

    # Kies output-formaat op basis van originele verhouding
    aspect = orig_width / orig_height
    if aspect > 1.2:
        output_size = "1536x1024"
    elif aspect < 0.83:
        output_size = "1024x1536"
    else:
        output_size = "1024x1024"

    prompt = build_prompt(preset, gender)

    print(f"[generate] model={MODEL} preset={preset} gender={gender} "
          f"input={orig_width}x{orig_height} → output={output_size}")
    print(f"[generate] prompt: {prompt[:120]}...")

    try:
        response = client.images.edit(
            model=MODEL,
            image=png_buffer,
            prompt=prompt,
            size=output_size,
            quality="high",
            n=1,
        )
    except Exception as e:
        raise HTTPException(500, f"OpenAI API fout: {e}")

    output_b64 = response.data[0].b64_json
    if not output_b64:
        raise HTTPException(500, "Geen beeld terug van OpenAI.")

    out_name = f"{file.filename.rsplit('.', 1)[0]}_{gender}_{preset}.png"
    out_path = OUTPUT_DIR / out_name
    out_path.write_bytes(base64.b64decode(output_b64))

    print(f"[generate] klaar — saved={out_path}")

    return JSONResponse({
        "image_b64": output_b64,
        "saved_as": str(out_path),
        "preset": preset,
        "gender": gender,
        "output_size": output_size,
        "input_size": f"{orig_width}x{orig_height}",
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

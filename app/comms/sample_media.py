"""
ResiliNER / SafeSlope-NER - Sample Media Generator & Curated Test Assets
Member 6: Communications & Bot Developer

Generates realistic sample hazard images for immediate zero-asset testing:
1. Road Tension Crack (Asphalt road with prominent jagged fracture lines)
2. Surface Rockfall (Mountain slope with boulder debris and rubble)
3. Landslide Scar / Mudflow (Brown earth displacement / soil mass failure)
4. Blocked Culvert / Drainage Failure (Culvert outlet inundated with silt & debris)
5. Clear Road / Normal (Intact mountain road with clear tarmac)
"""

import io
import os
import base64
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "samples")


def ensure_samples_dir():
    os.makedirs(SAMPLES_DIR, exist_ok=True)


def generate_tension_crack_sample() -> Image.Image:
    """Generate a realistic test image simulating a road tension crack."""
    # Dark asphalt background with road texture
    width, height = 400, 300
    img = Image.new("RGB", (width, height), color=(65, 68, 72))
    draw = ImageDraw.Draw(img)

    # Asphalt noise/texture
    np_img = np.array(img)
    noise = np.random.randint(-15, 15, (height, width, 3), dtype=np.int16)
    np_img = np.clip(np_img + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(np_img)
    draw = ImageDraw.Draw(img)

    # Yellow road center line
    draw.line([(0, 220), (width, 220)], fill=(220, 180, 40), width=6)

    # Deep jagged tension crack across the asphalt
    crack_points = [
        (40, 60), (90, 85), (130, 80), (165, 115), (200, 110),
        (235, 145), (270, 160), (310, 190), (350, 240), (380, 275)
    ]
    # Crack shadow / depth
    draw.line(crack_points, fill=(15, 15, 15), width=7)
    draw.line([(x + 2, y + 1) for x, y in crack_points], fill=(30, 30, 32), width=4)

    # Minor branching cracks
    draw.line([(165, 115), (195, 95), (225, 100)], fill=(20, 20, 20), width=3)
    draw.line([(270, 160), (250, 195), (265, 230)], fill=(20, 20, 20), width=3)

    return img.filter(ImageFilter.SMOOTH_MORE)


def generate_rockfall_sample() -> Image.Image:
    """Generate a realistic test image simulating surface rockfall boulders on road."""
    width, height = 400, 300
    # Mountain slope & road gradient
    img = Image.new("RGB", (width, height), color=(90, 85, 80))
    draw = ImageDraw.Draw(img)

    # Road surface at bottom
    draw.polygon([(0, 180), (width, 180), (width, 300), (0, 300)], fill=(75, 75, 75))

    # Mountain cut slope at top
    draw.polygon([(0, 0), (width, 0), (width, 180), (0, 180)], fill=(115, 98, 80))

    # Large rock boulders & rubble on road
    boulders = [
        [(140, 170), (200, 150), (220, 205), (150, 225)],
        [(210, 190), (270, 175), (285, 235), (230, 245)],
        [(90, 210), (135, 195), (145, 240), (105, 250)],
        [(280, 215), (320, 205), (335, 245), (290, 255)],
    ]
    for b in boulders:
        draw.polygon(b, fill=(135, 128, 120), outline=(50, 45, 40))
        # Highlight facets
        draw.line([b[0], b[1]], fill=(175, 170, 160), width=3)

    # Small scattered scree stones
    np_img = np.array(img)
    noise = np.random.randint(-20, 20, (height, width, 3), dtype=np.int16)
    np_img = np.clip(np_img + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(np_img)


def generate_mudflow_sample() -> Image.Image:
    """Generate a realistic test image simulating mudflow / landslide scar."""
    width, height = 400, 300
    img = Image.new("RGB", (width, height), color=(70, 95, 55)) # Surrounding hillside green
    draw = ImageDraw.Draw(img)

    # Brown muddy landslide chute / tongue descending slope
    mud_scar = [
        (160, 0), (240, 0), (260, 70), (300, 150),
        (340, 230), (360, 300), (80, 300), (120, 220), (140, 120)
    ]
    draw.polygon(mud_scar, fill=(110, 75, 45))

    # Internal mud streaks & wet saturation ripples
    draw.line([(180, 40), (220, 160), (200, 280)], fill=(75, 48, 28), width=8)
    draw.line([(220, 70), (270, 190), (280, 290)], fill=(85, 55, 32), width=6)
    draw.line([(140, 150), (160, 240)], fill=(65, 40, 22), width=5)

    np_img = np.array(img)
    noise = np.random.randint(-15, 15, (height, width, 3), dtype=np.int16)
    np_img = np.clip(np_img + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(np_img)


def generate_blocked_culvert_sample() -> Image.Image:
    """Generate a realistic test image simulating blocked culvert / water surge."""
    width, height = 400, 300
    img = Image.new("RGB", (width, height), color=(100, 95, 88))
    draw = ImageDraw.Draw(img)

    # Concrete retaining wall
    draw.rectangle([(50, 40), (350, 260)], fill=(128, 128, 124), outline=(70, 70, 68), width=4)

    # Culvert pipe opening (semi-submerged)
    draw.ellipse([(140, 100), (260, 220)], fill=(30, 30, 30))

    # Debris mass, branches, and mud blocking lower 70% of the pipe
    draw.chord([(140, 100), (260, 220)], 20, 160, fill=(80, 55, 35))
    draw.line([(150, 170), (250, 150)], fill=(55, 38, 25), width=6)
    draw.line([(170, 140), (230, 190)], fill=(48, 32, 20), width=5)

    # Muddy water pooling at bottom
    draw.polygon([(0, 230), (width, 230), (width, 300), (0, 300)], fill=(92, 108, 98))

    np_img = np.array(img)
    noise = np.random.randint(-10, 10, (height, width, 3), dtype=np.int16)
    np_img = np.clip(np_img + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(np_img)


def generate_clear_road_sample() -> Image.Image:
    """Generate a normal mountain highway with clear pavement."""
    width, height = 400, 300
    img = Image.new("RGB", (width, height), color=(80, 110, 60)) # Lush hills
    draw = ImageDraw.Draw(img)

    # Smooth black asphalt road
    draw.polygon([(150, 80), (250, 80), (380, 300), (20, 300)], fill=(55, 55, 58))
    # Crisp white road striping
    draw.line([(200, 90), (200, 120)], fill=(240, 240, 240), width=3)
    draw.line([(200, 150), (200, 190)], fill=(240, 240, 240), width=5)
    draw.line([(200, 225), (200, 280)], fill=(240, 240, 240), width=7)

    return img


SAMPLE_GENERATORS = {
    "crack": ("road_tension_crack.jpg", generate_tension_crack_sample, "Road Tension Crack"),
    "rockfall": ("surface_rockfall.jpg", generate_rockfall_sample, "Surface Rockfall"),
    "mudflow": ("landslide_mudflow.jpg", generate_mudflow_sample, "Landslide Scar / Mudflow"),
    "culvert": ("blocked_culvert.jpg", generate_blocked_culvert_sample, "Blocked Culvert / Drainage Failure"),
    "clear": ("clear_road.jpg", generate_clear_road_sample, "Normal / No Hazard"),
}


def build_sample_assets() -> dict[str, str]:
    """Generate all sample assets on disk and return map of key -> file path."""
    ensure_samples_dir()
    paths = {}
    for key, (fname, gen_fn, _) in SAMPLE_GENERATORS.items():
        filepath = os.path.join(SAMPLES_DIR, fname)
        img = gen_fn()
        img.save(filepath, "JPEG", quality=85)
        paths[key] = filepath
    return paths


def get_sample_base64(key: str) -> str:
    """Return base64 data URI of a sample hazard image."""
    ensure_samples_dir()
    if key not in SAMPLE_GENERATORS:
        key = "crack"
    fname, gen_fn, _ = SAMPLE_GENERATORS[key]
    filepath = os.path.join(SAMPLES_DIR, fname)
    if not os.path.exists(filepath):
        img = gen_fn()
        img.save(filepath, "JPEG", quality=85)
    else:
        img = Image.open(filepath)
    
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64_str}"


def get_sample_bytes(key: str) -> bytes:
    """Return raw JPEG bytes of a sample hazard image."""
    ensure_samples_dir()
    if key not in SAMPLE_GENERATORS:
        key = "rockfall"
    fname, gen_fn, _ = SAMPLE_GENERATORS[key]
    filepath = os.path.join(SAMPLES_DIR, fname)
    if not os.path.exists(filepath):
        img = gen_fn()
        img.save(filepath, "JPEG", quality=85)
    with open(filepath, "rb") as f:
        return f.read()


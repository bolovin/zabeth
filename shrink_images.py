"""Downsize built site images in place so the published site stays small.

Source photos under src/ are never touched; this runs on the jupyter-book output.
"""

import os
import sys

from PIL import Image, ImageOps

IMAGES_DIR = "out/_build/html/_images"
MAX_EDGE = int(os.environ.get("MAX_EDGE", "2048"))
JPEG_QUALITY = int(os.environ.get("JPEG_QUALITY", "85"))
EXTENSIONS = {".jpg", ".jpeg", ".png"}


def shrink(path):
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image)
        scale = MAX_EDGE / max(image.size)
        if scale < 1:
            image = image.resize(
                (round(image.width * scale), round(image.height * scale)),
                Image.Resampling.LANCZOS,
            )
        if path.lower().endswith(".png"):
            image.save(path, optimize=True)
        else:
            image.convert("RGB").save(
                path, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True
            )


def main():
    if not os.path.isdir(IMAGES_DIR):
        sys.exit(f"missing {IMAGES_DIR}; run the book build first")
    before = after = count = 0
    for name in os.listdir(IMAGES_DIR):
        path = os.path.join(IMAGES_DIR, name)
        if os.path.splitext(name)[1].lower() not in EXTENSIONS:
            continue
        before += os.path.getsize(path)
        shrink(path)
        after += os.path.getsize(path)
        count += 1
    print(f"shrunk {count} images: {before / 2**20:.0f} MB -> {after / 2**20:.0f} MB")


if __name__ == "__main__":
    main()

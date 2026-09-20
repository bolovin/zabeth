"""Import a folder of photos into a section's images/ directory.

HEIC becomes JPEG, EXIF rotation is baked in, everything else is copied as-is.
Usage: poetry run python import_photos.py <source dir> <section, e.g. family/bernard>
"""

import os
import shutil
import sys

from PIL import Image, ImageOps
from pillow_heif import register_heif_opener

register_heif_opener()

ROOT_DIR = "src/zabeth"
HEIC = {".heic", ".heif"}
JPEG = {".jpg", ".jpeg"}
OTHER = {".png", ".gif", ".webp"}


def unique(dest_dir, name):
    stem, ext = os.path.splitext(name)
    candidate, n = name, 1
    while os.path.exists(os.path.join(dest_dir, candidate)):
        candidate = f"{stem}_{n}{ext}"
        n += 1
    return candidate


def import_one(src, dest_dir):
    name = os.path.basename(src)
    stem, ext = os.path.splitext(name)
    ext = ext.lower()
    if ext in HEIC or ext in JPEG:
        with Image.open(src) as image:
            needs_rewrite = ext in HEIC or image.getexif().get(274, 1) != 1
            if needs_rewrite:
                out = os.path.join(dest_dir, unique(dest_dir, f"{stem}.jpg"))
                rotated = ImageOps.exif_transpose(image).convert("RGB")
                rotated.save(out, "JPEG", quality=95, optimize=True)
                return out
    elif ext not in OTHER:
        return None
    out = os.path.join(dest_dir, unique(dest_dir, name))
    shutil.copy2(src, out)
    return out


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    source, section = sys.argv[1], sys.argv[2]
    dest_dir = os.path.join(ROOT_DIR, section, "images")
    os.makedirs(dest_dir, exist_ok=True)
    imported = skipped = 0
    for name in sorted(os.listdir(source)):
        if name.startswith("."):
            continue
        out = import_one(os.path.join(source, name), dest_dir)
        if out:
            imported += 1
        else:
            skipped += 1
            print(f"skipped {name}")
    print(f"imported {imported} into {dest_dir}, skipped {skipped}")


if __name__ == "__main__":
    main()

"""Import a folder of photos into a section's images/ directory.

HEIC becomes JPEG, EXIF rotation is baked in, everything else is copied as-is.
Usage: poetry run python import_photos.py <source dir> <section, e.g. family/bernard>
"""

import os
import re
import shutil
import sys

from PIL import Image, ImageOps
from pillow_heif import register_heif_opener

register_heif_opener()

ROOT_DIR = "src/zabeth"
HEIC = {".heic", ".heif"}
JPEG = {".jpg", ".jpeg"}
OTHER = {".png", ".gif", ".webp"}


def taken_names():
    """Basenames already used anywhere in the book, lowercased.

    The build flattens every section into one _images/ folder and the site is
    served from a case-sensitive host, so names must be unique across sections.
    """
    names = set()
    for dirpath, _, filenames in os.walk(ROOT_DIR):
        if os.path.basename(dirpath) == "images":
            names.update(f.lower() for f in filenames)
    return names


def unique(taken, name):
    stem, ext = os.path.splitext(name)
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("_")
    candidate, n = f"{stem}{ext}", 1
    while candidate.lower() in taken:
        candidate = f"{stem}_{n}{ext}"
        n += 1
    taken.add(candidate.lower())
    return candidate


def import_one(src, dest_dir, taken):
    name = os.path.basename(src)
    stem, ext = os.path.splitext(name)
    ext = ext.lower()
    if ext in HEIC or ext in JPEG:
        with Image.open(src) as image:
            needs_rewrite = ext in HEIC or image.getexif().get(274, 1) != 1
            if needs_rewrite:
                out = os.path.join(dest_dir, unique(taken, f"{stem}.jpg"))
                rotated = ImageOps.exif_transpose(image).convert("RGB")
                rotated.save(out, "JPEG", quality=95, optimize=True)
                return out
    elif ext not in OTHER:
        return None
    out = os.path.join(dest_dir, unique(taken, name))
    shutil.copy2(src, out)
    return out


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    source, section = sys.argv[1], sys.argv[2]
    dest_dir = os.path.join(ROOT_DIR, section, "images")
    os.makedirs(dest_dir, exist_ok=True)
    taken = taken_names()
    imported = skipped = 0
    for name in sorted(os.listdir(source)):
        if name.startswith("."):
            continue
        out = import_one(os.path.join(source, name), dest_dir, taken)
        if out:
            imported += 1
        else:
            skipped += 1
            print(f"skipped {name}")
    print(f"imported {imported} into {dest_dir}, skipped {skipped}")


if __name__ == "__main__":
    main()

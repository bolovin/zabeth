"""Audit src/ photos for redundant images before they get published.

Tiers: byte-identical, perceptual-hash identical (re-encodes), and near
duplicates within one folder that need a human look. Exits non-zero when the
first two tiers find anything, so `make audit` can gate a deploy.
"""

import hashlib
import os
import re
import sys
from collections import defaultdict
from itertools import combinations

import imagehash
from PIL import Image

ROOT_DIR = "src/zabeth"
EXTENSIONS = {".jpg", ".jpeg", ".png"}
NEAR_DISTANCE = 3
SAFE_NAME = re.compile(r"^[A-Za-z0-9._-]+$")


def image_paths():
    for dirpath, _, filenames in os.walk(ROOT_DIR):
        for name in sorted(filenames):
            if os.path.splitext(name)[1].lower() in EXTENSIONS:
                yield os.path.join(dirpath, name)


def report(title, groups):
    print(f"{title}: {len(groups)}")
    for group in groups:
        print("  " + "  |  ".join(os.path.relpath(p, ROOT_DIR) for p in group))


def filename_problems(paths):
    """The build flattens all sections into one _images/ folder served from a
    case-sensitive host, so basenames must be unique (ignoring case) and safe."""
    by_lower = defaultdict(list)
    unsafe = []
    for path in paths:
        name = os.path.basename(path)
        by_lower[name.lower()].append(path)
        if not SAFE_NAME.match(name):
            unsafe.append([path])
    clashes = [g for g in by_lower.values() if len(g) > 1]
    return clashes, unsafe


def main():
    by_sha = defaultdict(list)
    by_phash = defaultdict(list)
    dhashes = {}
    for path in image_paths():
        with open(path, "rb") as handle:
            by_sha[hashlib.sha256(handle.read()).hexdigest()].append(path)
        with Image.open(path) as image:
            rgb = image.convert("RGB")
            by_phash[str(imagehash.phash(rgb))].append(path)
            dhashes[path] = imagehash.dhash(rgb)
    print(f"scanned {len(dhashes)} images under {ROOT_DIR}")

    identical = [g for g in by_sha.values() if len(g) > 1]
    keeper_of = {p: g[0] for g in by_sha.values() for p in g}
    reencoded = [
        g for g in by_phash.values() if len({keeper_of[p] for p in g}) > 1
    ]
    near = [
        (a, b)
        for a, b in combinations(dhashes, 2)
        if os.path.dirname(a) == os.path.dirname(b)
        and dhashes[a] != dhashes[b]
        and dhashes[a] - dhashes[b] <= NEAR_DISTANCE
    ]
    clashes, unsafe = filename_problems(dhashes)
    report("basename clashes across sections (case-insensitive)", clashes)
    report("unsafe filenames (spaces, parentheses, ...)", unsafe)
    report("byte-identical groups", identical)
    report("perceptual-identical groups (re-encodes)", reencoded)
    report(f"near duplicates in same folder (dhash <= {NEAR_DISTANCE}), review by eye", near)
    if identical or reencoded or clashes or unsafe:
        sys.exit(1)


if __name__ == "__main__":
    main()

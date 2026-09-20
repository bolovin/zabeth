from PIL import Image
import imagehash
import os
from collections import defaultdict


def find_duplicates(start_directory, hash_func=imagehash.phash):
    """Find and report duplicate images based on perceptual hash."""
    hashes = defaultdict(list)

    for root, _, files in os.walk(start_directory):
        for filename in files:
            if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                image_path = os.path.join(root, filename)
                try:
                    with Image.open(image_path) as img:
                        img_hash = hash_func(img)
                        hashes[str(img_hash)].append(image_path)
                except Exception as e:
                    print(f"Error hashing {image_path}: {e}")

    # Report duplicates
    for hash_value, paths in hashes.items():
        if len(paths) > 1:
            print(f"\nDuplicate images (hash={hash_value}):")
            for p in paths:
                print(f"  - {p}")


if __name__ == "__main__":
    start_dir = os.getcwd()
    print(f"Scanning for duplicate images in: {start_dir}")
    find_duplicates(start_dir)

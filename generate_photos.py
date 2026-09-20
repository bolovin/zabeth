import os

ROOT_DIR = "src/zabeth"  # Adjust if necessary
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}


def get_image_dirs(root_dir):
    # Get directories in ROOT_DIR that contain an 'images' subdirectory
    image_dirs = []
    for dirpath, dirnames, _ in os.walk(root_dir):
        if "images" in dirnames:
            image_dirs.append(os.path.relpath(dirpath, root_dir))
    return image_dirs


def generate_photos_md():
    # Get the image directories dynamically from ROOT_DIR
    image_dirs = get_image_dirs(ROOT_DIR)

    if not image_dirs:
        print(f"No directories with 'images' found under {ROOT_DIR}.")
        return

    for tree in image_dirs:
        dir_path = os.path.join(ROOT_DIR, tree)
        print(f"Scanning directory: {dir_path}")  # Debug line

        if not os.path.isdir(dir_path):
            print(f"Warning: '{dir_path}' is not a valid directory.")
            continue

        images_dir = os.path.join(dir_path, "images")
        print(f"Checking images directory: {images_dir}")  # Debug line

        if not os.path.exists(images_dir):
            continue  # Skip if no images directory

        image_files = sorted(
            f
            for f in os.listdir(images_dir)
            if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS
        )
        if not image_files:
            continue  # Skip if no images found

        # Define the photos.md path one level above the 'images' directory
        photos_md_path = os.path.join(dir_path, "photos.md")

        # If photos.md already exists, remove it to start fresh
        if os.path.exists(photos_md_path):
            os.remove(photos_md_path)
            print(f"Existing '{photos_md_path}' file removed.")

        # Write to photos.md file in the parent directory of the 'images' folder
        try:
            with open(photos_md_path, "w") as f:
                # Write image links to photos.md
                for image in image_files:
                    f.write(f"![{image}](images/{image})\n")

            print(f"'{photos_md_path}' created successfully.")

        except Exception as e:
            print(f"Error while generating {photos_md_path}: {e}")


def update_images():
    # Step 1: Generate the photos.md file
    generate_photos_md()


if __name__ == "__main__":
    update_images()

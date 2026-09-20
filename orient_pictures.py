from PIL import Image, ImageOps
import os


def needs_rotation(image):
    """Detect if an image is likely rotated incorrectly based on dimensions."""
    width, height = image.size
    return height > width  # Likely needs rotation if taller than wide


def correct_orientation(image_path):
    """Automatically fixes image orientation using EXIF data and manual checks."""
    try:
        image = Image.open(image_path)

        # Step 1: Apply EXIF-based auto-rotation
        image_corrected = ImageOps.exif_transpose(image)

        # Step 2: If EXIF fix didn't work, check if manual rotation is needed
        if needs_rotation(image_corrected):
            image_corrected = image_corrected.rotate(270, expand=True)
            print(f"Manually rotated: {image_path}")

        # Save corrected image
        image_corrected.save(image_path)
        print(f"Fixed: {image_path}")

    except Exception as e:
        print(f"Error processing {image_path}: {e}")


def process_images(start_directory):
    """Recursively processes images in the directory tree."""
    for root, _, files in os.walk(start_directory):
        for filename in files:
            if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                image_path = os.path.join(root, filename)
                correct_orientation(image_path)


if __name__ == "__main__":
    start_dir = os.getcwd()
    print(f"Scanning for images in: {start_dir}")
    process_images(start_dir)

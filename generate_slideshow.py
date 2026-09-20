import os

# Define paths
SRC_DIR = "src/zabeth"
OUTPUT_FILE = os.path.join(SRC_DIR, "slideshow.md")

# Supported image extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


def is_image_file(file):
    """Return True if the file is a valid image file based on its extension."""
    return os.path.splitext(file)[1].lower() in IMAGE_EXTENSIONS


def find_images():
    """Recursively find all image files in subdirectories of SRC_DIR."""
    image_paths = []
    for root, _, files in os.walk(SRC_DIR):
        for file in files:
            if is_image_file(file):
                # Extract only the filename, not the full path
                rel_path = os.path.relpath(os.path.join(root, file), SRC_DIR)
                # Keep only the filename, remove all directory structure
                filename = os.path.basename(rel_path)
                image_paths.append(filename)
    return sorted(image_paths)


def generate_slideshow():
    """Generate slideshow.md with all images formatted for Fancybox."""
    images = find_images()
    if not images:
        print("No images found!")
        return

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("```{raw} html\n")
        f.write(
            '<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>\n'
        )
        f.write(
            '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fancyapps/ui/dist/fancybox.css">\n'
        )
        f.write(
            '<script src="https://cdn.jsdelivr.net/npm/@fancyapps/ui/dist/fancybox.umd.js"></script>\n'
        )
        f.write('<script src="_static/fancybox-init.js"></script>\n\n')

        # Only show the "View Slideshow" button
        f.write('<div class="photo-gallery">\n')
        f.write('  <button id="view-slideshow">View Slideshow</button>\n')
        f.write("</div>\n")

        # Full gallery section (hidden initially)
        f.write('<div id="full-gallery" style="display:none;">\n')
        for img in images:
            f.write(f'  <a data-fancybox="gallery" href="_images/{img}">\n')
            f.write(
                f'    <img src="_images/{img}" width="200" style="display:none;">\n'
            )  # Hide thumbnails
            f.write("  </a>\n")
        f.write("</div>\n")

        f.write(
            """
        <script>
          // When the "View Slideshow" button is clicked
          document.getElementById('view-slideshow').addEventListener('click', function() {
            // Hide the thumbnails and keep the button visible
            document.getElementById('full-gallery').style.display = 'block'; // Show gallery section

            // Shuffle the gallery items dynamically using JavaScript
            let items = document.querySelectorAll('#full-gallery a');
            let shuffledItems = Array.from(items);
            shuffledItems.sort(() => Math.random() - 0.5); // Shuffle the items

            // Empty the gallery and re-append shuffled items
            let gallery = document.getElementById('full-gallery');
            gallery.innerHTML = ''; // Clear current gallery
            shuffledItems.forEach(item => gallery.appendChild(item)); // Append shuffled items

            // Initialize Fancybox for shuffled gallery
            Fancybox.bind("#full-gallery a", {
              loop: true
            });

            // Trigger Fancybox on the first item in the gallery
            shuffledItems[0].click();
          });
        </script>
        """
        )

    print(f"✅ Generated {OUTPUT_FILE} with {len(images)} images.")


if __name__ == "__main__":
    generate_slideshow()

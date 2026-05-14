"""
Shared Cloudinary helpers for the blog_pro Flask app.

  - compress_image : resize + quality-reduce an uploaded file with Pillow
  - upload_image   : compress then push to Cloudinary, returns secure_url
  - delete_image   : destroy an asset on Cloudinary by its URL
"""

import io
import re
import secrets

import cloudinary
import cloudinary.uploader
from PIL import Image, ImageOps


# ---------------------------------------------------------------------------
# Compression
# ---------------------------------------------------------------------------
from PIL import Image, ImageOps
import io


def compress_image(file_obj, max_size=(1080, 1080), quality=60) -> io.BytesIO:
    """
    Resize + compress image while preserving correct orientation.
    """

    img = Image.open(file_obj)

    # FIX: apply EXIF orientation
    img = ImageOps.exif_transpose(img)

    # Convert to RGB for JPEG
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    # Resize
    img.thumbnail(max_size, Image.LANCZOS)

    # Save compressed image
    output = io.BytesIO()
    img.save(output, format="JPEG", quality=quality, optimize=True)

    output.seek(0)
    return output


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------

def upload_image(file_obj, folder: str) -> str:
    """
    Compress *file_obj* and upload it to Cloudinary inside *folder*.

    Returns the ``secure_url`` of the uploaded asset.

    Example folders:
        ``"profiles/42"``   – profile picture for user with id 42
        ``"posts/42"``      – post image belonging to user with id 42
    """
    compressed = compress_image(file_obj)
    public_id = secrets.token_hex(8)          # random, collision-safe name

    result = cloudinary.uploader.upload(
        compressed,
        folder=folder,
        public_id=public_id,
        resource_type="image",
    )
    return result["secure_url"]


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

_CLOUDINARY_URL_RE = re.compile(
    r"https?://res\.cloudinary\.com/[^/]+/image/upload/(?:v\d+/)?(.+?)(?:\.[a-zA-Z]+)?$"
)


def delete_image(cloudinary_url: str) -> None:
    """
    Destroy the image at *cloudinary_url* on Cloudinary.

    Silently does nothing when *cloudinary_url* is ``None``, empty, or
    looks like the default local placeholder (``'default.JPG'``).
    """
    if not cloudinary_url or not cloudinary_url.startswith("https://"):
        return

    match = _CLOUDINARY_URL_RE.match(cloudinary_url)
    if not match:
        return                          # not a recognisable Cloudinary URL

    public_id = match.group(1)
    try:
        cloudinary.uploader.destroy(public_id)
    except Exception:
        pass                            # don't crash the request on cleanup failure

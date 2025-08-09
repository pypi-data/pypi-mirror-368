"""
Image functions/utilities.
"""

import os
import hashlib
import tempfile
import subprocess
from PIL import Image, ImageChops
import cv2
from skimage.metrics import structural_similarity as ssim
import uuid
from typing import Optional

def sha256_hash(filepath: str) -> str:
    """Compute the SHA-256 hash of a file."""
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def compare_images(image1_path: str, image2_path: str) -> None:
    """
    Compare two images using multiple techniques:
    
    - SHA-256 hash comparison (byte-level)
    - Pixel-by-pixel comparison using Pillow (ImageChops)
    - Structural Similarity Index (SSIM) using scikit-image
    - ImageMagick 'compare' with Absolute Error (AE) metric
    
    Outputs detailed results and stores an ImageMagick diff image in a
    unique temporary folder based on a UUID.

    Parameters:
        image1_path (str): Path to the first image.
        image2_path (str): Path to the second image.
    """
    print(f"🔍 Comparing:\n  Image 1: {image1_path}\n  Image 2: {image2_path}\n")

    # --- Hash comparison ---
    hash1: str = sha256_hash(image1_path)
    hash2: str = sha256_hash(image2_path)
    print(f"🔐 Hash 1: {hash1}")
    print(f"🔐 Hash 2: {hash2}")
    print(f"📢 Hash message: {'✅ Hashes match' if hash1 == hash2 else '❌ Hashes differ'}\n")

    # --- ImageChops pixel difference ---
    img1: Image.Image = Image.open(image1_path)
    img2: Image.Image = Image.open(image2_path)

    print(f"🖼️ Image resolution: {img1.width}×{img1.height}")

    if img1.size != img2.size or img1.mode != img2.mode:
        print("⚠️ ImageChops skipped: images differ in size or mode\n")
    else:
        diff_bbox: Optional[tuple[int, int, int, int]] = ImageChops.difference(img1, img2).getbbox()
        print(f"🧮 ImageChops.difference(img1, img2).getbbox(): {diff_bbox}")
        if diff_bbox is None:
            print("📢 ImageChops message: ✅ Images are pixel-perfect identical\n")
        else:
            bbox_width: int = diff_bbox[2] - diff_bbox[0]
            bbox_height: int = diff_bbox[3] - diff_bbox[1]
            print(f"📢 ImageChops message: ❌ Images differ within bounding box {diff_bbox}, covering {bbox_width}×{bbox_height} pixels\n")

    # --- SSIM comparison ---
    img1_gray = cv2.imread(image1_path, cv2.IMREAD_GRAYSCALE)
    img2_gray = cv2.imread(image2_path, cv2.IMREAD_GRAYSCALE)

    if img1_gray.shape != img2_gray.shape:
        img2_gray = cv2.resize(img2_gray, (img1_gray.shape[1], img1_gray.shape[0]))

    ssim_score: float
    ssim_score, _ = ssim(img1_gray, img2_gray, full=True)
    print(f"📏 SSIM score: {ssim_score:.4f}")
    if ssim_score == 1.0:
        print("📢 SSIM message: ✅ Visually identical\n")
    elif ssim_score > 0.95:
        print("📢 SSIM message: 👍 Very similar\n")
    else:
        print("📢 SSIM message: ❌ Visually different\n")

    # --- ImageMagick metric comparison ---
    unique_id: str = uuid.uuid4().hex
    output_dir: str = os.path.join(tempfile.gettempdir(), unique_id)
    os.makedirs(output_dir, exist_ok=True)

    temp_diff_path: str = os.path.join(output_dir, "imagemagick_diff_output.png")

    try:
        result = subprocess.run(
            ["magick", "compare", "-metric", "AE", image1_path, image2_path, temp_diff_path],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            check=True
        )
        # This is rare — identical images may not trigger an error
        metric_output: str = result.stderr.strip()
    except FileNotFoundError:
        print("❌ Error: ImageMagick 'magick' command not found. Make sure ImageMagick is installed and in your PATH.\n")
        return
    except subprocess.CalledProcessError as e:
        metric_output = e.stderr.strip()

    print(f"📊 ImageMagick metric (Absolute Error): {metric_output}")

    if metric_output.strip().startswith("0"):
        print("🗑️ ImageMagick message: ✅ No difference detected — skipping diff image output\n")
    else:
        print(f"📁 ImageMagick difference stored in: {temp_diff_path}")
        print("📢 ImageMagick message: ❌ Difference detected\n")
#!/usr/bin/env python3
"""
Separate a composite image into individual images based on connected components.
Each spatially separated region becomes its own image file.
"""

import cv2
import numpy as np
from pathlib import Path
import argparse


def separate_images(image_path, output_dir=None, min_area=500, padding=10):
    """
    Separate a composite image into individual images based on connectivity.

    Args:
        image_path: Path to the input image
        output_dir: Directory to save separated images (defaults to same dir as input)
        min_area: Minimum area for a valid component (filters out noise)
        padding: Pixels of padding to add around each extracted image
    """
    # Read the image
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    original = img.copy()

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Create binary image (inverse threshold to get non-white regions as foreground)
    # Since your image has white background, we want to detect non-white content
    _, binary = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)

    # Find connected components
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary, connectivity=8)

    # Set up output directory
    if output_dir is None:
        output_dir = Path(image_path).parent / "separated_images"
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    # Extract and save each component
    components = []
    for i in range(1, num_labels):  # Skip 0 (background)
        # Get component stats
        x, y, w, h, area = stats[i]

        # Filter out small components (noise)
        if area < min_area:
            continue

        # Add padding (ensure we don't go out of bounds)
        x_start = max(0, x - padding)
        y_start = max(0, y - padding)
        x_end = min(original.shape[1], x + w + padding)
        y_end = min(original.shape[0], y + h + padding)

        # Extract the component region from original image
        component_img = original[y_start:y_end, x_start:x_end]

        # Store component info for sorting
        components.append({
            'image': component_img,
            'y': y,  # Top position for vertical sorting
            'x': x,  # Left position
            'area': area,
            'bounds': (x_start, y_start, x_end, y_end)
        })

    # Sort components by vertical position (top to bottom)
    components.sort(key=lambda c: c['y'])

    # Save each component
    input_name = Path(image_path).stem
    saved_files = []

    for idx, comp in enumerate(components, 1):
        output_path = output_dir / f"{input_name}_part_{idx:02d}.png"
        cv2.imwrite(str(output_path), comp['image'])

        saved_files.append(output_path)
        print(f"Saved: {output_path}")
        print(f"  Position: ({comp['x']}, {comp['y']})")
        print(f"  Size: {comp['image'].shape[1]}x{comp['image'].shape[0]}")
        print(f"  Area: {comp['area']} pixels")
        print()

    print(f"Successfully separated {len(saved_files)} images")
    return saved_files


def analyze_connectivity(image_path):
    """
    Analyze the image to provide information about connected components.
    Useful for debugging and determining optimal parameters.
    """
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary, connectivity=8)

    print(f"Found {num_labels - 1} connected components (excluding background)")
    print("\nComponent details:")

    for i in range(1, num_labels):
        x, y, w, h, area = stats[i]
        print(f"Component {i}:")
        print(f"  Position: ({x}, {y})")
        print(f"  Size: {w}x{h}")
        print(f"  Area: {area} pixels")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Separate a composite image into individual images")
    parser.add_argument("image", help="Path to the input image")
    parser.add_argument("-o", "--output", help="Output directory (default: ./separated_images)")
    parser.add_argument("-m", "--min-area", type=int, default=500,
                        help="Minimum area for valid components (default: 500)")
    parser.add_argument("-p", "--padding", type=int, default=10,
                        help="Padding to add around extracted images (default: 10)")
    parser.add_argument("--analyze", action="store_true",
                        help="Analyze connectivity without separating")

    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Error: Image file not found: {image_path}")
        exit(1)

    if args.analyze:
        analyze_connectivity(image_path)
    else:
        try:
            saved_files = separate_images(
                image_path,
                output_dir=args.output,
                min_area=args.min_area,
                padding=args.padding
            )
        except Exception as e:
            print(f"Error: {e}")
            exit(1)
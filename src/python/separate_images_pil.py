#!/usr/bin/env python3
"""
Separate a composite image into individual images based on connected components using PIL.
Each spatially separated region becomes its own image file.
"""

from PIL import Image
import numpy as np
from pathlib import Path
import argparse
from scipy import ndimage
from scipy.ndimage import label, find_objects


def separate_images(image_path, output_dir=None, min_area=500, padding=10, threshold=250):
    """
    Separate a composite image into individual images based on connectivity.

    Args:
        image_path: Path to the input image
        output_dir: Directory to save separated images (defaults to same dir as input)
        min_area: Minimum area for a valid component (filters out noise)
        padding: Pixels of padding to add around each extracted image
        threshold: Threshold for binary conversion (pixels above this are background)
    """
    # Read the image
    img = Image.open(image_path)

    # Convert to RGBA if not already (to preserve transparency if present)
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    original = np.array(img)

    # Convert to grayscale for component detection
    gray = img.convert('L')
    gray_array = np.array(gray)

    # Create binary image (pixels below threshold are foreground)
    binary = gray_array < threshold

    # Find connected components
    labeled_array, num_features = label(binary)

    # Find bounding boxes for each component
    slices = find_objects(labeled_array)

    # Set up output directory
    if output_dir is None:
        output_dir = Path(image_path).parent / "separated_images"
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    # Extract and save each component
    components = []

    for i, slice_tuple in enumerate(slices):
        if slice_tuple is None:
            continue

        # Get the slice boundaries
        y_slice, x_slice = slice_tuple

        # Calculate area
        component_mask = labeled_array[slice_tuple] == (i + 1)
        area = np.sum(component_mask)

        # Filter out small components (noise)
        if area < min_area:
            continue

        # Add padding (ensure we don't go out of bounds)
        y_start = max(0, y_slice.start - padding)
        y_end = min(original.shape[0], y_slice.stop + padding)
        x_start = max(0, x_slice.start - padding)
        x_end = min(original.shape[1], x_slice.stop + padding)

        # Extract the component region from original image
        component_img = original[y_start:y_end, x_start:x_end]

        # Store component info for sorting
        components.append({
            'image': component_img,
            'y': y_slice.start,  # Top position for vertical sorting
            'x': x_slice.start,  # Left position
            'area': area,
            'bounds': (x_start, y_start, x_end, y_end)
        })

    # Sort components by vertical position (top to bottom)
    components.sort(key=lambda c: c['y'])

    # Save each component
    input_name = Path(image_path).stem
    saved_files = []

    # Labels for each component (based on your image)
    labels = ["Planning Agent", "Creator Writer", "Interface Chat Agent", "Domain Expert"]

    for idx, comp in enumerate(components):
        # Use descriptive name if available, otherwise generic
        if idx < len(labels):
            clean_label = labels[idx].replace(" ", "_").replace("/", "_")
            output_path = output_dir / f"{input_name}_{idx+1:02d}_{clean_label}.png"
        else:
            output_path = output_dir / f"{input_name}_part_{idx+1:02d}.png"

        # Convert numpy array back to PIL Image and save
        pil_img = Image.fromarray(comp['image'])
        pil_img.save(output_path)

        saved_files.append(output_path)
        print(f"Saved: {output_path}")
        print(f"  Position: ({comp['x']}, {comp['y']})")
        print(f"  Size: {comp['image'].shape[1]}x{comp['image'].shape[0]}")
        print(f"  Area: {comp['area']} pixels")
        print()

    print(f"Successfully separated {len(saved_files)} images")
    return saved_files


def analyze_connectivity(image_path, threshold=250):
    """
    Analyze the image to provide information about connected components.
    Useful for debugging and determining optimal parameters.
    """
    img = Image.open(image_path)
    gray = img.convert('L')
    gray_array = np.array(gray)

    # Create binary image
    binary = gray_array < threshold

    # Find connected components
    labeled_array, num_features = label(binary)
    slices = find_objects(labeled_array)

    print(f"Found {num_features} connected components")
    print("\nComponent details:")

    for i, slice_tuple in enumerate(slices):
        if slice_tuple is None:
            continue

        y_slice, x_slice = slice_tuple
        component_mask = labeled_array[slice_tuple] == (i + 1)
        area = np.sum(component_mask)

        print(f"Component {i+1}:")
        print(f"  Position: ({x_slice.start}, {y_slice.start})")
        print(f"  Size: {x_slice.stop - x_slice.start}x{y_slice.stop - y_slice.start}")
        print(f"  Area: {area} pixels")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Separate a composite image into individual images")
    parser.add_argument("image", help="Path to the input image")
    parser.add_argument("-o", "--output", help="Output directory (default: ./separated_images)")
    parser.add_argument("-m", "--min-area", type=int, default=500,
                        help="Minimum area for valid components (default: 500)")
    parser.add_argument("-p", "--padding", type=int, default=10,
                        help="Padding to add around extracted images (default: 10)")
    parser.add_argument("-t", "--threshold", type=int, default=250,
                        help="Threshold for background detection (default: 250)")
    parser.add_argument("--analyze", action="store_true",
                        help="Analyze connectivity without separating")

    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Error: Image file not found: {image_path}")
        exit(1)

    if args.analyze:
        analyze_connectivity(image_path, threshold=args.threshold)
    else:
        try:
            saved_files = separate_images(
                image_path,
                output_dir=args.output,
                min_area=args.min_area,
                padding=args.padding,
                threshold=args.threshold
            )
        except Exception as e:
            print(f"Error: {e}")
            exit(1)
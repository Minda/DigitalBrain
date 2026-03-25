# Optimizing Images

Optimize images for web use by converting formats and reducing file sizes while maintaining quality.

## Default Output Location

Optimized images should be saved to `personal/images/` with organized subdirectories:
- `personal/images/blog/` - Blog post images (Substack, etc.)
- `personal/images/screenshots/` - Optimized screenshots
- `personal/images/diagrams/` - Diagrams and visualizations
- `personal/images/archive/` - Older images for reference

## Usage

This skill provides two methods for image optimization:

### Method 1: Rust CLI (mm image)
The `mm` CLI tool includes image optimization commands:
- `mm image optimize <input> -o <output> -q <quality> -f <format>`
- `mm image info <path>`

### Method 2: Python Script
For quick conversions when the Rust CLI is unavailable.

## Quick Start

To optimize an image for web use:

```bash
# Using the Rust CLI - saves to personal/images/
mm image optimize screenshot.png -o personal/images/screenshots/screenshot-optimized.jpg -q 85

# For blog posts
mm image optimize banner.png -o personal/images/blog/post-banner-2026-03.jpg -q 85

# Using Python
python -c "
from PIL import Image
img = Image.open('input.png')
if img.mode == 'RGBA':
    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
    rgb_img.paste(img, mask=img.split()[3] if len(img.split()) == 4 else None)
    img = rgb_img
img.save('personal/images/blog/output.jpg', 'JPEG', quality=85, optimize=True)
"
```

## Features

- **Format conversion**: PNG to JPEG, or maintain format
- **Quality optimization**: Adjustable JPEG quality (1-100)
- **Size reduction**: Typically 70-90% file size reduction
- **Transparency handling**: Converts RGBA to RGB with white background
- **Batch processing**: Can be scripted for multiple files

## Python Implementation

```python
from PIL import Image
import os

def optimize_image(input_path, output_path=None, quality=85, format='JPEG'):
    """
    Optimize an image file.

    Args:
        input_path: Path to input image
        output_path: Path for output (defaults to input_optimized.ext)
        quality: JPEG quality (1-100, default 85)
        format: Output format ('JPEG' or 'PNG')
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Generate output path if not provided
    if output_path is None:
        base, _ = os.path.splitext(input_path)
        ext = '.jpg' if format == 'JPEG' else '.png'
        output_path = f"{base}_optimized{ext}"

    # Open and convert image
    img = Image.open(input_path)

    # Convert RGBA to RGB if saving as JPEG
    if format == 'JPEG' and img.mode == 'RGBA':
        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
        rgb_img.paste(img, mask=img.split()[3] if len(img.split()) == 4 else None)
        img = rgb_img

    # Save with optimization
    save_kwargs = {'optimize': True}
    if format == 'JPEG':
        save_kwargs['quality'] = quality

    img.save(output_path, format, **save_kwargs)

    # Report results
    input_size = os.path.getsize(input_path)
    output_size = os.path.getsize(output_path)
    reduction = 100 - (output_size / input_size * 100)

    return {
        'input_path': input_path,
        'output_path': output_path,
        'input_size': input_size,
        'output_size': output_size,
        'reduction_percent': reduction
    }
```

## Rust Implementation

Located in `src/crates/minmind-cli/src/image.rs`, the Rust implementation provides:
- High-performance image processing
- Command-line interface via `mm image`
- Support for multiple formats
- Detailed image information

## Common Use Cases

### 1. Optimize Images for Web
```bash
mm image optimize screenshot.png -o screenshot.jpg -q 85
```

### 2. Batch Convert PNG to JPEG
```python
import glob
from PIL import Image

for png_file in glob.glob("*.png"):
    img = Image.open(png_file)
    jpg_file = png_file.replace('.png', '.jpg')
    if img.mode == 'RGBA':
        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
        rgb_img.paste(img, mask=img.split()[3])
        img = rgb_img
    img.save(jpg_file, 'JPEG', quality=85, optimize=True)
    print(f"Converted {png_file} to {jpg_file}")
```

### 3. Get Image Information
```bash
mm image info photo.jpg
```

### 4. Substack Header Image Workflow
Complete workflow for optimizing a Substack header image from Dropbox:

```bash
# Step 1: Create the blog images directory if it doesn't exist
mkdir -p personal/images/blog

# Step 2: Convert and optimize the image
python -c "
from PIL import Image
import os

input_path = '/Users/min/Dropbox/CLIENTS/PHOTOS/* Substack/your-image.png'
output_path = 'personal/images/blog/substack-header-2026-03.jpg'

if os.path.exists(input_path):
    img = Image.open(input_path)
    # Convert RGBA to RGB if necessary
    if img.mode == 'RGBA':
        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
        rgb_img.paste(img, mask=img.split()[3] if len(img.split()) == 4 else None)
        img = rgb_img
    # Save as JPEG with optimized quality
    img.save(output_path, 'JPEG', quality=85, optimize=True)

    # Get file sizes
    input_size = os.path.getsize(input_path)
    output_size = os.path.getsize(output_path)
    reduction = 100 - (output_size / input_size * 100)

    print(f'✓ Image optimized successfully!')
    print(f'  Input:  {input_size:,} bytes ({input_size/1024/1024:.1f} MB)')
    print(f'  Output: {output_size:,} bytes ({output_size/1024:.1f} KB)')
    print(f'  Size reduction: {reduction:.1f}%')
    print(f'  Saved to: {output_path}')
else:
    print(f'Error: File not found')
"
```

**Typical results:**

*Header images:*
- Input: 2.0 MB PNG → Output: 289 KB JPEG (85.7% reduction)
- Quality: Excellent for web use at 85% JPEG quality

*Artistic/collage images:*
- Input: 2.3 MB PNG → Output: 392 KB JPEG (83.6% reduction)
- Quality: Excellent detail preservation for complex artwork

**Naming convention:**
- Use descriptive names with dates: `substack-header-2026-03.jpg`
- Include purpose: `substack-`, `blog-post-`, `article-`, `robot-art-collage-`
- Include date for tracking: `-2026-03` or `-2026-03-16`

**Handling multiple image variations:**
When you have multiple versions of the same image (e.g., `_1.png`, `_2.png`), convert each with descriptive suffixes:
- `robot-art-collage-v1-2026-03.jpg`
- `robot-art-collage-v2-2026-03.jpg`
- `robot-art-collage-v3-2026-03.jpg`

## Best Practices

1. **Quality Settings**:
   - 95-100: Maximum quality, larger files
   - 85-95: High quality, good for photos
   - 75-85: Good quality, balanced size (recommended)
   - 60-75: Acceptable quality, smaller files
   - Below 60: Lower quality, very small files

2. **Format Choice**:
   - Use JPEG for photos and complex images
   - Use PNG for images with transparency or text
   - Use WebP for modern web applications (future support)

3. **Batch Processing**:
   - Process multiple files in parallel for speed
   - Keep originals as backup
   - Use consistent naming conventions

## Dependencies

- **Python**: Pillow (`pip install Pillow` or `uv pip install Pillow`)
- **Rust**: image crate (included in Cargo.toml)

## Troubleshooting

If the Rust CLI fails to build due to edition2024 requirements:
1. Use image crate version 0.24 instead of 0.25
2. Or use the Python implementation as fallback

## Related Skills

- `download-url` - Download images from the web
- `getting-file-view-links` - Share optimized images via web links
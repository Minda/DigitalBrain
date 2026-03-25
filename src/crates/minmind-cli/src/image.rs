//! Image optimization utilities

use anyhow::Result;
use image::{GenericImageView, ImageFormat, ImageOutputFormat};
use std::fs;
use std::io::{BufReader, BufWriter};
use std::path::Path;

/// Optimize an image file
pub fn optimize_image(
    input_path: &Path,
    output_path: &Path,
    quality: u8,
    format: Option<String>,
) -> Result<()> {
    // Open the input image
    let input_file = fs::File::open(input_path)?;
    let reader = BufReader::new(input_file);

    // Load the image
    let img = image::load(reader, ImageFormat::from_path(input_path)?)?;

    // Determine output format
    let output_format = if let Some(fmt) = format {
        match fmt.to_lowercase().as_str() {
            "jpg" | "jpeg" => ImageOutputFormat::Jpeg(quality),
            "png" => ImageOutputFormat::Png,
            "webp" => {
                // WebP is not directly supported by the image crate
                // For now, default to JPEG
                eprintln!("WebP format not supported yet, using JPEG instead");
                ImageOutputFormat::Jpeg(quality)
            }
            _ => {
                eprintln!("Unknown format '{}', using JPEG", fmt);
                ImageOutputFormat::Jpeg(quality)
            }
        }
    } else {
        // Default to JPEG for optimization
        ImageOutputFormat::Jpeg(quality)
    };

    // Create output file
    let output_file = fs::File::create(output_path)?;
    let writer = BufWriter::new(output_file);

    // Write the optimized image
    img.write_to(&mut BufWriter::new(writer), output_format)?;

    // Report size reduction
    let input_size = fs::metadata(input_path)?.len();
    let output_size = fs::metadata(output_path)?.len();
    let reduction = 100.0 - (output_size as f64 / input_size as f64 * 100.0);

    println!("✓ Image optimized successfully!");
    println!("  Input:  {} ({} bytes)", input_path.display(), input_size);
    println!("  Output: {} ({} bytes)", output_path.display(), output_size);
    println!("  Size reduction: {:.1}%", reduction);

    Ok(())
}

/// Get image information
pub fn get_image_info(path: &Path) -> Result<()> {
    let img = image::open(path)?;
    let (width, height) = img.dimensions();
    let color_type = img.color();
    let file_size = fs::metadata(path)?.len();

    println!("Image Information:");
    println!("  File: {}", path.display());
    println!("  Dimensions: {}x{}", width, height);
    println!("  Color type: {:?}", color_type);
    println!("  File size: {} bytes ({:.2} MB)", file_size, file_size as f64 / 1_048_576.0);

    Ok(())
}
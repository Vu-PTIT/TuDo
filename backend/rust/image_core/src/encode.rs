use std::io::Cursor;

use image::{
    codecs::{jpeg::JpegEncoder, png::PngEncoder, webp::WebPEncoder},
    DynamicImage, ExtendedColorType, GenericImageView, ImageEncoder,
};

use crate::decode::SupportedFormat;
use crate::errors::ImageCoreError;

const JPEG_QUALITY: u8 = 88;

/// Re-encodes a DynamicImage into a fresh byte buffer with no source EXIF/ICC/XMP metadata.
pub fn encode_clean_image(
    img: &DynamicImage,
    source_format: SupportedFormat,
    preserve_alpha: bool,
) -> Result<(Vec<u8>, SupportedFormat), ImageCoreError> {
    let has_alpha = img.color().has_alpha() && preserve_alpha;
    let target_format = match (source_format, has_alpha) {
        (SupportedFormat::Jpeg, true) => SupportedFormat::Png,
        (fmt, _) => fmt,
    };

    let (width, height) = img.dimensions();
    let mut out = Vec::new();

    match target_format {
        SupportedFormat::Jpeg => {
            let rgb = img.to_rgb8();
            let encoder = JpegEncoder::new_with_quality(&mut out, JPEG_QUALITY);
            encoder
                .write_image(rgb.as_raw(), width, height, ExtendedColorType::Rgb8)
                .map_err(|e| {
                    ImageCoreError::invalid_image(format!("Failed to encode JPEG: {e}"))
                })?;
        }
        SupportedFormat::Png => {
            let encoder = PngEncoder::new(Cursor::new(&mut out));
            if has_alpha {
                let rgba = img.to_rgba8();
                encoder
                    .write_image(rgba.as_raw(), width, height, ExtendedColorType::Rgba8)
                    .map_err(|e| {
                        ImageCoreError::invalid_image(format!("Failed to encode PNG: {e}"))
                    })?;
            } else {
                let rgb = img.to_rgb8();
                encoder
                    .write_image(rgb.as_raw(), width, height, ExtendedColorType::Rgb8)
                    .map_err(|e| {
                        ImageCoreError::invalid_image(format!("Failed to encode PNG: {e}"))
                    })?;
            }
        }
        SupportedFormat::WebP => {
            let encoder = WebPEncoder::new_lossless(Cursor::new(&mut out));
            if has_alpha {
                let rgba = img.to_rgba8();
                encoder
                    .write_image(rgba.as_raw(), width, height, ExtendedColorType::Rgba8)
                    .map_err(|e| {
                        ImageCoreError::invalid_image(format!("Failed to encode WebP: {e}"))
                    })?;
            } else {
                let rgb = img.to_rgb8();
                encoder
                    .write_image(rgb.as_raw(), width, height, ExtendedColorType::Rgb8)
                    .map_err(|e| {
                        ImageCoreError::invalid_image(format!("Failed to encode WebP: {e}"))
                    })?;
            }
        }
    }

    Ok((out, target_format))
}


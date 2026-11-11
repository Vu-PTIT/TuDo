use std::io::Cursor;

use image::{DynamicImage, ImageFormat, ImageReader, Limits};

use crate::errors::ImageCoreError;
use crate::limits::{ImageLimits, MAX_DECODE_ALLOC_BYTES};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SupportedFormat {
    Jpeg,
    Png,
    WebP,
}

impl SupportedFormat {
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::Jpeg => "jpeg",
            Self::Png => "png",
            Self::WebP => "webp",
        }
    }

    pub fn to_image_format(self) -> ImageFormat {
        match self {
            Self::Jpeg => ImageFormat::Jpeg,
            Self::Png => ImageFormat::Png,
            Self::WebP => ImageFormat::WebP,
        }
    }
}

pub fn detect_format(data: &[u8]) -> Result<SupportedFormat, ImageCoreError> {
    if is_heic_or_heif(data) {
        return Err(ImageCoreError::unsupported_format(
            "HEIC/HEIF format is not supported in MVP; please convert to JPG, PNG, or WebP",
        ));
    }

    let guessed = image::guess_format(data).map_err(|_| {
        ImageCoreError::unsupported_format(
            "Unable to recognize image format; only JPG, PNG, and WebP are supported",
        )
    })?;

    match guessed {
        ImageFormat::Jpeg => Ok(SupportedFormat::Jpeg),
        ImageFormat::Png => Ok(SupportedFormat::Png),
        ImageFormat::WebP => Ok(SupportedFormat::WebP),
        other => Err(ImageCoreError::unsupported_format(format!(
            "Format {:?} is not supported; only JPG, PNG, and WebP are supported",
            other
        ))),
    }
}

fn is_heic_or_heif(data: &[u8]) -> bool {
    if data.len() < 12 {
        return false;
    }
    if &data[4..8] != b"ftyp" {
        return false;
    }
    let brand = &data[8..12];
    matches!(
        brand,
        b"heic" | b"heix" | b"hevc" | b"hevx" | b"mif1" | b"msf1" | b"avif"
    )
}

/// Extract EXIF Orientation tag (1..=8) from JPEG or WebP/PNG bytes if present.
pub fn extract_exif_orientation(data: &[u8]) -> u16 {
    // Check JPEG APP1 EXIF marker
    if data.len() > 4 && data[0] == 0xFF && data[1] == 0xD8 {
        let mut offset = 2usize;
        while offset + 4 <= data.len() {
            if data[offset] != 0xFF {
                break;
            }
            let marker = data[offset + 1];
            if marker == 0xDA || marker == 0xD9 {
                break;
            }
            let seg_len = u16::from_be_bytes([data[offset + 2], data[offset + 3]]) as usize;
            if seg_len < 2 || offset + 2 + seg_len > data.len() {
                break;
            }
            if marker == 0xE1 && seg_len >= 8 {
                let payload = &data[offset + 4..offset + 2 + seg_len];
                if payload.starts_with(b"Exif\0\0") {
                    if let Some(orient) = parse_tiff_orientation(&payload[6..]) {
                        return orient;
                    }
                }
            }
            offset += 2 + seg_len;
        }
    }
    1
}

fn parse_tiff_orientation(tiff: &[u8]) -> Option<u16> {
    if tiff.len() < 8 {
        return None;
    }
    let little_endian = match &tiff[0..2] {
        b"II" => true,
        b"MM" => false,
        _ => return None,
    };
    let read_u16 = |b: &[u8], pos: usize| -> Option<u16> {
        let slice = b.get(pos..pos + 2)?;
        Some(if little_endian {
            u16::from_le_bytes([slice[0], slice[1]])
        } else {
            u16::from_be_bytes([slice[0], slice[1]])
        })
    };
    let read_u32 = |b: &[u8], pos: usize| -> Option<u32> {
        let slice = b.get(pos..pos + 4)?;
        Some(if little_endian {
            u32::from_le_bytes([slice[0], slice[1], slice[2], slice[3]])
        } else {
            u32::from_be_bytes([slice[0], slice[1], slice[2], slice[3]])
        })
    };

    if read_u16(tiff, 2)? != 42 {
        return None;
    }
    let ifd_offset = read_u32(tiff, 4)? as usize;
    let num_entries = read_u16(tiff, ifd_offset)? as usize;
    let entries_start = ifd_offset.checked_add(2)?;

    for i in 0..num_entries {
        let entry_offset = entries_start.checked_add(i.checked_mul(12)?)?;
        let tag = read_u16(tiff, entry_offset)?;
        if tag == 0x0112 {
            // Orientation tag
            let field_type = read_u16(tiff, entry_offset + 2)?;
            let count = read_u32(tiff, entry_offset + 4)?;
            if field_type == 3 && count == 1 {
                let val = read_u16(tiff, entry_offset + 8)?;
                if (1..=8).contains(&val) {
                    return Some(val);
                }
            }
        }
    }
    None
}

pub fn apply_orientation(img: DynamicImage, orientation: u16) -> DynamicImage {
    match orientation {
        2 => img.fliph(),
        3 => img.rotate180(),
        4 => img.flipv(),
        5 => img.rotate90().fliph(),
        6 => img.rotate90(),
        7 => img.rotate270().fliph(),
        8 => img.rotate270(),
        _ => img,
    }
}

pub fn decode_and_orient(
    data: &[u8],
    limits: &ImageLimits,
) -> Result<(DynamicImage, SupportedFormat), ImageCoreError> {
    limits.check_byte_size(data)?;
    let format = detect_format(data)?;

    let mut reader = ImageReader::with_format(Cursor::new(data), format.to_image_format());
    let mut decoder_limits = Limits::default();
    decoder_limits.max_alloc = Some(MAX_DECODE_ALLOC_BYTES);
    reader.limits(decoder_limits);

    let (width, height) = reader
        .into_dimensions()
        .map_err(|e| ImageCoreError::invalid_image(format!("Failed to read image header: {e}")))?;

    limits.check_dimensions(width, height)?;

    let mut reader = ImageReader::with_format(Cursor::new(data), format.to_image_format());
    let mut decoder_limits = Limits::default();
    decoder_limits.max_alloc = Some(MAX_DECODE_ALLOC_BYTES);
    reader.limits(decoder_limits);

    let decoded = reader
        .decode()
        .map_err(|e| ImageCoreError::invalid_image(format!("Failed to decode image: {e}")))?;

    let orientation = extract_exif_orientation(data);
    let oriented = apply_orientation(decoded, orientation);

    Ok((oriented, format))
}


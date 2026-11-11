use crate::errors::ImageCoreError;

pub const DEFAULT_MAX_BYTES: usize = 10 * 1024 * 1024; // 10 MB
pub const DEFAULT_MAX_PIXELS: u64 = 25_000_000; // 25 Megapixels
pub const DEFAULT_MAX_DIMENSION: u32 = 2048; // Normalized output max edge
pub const DEFAULT_THUMBNAIL_SIZE: u32 = 400; // Thumbnail max edge
pub const MAX_DECODE_ALLOC_BYTES: u64 = 128 * 1024 * 1024; // 128 MB decoder memory cap

#[derive(Debug, Clone, Copy)]
pub struct ImageLimits {
    pub max_bytes: usize,
    pub max_pixels: u64,
    pub max_dimension: u32,
    pub thumbnail_size: u32,
}

impl Default for ImageLimits {
    fn default() -> Self {
        Self {
            max_bytes: DEFAULT_MAX_BYTES,
            max_pixels: DEFAULT_MAX_PIXELS,
            max_dimension: DEFAULT_MAX_DIMENSION,
            thumbnail_size: DEFAULT_THUMBNAIL_SIZE,
        }
    }
}

impl ImageLimits {
    pub fn check_byte_size(&self, data: &[u8]) -> Result<(), ImageCoreError> {
        if data.is_empty() {
            return Err(ImageCoreError::invalid_image("Image byte stream is empty"));
        }
        if data.len() > self.max_bytes {
            return Err(ImageCoreError::too_large(format!(
                "Image size {} bytes exceeds maximum allowed {} bytes",
                data.len(),
                self.max_bytes
            )));
        }
        Ok(())
    }

    pub fn check_dimensions(&self, width: u32, height: u32) -> Result<(), ImageCoreError> {
        if width == 0 || height == 0 {
            return Err(ImageCoreError::invalid_image(
                "Image dimensions must be positive",
            ));
        }
        let pixels = (width as u64).saturating_mul(height as u64);
        if pixels > self.max_pixels {
            return Err(ImageCoreError::too_large(format!(
                "Image pixel count {} ({}x{}) exceeds maximum allowed {} pixels",
                pixels, width, height, self.max_pixels
            )));
        }
        Ok(())
    }
}


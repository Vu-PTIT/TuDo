use image::{imageops::FilterType, DynamicImage, GenericImageView};

pub fn resize_within(img: &DynamicImage, max_edge: u32) -> DynamicImage {
    let (w, h) = img.dimensions();
    if w <= max_edge && h <= max_edge {
        return img.clone();
    }
    img.resize(max_edge, max_edge, FilterType::Lanczos3)
}

pub fn create_thumbnail(img: &DynamicImage, thumbnail_size: u32) -> DynamicImage {
    let (w, h) = img.dimensions();
    if w <= thumbnail_size && h <= thumbnail_size {
        return img.clone();
    }
    img.resize(thumbnail_size, thumbnail_size, FilterType::Triangle)
}

pub fn has_meaningful_alpha(img: &DynamicImage) -> bool {
    if !img.color().has_alpha() {
        return false;
    }
    let rgba = img.to_rgba8();
    let mut has_opaque_or_semi = false;
    for pixel in rgba.pixels() {
        if pixel[3] > 0 {
            has_opaque_or_semi = true;
            break;
        }
    }
    has_opaque_or_semi
}


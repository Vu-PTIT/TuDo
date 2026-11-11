use closet_loop_image_core::errors::ImageErrorCode;
use closet_loop_image_core::limits::ImageLimits;
use closet_loop_image_core::{normalize_image_native, validate_cutout_native};
use image::{DynamicImage, RgbaImage};
use std::io::Cursor;

#[test]
fn rejects_empty_input() {
    let limits = ImageLimits::default();
    let err = normalize_image_native(&[], &limits).unwrap_err();
    assert_eq!(err.code, ImageErrorCode::InvalidImage);
}

#[test]
fn rejects_exceeding_byte_limit() {
    let mut limits = ImageLimits::default();
    limits.max_bytes = 64;
    let data = vec![0u8; 100];
    let err = normalize_image_native(&data, &limits).unwrap_err();
    assert_eq!(err.code, ImageErrorCode::ImageTooLarge);
}

#[test]
fn rejects_heic_magic_bytes() {
    let limits = ImageLimits::default();
    let heic_header = b"\x00\x00\x00\x18ftypheic\x00\x00\x00\x00";
    let err = normalize_image_native(heic_header, &limits).unwrap_err();
    assert_eq!(err.code, ImageErrorCode::UnsupportedFormat);
}

#[test]
fn rejects_gif_format() {
    let limits = ImageLimits::default();
    let gif_header = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;";
    let err = normalize_image_native(gif_header, &limits).unwrap_err();
    assert_eq!(err.code, ImageErrorCode::UnsupportedFormat);
}

#[test]
fn rejects_exceeding_pixel_limit() {
    let mut limits = ImageLimits::default();
    limits.max_pixels = 100; // max 10x10

    let img = DynamicImage::ImageRgba8(RgbaImage::new(20, 20));
    let mut buf = Vec::new();
    img.write_to(&mut Cursor::new(&mut buf), image::ImageFormat::Png)
        .unwrap();

    let err = normalize_image_native(&buf, &limits).unwrap_err();
    assert_eq!(err.code, ImageErrorCode::ImageTooLarge);
}

#[test]
fn rejects_cutout_without_alpha() {
    let limits = ImageLimits::default();
    let img = DynamicImage::new_rgb8(16, 16);
    let mut buf = Vec::new();
    img.write_to(&mut Cursor::new(&mut buf), image::ImageFormat::Jpeg)
        .unwrap();

    let err = validate_cutout_native(&buf, &limits).unwrap_err();
    assert_eq!(err.code, ImageErrorCode::InvalidImage);
}


use closet_loop_image_core::decode::extract_exif_orientation;
use closet_loop_image_core::limits::ImageLimits;
use closet_loop_image_core::{normalize_image_native, validate_cutout_native};
use image::{DynamicImage, GenericImageView, Rgba, RgbaImage};
use std::io::Cursor;

#[test]
fn normalizes_and_creates_thumbnail() {
    let mut limits = ImageLimits::default();
    limits.max_dimension = 100;
    limits.thumbnail_size = 40;

    let img = DynamicImage::new_rgb8(200, 100);
    let mut buf = Vec::new();
    img.write_to(&mut Cursor::new(&mut buf), image::ImageFormat::Jpeg)
        .unwrap();

    let out = normalize_image_native(&buf, &limits).unwrap();
    assert_eq!(out.width, 100);
    assert_eq!(out.height, 50);
    assert_eq!(out.thumbnail_width, 40);
    assert_eq!(out.thumbnail_height, 20);
    assert_eq!(out.format, "jpeg");
    assert!(!out.has_alpha);
}

#[test]
fn strips_exif_and_applies_orientation() {
    let img = DynamicImage::new_rgb8(40, 20);
    let mut jpeg_bytes = Vec::new();
    img.write_to(&mut Cursor::new(&mut jpeg_bytes), image::ImageFormat::Jpeg)
        .unwrap();

    // Inject minimal APP1 Exif header with Orientation = 6 (Rotate 90 CW) right after SOI (FF D8)
    let exif_tiff: [u8; 26] = [
        b'I', b'I', 42, 0, 8, 0, 0, 0, // Little-endian TIFF header, IFD at offset 8
        1, 0, // 1 entry
        0x12, 0x01, // Tag 0x0112 (Orientation)
        3, 0, // Type SHORT (3)
        1, 0, 0, 0, // Count 1
        6, 0, 0, 0, // Value 6 (Rotate 90 CW)
        0, 0, 0, 0, // Next IFD offset 0
    ];
    let mut app1 = vec![0xFF, 0xE1];
    let seg_len = (2 + 6 + exif_tiff.len()) as u16;
    app1.extend_from_slice(&seg_len.to_be_bytes());
    app1.extend_from_slice(b"Exif\0\0");
    app1.extend_from_slice(&exif_tiff);

    let mut with_exif = Vec::new();
    with_exif.extend_from_slice(&jpeg_bytes[..2]);
    with_exif.extend_from_slice(&app1);
    with_exif.extend_from_slice(&jpeg_bytes[2..]);

    assert_eq!(extract_exif_orientation(&with_exif), 6);

    let limits = ImageLimits::default();
    let out = normalize_image_native(&with_exif, &limits).unwrap();
    // 40x20 rotated 90 CW becomes 20x40
    assert_eq!(out.width, 20);
    assert_eq!(out.height, 40);
    // Clean output has no EXIF orientation
    assert_eq!(extract_exif_orientation(&out.image_bytes), 1);
    assert!(!out.image_bytes.windows(6).any(|w| w == b"Exif\0\0"));
}

#[test]
fn preserves_alpha_in_cutout() {
    let mut rgba = RgbaImage::new(32, 32);
    rgba.put_pixel(10, 10, Rgba([255, 50, 100, 200]));
    let img = DynamicImage::ImageRgba8(rgba);

    let mut buf = Vec::new();
    img.write_to(&mut Cursor::new(&mut buf), image::ImageFormat::Png)
        .unwrap();

    let limits = ImageLimits::default();
    let out = validate_cutout_native(&buf, &limits).unwrap();
    assert!(out.has_alpha);
    assert_eq!(out.format, "png");

    let decoded = image::load_from_memory(&out.image_bytes).unwrap();
    assert!(decoded.color().has_alpha());
    assert_eq!(decoded.dimensions(), (32, 32));
}


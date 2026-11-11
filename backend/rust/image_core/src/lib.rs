pub mod decode;
pub mod encode;
pub mod errors;
pub mod limits;
pub mod transform;

use image::GenericImageView;

use crate::decode::decode_and_orient;
use crate::encode::encode_clean_image;
use crate::errors::ImageCoreError;
use crate::limits::ImageLimits;
use crate::transform::{create_thumbnail, has_meaningful_alpha, resize_within};

#[derive(Debug, Clone)]
pub struct NormalizedImageOutput {
    pub image_bytes: Vec<u8>,
    pub thumbnail_bytes: Vec<u8>,
    pub width: u32,
    pub height: u32,
    pub thumbnail_width: u32,
    pub thumbnail_height: u32,
    pub format: String,
    pub has_alpha: bool,
}

pub fn normalize_image_native(
    data: &[u8],
    limits: &ImageLimits,
) -> Result<NormalizedImageOutput, ImageCoreError> {
    let (oriented, source_format) = decode_and_orient(data, limits)?;
    let normalized = resize_within(&oriented, limits.max_dimension);
    let (width, height) = normalized.dimensions();
    let has_alpha = normalized.color().has_alpha();

    let (image_bytes, final_format) = encode_clean_image(&normalized, source_format, has_alpha)?;

    let thumb = create_thumbnail(&normalized, limits.thumbnail_size);
    let (thumbnail_width, thumbnail_height) = thumb.dimensions();
    let (thumbnail_bytes, _) = encode_clean_image(&thumb, final_format, has_alpha)?;

    Ok(NormalizedImageOutput {
        image_bytes,
        thumbnail_bytes,
        width,
        height,
        thumbnail_width,
        thumbnail_height,
        format: final_format.as_str().to_string(),
        has_alpha,
    })
}

pub fn validate_cutout_native(
    data: &[u8],
    limits: &ImageLimits,
) -> Result<NormalizedImageOutput, ImageCoreError> {
    let (oriented, source_format) = decode_and_orient(data, limits)?;
    if !has_meaningful_alpha(&oriented) {
        return Err(ImageCoreError::invalid_image(
            "Cutout image must contain an alpha channel and non-empty foreground pixels",
        ));
    }

    let normalized = resize_within(&oriented, limits.max_dimension);
    let (width, height) = normalized.dimensions();
    let (image_bytes, final_format) = encode_clean_image(&normalized, source_format, true)?;

    let thumb = create_thumbnail(&normalized, limits.thumbnail_size);
    let (thumbnail_width, thumbnail_height) = thumb.dimensions();
    let (thumbnail_bytes, _) = encode_clean_image(&thumb, final_format, true)?;

    Ok(NormalizedImageOutput {
        image_bytes,
        thumbnail_bytes,
        width,
        height,
        thumbnail_width,
        thumbnail_height,
        format: final_format.as_str().to_string(),
        has_alpha: true,
    })
}

#[cfg(feature = "python")]
mod python_bindings {
    use pyo3::exceptions::PyValueError;
    use pyo3::prelude::*;
    use pyo3::types::{PyBytes, PyDict};

    use super::*;
    use crate::limits::{
        DEFAULT_MAX_BYTES, DEFAULT_MAX_DIMENSION, DEFAULT_MAX_PIXELS, DEFAULT_THUMBNAIL_SIZE,
    };

    fn to_py_err(err: ImageCoreError) -> PyErr {
        PyValueError::new_err((err.code_str, err.message))
    }

    fn output_to_py_dict(py: Python<'_>, output: NormalizedImageOutput) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        dict.set_item("image_bytes", PyBytes::new(py, &output.image_bytes))?;
        dict.set_item("thumbnail_bytes", PyBytes::new(py, &output.thumbnail_bytes))?;
        dict.set_item("width", output.width)?;
        dict.set_item("height", output.height)?;
        dict.set_item("thumbnail_width", output.thumbnail_width)?;
        dict.set_item("thumbnail_height", output.thumbnail_height)?;
        dict.set_item("format", output.format)?;
        dict.set_item("has_alpha", output.has_alpha)?;
        Ok(dict.into_any().unbind())
    }

    #[pyfunction]
    #[pyo3(signature = (
        data,
        max_bytes = DEFAULT_MAX_BYTES,
        max_pixels = DEFAULT_MAX_PIXELS,
        max_dimension = DEFAULT_MAX_DIMENSION,
        thumbnail_size = DEFAULT_THUMBNAIL_SIZE
    ))]
    fn normalize_image(
        py: Python<'_>,
        data: &[u8],
        max_bytes: usize,
        max_pixels: u64,
        max_dimension: u32,
        thumbnail_size: u32,
    ) -> PyResult<PyObject> {
        let limits = ImageLimits {
            max_bytes,
            max_pixels,
            max_dimension,
            thumbnail_size,
        };
        let input_vec = data.to_vec();
        let result = py
            .allow_threads(move || normalize_image_native(&input_vec, &limits))
            .map_err(to_py_err)?;
        output_to_py_dict(py, result)
    }

    #[pyfunction]
    #[pyo3(signature = (
        data,
        max_bytes = DEFAULT_MAX_BYTES,
        max_pixels = DEFAULT_MAX_PIXELS,
        max_dimension = DEFAULT_MAX_DIMENSION,
        thumbnail_size = DEFAULT_THUMBNAIL_SIZE
    ))]
    fn validate_cutout(
        py: Python<'_>,
        data: &[u8],
        max_bytes: usize,
        max_pixels: u64,
        max_dimension: u32,
        thumbnail_size: u32,
    ) -> PyResult<PyObject> {
        let limits = ImageLimits {
            max_bytes,
            max_pixels,
            max_dimension,
            thumbnail_size,
        };
        let input_vec = data.to_vec();
        let result = py
            .allow_threads(move || validate_cutout_native(&input_vec, &limits))
            .map_err(to_py_err)?;
        output_to_py_dict(py, result)
    }

    #[pymodule]
    fn closet_loop_image_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
        m.add_function(wrap_pyfunction!(normalize_image, m)?)?;
        m.add_function(wrap_pyfunction!(validate_cutout, m)?)?;
        Ok(())
    }
}

use thiserror::Error;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ImageErrorCode {
    InvalidImage,
    ImageTooLarge,
    UnsupportedFormat,
}

impl ImageErrorCode {
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::InvalidImage => "INVALID_IMAGE",
            Self::ImageTooLarge => "IMAGE_TOO_LARGE",
            Self::UnsupportedFormat => "UNSUPPORTED_FORMAT",
        }
    }
}

#[derive(Debug, Error, Clone, PartialEq, Eq)]
#[error("{code_str}: {message}")]
pub struct ImageCoreError {
    pub code: ImageErrorCode,
    pub code_str: &'static str,
    pub message: String,
}

impl ImageCoreError {
    pub fn new(code: ImageErrorCode, message: impl Into<String>) -> Self {
        Self {
            code,
            code_str: code.as_str(),
            message: message.into(),
        }
    }

    pub fn invalid_image(message: impl Into<String>) -> Self {
        Self::new(ImageErrorCode::InvalidImage, message)
    }

    pub fn too_large(message: impl Into<String>) -> Self {
        Self::new(ImageErrorCode::ImageTooLarge, message)
    }

    pub fn unsupported_format(message: impl Into<String>) -> Self {
        Self::new(ImageErrorCode::UnsupportedFormat, message)
    }
}


#!/usr/bin/env python3
"""
FastMCP Compatibility Utilities

This module provides compatibility fixes and enhancements for FastMCP Image types
to resolve serialization issues and improve API consistency.

Issue #171: FastMCP Image class stores format in _format (private attribute)
but some code may expect to access it as .format (public attribute).
"""

from typing import Any
from fastmcp.utilities.types import Image as FastMCPImage


def patch_fastmcp_image_compatibility():
    """
    Patch FastMCP Image class to add public format property for compatibility.

    This function adds a public 'format' property to the FastMCP Image class
    that provides access to the private '_format' attribute, ensuring backward
    compatibility with code that expects to access the format directly.
    """

    # Check if the property already exists to avoid double-patching
    if hasattr(FastMCPImage, 'format') and isinstance(getattr(FastMCPImage, 'format'), property):
        return  # Already patched

    def format_property(self) -> str | None:
        """Get the image format."""
        return getattr(self, '_format', None)

    def format_setter(self, value: str | None) -> None:
        """Set the image format."""
        self._format = value
        # Update mime type when format changes
        self._mime_type = self._get_mime_type()

    # Add the format property to the FastMCP Image class
    FastMCPImage.format = property(format_property, format_setter, doc="Image format (e.g., 'png', 'jpeg')")


def create_enhanced_image(
        path: str | None = None,
        data: bytes | None = None,
        format: str | None = None,
        annotations: Any | None = None
) -> FastMCPImage:
    """
    Create a FastMCP Image with enhanced compatibility.

    This function creates a FastMCP Image and ensures the compatibility
    patch is applied, providing a consistent API.

    Args:
        path: Path to image file
        data: Raw image data as bytes
        format: Image format (e.g., 'png', 'jpeg')
        annotations: Optional annotations

    Returns:
        FastMCP Image instance with compatibility enhancements
    """
    # Ensure compatibility patch is applied
    patch_fastmcp_image_compatibility()

    # Create the image using the standard FastMCP constructor
    return FastMCPImage(path=path, data=data, format=format, annotations=annotations)


def ensure_image_compatibility(image: FastMCPImage) -> FastMCPImage:
    """
    Ensure an existing FastMCP Image has compatibility enhancements.

    Args:
        image: Existing FastMCP Image instance

    Returns:
        The same image instance with compatibility enhancements applied
    """
    # Ensure compatibility patch is applied to the class
    patch_fastmcp_image_compatibility()

    return image


def get_image_format(image: FastMCPImage) -> str | None:
    """
    Safely get the format of a FastMCP Image.

    This function provides a safe way to get the image format regardless
    of whether the compatibility patch has been applied.

    Args:
        image: FastMCP Image instance

    Returns:
        Image format string or None if not set
    """
    # Try the public property first (if patched)
    if hasattr(image, 'format') and isinstance(getattr(type(image), 'format', None), property):
        return image.format

    # Fall back to private attribute
    return getattr(image, '_format', None)


def get_image_mime_type(image: FastMCPImage) -> str:
    """
    Safely get the MIME type of a FastMCP Image.

    Args:
        image: FastMCP Image instance

    Returns:
        MIME type string
    """
    return getattr(image, '_mime_type', 'application/octet-stream')


def serialize_image_info(image: FastMCPImage) -> dict[str, Any]:
    """
    Serialize FastMCP Image information for debugging/logging.

    This function safely extracts image information without risking
    attribute access errors.

    Args:
        image: FastMCP Image instance

    Returns:
        Dictionary with image information
    """
    return {
        'type': type(image).__name__,
        'format': get_image_format(image),
        'mime_type': get_image_mime_type(image),
        'has_data': image.data is not None,
        'data_length': len(image.data) if image.data else 0,
        'has_path': image.path is not None,
        'path': str(image.path) if image.path else None,
        'has_annotations': image.annotations is not None,
    }


# Auto-apply the compatibility patch when this module is imported
patch_fastmcp_image_compatibility()
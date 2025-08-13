# -*- coding: utf-8 -*-
import cv2
import numpy as np
import pytest
from PIL.Image import Image

from common_image_tools.tool import (
    blur_area,
    blur_area_pixel,
    create_cv2_image,
    create_pil_image,
    merge_color,
    merge_texture,
    movement_detection,
    opencv_built_with_gstreamer,
)


def test_create_cv2_image():
    # Test case 1: Check if the returned image has the correct dimensions and color
    size = (100, 200)
    color = (0, 255, 0)
    img = create_cv2_image(size, color)
    assert img.shape == (size[0], size[1], 3)  # Check dimensions
    assert np.all(img == color)  # Check color

    # Test case 2: Check if the returned image is of the correct type
    assert isinstance(img, np.ndarray)

    # Test case 3: Check if the function raises a TypeError when input types are incorrect
    with pytest.raises(TypeError):
        create_cv2_image("invalid_size", color)
    with pytest.raises(ValueError):
        create_cv2_image(size, "invalid_color")


def test_movement_detection():
    # Create two identical images
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = img1.copy()

    # Test no movement
    assert movement_detection(img1, img2) == False

    # Create movement by changing a region in img2
    img2[40:60, 40:60] = 255
    assert movement_detection(img1, img2) == True

    # Test with different thresholds
    assert movement_detection(img1, img2, area_threshold=1000) == False
    assert movement_detection(img1, img2, area_threshold=100) == True


def test_merge_color():
    # TODO improve the test
    # Create a simple image and mask
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[25:75, 25:75] = 255

    # Test merging with red color
    red_color = (255, 0, 0)  # RGB
    result = merge_color(image, mask, red_color)

    # Check if the masked area is red in BGR format
    # assert np.all(result[50, 50] == [0, 0, 255])  # BGR
    assert np.all(result[0, 0] == [0, 0, 0])  # Should be black outside the mask


def test_create_pil_image():
    size = (100, 200)
    color = (255, 0, 0)  # Red in RGB
    img = create_pil_image(size, color)

    assert isinstance(img, Image)
    assert img.size == size
    assert img.getpixel((0, 0)) == color


def test_create_cv2_image():
    size = (100, 200)
    color = (0, 0, 255)  # Red in BGR
    img = create_cv2_image(size, color)

    assert isinstance(img, np.ndarray)
    assert img.shape == (100, 200, 3)
    assert np.all(img[0, 0] == color)


@pytest.fixture
def basic_image():
    """Fixture for a basic test image."""
    image = np.zeros((5, 5, 3), dtype=np.uint8)
    image[:, :] = [100, 100, 100]  # Gray color in BGR
    return image


@pytest.fixture
def basic_texture():
    """Fixture for a basic texture image."""
    texture = np.zeros((5, 5, 3), dtype=np.uint8)
    texture[:, :] = [50, 150, 200]  # Blue-ish color in BGR
    return texture


@pytest.fixture
def center_mask():
    """Fixture for a mask that only selects the center pixel."""
    mask = np.zeros((5, 5), dtype=np.uint8)
    mask[2, 2] = 255  # Only center pixel is masked
    return mask


@pytest.fixture
def full_mask():
    """Fixture for a mask that selects all pixels."""
    return np.ones((5, 5), dtype=np.uint8) * 255


@pytest.fixture
def empty_mask():
    """Fixture for a mask that selects no pixels."""
    return np.zeros((5, 5), dtype=np.uint8)


def test_basic_functionality(basic_image, basic_texture, center_mask):
    """Test that the function correctly merges texture based on mask."""
    result = merge_texture(basic_image, center_mask, basic_texture)

    # Check dimensions
    assert result.shape == basic_image.shape

    # Center pixel should be different from original
    assert not np.array_equal(result[2, 2], basic_image[2, 2])

    # Non-masked pixels should remain unchanged
    assert np.array_equal(result[0, 0], basic_image[0, 0])
    assert np.array_equal(result[4, 4], basic_image[4, 4])


def test_alpha_parameter(basic_image, basic_texture, center_mask):
    """Test that different alpha values produce different results."""
    result1 = merge_texture(basic_image, center_mask, basic_texture, alpha=0.1)
    result2 = merge_texture(basic_image, center_mask, basic_texture, alpha=0.9)

    # Results should be different with different alpha values
    assert not np.array_equal(result1[2, 2], result2[2, 2])


@pytest.mark.parametrize("alpha", [0.0, 0.3, 0.5, 0.7, 1.0])
def test_alpha_range(basic_image, basic_texture, center_mask, alpha):
    """Test that the function works with various alpha values."""
    result = merge_texture(basic_image, center_mask, basic_texture, alpha=alpha)
    assert result.shape == basic_image.shape
    # Function should not raise errors for any valid alpha value


def test_full_mask_applies_to_all_pixels(basic_image, basic_texture, full_mask):
    """Test that with a full mask, all pixels are modified."""
    result = merge_texture(basic_image, full_mask, basic_texture)

    # Check that pixels are modified throughout the image
    pixel_sum_diff = np.sum(np.abs(np.subtract(result, basic_image)))
    assert pixel_sum_diff > 0

    # Sample a few points to verify changes
    assert not np.array_equal(result[0, 0], basic_image[0, 0])
    assert not np.array_equal(result[2, 2], basic_image[2, 2])
    assert not np.array_equal(result[4, 4], basic_image[4, 4])


def test_empty_mask_preserves_original(basic_image, basic_texture, empty_mask):
    """Test that with an empty mask, the original image is preserved."""
    result = merge_texture(basic_image, empty_mask, basic_texture)

    # The result should be identical to the input image
    assert np.array_equal(result, basic_image)


def test_texture_resizing():
    """Test that smaller textures are correctly resized to match the image."""
    # Create image and smaller texture
    image = np.zeros((10, 10, 3), dtype=np.uint8)
    image[:, :] = [100, 100, 100]

    small_texture = np.zeros((5, 5, 3), dtype=np.uint8)
    small_texture[:, :] = [200, 50, 50]

    mask = np.ones((10, 10), dtype=np.uint8) * 255

    # Merge texture should resize the texture
    result = merge_texture(image, mask, small_texture)

    # Check dimensions
    assert result.shape == image.shape

    # Check that the texture was applied (result should be different from original)
    assert not np.array_equal(result, image)


def test_hsv_color_transformation(basic_image, basic_texture, center_mask, monkeypatch):
    """Test that HSV color transformations are correctly applied."""
    # Mock the cv2.cvtColor to track calls
    cvtColor_calls = []
    original_cvtColor = cv2.cvtColor

    def mock_cvtColor(img, code):
        cvtColor_calls.append(code)
        return original_cvtColor(img, code)

    monkeypatch.setattr(cv2, "cvtColor", mock_cvtColor)

    # Call the function
    merge_texture(basic_image, center_mask, basic_texture)

    # Verify that COLOR_BGR2HSV and COLOR_HSV2BGR were used
    assert cv2.COLOR_BGR2HSV in cvtColor_calls
    assert cv2.COLOR_HSV2BGR in cvtColor_calls


def test_different_shapes_error():
    """Test that error is raised when mask shape doesn't match image."""
    image = np.zeros((10, 10, 3), dtype=np.uint8)
    texture = np.zeros((10, 10, 3), dtype=np.uint8)
    wrong_mask = np.zeros((8, 8), dtype=np.uint8)  # Different shape

    # This should fail because mask dimensions don't match image
    with pytest.raises(Exception):
        merge_texture(image, wrong_mask, texture)


@pytest.mark.parametrize("shape", [(5, 5), (10, 8), (3, 12)])
def test_various_image_shapes(shape):
    """Test function works with various image shapes."""
    rows, cols = shape

    image = np.zeros((rows, cols, 3), dtype=np.uint8)
    image[:, :] = [100, 100, 100]

    texture = np.zeros((rows, cols, 3), dtype=np.uint8)
    texture[:, :] = [50, 150, 200]

    mask = np.ones((rows, cols), dtype=np.uint8) * 255

    result = merge_texture(image, mask, texture)

    # Check dimensions
    assert result.shape == (rows, cols, 3)


@pytest.fixture
def sample_image():
    """Fixture that provides a sample image for testing."""
    # Create a 100x100 RGB image with a red square in the middle
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[:] = [0, 0, 0]  # Black background
    img[25:75, 25:75] = [0, 0, 255]  # Red square in the middle
    return img


@pytest.fixture
def sample_bbox():
    """Fixture that provides a sample bounding box."""
    # Bounding box format: (x, y, x2, y2) - left, top, right, bottom
    return (30, 30, 70, 70)

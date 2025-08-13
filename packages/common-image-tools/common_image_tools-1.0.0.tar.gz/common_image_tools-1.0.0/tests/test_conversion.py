from unittest.mock import patch

import cv2
import numpy as np
from PIL import Image

from common_image_tools.conversion import cv2_to_pil, pil_to_cv2


class TestPillowOpenCVConversion:
    def test_pil_to_cv2_rgb(self):
        """Test conversion from PIL RGB image to OpenCV BGR image."""
        # Create a simple RGB PIL image (red, green, blue pixels)
        pil_image = Image.new("RGB", (3, 1))
        pil_image.putpixel((0, 0), (255, 0, 0))  # Red
        pil_image.putpixel((1, 0), (0, 255, 0))  # Green
        pil_image.putpixel((2, 0), (0, 0, 255))  # Blue

        # Convert to OpenCV
        cv2_image = pil_to_cv2(pil_image)

        # Verify conversion (OpenCV uses BGR format)
        assert cv2_image.shape == (1, 3, 3)
        assert np.array_equal(cv2_image[0, 0], [0, 0, 255])  # Red in BGR
        assert np.array_equal(cv2_image[0, 1], [0, 255, 0])  # Green in BGR
        assert np.array_equal(cv2_image[0, 2], [255, 0, 0])  # Blue in BGR

    def test_pil_to_cv2_rgba(self):
        """Test conversion from PIL RGBA image to OpenCV BGRA image."""
        # Create a simple RGBA PIL image
        pil_image = Image.new("RGBA", (2, 1))
        pil_image.putpixel((0, 0), (255, 0, 0, 128))  # Red with 50% alpha
        pil_image.putpixel((1, 0), (0, 255, 0, 255))  # Green with 100% alpha

        # Convert to OpenCV
        cv2_image = pil_to_cv2(pil_image)

        # Verify conversion (OpenCV uses BGRA format)
        assert cv2_image.shape == (1, 2, 4)
        assert np.array_equal(cv2_image[0, 0], [0, 0, 255, 128])  # Red in BGRA
        assert np.array_equal(cv2_image[0, 1], [0, 255, 0, 255])  # Green in BGRA

    def test_cv2_to_pil_bgr(self):
        """Test conversion from OpenCV BGR image to PIL RGB image."""
        # Create a simple BGR OpenCV image
        cv2_image = np.zeros((1, 3, 3), dtype=np.uint8)
        cv2_image[0, 0] = [0, 0, 255]  # Red in BGR
        cv2_image[0, 1] = [0, 255, 0]  # Green in BGR
        cv2_image[0, 2] = [255, 0, 0]  # Blue in BGR

        # Convert to PIL
        pil_image = cv2_to_pil(cv2_image)

        # Verify conversion
        assert pil_image.mode == "RGB"
        assert pil_image.size == (3, 1)
        assert pil_image.getpixel((0, 0)) == (255, 0, 0)  # Red in RGB
        assert pil_image.getpixel((1, 0)) == (0, 255, 0)  # Green in RGB
        assert pil_image.getpixel((2, 0)) == (0, 0, 255)  # Blue in RGB

    def test_cv2_to_pil_bgra(self):
        """Test conversion from OpenCV BGRA image to PIL RGBA image."""
        # Create a simple BGRA OpenCV image
        cv2_image = np.zeros((1, 2, 4), dtype=np.uint8)
        cv2_image[0, 0] = [0, 0, 255, 128]  # Red in BGRA with 50% alpha
        cv2_image[0, 1] = [0, 255, 0, 255]  # Green in BGRA with 100% alpha

        # Convert to PIL
        pil_image = cv2_to_pil(cv2_image)

        # Verify conversion
        assert pil_image.mode == "RGBA"
        assert pil_image.size == (2, 1)
        assert pil_image.getpixel((0, 0)) == (255, 0, 0, 128)  # Red in RGBA
        assert pil_image.getpixel((1, 0)) == (0, 255, 0, 255)  # Green in RGBA

    def test_roundtrip_rgb(self):
        """Test roundtrip conversion: PIL RGB -> OpenCV BGR -> PIL RGB."""
        # Create a simple RGB PIL image
        original = Image.new("RGB", (2, 2))
        original.putpixel((0, 0), (255, 0, 0))
        original.putpixel((1, 0), (0, 255, 0))
        original.putpixel((0, 1), (0, 0, 255))
        original.putpixel((1, 1), (100, 100, 100))

        # Convert PIL -> OpenCV -> PIL
        result = cv2_to_pil(pil_to_cv2(original))

        # Compare pixels
        for x in range(2):
            for y in range(2):
                assert original.getpixel((x, y)) == result.getpixel((x, y))

    def test_roundtrip_rgba(self):
        """Test roundtrip conversion: PIL RGBA -> OpenCV BGRA -> PIL RGBA."""
        # Create a simple RGBA PIL image
        original = Image.new("RGBA", (2, 2))
        original.putpixel((0, 0), (255, 0, 0, 128))
        original.putpixel((1, 0), (0, 255, 0, 200))
        original.putpixel((0, 1), (0, 0, 255, 255))
        original.putpixel((1, 1), (100, 100, 100, 50))

        # Convert PIL -> OpenCV -> PIL
        result = cv2_to_pil(pil_to_cv2(original))

        # Compare pixels
        for x in range(2):
            for y in range(2):
                assert original.getpixel((x, y)) == result.getpixel((x, y))

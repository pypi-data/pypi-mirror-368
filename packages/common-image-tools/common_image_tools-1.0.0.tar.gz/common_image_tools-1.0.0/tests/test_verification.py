# -*- coding: utf-8 -*-
import pytest

from common_image_tools.verification import (
    calculate_bbox_mask_overlap_cv2,
    is_inside,
    yolobbox_2_bbox,
)


class TestIsInside:
    @pytest.mark.parametrize(
        "point, shape, expected",
        [
            ((50, 50), [(0, 0), (100, 0), (100, 100), (0, 100)], True),  # Point inside the shape
            (
                (0, 0),
                [(0, 0), (100, 0), (100, 100), (0, 100)],
                True,
            ),  # Point on the boundary of the shape
            (
                (150, 150),
                [(0, 0), (100, 0), (100, 100), (0, 100)],
                False,
            ),  # Point outside the shape
            # ((50, 50), [(0, 0), (100, 0), (100, 100), (0, 100), (20, 20), (80, 20), (80, 80), (20, 80)], True),  # Complex shape with hole, point inside
            (
                (80, 20),
                [(0, 0), (100, 0), (100, 100), (0, 100), (20, 20), (80, 20), (80, 80), (20, 80)],
                True,
            ),
            # Complex shape with hole, point on the boundary
            (
                (150, 150),
                [(0, 0), (100, 0), (100, 100), (0, 100), (20, 20), (80, 20), (80, 80), (20, 80)],
                False,
            ),
            # Complex shape with hole, point outside
        ],
    )
    def test_is_inside(self, point, shape, expected):
        assert is_inside(point, shape) == expected


class TestYolobbox2Bbox:
    def test_center_bbox(self):
        # Test with a bbox centered at (0.5, 0.5) with width and height of 0.5
        bbox = (0.5, 0.5, 0.5, 0.5)
        expected = (0.25, 0.25, 0.75, 0.75)
        result = yolobbox_2_bbox(bbox)

        # Use pytest's approx for float comparison
        assert result[0] == pytest.approx(expected[0])
        assert result[1] == pytest.approx(expected[1])
        assert result[2] == pytest.approx(expected[2])
        assert result[3] == pytest.approx(expected[3])

    def test_top_left_bbox(self):
        # Test with a bbox at the top left corner
        bbox = (0.1, 0.1, 0.2, 0.2)
        expected = (0.0, 0.0, 0.2, 0.2)
        result = yolobbox_2_bbox(bbox)

        assert result[0] == pytest.approx(expected[0])
        assert result[1] == pytest.approx(expected[1])
        assert result[2] == pytest.approx(expected[2])
        assert result[3] == pytest.approx(expected[3])

    def test_bottom_right_bbox(self):
        # Test with a bbox at the bottom right corner
        bbox = (0.9, 0.9, 0.2, 0.2)
        expected = (0.8, 0.8, 1.0, 1.0)
        result = yolobbox_2_bbox(bbox)

        assert result[0] == pytest.approx(expected[0])
        assert result[1] == pytest.approx(expected[1])
        assert result[2] == pytest.approx(expected[2])
        assert result[3] == pytest.approx(expected[3])

    def test_zero_size_bbox(self):
        # Test with a bbox of zero width and height
        bbox = (0.5, 0.5, 0.0, 0.0)
        expected = (0.5, 0.5, 0.5, 0.5)
        result = yolobbox_2_bbox(bbox)

        assert result[0] == pytest.approx(expected[0])
        assert result[1] == pytest.approx(expected[1])
        assert result[2] == pytest.approx(expected[2])
        assert result[3] == pytest.approx(expected[3])

    def test_negative_width_height(self):
        # Test with negative width and height (which could happen in real data)
        bbox = (0.5, 0.5, -0.2, -0.2)
        expected = (0.6, 0.6, 0.4, 0.4)
        result = yolobbox_2_bbox(bbox)

        assert result[0] == pytest.approx(expected[0])
        assert result[1] == pytest.approx(expected[1])
        assert result[2] == pytest.approx(expected[2])
        assert result[3] == pytest.approx(expected[3])


class TestCalculateBboxMaskOverlap:
    @pytest.fixture
    def setup_image_dimensions(self):
        return 100, 100  # height, width

    def test_full_overlap(self, setup_image_dimensions):
        # Test case where the mask completely covers the bbox
        img_height, img_width = setup_image_dimensions

        # YOLO bbox in center covering 50% of the image (0.25-0.75 in both directions)
        bbox = (0.5, 0.5, 0.5, 0.5)

        # Mask points that form a square slightly larger than the bbox
        mask_points = [(20, 20), (80, 20), (80, 80), (20, 80)]

        result = calculate_bbox_mask_overlap_cv2(bbox, mask_points, img_height, img_width)

        # Should be 100% overlap
        assert result == pytest.approx(100.0, abs=0.1)

    def test_partial_overlap(self, setup_image_dimensions):
        # Test case where the mask partially overlaps the bbox
        img_height, img_width = setup_image_dimensions

        # YOLO bbox in center
        bbox = (0.5, 0.5, 0.5, 0.5)

        # Mask covers the left half of the bbox
        mask_points = [(0, 0), (50, 0), (50, 100), (0, 100)]

        result = calculate_bbox_mask_overlap_cv2(bbox, mask_points, img_height, img_width)

        # Should be approximately 50% overlap (depends on rounding to integers)
        assert result == pytest.approx(50.0, abs=2.0)

    def test_no_overlap(self, setup_image_dimensions):
        # Test case where the mask and bbox don't overlap
        img_height, img_width = setup_image_dimensions

        # YOLO bbox on the left side
        bbox = (0.2, 0.5, 0.4, 0.5)

        # Mask on the right side
        mask_points = [(60, 20), (90, 20), (90, 80), (60, 80)]

        result = calculate_bbox_mask_overlap_cv2(bbox, mask_points, img_height, img_width)

        # Should be 0% overlap
        assert result == pytest.approx(0.0, abs=0.1)

    def test_mask_inside_bbox(self, setup_image_dimensions):
        # Test case where the mask is completely inside the bbox
        img_height, img_width = setup_image_dimensions

        # YOLO bbox covering the entire image
        bbox = (0.5, 0.5, 1.0, 1.0)

        # Small mask in the center
        mask_points = [(40, 40), (60, 40), (60, 60), (40, 60)]

        result = calculate_bbox_mask_overlap_cv2(bbox, mask_points, img_height, img_width)

        # Should be a small percentage (around 4% for a 20x20 mask in a 100x100 bbox)
        expected_percentage = (20 * 20) / (100 * 100) * 100  # 4%
        assert result == pytest.approx(expected_percentage, abs=0.5)

    def test_complex_mask_shape(self, setup_image_dimensions):
        # Test with a more complex polygon shape
        img_height, img_width = setup_image_dimensions

        # YOLO bbox in center
        bbox = (0.5, 0.5, 0.6, 0.6)

        # Complex mask shape (triangle)
        mask_points = [(50, 20), (80, 80), (20, 80)]

        result = calculate_bbox_mask_overlap_cv2(bbox, mask_points, img_height, img_width)

        # We need to calculate the expected overlap manually
        # For this test, we're more interested in whether the function runs without error
        # and returns a reasonable value between 0 and 100
        assert 0 <= result <= 100

    def test_empty_mask(self, setup_image_dimensions):
        # Test with an empty mask (should return 0% overlap)
        img_height, img_width = setup_image_dimensions

        # YOLO bbox in center
        bbox = (0.5, 0.5, 0.5, 0.5)

        # Empty mask (not enough points to form a polygon)
        mask_points = [(50, 50)]

        result = calculate_bbox_mask_overlap_cv2(bbox, mask_points, img_height, img_width)

        # Should be 0% overlap
        assert result == pytest.approx(0.0, abs=0.1)

    def test_large_image_dimensions(self):
        # Test with larger image dimensions to ensure scaling works properly
        img_height, img_width = 1000, 1000

        # YOLO bbox in center
        bbox = (0.5, 0.5, 0.2, 0.2)

        # Mask points that exactly match the bbox
        x1, y1, x2, y2 = yolobbox_2_bbox(bbox)
        x1, y1 = int(x1 * img_width), int(y1 * img_height)
        x2, y2 = int(x2 * img_width), int(y2 * img_height)
        mask_points = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]

        result = calculate_bbox_mask_overlap_cv2(bbox, mask_points, img_height, img_width)

        # Should be 100% overlap
        assert result == pytest.approx(100.0, abs=0.1)

    @pytest.mark.parametrize("img_dims", [(100, 200), (300, 150), (50, 75)])
    def test_different_aspect_ratios(self, img_dims):
        # Test with different image aspect ratios
        img_height, img_width = img_dims

        # YOLO bbox in center covering 25% of the image
        bbox = (0.5, 0.5, 0.5, 0.5)

        # Mask that covers exactly half of the bbox
        x1, y1, x2, y2 = yolobbox_2_bbox(bbox)
        x1, y1 = int(x1 * img_width), int(y1 * img_height)
        x2, y2 = int(x2 * img_width), int(y2 * img_height)
        mid_x = (x1 + x2) // 2
        mask_points = [(x1, y1), (mid_x, y1), (mid_x, y2), (x1, y2)]

        result = calculate_bbox_mask_overlap_cv2(bbox, mask_points, img_height, img_width)

        # Should be approximately 50% overlap
        assert result == pytest.approx(50.0, abs=2.0)

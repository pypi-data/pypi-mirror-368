# -*- coding: utf-8 -*-
from unittest.mock import Mock, patch

import cv2
import dlib
import numpy as np
import pytest
from PIL import Image

from common_image_tools.conversion import cv2_to_pil, pil_to_cv2, rect_to_tuple, tuple_to_rect


class TestTupleToRect:
    @pytest.mark.parametrize(
        "bbox, expected_rect",
        [
            ((0, 0, 10, 10), dlib.rectangle(0, 0, 10, 10)),
            ((-5, -5, 10, 10), dlib.rectangle(-5, -5, 5, 5)),
            ((100, 200, 30, 40), dlib.rectangle(100, 200, 130, 240)),
        ],
    )
    def test_valid_bboxes(self, bbox, expected_rect):
        rect = tuple_to_rect(bbox)
        assert rect == expected_rect


class TestRectToTuple:
    @pytest.mark.parametrize(
        "rect, expected_tuple",
        [
            (dlib.rectangle(0, 0, 10, 10), (0, 0, 10, 10)),  # Test case 1
            (dlib.rectangle(-5, -5, 5, 5), (-5, -5, 10, 10)),  # Test case 2
            (dlib.rectangle(100, 200, 130, 240), (100, 200, 30, 40)),  # Test case 3
            # Add more test cases for other scenarios
        ],
    )
    def test_rect_to_tuple(self, rect, expected_tuple):
        assert rect_to_tuple(rect) == expected_tuple


# Test pil_to_cv2 function
def test_pil_to_cv2_rgb():
    mock_pil_image = Mock(spec=Image.Image)
    mock_np_array = np.array([[[1, 2, 3]]])

    with patch("numpy.array", return_value=mock_np_array):
        with patch("cv2.cvtColor", return_value="cv2_image") as mock_cvtColor:
            result = pil_to_cv2(mock_pil_image)

    assert result == "cv2_image"
    mock_cvtColor.assert_called_once_with(mock_np_array, cv2.COLOR_RGB2BGR)


def test_pil_to_cv2_rgba():
    mock_pil_image = Mock(spec=Image.Image)
    mock_np_array = np.array([[[1, 2, 3, 4]]])

    with patch("numpy.array", return_value=mock_np_array):
        with patch("cv2.cvtColor", return_value="cv2_image") as mock_cvtColor:
            result = pil_to_cv2(mock_pil_image)

    assert result == "cv2_image"
    mock_cvtColor.assert_called_once_with(mock_np_array, cv2.COLOR_RGBA2BGRA)


# Test cv2_to_pil function
def test_cv2_to_pil_rgb():
    mock_cv2_image = np.array([[[1, 2, 3]]])

    with patch("cv2.cvtColor", return_value="rgb_image") as mock_cvtColor:
        with patch("PIL.Image.fromarray", return_value="pil_image") as mock_fromarray:
            result = cv2_to_pil(mock_cv2_image)

    assert result == "pil_image"
    mock_cvtColor.assert_called_once_with(mock_cv2_image, cv2.COLOR_BGR2RGB)
    mock_fromarray.assert_called_once_with("rgb_image")


def test_cv2_to_pil_rgba():
    mock_cv2_image = np.array([[[1, 2, 3, 4]]])

    with patch("cv2.cvtColor", return_value="rgba_image") as mock_cvtColor:
        with patch("PIL.Image.fromarray", return_value="pil_image") as mock_fromarray:
            result = cv2_to_pil(mock_cv2_image)

    assert result == "pil_image"
    mock_cvtColor.assert_called_once_with(mock_cv2_image, cv2.COLOR_BGRA2RGBA)
    mock_fromarray.assert_called_once_with("rgba_image")


# Test rect_to_tuple function
def test_rect_to_tuple():
    mock_rect = Mock(spec=dlib.rectangle)
    mock_rect.left.return_value = 10
    mock_rect.top.return_value = 20
    mock_rect.right.return_value = 30
    mock_rect.bottom.return_value = 50

    result = rect_to_tuple(mock_rect)

    assert result == (10, 20, 20, 30)


# Test tuple_to_rect function
def test_tuple_to_rect():
    bbox = (10, 20, 30, 40)

    with patch("dlib.rectangle", return_value="dlib_rectangle") as mock_rectangle:
        result = tuple_to_rect(bbox)

    assert result == "dlib_rectangle"
    mock_rectangle.assert_called_once_with(10, 20, 40, 60)

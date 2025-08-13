# -*- coding: utf-8 -*-
import cv2
import numpy as np
import pytest
from PIL import Image

from common_image_tools.visualization import draw_contour, draw_points_shape


def test_draw_points_shape():
    # Create a blank image
    img = np.zeros((100, 100, 3), dtype=np.uint8)

    # Define points for a triangle
    points = [(10, 10), (90, 10), (50, 90)]

    # Draw the shape
    result = draw_points_shape(img, points, color=(0, 255, 0))

    # Check if the lines are drawn (non-zero pixels)
    assert np.sum(result) > 0

    # Check if the color is correct (green)
    assert np.any(result[:, :, 1] > 0)
    assert np.all(result[:, :, 0] == 0)
    assert np.all(result[:, :, 2] == 0)

    # Optionally, save the image for visual inspection
    cv2.imwrite("draw_points_shape_result.png", result)


def test_draw_contour():
    # Create a blank image
    img = np.zeros((100, 100), dtype=np.uint8)

    # Define points for a square
    points = [(20, 20), (80, 20), (80, 80), (20, 80)]

    # Test unfilled contour
    result_unfilled = draw_contour(img.copy(), points, fill=False)
    assert np.sum(result_unfilled) > 0
    # Check that some pixels are still black (not all are white)
    assert np.sum(result_unfilled == 0) > 0
    cv2.imwrite("draw_contour_unfilled.png", result_unfilled)

    # Test filled contour
    result_filled = draw_contour(img.copy(), points, fill=True)
    assert np.sum(result_filled) > np.sum(result_unfilled)
    # Check that all pixels inside the square are white
    assert np.all(result_filled[30:70, 30:70] == 255)
    cv2.imwrite("draw_contour_filled.png", result_filled)

    # Visual check
    print(f"Unfilled contour sum: {np.sum(result_unfilled)}")
    print(f"Filled contour sum: {np.sum(result_filled)}")


# Add more tests for other functions as needed


def visualize_draw_functions():
    # Create a larger blank image for better visualization
    img = np.zeros((200, 200, 3), dtype=np.uint8)

    # Test draw_points_shape
    points_shape = [(50, 50), (150, 50), (100, 150)]
    img_points = draw_points_shape(img.copy(), points_shape, color=(0, 255, 0))
    cv2.imwrite("visualize_draw_points_shape.png", img_points)

    # Test draw_contour (unfilled)
    img_contour_unfilled = draw_contour(img[:, :, 0].copy(), points_shape, fill=False)
    cv2.imwrite("visualize_draw_contour_unfilled.png", img_contour_unfilled)

    # Test draw_contour (filled)
    img_contour_filled = draw_contour(img[:, :, 0].copy(), points_shape, fill=True)
    cv2.imwrite("visualize_draw_contour_filled.png", img_contour_filled)


# Run the visualization function
# visualize_draw_functions()

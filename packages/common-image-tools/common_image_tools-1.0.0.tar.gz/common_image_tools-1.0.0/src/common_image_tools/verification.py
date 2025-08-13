# -*- coding: utf-8 -*-
from __future__ import annotations

import cv2
import numpy as np


def is_inside(point: tuple, shape: list) -> bool:
    """
    Checks if a given point lies inside or on the boundary of a shape.

    This function uses the OpenCV function cv2.pointPolygonTest to determine whether the point is inside the shape,
    on the boundary, or outside the shape.

    Parameters:
        point (tuple): A tuple representing the (x, y) coordinates of the point.
        shape (list): A list of tuples representing the vertices of the shape in the format [(x1, y1), (x2, y2), ...].

    Returns:
        bool: True if the point is inside or on the boundary of the shape, False otherwise.

    Note:
        The pointPolygonTest function returns +1 if the point is inside the contour, -1 if it is outside, and 0 if
        it is on the contour.

    Example:
        >>> is_inside((50, 50), [(0, 0), (100, 0), (100, 100), (0, 100)])
        Returns True if the point (50, 50) is inside the square [(0, 0), (100, 0), (100, 100), (0, 100)].
    """
    ctn = np.array(shape)
    ctn = ctn.reshape((-1, 1, 2))

    # When measureDist=false , the return value is +1, -1, and 0, respectively. Otherwise, the return value is a
    # signed distance between the point and the nearest contour edge.
    result = cv2.pointPolygonTest(ctn, point, measureDist=False)

    return result >= 0


def yolobbox_2_bbox(bbox):
    x, y, w, h = bbox
    x1, y1 = x - w / 2, y - h / 2
    x2, y2 = x + w / 2, y + h / 2
    return x1, y1, x2, y2


def calculate_bbox_mask_overlap_cv2(bbox, mask_points, img_height=None, img_width=None):
    """
    Calculate the percentage of a bounding box that overlaps with a mask defined by points,
    using contour area for calculations.

    :param bbox: A tuple of (x1, y1, x2, y2) representing the bounding box
    :param mask_points: A list of (x, y) tuples representing the mask polygon
    :param img_height: The height of the image
    :param img_width: The width of the image
    :return: The overlap percentage
    """
    # Extract bounding box coordinates
    x1, y1, x2, y2 = yolobbox_2_bbox(bbox=bbox)
    x1 = int(x1 * img_width)
    y1 = int(y1 * img_height)
    x2 = int(x2 * img_width)
    y2 = int(y2 * img_height)

    # Create a blank image for mask and overlap calculation
    mask = np.zeros((img_height, img_width), dtype=np.uint8)
    bbox_mask = np.zeros((img_height, img_width), dtype=np.uint8)

    # Draw the mask polygon and bounding box on separate masks
    mask_points_array = np.array(mask_points, dtype=np.int32)
    cv2.fillPoly(mask, [mask_points_array], 255)
    cv2.rectangle(bbox_mask, (x1, y1), (x2, y2), 255, -1)

    # Calculate the overlap
    overlap = cv2.bitwise_and(mask, bbox_mask)

    # Find contours for mask and overlap
    mask_contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    overlap_contours, _ = cv2.findContours(overlap, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Calculate areas using contour area
    mask_area = sum(cv2.contourArea(contour) for contour in mask_contours)
    overlap_area = sum(cv2.contourArea(contour) for contour in overlap_contours)
    bbox_area = (x2 - x1) * (y2 - y1)

    # Calculate the percentage
    overlap_percentage = (overlap_area / bbox_area) * 100

    return overlap_percentage

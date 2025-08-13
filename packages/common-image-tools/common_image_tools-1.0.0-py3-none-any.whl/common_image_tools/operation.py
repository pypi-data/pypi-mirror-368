# -*- coding: utf-8 -*-
from __future__ import annotations

from math import ceil
from typing import Union

import cv2
import numpy as np


def resize_image_with_aspect_ratio(image: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    """
    Resize an image while maintaining its aspect ratio using OpenCV.

    Parameters:
        image (np.ndarray): The input image as a NumPy array.
        size (tuple): A tuple (width, height) specifying the new size.

    Returns:
        np.ndarray: The resized image as a NumPy array.
    """
    height, width = size

    # Calculate the aspect ratio
    aspect_ratio = width / float(height)

    # Calculate new dimensions while preserving the aspect ratio
    if image.shape[1] / image.shape[0] > aspect_ratio:
        new_width = width
        new_height = int(width / image.shape[1] * image.shape[0])

    else:
        new_height = height
        new_width = int(height / image.shape[0] * image.shape[1])

    # Resize the image using the calculated dimensions
    resized_image = cv2.resize(image, (new_width, new_height))

    # Save the resized image
    return resized_image


def is_point_in_bbox(point: tuple[int, int], bbox: tuple[int, int, int, int]) -> bool:
    x1, y1, w, h = bbox
    x2, y2 = x1 + w, y1 + h
    x, y = point
    if x1 < x < x2 and y1 < y < y2:
        return True
    return False


def is_point_in_shape(point, shape_contour) -> bool:
    ctn = np.array(shape_contour)
    ctn = ctn.reshape((-1, 1, 2))

    # When measureDist=false , the return value is +1, -1, and 0, respectively. Otherwise, the return value is a
    # signed distance between the point and the nearest contour edge.
    result = cv2.pointPolygonTest(ctn, point, measureDist=False)

    return result >= 0


def scale_bboxes(bboxes: list[tuple], scale_factor: float) -> list[tuple]:
    f_bboxes = []
    for box in bboxes:
        x, y, w, h = box
        f_bboxes.append(
            (
                ceil(x * scale_factor),
                ceil(y * scale_factor),
                ceil(w * scale_factor),
                ceil(h * scale_factor),
            )
        )

    return f_bboxes


def bbox_centroid(bbox: tuple[int, int, int, int]) -> tuple[int, int]:
    """Calculate the centroid coordinates of a bounding box.

    Parameters:
        bbox (tuple): A tuple representing the bounding box in the format (x, y, width, height).

    Returns:
        tuple: A tuple containing the coordinates of the centroid as integers (center_x, center_y).
    """
    x, y, w, h = bbox
    center_x = x + (w / 2)
    center_y = y + (h / 2)
    return int(center_x), int(center_y)


def scaled_bbox_centroid(
    image: np.ndarray, bbox: tuple[float, float, float, float]
) -> tuple[int, int]:
    """Calculate the centroid coordinates of a bounding box and scale them to the image size.

    Parameters:
        image (numpy.ndarray): The image to get the shape of. (To scale the bounding box)
        bbox (tuple): A tuple representing the bounding box in the format (x, y, width, height).

    Returns:
        tuple: A tuple containing the coordinates of the centroid as integers (center_x, center_y).
    """
    x, y, w, h = bbox

    x_scaled = int(round(x * image.shape[1]))
    y_scaled = int(round(y * image.shape[0]))
    w_scaled = int(round(w * image.shape[1]))
    h_scaled = int(round(h * image.shape[0]))

    center_x = x_scaled + (w_scaled / 2)
    center_y = y_scaled + (h_scaled / 2)
    return int(center_x), int(center_y)


def scale_bbox_xywh_to_frame_size(
    bbox: list[Union[int, float]],
    source_size: tuple[Union[int, float], Union[int, float]],
    dest_size: tuple[Union[int, float], Union[int, float]],
) -> list[float]:
    """
    Scale a bounding box from source frame coordinates to destination frame coordinates.

    This function takes a bounding box defined in [x, y, width, height] format and scales
    it proportionally from a source frame size to a destination frame size. The scaling
    is applied independently to x/width (horizontal) and y/height (vertical) dimensions.

    Args:
        bbox: Bounding box in [x, y, width, height] format where:
            - x: Left coordinate of the bounding box
            - y: Top coordinate of the bounding box
            - width: Width of the bounding box
            - height: Height of the bounding box
        source_size: Tuple of (width, height) representing the source frame dimensions
        dest_size: Tuple of (width, height) representing the destination frame dimensions

    Returns:
        List[float]: Scaled bounding box in [x, y, width, height] format with coordinates
                    adjusted for the destination frame size

    Raises:
        ValueError: If bbox doesn't have exactly 4 elements
        ValueError: If source_size or dest_size don't have exactly 2 elements
        ZeroDivisionError: If source frame dimensions are zero

    Examples:
        >>> # Scale bbox from 320x240 to 640x480 (2x scaling)
        >>> bbox = [10, 20, 50, 80]
        >>> source = (320, 240)
        >>> dest = (640, 480)
        >>> scale_bbox_xywh_to_frame_size(bbox, source, dest)
        [20.0, 40.0, 100.0, 160.0]

        >>> # Scale bbox from 1920x1080 to 640x360 (downscaling)
        >>> bbox = [100, 200, 300, 400]
        >>> source = (1920, 1080)
        >>> dest = (640, 360)
        >>> scale_bbox_xywh_to_frame_size(bbox, source, dest)
        [33.333333333333336, 66.66666666666667, 100.0, 133.33333333333334]
    """
    # Input validation
    if len(bbox) != 4:
        raise ValueError(f"bbox must have exactly 4 elements, got {len(bbox)}")

    if len(source_size) != 2:
        raise ValueError(f"source_size must have exactly 2 elements, got {len(source_size)}")

    if len(dest_size) != 2:
        raise ValueError(f"dest_size must have exactly 2 elements, got {len(dest_size)}")

    x, y, w, h = bbox
    src_w, src_h = source_size
    dest_w, dest_h = dest_size

    # Check for zero division
    if src_w == 0:
        raise ZeroDivisionError("Source width cannot be zero")
    if src_h == 0:
        raise ZeroDivisionError("Source height cannot be zero")

    # Calculate scaling factors
    scale_x = dest_w / src_w
    scale_y = dest_h / src_h

    # Apply scaling
    new_x = x * scale_x
    new_y = y * scale_y
    new_w = w * scale_x
    new_h = h * scale_y

    return [new_x, new_y, new_w, new_h]

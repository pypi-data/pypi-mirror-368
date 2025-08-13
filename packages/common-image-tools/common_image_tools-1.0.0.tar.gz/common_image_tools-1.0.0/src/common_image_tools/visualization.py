# -*- coding: utf-8 -*-
from __future__ import annotations

import cv2
import numpy as np


def draw_points_shape(img, roi_points, color):
    for v in range(1, len(roi_points)):
        cv2.line(img, roi_points[v], roi_points[v - 1], color, 2)

    cv2.line(img, roi_points[0], roi_points[-1], color, 2)

    return img


def draw_contour(image: np.ndarray, points, fill: bool):
    points = np.array(points, dtype=np.int32)
    points = points.reshape((-1, 1, 2))

    if fill:
        cv2.fillPoly(image, [points], color=(255, 255, 255))
    else:
        cv2.polylines(image, [points], isClosed=True, color=(255, 255, 255), thickness=3)

    return image


def draw_point_or_contour_point(
    image: np.ndarray,
    points: list[tuple[float | int, float | int]],
    fill: bool = False,
    draw_points: bool = False,
    color: tuple[int, int, int] = (255, 255, 255),
) -> np.ndarray:
    # Convert float coordinates to integers
    points = [(int(x), int(y)) for x, y in points]
    points = np.array(points)

    overlay = image.copy()

    # Draw individual points if draw_points is True
    if draw_points:
        for point in points:
            x, y = point
            cv2.circle(image, (x, y), radius=3, color=color, thickness=-1)

    if len(points) >= 3:
        if fill:
            cv2.fillPoly(image, [points], color=color)
        else:
            # Create fully opaque fill
            cv2.fillPoly(overlay, [points], color=color)  # White fill
            # Blend the overlay with original image for semi-transparent fill
            image = cv2.addWeighted(overlay, 0.3, image, 0.7, 0)
            # Add solid white contour on top
            cv2.polylines(
                image, [points], isClosed=True, color=color, thickness=2, lineType=cv2.LINE_AA
            )
    else:
        # For lines with less than 4 points - solid line
        cv2.polylines(
            image, [points], isClosed=False, color=color, thickness=2, lineType=cv2.LINE_AA
        )

    return image

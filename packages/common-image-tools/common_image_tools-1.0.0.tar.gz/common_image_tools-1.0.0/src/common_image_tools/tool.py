# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Tuple

import cv2
import numpy as np
from PIL import Image


def opencv_built_with_gstreamer() -> bool:
    """Check if OpenCV has been built with GStreamer support.

    Returns:
        bool: True if OpenCV has been built with GStreamer support, False otherwise.
    """
    # Get build information
    build_info = cv2.getBuildInformation()
    # Get the row with GStreamer information
    gstreamer_info = [x for x in build_info.split("\n") if "GStreamer" in x]
    # Check if "YES" is in the row
    return "YES" in gstreamer_info[0]


def movement_detection(
    image1: np.ndarray,
    image2: np.ndarray,
    area_threshold: int = 400,
    blur_size: int = 5,
    threshold_sensitivity: int = 25,
) -> bool:
    """Detect if a difference is present between two images.

    Args:
        image1 (np.ndarray): Image in opencv format (BGR)
        image2 (np.ndarray): Image in opencv format (BGR)
        area_threshold (int, optional): Area threshold. Defaults to 400.
        blur_size (int, optional): Blur size. Defaults to 5.
        threshold_sensitivity (int, optional): Threshold of a pixel to be considered different. Defaults to 25.

    Returns:
        bool: True if there is movement, False otherwise
    """

    delta_frame = cv2.absdiff(image1, image2)

    gray = cv2.cvtColor(delta_frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (blur_size, blur_size), 0)
    _, th = cv2.threshold(blur, threshold_sensitivity, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(th, np.ones((3, 3), np.uint8), iterations=3)

    c, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    difference = np.sum([cv2.contourArea(contour) for contour in c])

    # === DEBUG ===
    # try:
    #     cv2.imshow("Frame1", image1)
    #     cv2.imshow("Frame2", image2)
    #     cv2.imshow("Blur", blur)
    #     if difference > area_threshold:
    #         font = cv2.FONT_HERSHEY_SIMPLEX
    #         cv2.putText(dilated, 'Movimento Rilevato', (10, 50), font, 1, (255, 0, 0), 2, cv2.LINE_AA)
    #     else:
    #         pass
    #     cv2.imshow("Differenza", dilated)
    #     cv2.imshow("C", c)
    # except:
    #     pass
    # === END DEBUG===

    return difference > area_threshold


def merge_color(image: np.ndarray, mask: np.ndarray, target_color_rgb: tuple) -> np.ndarray:
    """Merge the target color with the image using the mask using hsv color space.

    Args:
        image (np.ndarray): Image in opencv format (BGR)
        mask (np.ndarray): Mask in opencv format one channel
        target_color_rgb (tuple): Target color in RGB format

    Returns:
        np.ndarray: Image with merged color in opencv format (BGR)

    """
    hsv_image = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2HSV)

    h, s, v = cv2.split(hsv_image)

    color_to_merge = np.uint8([[target_color_rgb[::-1]]])
    hsv_color = cv2.cvtColor(color_to_merge, cv2.COLOR_BGR2HSV)

    h.fill(hsv_color[0][0][0])
    s.fill(hsv_color[0][0][1])

    new_hsv_image = cv2.merge([h, s, v])

    new_hsv_image = cv2.cvtColor(new_hsv_image, cv2.COLOR_HSV2BGR)

    colored_image = cv2.bitwise_and(new_hsv_image, new_hsv_image, mask=mask)
    original_image = cv2.bitwise_and(image, image, mask=cv2.bitwise_not(mask))
    final_img = cv2.bitwise_xor(colored_image, original_image)

    return final_img


def merge_texture(image, mask, texture, alpha=0.3):
    """Merge the texture with the image using the mask using hsv color space."""

    # if texture is smaller than image, resize it
    # if texture.shape[0] < image.shape[0] or texture.shape[1] < image.shape[1]:
    pattern = cv2.resize(texture, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_AREA)
    # pattern = pil_image_to_cv2(resize_image(cv2_image_to_pil(texture), image.shape[1]))
    # pattern = texture[0:image.shape[0], 0:image.shape[1]]

    # crop texture to image size

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv_image)

    hsv_pattern = cv2.cvtColor(pattern, cv2.COLOR_BGR2HSV)
    hp, sp, vp = cv2.split(hsv_pattern)

    # new_h = cv2.add(hp, h)
    # new_s = cv2.add(sp, s)
    # new_v = cv2.add(vp, vp)

    beta = 1.0 - alpha
    new_v = cv2.addWeighted(v, alpha, vp, beta, 0)

    new_hsv_image = cv2.merge([hp, sp, new_v])
    # new_hsv_image = cv2.merge([new_h, new_s, v])

    new_hsv_image = cv2.cvtColor(new_hsv_image, cv2.COLOR_HSV2BGR)

    colored_image = cv2.bitwise_and(new_hsv_image, new_hsv_image, mask=mask)
    original_image = cv2.bitwise_and(image, image, mask=cv2.bitwise_not(mask))
    final_img = cv2.bitwise_xor(colored_image, original_image)

    return final_img


def create_pil_image(size: Tuple[int, int], color: Tuple[int, int, int]) -> Image:
    """Create a PIL image with the specified color and size.

    Args:
        size (tuple): Size of the image
        color (tuple): Color of the image in RGB format

    Returns:
        PIL.Image: Image in PIL format (RGB)
    """
    from PIL import Image

    return Image.new("RGB", size, color)


def create_cv2_image(size: Tuple[int, int], color: Tuple[int, int, int]) -> np.ndarray:
    """
    Creates a NumPy array representing an image using OpenCV conventions.

    Parameters:
        size (tuple[int, int]): A tuple specifying the dimensions of the image in the format (height, width).
        color (tuple[int, int, int]): A tuple representing the color of the image in BGR (Blue, Green, Red) format.

    Returns:
        np.ndarray: An image represented as a NumPy array with dimensions (height, width, 3).
                    Each pixel in the image will have the specified color.

    Example:
        >>> create_cv2_image((100, 200), (0, 255, 0))
        Returns a 100x200 green image.
    """
    img = np.zeros((size[0], size[1], 3), np.uint8)
    img[:] = color
    return img


def blur_area(img: np.ndarray, bbox: tuple[int, int, int, int], factor: float = 3.0) -> np.ndarray:
    # crop image within the bbox
    image = img[bbox[1] : bbox[3], bbox[0] : bbox[2]]

    # automatically determine the size of the blurring kernel based
    # on the spatial dimensions of the input image
    (h, w) = image.shape[:2]
    k_w = int(w / factor)
    k_h = int(h / factor)
    # ensure the width of the kernel is odd
    if k_w % 2 == 0:
        k_w -= 1
    # ensure the height of the kernel is odd
    if k_h % 2 == 0:
        k_h -= 1
    # apply a Gaussian blur to the input image using our computed
    # kernel size
    blurred_image = cv2.GaussianBlur(image, (k_w, k_h), 0)

    # Apply the blurred img to the original
    img[bbox[1] : bbox[3], bbox[0] : bbox[2]] = blurred_image

    return img


def blur_area_pixel(
    img: np.ndarray, bbox: tuple[int, int, int, int], blocks: int = 20, padding: int = 0
) -> np.ndarray:
    (original_h, original_w) = img.shape[:2]

    # Extract (x, y, w, h) from bbox
    x, y, w, h = bbox

    # Calculate the padded bounding box
    padded_bbox = (
        max(0, x - padding),  # x1
        max(0, y - padding),  # y1
        min(original_w, x + w + padding),  # x2
        min(original_h, y + h + padding),  # y2
    )

    # Crop image within the padded bounding box
    image = img[padded_bbox[1] : padded_bbox[3], padded_bbox[0] : padded_bbox[2]]

    # Divide the input image into NxN blocks
    (h, w) = image.shape[:2]
    x_steps = np.linspace(0, w, blocks + 1, dtype="int")
    y_steps = np.linspace(0, h, blocks + 1, dtype="int")

    # Loop over the blocks in both the x and y direction
    for i in range(1, len(y_steps)):
        for j in range(1, len(x_steps)):
            # Compute the starting and ending (x, y)-coordinates for the current block
            start_x = x_steps[j - 1]
            start_y = y_steps[i - 1]
            end_x = x_steps[j]
            end_y = y_steps[i]
            # Extract the ROI using NumPy array slicing, compute the mean of the ROI
            roi = image[start_y:end_y, start_x:end_x]
            (B, G, R) = [int(x) for x in cv2.mean(roi)[:3]]
            # Draw a rectangle with the mean RGB values over the ROI in the original image
            cv2.rectangle(image, (start_x, start_y), (end_x, end_y), (B, G, R), -1)

    # Place the blurred area back into the original image
    img[padded_bbox[1] : padded_bbox[3], padded_bbox[0] : padded_bbox[2]] = image
    return img

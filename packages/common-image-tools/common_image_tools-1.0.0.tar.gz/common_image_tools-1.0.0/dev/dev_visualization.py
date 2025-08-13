# -*- coding: utf-8 -*-
import cv2
import numpy as np

from common_image_tools.visualization import draw_point_or_contour_point


def main():
    # Create a blank black image
    width, height = 800, 600
    image = np.zeros((height, width, 3), dtype=np.uint8)

    # Example 1: Draw a triangle
    triangle_points = [(100.10, 100.10), (300.10, 100.10), (200.10, 300.10)]
    image = draw_point_or_contour_point(image, triangle_points, fill=True, draw_points=True)

    # Example 2: Draw a rectangle with semi-transparent fill
    rectangle_points = [(400, 200), (600, 200), (600, 400), (400, 400)]
    image = draw_point_or_contour_point(image, rectangle_points, fill=False, draw_points=True)

    # Example 3: Draw a line (less than 3 points)
    line_points = [(100, 500), (700, 500)]
    image = draw_point_or_contour_point(image, line_points, draw_points=True)

    # Display the image
    cv2.imshow("Drawing Examples", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
import cv2
import numpy as np

from common_image_tools import tool


def main():
    img = cv2.imread("imgs/test_car.jpg")
    black = cv2.imread("imgs/black.jpg")
    # white = cv2.imread("imgs/white.jpg")

    # Create one channel mask with the same size of the image
    mask = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)

    # Draw a rectangle on the mask
    cv2.rectangle(mask, (100, 700), (1000, 1500), (255, 255, 255), -1)
    # cv2.rectangle(mask, (100, 700), (1000, 1500), (255, 255, 255), -1)

    colored_overlay = tool.create_cv2_image((img.shape[1], img.shape[0]), (255, 0, 0))

    img = tool.merge_color(img, mask, (255, 0, 0))
    # img = tool.merge_texture(img, mask, colored_overlay, alpha=0.5)

    cv2.imshow("img", img)
    cv2.waitKey(0)


if __name__ == "__main__":
    main()

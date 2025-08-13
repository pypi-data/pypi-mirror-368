# -*- coding: utf-8 -*-
import cv2

from common_image_tools.operation import resize_image_with_aspect_ratio
from common_image_tools.tool import blur_area, blur_area_pixel


# def main():
#     cap = cv2.VideoCapture(0)
#     previous_frame = None
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break
#
#         if previous_frame is not None:
#             movement_bbox = movement_detection_bbox(previous_frame, frame)
#         else:
#             movement_bbox = []
#
#         previous_frame = frame.copy()
#         if movement_bbox is not None:
#             frame = cv2.putText(
#                 frame, "Movement detected", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA
#             )
#             for bbox in movement_bbox:
#                 x, y, w, h = bbox
#                 frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
#
#         cv2.imshow("frame", frame)
#
#         if cv2.waitKey(3) & 0xFF == ord("q"):
#             break


def dev_blur_area():
    img = cv2.imread("imgs/WIN_20241223_12_11_37_Pro.jpg")

    img = resize_image_with_aspect_ratio(img, (600, 600))

    # bbox: x, y, w, h
    img = blur_area_pixel(img, (500, 200, 100, 300), padding=40)
    cv2.imshow("img", img)
    cv2.waitKey(0)


if __name__ == "__main__":
    dev_blur_area()

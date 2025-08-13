# -*- coding: utf-8 -*-
import cv2

from common_image_tools import OpencvBackendMode, VideoSource

# To test this is useful to use the docker-compose in magic-stream.


def main():
    raw_source = "rtsp://admin:admin@192.168.1.116:554/live/ch1?token=95db6a228c1a9bdf245e0189c2c3f57b"
    source = VideoSource(
        raw_source,
        target_frame_height=480,
        target_frame_width=640,
        opencv_backend=OpencvBackendMode.OPENCV_GSTREAMER,
    )

    print(source.parsed_source)

    cap = cv2.VideoCapture(source.parsed_source)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Frame", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


if __name__ == "__main__":
    main()

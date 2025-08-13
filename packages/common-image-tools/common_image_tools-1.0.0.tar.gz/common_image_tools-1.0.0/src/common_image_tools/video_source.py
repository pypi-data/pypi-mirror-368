# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from enum import Enum

from loguru import logger

from common_image_tools.tool import opencv_built_with_gstreamer


def is_jetson_device() -> bool:
    """
    Check if the current device is a Jetson by looking for the device-tree model file
    and checking its content for "Jetson" string.

    Returns:
        bool: True if running on a Jetson device, False otherwise
    """
    model_path = "/proc/device-tree/model"

    try:
        if os.path.exists(model_path):
            with open(model_path, "r") as f:
                model_info = f.read().lower()
                return "jetson" in model_info
    except Exception as e:
        logger.debug(f"Error checking for Jetson device: {e}")

    return False


class OpencvBackendMode(Enum):
    """Enum class to define the OpenCV backend mode for the video source"""

    # Use gstreamer backend if available, otherwise use the default OpenCV backend
    AUTO = 0

    # The default OpenCV backend is used
    OPENCV_DEFAULT = 1

    # Only for Jetson devices, the gstreamer pipeline uses a plugin for hardware acceleration
    OPENCV_GSTREAMER_JETSON = 2

    # Use the gstreamer backend
    OPENCV_GSTREAMER = 3


class VideoSource:
    def __init__(
        self,
        source,
        target_frame_height: int = None,
        target_frame_width: int = None,
        target_fps: int | None = None,
        opencv_backend: OpencvBackendMode = OpencvBackendMode.AUTO,
    ):
        """
        The VideoSource class is used to parse the video source and set the target shape of the video frames.

        Args:
            source: The video source, it can be a rtsp link, a video file or a webcam number
            target_frame_height: The target height of the video frames
            target_frame_width: The target width of the video frames
            opencv_backend: The OpenCV backend mode to use, by default it is set to AUTO

        Raises:
            ValueError: If the source format is not supported
        """
        self.unparsed_source = source
        self._validate_source(source)  # Add source validation during initialization
        self.target_shape: tuple[int, int] | None = (target_frame_height, target_frame_width)
        self.target_fps = target_fps

        if opencv_backend == OpencvBackendMode.AUTO:
            if opencv_built_with_gstreamer():
                # If we're on a Jetson device, use the Jetson-specific backend
                if is_jetson_device():
                    self.opencv_backend = OpencvBackendMode.OPENCV_GSTREAMER_JETSON
                    logger.debug("Detected Jetson device, using OPENCV_GSTREAMER_JETSON backend")
                else:
                    self.opencv_backend = OpencvBackendMode.OPENCV_GSTREAMER
                    logger.debug("Using standard OPENCV_GSTREAMER backend")
            else:
                self.opencv_backend = OpencvBackendMode.OPENCV_DEFAULT
                logger.debug("GStreamer not available, using OPENCV_DEFAULT backend")
        else:
            self.opencv_backend = opencv_backend

        logger.debug(f"Using {self.opencv_backend} OpenCV backend")

    def _validate_source(self, source) -> None:
        """
        Validate if the source format is supported.

        Args:
            source: The video source to validate

        Raises:
            ValueError: If the source format is not supported
        """
        source_str = str(source)
        valid_source = (
            "rtsp" in source_str or ".mp4" in source_str or "/dev/video" in source_str or source_str.isdigit()
        )
        if not valid_source:
            raise ValueError(f"The video source {source} is not supported")

    def _create_gstreamer_pipeline(self, use_jetson: bool = False) -> str:
        """
        Create a GStreamer pipeline string based on the source type and device capabilities.

        Args:
            use_jetson: Whether to use Jetson-specific GStreamer elements

        Returns:
            str: The complete GStreamer pipeline string
        """
        if "rtsp" in str(self.unparsed_source):
            if use_jetson:
                pipeline = f"uridecodebin uri={self.unparsed_source} ! nvvidconv ! "
            else:
                pipeline = f"uridecodebin uri={self.unparsed_source} ! videoconvert ! videoscale ! "

        elif ".mp4" in str(self.unparsed_source):
            if use_jetson:
                pipeline = f"filesrc location={self.unparsed_source} ! decodebin ! nvvidconv ! "
            else:
                pipeline = f"filesrc location={self.unparsed_source} ! decodebin ! videoconvert ! videoscale ! "

        elif "/dev/video" in str(self.unparsed_source):
            if not all(self.target_shape):
                raise ValueError("The target shape must be set for the webcam video source")
            if not self.target_fps:
                raise ValueError("The target fps must be set for the webcam video source")

            if use_jetson:
                return (
                    f"v4l2src device={self.unparsed_source} ! "
                    f"image/jpeg,format=MJPG,width={self.target_shape[1]},height={self.target_shape[0]},"
                    f"framerate={self.target_fps}/1 ! nvv4l2decoder mjpeg=1 ! nvvidconv ! "
                    f"video/x-raw,format=BGRx ! appsink drop=1"
                )
            else:
                return (
                    f"v4l2src device={self.unparsed_source} ! "
                    f"image/jpeg,format=MJPG,width={self.target_shape[1]},height={self.target_shape[0]},"
                    f"framerate={self.target_fps}/1 ! jpegdec ! videoconvert ! "
                    f"video/x-raw,format=BGR ! appsink drop=1"
                )

        elif str(self.unparsed_source).isdigit():
            logger.warning("The webcam video source is experimental")
            raise NotImplementedError(f"Integer video source {self.unparsed_source} not yet supported")

        else:
            raise ValueError(f"The video source {self.unparsed_source} is not supported")

        # Add format-specific elements
        if use_jetson:
            pipeline += "video/x-raw(memory:NVMM) ! nvvidconv ! video/x-raw,format=BGRx ! "
        else:
            pipeline += "video/x-raw,format=BGR ! "

        # Add framerate control if specified
        if self.target_fps is not None:
            pipeline += f"videorate ! video/x-raw,framerate={self.target_fps}/1 ! "

        # Add format conversion
        if use_jetson:
            pipeline += "videoconvert ! video/x-raw,format=BGR"
        else:
            pipeline += "videoconvert ! video/x-raw,format=BGR"

        # Add resolution scaling if target shape is specified
        if all(self.target_shape):
            pipeline += f",width={self.target_shape[1]},height={self.target_shape[0]}"

        # Final sink
        pipeline += " ! appsink drop=1"

        return pipeline

    @property
    def parsed_source(self):
        """
        Parse the video source and return the appropriate source string or value based on the backend mode and parameters.

        Returns:
            The parsed video source according to the configured backend mode and parameters.
        """
        if self.opencv_backend in [
            OpencvBackendMode.OPENCV_GSTREAMER,
            OpencvBackendMode.OPENCV_GSTREAMER_JETSON,
        ]:
            use_jetson = self.opencv_backend == OpencvBackendMode.OPENCV_GSTREAMER_JETSON
            return self._create_gstreamer_pipeline(use_jetson=use_jetson)

        elif self.opencv_backend == OpencvBackendMode.OPENCV_DEFAULT:
            if str(self.unparsed_source).isdigit():
                return int(self.unparsed_source)
            return self.unparsed_source

    def __eq__(self, other):
        return (
            self.unparsed_source == other.unparsed_source
            and self.target_shape == other.target_shape
            and self.target_fps == other.target_fps
        )

    def __ne__(self, other):
        return (
            self.unparsed_source != other.unparsed_source
            or self.target_shape != other.target_shape
            or self.target_fps != other.target_fps
        )

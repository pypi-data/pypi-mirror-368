# -*- coding: utf-8 -*-
# type: ignore
from unittest.mock import mock_open, patch

import pytest
from loguru import logger

from common_image_tools.video_source import OpencvBackendMode, VideoSource, is_jetson_device


@pytest.fixture
def rtsp_source():
    return "rtsp://example.com/stream"


@pytest.fixture
def video_file_source():
    return "test_video.mp4"


@pytest.fixture
def webcam_source():
    return "/dev/video0"


def test_video_source_init_default():
    source = VideoSource("test_video.mp4")
    assert source.unparsed_source == "test_video.mp4"
    assert source.target_shape == (None, None)
    assert source.target_fps is None


def test_video_source_init_with_params():
    source = VideoSource(
        "test_video.mp4",
        target_frame_height=720,
        target_frame_width=1280,
        target_fps=30,
        opencv_backend=OpencvBackendMode.OPENCV_DEFAULT,
    )
    assert source.unparsed_source == "test_video.mp4"
    assert source.target_shape == (720, 1280)
    assert source.target_fps == 30
    assert source.opencv_backend == OpencvBackendMode.OPENCV_DEFAULT


def test_video_source_equality():
    source1 = VideoSource("test_video.mp4", target_frame_height=720, target_frame_width=1280)
    source2 = VideoSource("test_video.mp4", target_frame_height=720, target_frame_width=1280)
    source3 = VideoSource("test_video.mp4", target_frame_height=1080, target_frame_width=1920)

    assert source1 == source2
    assert source1 != source3


def test_gstreamer_pipeline_rtsp(rtsp_source):
    source = VideoSource(
        rtsp_source,
        target_frame_height=720,
        target_frame_width=1280,
        target_fps=30,
        opencv_backend=OpencvBackendMode.OPENCV_GSTREAMER,
    )
    pipeline = source.parsed_source
    assert "uridecodebin" in pipeline
    assert "videoconvert" in pipeline
    assert "width=1280,height=720" in pipeline
    assert "framerate=30/1" in pipeline


def test_gstreamer_pipeline_video_file(video_file_source):
    source = VideoSource(
        video_file_source,
        target_frame_height=720,
        target_frame_width=1280,
        opencv_backend=OpencvBackendMode.OPENCV_GSTREAMER,
    )
    pipeline = source.parsed_source
    assert "filesrc" in pipeline
    assert "videoconvert" in pipeline
    assert "width=1280,height=720" in pipeline


def test_gstreamer_pipeline_webcam(webcam_source):
    source = VideoSource(
        webcam_source,
        target_frame_height=720,
        target_frame_width=1280,
        target_fps=30,
        opencv_backend=OpencvBackendMode.OPENCV_GSTREAMER,
    )
    pipeline = source.parsed_source
    assert "v4l2src" in pipeline
    assert "videoconvert" in pipeline
    assert "width=1280,height=720" in pipeline


def test_webcam_without_dimensions():
    with pytest.raises(ValueError, match="The target shape must be set for the webcam video source"):
        source = VideoSource("/dev/video0", opencv_backend=OpencvBackendMode.OPENCV_GSTREAMER)
        _ = source.parsed_source


def test_webcam_without_fps():
    with pytest.raises(ValueError, match="The target fps must be set for the webcam video source"):
        source = VideoSource(
            "/dev/video0",
            target_frame_height=720,
            target_frame_width=1280,
            opencv_backend=OpencvBackendMode.OPENCV_GSTREAMER,
        )
        _ = source.parsed_source


def test_unsupported_source():
    with pytest.raises(ValueError, match="The video source .* is not supported"):
        source = VideoSource("unsupported://source")
        _ = source.parsed_source


@pytest.mark.parametrize(
    "file_content,exists,expected",
    [
        ("NVIDIA Jetson Nano", True, True),
        ("NVIDIA Jetson Xavier", True, True),
        ("Some Other Device", True, False),
        ("", True, False),
    ],
)
def test_is_jetson_device(file_content, exists, expected):
    with patch("os.path.exists") as mock_exists, patch("builtins.open", mock_open(read_data=file_content)):
        mock_exists.return_value = exists
        assert is_jetson_device() == expected


def test_is_jetson_device_file_not_exists():
    with patch("os.path.exists", return_value=False):
        assert is_jetson_device() == False


def test_is_jetson_device_permission_error():
    with patch("os.path.exists", return_value=True), patch("builtins.open", side_effect=PermissionError):
        assert is_jetson_device() == False


def test_is_jetson_device_io_error():
    with patch("os.path.exists", return_value=True), patch("builtins.open", side_effect=IOError):
        assert is_jetson_device() == False


@pytest.mark.parametrize(
    "backend_mode,gstreamer_available,is_jetson,expected_backend",
    [
        (OpencvBackendMode.AUTO, True, True, OpencvBackendMode.OPENCV_GSTREAMER_JETSON),
        (OpencvBackendMode.AUTO, True, False, OpencvBackendMode.OPENCV_GSTREAMER),
        (OpencvBackendMode.AUTO, False, False, OpencvBackendMode.OPENCV_DEFAULT),
        (OpencvBackendMode.OPENCV_DEFAULT, True, True, OpencvBackendMode.OPENCV_DEFAULT),
        (OpencvBackendMode.OPENCV_GSTREAMER, True, True, OpencvBackendMode.OPENCV_GSTREAMER),
        (OpencvBackendMode.OPENCV_GSTREAMER_JETSON, True, True, OpencvBackendMode.OPENCV_GSTREAMER_JETSON),
    ],
)
def test_backend_mode_selection(backend_mode, gstreamer_available, is_jetson, expected_backend):
    with patch("common_image_tools.video_source.opencv_built_with_gstreamer", return_value=gstreamer_available), patch(
        "common_image_tools.video_source.is_jetson_device", return_value=is_jetson
    ):
        source = VideoSource("test_video.mp4", opencv_backend=backend_mode)
        assert source.opencv_backend == expected_backend


@pytest.mark.parametrize(
    "source_type,use_jetson,expected_elements",
    [
        ("rtsp://example.com/stream", True, ["uridecodebin", "nvvidconv", "video/x-raw(memory:NVMM)"]),
        ("rtsp://example.com/stream", False, ["uridecodebin", "decodebin", "videoconvert"]),
        ("test.mp4", True, ["filesrc", "nvvidconv", "video/x-raw(memory:NVMM)"]),
        ("test.mp4", False, ["filesrc", "decodebin", "videoconvert"]),
    ],
)
def test_gstreamer_pipeline_variations(source_type, use_jetson, expected_elements):
    source = VideoSource(
        source_type,
        target_frame_height=720,
        target_frame_width=1280,
        target_fps=30,
        opencv_backend=OpencvBackendMode.OPENCV_GSTREAMER_JETSON if use_jetson else OpencvBackendMode.OPENCV_GSTREAMER,
    )
    pipeline = source.parsed_source
    for element in expected_elements:
        assert element in pipeline


def test_opencv_default_backend_integer_source():
    source = VideoSource("0", opencv_backend=OpencvBackendMode.OPENCV_DEFAULT)
    assert source.parsed_source == 0


def test_opencv_default_backend_string_source():
    test_source = "test_video.mp4"
    source = VideoSource(test_source, opencv_backend=OpencvBackendMode.OPENCV_DEFAULT)
    assert source.parsed_source == test_source


@pytest.mark.parametrize(
    "source1_params,source2_params,expected_equal",
    [
        (
            {"source": "test.mp4", "target_frame_height": 720, "target_frame_width": 1280, "target_fps": 30},
            {"source": "test.mp4", "target_frame_height": 720, "target_frame_width": 1280, "target_fps": 30},
            True,
        ),
        (
            {"source": "test.mp4", "target_frame_height": 720, "target_frame_width": 1280, "target_fps": 30},
            {"source": "other.mp4", "target_frame_height": 720, "target_frame_width": 1280, "target_fps": 30},
            False,
        ),
        (
            {"source": "test.mp4", "target_frame_height": 720, "target_frame_width": 1280, "target_fps": 30},
            {"source": "test.mp4", "target_frame_height": 1080, "target_frame_width": 1280, "target_fps": 30},
            False,
        ),
        (
            {"source": "test.mp4", "target_frame_height": 720, "target_frame_width": 1280, "target_fps": 30},
            {"source": "test.mp4", "target_frame_height": 720, "target_frame_width": 1280, "target_fps": 60},
            False,
        ),
    ],
)
def test_equality_variations(source1_params, source2_params, expected_equal):
    source1 = VideoSource(**source1_params)
    source2 = VideoSource(**source2_params)
    assert (source1 == source2) == expected_equal
    assert (source1 != source2) != expected_equal


def test_enum_values():
    assert OpencvBackendMode.AUTO.value == 0
    assert OpencvBackendMode.OPENCV_DEFAULT.value == 1
    assert OpencvBackendMode.OPENCV_GSTREAMER_JETSON.value == 2
    assert OpencvBackendMode.OPENCV_GSTREAMER.value == 3


def test_gstreamer_pipeline_webcam_jetson():
    source = VideoSource(
        "/dev/video0",
        target_frame_height=720,
        target_frame_width=1280,
        target_fps=30,
        opencv_backend=OpencvBackendMode.OPENCV_GSTREAMER_JETSON,
    )
    pipeline = source.parsed_source

    # Check for Jetson-specific elements
    assert "v4l2src device=/dev/video0" in pipeline
    assert "image/jpeg,format=MJPG" in pipeline
    assert "width=1280,height=720" in pipeline
    assert "framerate=30/1" in pipeline
    assert "nvv4l2decoder mjpeg=1" in pipeline
    assert "nvvidconv" in pipeline
    assert "video/x-raw,format=BGRx" in pipeline
    assert "appsink drop=1" in pipeline

    # Verify the complete pipeline structure
    expected_pipeline = (
        "v4l2src device=/dev/video0 ! "
        "image/jpeg,format=MJPG,width=1280,height=720,framerate=30/1 ! "
        "nvv4l2decoder mjpeg=1 ! nvvidconv ! "
        "video/x-raw,format=BGRx ! appsink drop=1"
    )
    assert pipeline == expected_pipeline


@pytest.mark.parametrize(
    "invalid_source,expected_error",
    [
        ("invalid://path", "The video source invalid://path is not supported"),
        ("unknown_format.xyz", "The video source unknown_format.xyz is not supported"),
        ("", "The video source  is not supported"),
        (None, "The video source None is not supported"),
        ({"invalid": "type"}, "The video source {'invalid': 'type'} is not supported"),
    ],
)
def test_invalid_source_formats(invalid_source, expected_error):
    with pytest.raises(ValueError) as exc_info:
        source = VideoSource(invalid_source)

    assert str(exc_info.value) == expected_error

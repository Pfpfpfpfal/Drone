# pyright: reportMissingImports=false
# target_detector подключается через sys.path во время выполнения (pytest).

"""Тесты OpenCV-детектора цели и генератора команд движения."""

from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

CV_ROOT = Path(__file__).resolve().parents[2] / "cv_module"
if str(CV_ROOT) not in sys.path:
    sys.path.insert(0, str(CV_ROOT))

from target_detector import Detection, TargetDetector, command_to_motion  # noqa: E402


def _frame_with_circle(cx: int, cy: int, r: int = 40, w=640, h=480) -> np.ndarray:
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[:] = (60, 60, 60)
    cv2.circle(img, (cx, cy), r, (0, 0, 255), -1)
    return img


def test_detects_red_circle():
    frame = _frame_with_circle(320, 240)
    detector = TargetDetector()
    det = detector.detect(frame)
    assert det.found
    assert abs(det.cx - 320) < 5
    assert abs(det.cy - 240) < 5


def test_command_right_when_circle_on_right():
    frame = _frame_with_circle(448, 240)
    detector = TargetDetector()
    det = detector.detect(frame)
    assert detector.control_command(det, frame.shape[1]) == "right"


def test_command_forward_when_centered():
    frame = _frame_with_circle(320, 240)
    detector = TargetDetector()
    det = detector.detect(frame)
    assert detector.control_command(det, frame.shape[1]) == "forward"


def test_command_search_when_no_target():
    detector = TargetDetector()
    frame = np.zeros((480, 640, 3), dtype=np.uint8)  # без красного
    det = detector.detect(frame)
    assert not det.found
    assert detector.control_command(det, 640) == "search"


def test_command_to_motion():
    assert command_to_motion("forward")["vx"] > 0
    assert command_to_motion("left")["yaw_rate"] > 0
    assert command_to_motion("right")["yaw_rate"] < 0
    assert command_to_motion("search")["vx"] == 0.0
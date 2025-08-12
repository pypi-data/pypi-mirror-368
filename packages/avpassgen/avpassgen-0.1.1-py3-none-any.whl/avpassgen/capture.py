from __future__ import annotations
import time
import io
from typing import Optional, Tuple

import numpy as np

try:
    import cv2
    _HAS_CV2 = True
except Exception:
    _HAS_CV2 = False

try:
    import sounddevice as sd
    _HAS_SD = True
except Exception:
    _HAS_SD = False

from .exceptions import CaptureError


def _downscale_gray(frame: np.ndarray, size: Tuple[int, int] = (64, 64)) -> np.ndarray:
    # frame: BGR or RGB; handle both by averaging channels
    if frame.ndim == 3 and frame.shape[2] == 3:
        gray = frame.mean(axis=2)  # quick luminance approx
    else:
        gray = frame
    # simple nearest/area resize via numpy (fast path); fallback to cv2 if available
    if _HAS_CV2:
        gray_resized = cv2.resize(gray.astype(np.uint8), size, interpolation=cv2.INTER_AREA)
    else:
        # naive downscale
        h, w = gray.shape
        ys = np.linspace(0, h - 1, size[1]).astype(int)
        xs = np.linspace(0, w - 1, size[0]).astype(int)
        gray_resized = gray[np.ix_(ys, xs)].astype(np.uint8)
    return gray_resized


def capture_video_bytes(duration_s: float = 2.0, device_index: int = 0, fps: int = 15) -> bytes:
    if not _HAS_CV2:
        raise CaptureError("OpenCV no disponible para captura de video")
    cap = cv2.VideoCapture(device_index)
    if not cap.isOpened():
        raise CaptureError(f"No se pudo abrir la cámara index={device_index}")

    frames = []
    t_end = time.time() + duration_s
    last = None
    try:
        while time.time() < t_end:
            ok, frame = cap.read()
            if not ok:
                continue
            small = _downscale_gray(frame, (64, 64))
            if last is not None:
                diff = cv2.absdiff(small, last)
                frames.append(diff)
            else:
                frames.append(small)
            last = small
            time.sleep(max(0, 1.0 / fps))
    finally:
        cap.release()
    if not frames:
        raise CaptureError("No se capturaron frames")
    arr = np.stack(frames, axis=0).astype(np.uint8)
    return arr.tobytes()


def capture_audio_bytes(duration_s: float = 2.0, samplerate: int = 16000, channels: int = 1) -> bytes:
    if not _HAS_SD:
        raise CaptureError("sounddevice no disponible para captura de audio")
    try:
        rec = sd.rec(int(duration_s * samplerate), samplerate=samplerate, channels=channels, dtype="float32")
        sd.wait()
    except Exception as e:
        raise CaptureError(f"Fallo de captura de audio: {e}")
    # quantize to int16 to increase sensitivity to small variations
    ints = np.clip(rec * 32768.0, -32768, 32767).astype(np.int16)
    return ints.tobytes()


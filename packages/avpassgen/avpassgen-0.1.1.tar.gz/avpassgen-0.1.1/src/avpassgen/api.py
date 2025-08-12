from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import os

from .capture import capture_video_bytes, capture_audio_bytes
from .entropy import sha512, hkdf_mix, estimate_entropy_bits
from .password import generate_from_seed
from .exceptions import CaptureError, LowEntropyError


@dataclass
class AvPassGenConfig:
    duration_s: float = 2.0
    use_video: bool = True
    use_audio: bool = True
    video_device: int = 0
    audio_samplerate: int = 16000
    audio_channels: int = 1
    min_entropy_bits: int = 256  # heuristic lower bound
    deterministic_salt: Optional[bytes] = None  # provide to make runs reproducible per-session


def capture_entropy(cfg: AvPassGenConfig) -> bytes:
    chunks: list[bytes] = []

    if cfg.use_video:
        try:
            vb = capture_video_bytes(duration_s=cfg.duration_s, device_index=cfg.video_device)
            chunks.append(sha512(vb))
        except CaptureError:
            pass

    if cfg.use_audio:
        try:
            ab = capture_audio_bytes(duration_s=cfg.duration_s, samplerate=cfg.audio_samplerate, channels=cfg.audio_channels)
            chunks.append(sha512(ab))
        except CaptureError:
            pass

    # Always mix with OS randomness to avoid total failure
    chunks.append(os.urandom(32))

    ikm = sha512(b"".join(chunks))

    # Optional deterministic salt (e.g., for reproducible sessions/tests)
    salt = cfg.deterministic_salt if cfg.deterministic_salt is not None else None
    seed = hkdf_mix(ikm, salt=salt, info=b"avpassgen/seed", length=32)

    # Heuristic entropy check (on IKM pre-mix)
    if estimate_entropy_bits(ikm) < cfg.min_entropy_bits and cfg.deterministic_salt is None:
        # If not deterministic mode, warn by raising (caller may catch and continue)
        raise LowEntropyError("Entropía estimada por debajo del umbral; intenta mayor duración o cambia la escena/ambiente")

    return seed


def generate_passwords(
    *,
    length: int = 20,
    count: int = 1,
    charset: str = "base64url",
    cfg: Optional[AvPassGenConfig] = None,
) -> list[str]:
    cfg = cfg or AvPassGenConfig()
    seed = capture_entropy(cfg)
    return generate_from_seed(seed, length=length, charset=charset, count=count)

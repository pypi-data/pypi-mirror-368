import os
import avpassgen.api as api

def test_generate_passwords_mock(monkeypatch):
    # Simula capturas de audio/video: bytes deterministas
    def fake_video(*a, **k): return b"video-bytes-" + b"\x00"*128
    def fake_audio(*a, **k): return b"audio-bytes-" + b"\x01"*128

    from avpassgen import capture
    monkeypatch.setattr(capture, "capture_video_bytes", fake_video)
    monkeypatch.setattr(capture, "capture_audio_bytes", fake_audio)

    cfg = api.AvPassGenConfig(duration_s=0.1, use_video=True, use_audio=True,
                              deterministic_salt=b"test-salt",  # reproducible en test
                              min_entropy_bits=0)               # desactiva heurística

    pwds = api.generate_passwords(length=16, count=3, cfg=cfg)
    assert len(pwds) == 3
    assert all(len(p) == 16 for p in pwds)

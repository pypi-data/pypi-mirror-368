from __future__ import annotations
import os
import hashlib
from typing import Optional

from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes


def sha512(data: bytes) -> bytes:
    return hashlib.sha512(data).digest()


def hkdf_mix(ikm: bytes, *, salt: Optional[bytes] = None, info: bytes = b"avpassgen/seed", length: int = 32) -> bytes:
    """Mix input key material with OS CSPRNG via salt to produce a seed.
    If salt is None, uses 32 random bytes from os.urandom.
    """
    if salt is None:
        salt = os.urandom(32)
    hk = HKDF(algorithm=hashes.SHA256(), length=length, salt=salt, info=info)
    return hk.derive(ikm)


def estimate_entropy_bits(data: bytes) -> float:
    """Very rough lower-bound estimate using byte histogram (Shannon)."""
    if not data:
        return 0.0
    from math import log2
    hist = [0] * 256
    for b in data:
        hist[b] += 1
    total = len(data)
    H = 0.0
    for c in hist:
        if c:
            p = c / total
            H -= p * log2(p)
    return H * total  # bits
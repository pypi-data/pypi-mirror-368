from __future__ import annotations
import hmac
import struct
from typing import Iterable
from cryptography.hazmat.primitives import hashes, hmac as hmac_mod

# Character sets
ALNUM = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
ALNUM_SYM = ALNUM + "!@#$%^&*()-_=+[]{};:,.?/"  # adjust as needed
BASE64URL = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"  # no padding


def _expand(seed: bytes, nbytes: int, context: bytes = b"avpassgen/expand") -> bytes:
    """Deterministic expansion using HMAC-SHA256 (HKDF-like expand)."""
    out = b""
    counter = 1
    key = seed
    while len(out) < nbytes:
        hm = hmac_mod.HMAC(key, hashes.SHA256())
        hm.update(out[-32:] if out else b"")
        hm.update(context)
        hm.update(struct.pack("!I", counter))
        block = hm.finalize()
        out += block
        counter += 1
    return out[:nbytes]


def _map_bytes_to_charset(raw: bytes, charset: str, length: int) -> str:
    chars = []
    L = len(charset)
    acc = 0
    bits = 0
    for b in raw:
        acc = (acc << 8) | b
        bits += 8
        while bits >= 6 and len(chars) < length:  # 6 bits per step is OK; will mod L below
            idx = acc & 0x3F
            acc >>= 6
            bits -= 6
            chars.append(charset[idx % L])
            if len(chars) == length:
                break
        if len(chars) == length:
            break
    if len(chars) < length:
        # fallback if not enough chars
        import secrets
        for _ in range(length - len(chars)):
            chars.append(charset[secrets.randbelow(L)])
    return "".join(chars)


def generate_from_seed(seed: bytes, *, length: int = 20, charset: str = "base64url", count: int = 1) -> list[str]:
    if charset == "base64url":
        alphabet = BASE64URL
    elif charset == "alnum":
        alphabet = ALNUM
    elif charset == "alnum+sym":
        alphabet = ALNUM_SYM
    else:
        raise ValueError("charset inválido: elige base64url, alnum, alnum+sym")

    pwds = []
    for i in range(count):
        raw = _expand(seed, nbytes=length * 2, context=b"avpassgen/pw/%d" % i)
        pwds.append(_map_bytes_to_charset(raw, alphabet, length))
    return pwds
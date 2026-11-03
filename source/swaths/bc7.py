"""Minimal BC7 encoder (mode 6 only: one subset, RGBA 7+p bit endpoints, 4-bit indices), numpy vectorised.
Good enough for terrain fill layers, which the game packs into a BC7 texture array with the base game layers."""
import numpy as np

WEIGHTS = np.array([0, 4, 9, 13, 17, 21, 26, 30, 34, 38, 43, 47, 51, 55, 60, 64], dtype=np.int32)


def _blocks(rgba):
    h, w, _ = rgba.shape
    return rgba.reshape(h // 4, 4, w // 4, 4, 4).transpose(0, 2, 1, 3, 4).reshape(-1, 16, 4).astype(np.int32)


def encode(rgba):
    """rgba: HxWx4 uint8, H and W multiples of 4. Returns BC7 bytes (row-major blocks)."""
    px = _blocks(rgba)
    lo, hi = px.min(axis=1), px.max(axis=1)
    c0, c1 = lo >> 1, np.minimum((np.maximum(hi - 1, 0) + 1) >> 1, 127)  # e0 = 2*c0 <= lo, e1 = 2*c1+1 >= hi
    e0, e1 = c0 << 1, (c1 << 1) | 1
    palette = ((64 - WEIGHTS)[None, :, None] * e0[:, None, :] + WEIGHTS[None, :, None] * e1[:, None, :] + 32) >> 6
    dist = ((px[:, :, None, :] - palette[:, None, :, :]) ** 2).sum(axis=3)
    idx = dist.argmin(axis=2)
    # Anchor (pixel 0) index must have its top bit clear: swap endpoints and invert indices.
    swap = idx[:, 0] >= 8
    c0[swap], c1[swap] = c1[swap].copy(), c0[swap].copy()
    p0 = np.where(swap, 1, 0)
    p1 = np.where(swap, 0, 1)
    idx[swap] = 15 - idx[swap]
    out = bytearray()
    for b in range(px.shape[0]):
        v, pos = 1 << 6, 7  # mode 6
        for ch in range(4):
            v |= int(c0[b, ch]) << pos; pos += 7
            v |= int(c1[b, ch]) << pos; pos += 7
        v |= int(p0[b]) << pos; pos += 1
        v |= int(p1[b]) << pos; pos += 1
        v |= int(idx[b, 0]) << pos; pos += 3
        for i in range(1, 16):
            v |= int(idx[b, i]) << pos; pos += 4
        out += v.to_bytes(16, "little")
    return bytes(out)

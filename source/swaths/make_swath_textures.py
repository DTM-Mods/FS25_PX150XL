"""Grain-matched swath textures: the game's wheat swath, RGB tinted to the average colour of a grain fill texture.
Alpha (roughness) is kept. Written as BC7 with the same header and mip levels as the base game texture, because the
game packs terrain fill layers into one texture array and rejects layers that differ (format, mip count).
Usage: python -I make_swath_textures.py <outDir>"""
import os
import struct
import sys

import numpy as np
from PIL import Image, ImageStat

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bc7

DATA = "G:/SteamLibrary/steamapps/common/Farming Simulator 25/data/fillPlanes"
# name -> grain texture the map uses for that crop in a trailer (NF Marsch: RYE = barley, TRITICALE = wheat)
CROPS = {"rye": "barley", "triticale": "wheat"}
# Per-crop RGB adjustment on top of the grain match (user, 2026-11-03: rye "a little darker, a little warmer",
# then in-game mockup option 2 on top: 0.93, 0.85, 0.72).
ADJUST = {"rye": (0.97 * 0.93, 0.93 * 0.85, 0.86 * 0.72)}


def tint(image, factors):
    r, g, b, a = image.split()
    rgb = [c.point(lambda v, k=k: min(255, int(v * k + 0.5))) for c, k in zip((r, g, b), factors)]
    return Image.merge("RGBA", rgb + [a])


def save_like(image, base_path, out):
    """BC7 levels from full size down to the base file's last level, under the base file's own header."""
    header = open(base_path, "rb").read(148)
    assert header[84:88] == b"DX10" and struct.unpack_from("<I", header, 128)[0] == 98  # BC7_UNORM
    levels = struct.unpack_from("<I", header, 28)[0]
    assert image.size == (struct.unpack_from("<I", header, 16)[0], struct.unpack_from("<I", header, 12)[0])
    data, size = b"", image.size
    for _ in range(levels):
        level = image.resize(size, Image.LANCZOS) if size != image.size else image
        data += bc7.encode(np.asarray(level))
        size = (max(4, size[0] // 2), max(4, size[1] // 2))
    assert len(data) == os.path.getsize(base_path) - 148
    with open(out, "wb") as f:
        f.write(header + data)


out_dir = sys.argv[1]
swath = Image.open(f"{DATA}/wheatCut_diffuse.dds").convert("RGBA")
swath_far = Image.open(f"{DATA}/distance/wheatCutDistance_diffuse.dds").convert("RGBA")
swath_mean = ImageStat.Stat(swath.convert("RGB")).mean
for crop, grain_name in CROPS.items():
    grain_mean = ImageStat.Stat(Image.open(f"{DATA}/{grain_name}_diffuse.dds").convert("RGB")).mean
    factors = [g / s * k for g, s, k in zip(grain_mean, swath_mean, ADJUST.get(crop, (1, 1, 1)))]
    save_like(tint(swath, factors), f"{DATA}/wheatCut_diffuse.dds", f"{out_dir}/{crop}Swath_diffuse.dds")
    save_like(tint(swath_far, factors), f"{DATA}/distance/wheatCutDistance_diffuse.dds", f"{out_dir}/{crop}SwathDistance_diffuse.dds")
    print(crop, "from", grain_name, "factors", [round(k, 3) for k in factors])

#!/usr/bin/env python3
"""AWAKE - a cosmic fractal bloom.

Generative artwork in pure Python (standard library only).  An
eight-fold symmetric Julia-set bloom floats over a warped nebula,
ringed by a petalled mandala.  The picture is rendered once per
symmetry wedge and mirrored, which keeps a 1024x1024 frame fast
while staying perfectly deterministic: no randomness, no clock,
the same bytes on every run.

Run it with MAKEFUN_OUTPUT_DIR set; it writes entry.png there.
"""

import math
import os
import struct
import zlib

SIZE = 1024                    # output is SIZE x SIZE pixels
HALF = SIZE // 2
SCALE = 1.35                   # half-width of the view, plane units
JULIA_C = (-0.76, 0.21)        # seed constant of the bloom
MAX_ITER = 56                  # escape-time iteration budget
ESCAPE2 = 16.0                 # squared escape radius (radius 4)


# ---------------------------------------------------------------- PNG

def write_png(path, pixels):
    """Write RGB `pixels` (bytearray, SIZE*SIZE*3) as a PNG file.

    Each scanline uses the Sub filter, which compresses the smooth
    gradients of this image far better than unfiltered rows.
    """
    stride = SIZE * 3
    raw = bytearray()
    for y in range(SIZE):
        row = pixels[y * stride:(y + 1) * stride]
        filt = bytearray(stride)
        for i in range(stride):
            left = row[i - 3] if i >= 3 else 0
            filt[i] = (row[i] - left) & 0xFF
        raw.append(1)
        raw.extend(filt)

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", SIZE, SIZE, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)


# ------------------------------------------------------------- layers

def nebula(a, b):
    """Warped deep-space backdrop: a purple-to-blue ramp with teal
    clouds where two sine warps agree."""
    n1 = math.sin(3.0 * a + 2.2 * math.sin(2.6 * b + 1.7 * math.sin(1.9 * a)))
    n2 = math.cos(3.4 * b + 2.0 * math.sin(2.2 * a + 0.8))
    neb = 0.5 + 0.25 * n1 + 0.25 * n2
    red = 0.05 + 0.05 * neb
    green = 0.02 + 0.11 * neb
    blue = 0.13 + 0.27 * neb
    teal = max(0.0, n1 * n2)
    green += 0.30 * teal
    blue += 0.26 * teal
    return red, green, blue


def julia(a, b):
    """Julia-set bloom with orbit traps.

    Returns (shade, escaped, trap_origin, trap_point): the smooth
    escape-time shade, whether the orbit escaped, and the closest
    approaches of the orbit to the origin and to a fixed off-centre
    point.  The traps paint the glowing petal veins of the bloom -
    an orbit that passes near the origin leaves a golden filament.
    """
    zx = a * 1.12
    zy = b * 1.12
    cx, cy = JULIA_C
    trap_origin = 1e9
    trap_point = 1e9
    for i in range(MAX_ITER):
        d2 = zx * zx + zy * zy
        if d2 < trap_origin:
            trap_origin = d2
        dp = (zx - 0.35) * (zx - 0.35) + (zy + 0.10) * (zy + 0.10)
        if dp < trap_point:
            trap_point = dp
        if d2 > ESCAPE2:
            mu = i + 1.0 - math.log2(0.5 * math.log(d2))
            return mu / MAX_ITER, True, trap_origin, trap_point
        zx, zy = zx * zx - zy * zy + cx, 2.0 * zx * zy + cy
    return 0.0, False, trap_origin, trap_point


def starlight(a, b):
    """Sparse deterministic star sparkle, hashed from the folded
    coordinates so the starfield shares the image's symmetry."""
    cx = int(a * 260.0)
    cy = int(b * 260.0)
    h = math.sin(cx * 127.1 + cy * 311.7) * 43758.5453
    h -= math.floor(h)
    if h > 0.9965:
        return (h - 0.9965) / 0.0035
    return 0.0


def pixel(a, b):
    """Colour of the image at folded wedge coordinates (a, b),
    a >= b >= 0.  Layers: nebula, Julia bloom, mandala rings."""
    radius = math.hypot(a, b)
    theta = math.atan2(b, a)

    red, green, blue = nebula(a, b)

    shade, escaped, trap_origin, trap_point = julia(a, b)
    if escaped:
        fr = 0.30 + 0.45 * shade
        fg = 0.12 + 0.10 * shade
        fb = 0.62 + 0.20 * shade
    else:
        fr, fg, fb = 0.15, 0.05, 0.27
    # Golden petal veins where the orbit grazes the origin, teal
    # glints where it passes the off-centre trap point.  Interior
    # points burn brighter - they are the heart of the flower.
    gold = math.exp(-math.sqrt(trap_origin) * 4.0)
    glint = math.exp(-math.sqrt(trap_point) * 3.0)
    heart = 1.0 if escaped else 1.15
    fr += gold * 0.80 * heart + glint * 0.10
    fg += gold * 0.58 * heart + glint * 0.55
    fb += gold * 0.26 * heart + glint * 0.50
    w = max(0.15, min(1.0, 1.25 - 0.55 * radius))
    red = red * (1.0 - w) + fr * w
    green = green * (1.0 - w) + fg * w
    blue = blue * (1.0 - w) + fb * w

    # A warm halo breathing out of the centre, sparse stars, and a
    # gentle vignette to seat the bloom in deep space.
    halo = math.exp(-radius * radius * 4.5)
    red += halo * 0.16
    green += halo * 0.12
    blue += halo * 0.05
    star = starlight(a, b) * (1.0 - 0.35 * radius)
    red += star * 0.8
    green += star * 0.8
    blue += star * 0.85
    vignette = 1.0 - 0.38 * max(0.0, radius - 0.9)
    red = (red * vignette) ** 0.85
    green = (green * vignette) ** 0.85
    blue = (blue * vignette) ** 0.85

    # Concentric mandala rings, gently bent by a 16-petal wave and
    # brightest in a band around the bloom.
    petal = 0.5 + 0.5 * math.cos(16.0 * theta)
    ring = 0.5 + 0.5 * math.sin((radius + 0.03 * math.cos(16.0 * theta)) * 54.0)
    ring = ring ** 6
    band = math.exp(-abs(radius - 0.95) * 2.0)
    add = ring * (0.10 + 0.35 * band) * (0.35 + 0.65 * petal)
    red += add * 0.45
    green += add * 0.85
    blue += add * 0.80

    return red, green, blue


# ------------------------------------------------------------ render

def to_byte(value):
    if value <= 0.0:
        return 0
    if value >= 1.0:
        return 255
    return int(value * 255.0)


def render():
    """Render the full frame.  Only the canonical wedge (right,
    below centre, under the diagonal) is evaluated; every result is
    scattered to its eight dihedral mirror positions."""
    pixels = bytearray(SIZE * SIZE * 3)
    for py in range(HALF, SIZE):
        b = (py - HALF + 0.5) / HALF * SCALE
        for px in range(py, SIZE):
            a = (px - HALF + 0.5) / HALF * SCALE
            red, green, blue = pixel(a, b)
            rgb = (to_byte(red), to_byte(green), to_byte(blue))
            spots = ((px, py), (SIZE - 1 - px, py),
                     (px, SIZE - 1 - py), (SIZE - 1 - px, SIZE - 1 - py),
                     (py, px), (SIZE - 1 - py, px),
                     (py, SIZE - 1 - px), (SIZE - 1 - py, SIZE - 1 - px))
            for x, y in spots:
                off = (y * SIZE + x) * 3
                pixels[off] = rgb[0]
                pixels[off + 1] = rgb[1]
                pixels[off + 2] = rgb[2]
    return pixels


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", ".")
    os.makedirs(out_dir, exist_ok=True)
    write_png(os.path.join(out_dir, "entry.png"), render())


if __name__ == "__main__":
    main()

# AWAKE — a cosmic fractal bloom

[![Competition](https://make.fun/api/competitions/ai-excited-01/badge.svg)](https://make.fun/bounty/ai-excited-01)
[![Rank](https://make.fun/api/badges/repos/adriansyahbsc/awake-fractal-bloom/rank.svg)](https://make.fun/bounty/ai-excited-01)
[![Reward](https://make.fun/api/badges/repos/adriansyahbsc/awake-fractal-bloom/reward.svg)](https://make.fun/bounty/ai-excited-01)

![AWAKE — a cosmic fractal bloom](output.png)

A single generative artwork computed pixel by pixel in pure Python
(standard library only — no dependencies, no network). At its heart is
a Julia-set bloom whose orbits are trapped twice: passes near the
origin paint golden petal veins, passes near an off-centre point add
teal glints. The flower is folded into eight-fold dihedral symmetry,
wrapped in concentric mandala rings bent by a 16-petal wave, and set
into a warped purple-and-teal nebula with a warm central halo, sparse
deterministic stars and a soft vignette.

The render is fully deterministic — no randomness, no clock — so every
run produces byte-identical output. Only one symmetry wedge of the
frame is evaluated and mirrored to the other seven, which keeps the
1024×1024 render fast.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py
```

This writes `entry.png` into `$MAKEFUN_OUTPUT_DIR` (the current
directory if the variable is unset).

- Output: PNG, 1024×1024, RGB
- `output.png` in this repo: 774,941 bytes (sha256
  `6fdf87cb9fa9c426bd862385ef53c717a6845ceb86e6290b1849ca21e71a165f`),
  verified byte-identical across repeated runs
- Runtime: about 4 seconds on one core

## License

MIT — see `LICENSE`.

Built by an AI agent for make.fun's *Make the AI judge excited* bounty. Referral: https://make.fun/r/kj9js265

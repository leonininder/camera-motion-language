#!/usr/bin/env python3
"""Fail a clip if upper-frame brightness centroid drifts horizontally.

Threshold 0.08 of width matches 2026-09-20 recentered.mp4 (0.48 -> 0.63).
Usage: python measure_frame_drift.py VIDEO [--times 0,0.33,0.66,0.97]
Exit 2 = FAIL_DRIFT, 0 = PASS_LOCK, 1 = usage/io error.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

THRESH = 0.08


def _frac(png: Path) -> float:
    im = np.array(Image.open(png).convert("RGB"))
    h, w = im.shape[:2]
    lum = im.mean(axis=2)
    xs = np.arange(w)
    upper = lum[h // 8 : h // 2].mean(axis=0)
    return float((upper * xs).sum() / (upper.sum() + 1e-6) / w)


def measure(video: Path, rel_times: list[float]) -> list[float]:
    probe = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(video)],
        text=True,
    ).strip()
    dur = float(probe)
    fracs = []
    with tempfile.TemporaryDirectory() as td:
        for i, rel in enumerate(rel_times):
            t = max(0.0, min(dur * rel, max(dur - 0.05, 0)))
            png = Path(td) / f"{i}.png"
            subprocess.check_call(
                ["ffmpeg", "-y", "-ss", str(t), "-i", str(video),
                 "-frames:v", "1", str(png)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            fracs.append(_frac(png))
    return fracs


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("video")
    p.add_argument("--times", default="0,0.33,0.66,0.97")
    args = p.parse_args()
    video = Path(args.video)
    if not video.is_file():
        print("missing", video, file=sys.stderr)
        return 1
    rel = [float(x) for x in args.times.split(",")]
    fr = measure(video, rel)
    delta = fr[-1] - fr[0]
    tag = "FAIL_DRIFT" if abs(delta) > THRESH else "PASS_LOCK"
    print("fracs", [round(x, 3) for x in fr], "delta", round(delta, 3), tag)
    return 2 if tag == "FAIL_DRIFT" else 0


if __name__ == "__main__":
    raise SystemExit(main())

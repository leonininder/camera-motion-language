#!/usr/bin/env python3
"""Generate tiny synthetic MP4 golden clips for CML drift-gate smoke tests.

Writes into ../golden_clips/ (relative to this script):
  static_hold.mp4           — near-identical frames (locked cam + still subject)
  subject_wiggle_static_cam.mp4 — subject rectangle translates; cam locked
  pan_authorized.mp4        — large global background shift (simulates pan)

Requires: opencv-python (cv2), numpy.
Usage:
  python scripts/make_synthetic_goldens.py
  # or from project root after venv:
  python scripts/make_synthetic_goldens.py --out-dir golden_clips
"""
from __future__ import annotations

import argparse
from pathlib import Path


def _writer(path: Path, w: int, h: int, fps: int):
    import cv2

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    vw = cv2.VideoWriter(str(path), fourcc, fps, (w, h))
    if not vw.isOpened():
        raise RuntimeError(f"cannot open VideoWriter for {path}")
    return vw


def make_static_hold(path: Path, w: int = 320, h: int = 240, n: int = 24, fps: int = 12):
    import cv2
    import numpy as np

    vw = _writer(path, w, h, fps)
    bg = np.full((h, w, 3), (40, 40, 40), dtype=np.uint8)
    cv2.rectangle(bg, (120, 80), (200, 160), (0, 180, 255), -1)
    cv2.putText(bg, "HOLD", (130, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    for _ in range(n):
        vw.write(bg)
    vw.release()


def make_subject_wiggle(path: Path, w: int = 320, h: int = 240, n: int = 24, fps: int = 12):
    import cv2
    import numpy as np

    vw = _writer(path, w, h, fps)
    for i in range(n):
        frame = np.full((h, w, 3), (40, 40, 40), dtype=np.uint8)
        # locked "camera": fixed background dots
        for x in range(20, w, 40):
            for y in range(20, h, 40):
                cv2.circle(frame, (x, y), 2, (80, 80, 80), -1)
        # subject rectangle translates horizontally (subject motion, cam locked)
        x0 = 40 + int(i * 8)
        cv2.rectangle(frame, (x0, 90), (x0 + 60, 150), (0, 200, 0), -1)
        vw.write(frame)
    vw.release()


def make_pan_authorized(path: Path, w: int = 320, h: int = 240, n: int = 24, fps: int = 12):
    import cv2
    import numpy as np

    vw = _writer(path, w, h, fps)
    # Wide canvas; window slides = global feature shift (authorized pan proxy)
    canvas_w = w + n * 10
    canvas = np.full((h, canvas_w, 3), (30, 30, 50), dtype=np.uint8)
    for x in range(0, canvas_w, 30):
        color = (60 + (x * 3) % 150, 90, 120)
        cv2.rectangle(canvas, (x, 0), (x + 20, h), color, -1)
    cv2.rectangle(canvas, (canvas_w // 2 - 30, 90), (canvas_w // 2 + 30, 150), (0, 0, 255), -1)
    for i in range(n):
        x0 = i * 10
        frame = canvas[:, x0 : x0 + w].copy()
        vw.write(frame)
    vw.release()


def main() -> int:
    p = argparse.ArgumentParser(description="Write CML synthetic golden mp4s")
    p.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory (default: <project>/golden_clips)",
    )
    args = p.parse_args()
    try:
        import cv2  # noqa: F401
        import numpy  # noqa: F401
    except ImportError:
        print(
            "NEED: opencv-python and numpy.\n"
            "  python3 -m venv .venv && .venv/bin/pip install opencv-python-headless numpy\n"
            "  .venv/bin/python scripts/make_synthetic_goldens.py"
        )
        return 2

    out = args.out_dir
    if out is None:
        out = Path(__file__).resolve().parent.parent / "golden_clips"
    out.mkdir(parents=True, exist_ok=True)

    targets = {
        "static_hold.mp4": make_static_hold,
        "subject_wiggle_static_cam.mp4": make_subject_wiggle,
        "pan_authorized.mp4": make_pan_authorized,
    }
    for name, fn in targets.items():
        path = out / name
        fn(path)
        print(f"wrote {path}")
    print("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

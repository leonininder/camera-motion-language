#!/usr/bin/env python3
"""Camera Motion Language — frame drift gate (global feature proxy).

IMPORTANT — what this metric IS and IS NOT
------------------------------------------
Optical-flow median + ORB first-to-each-sample median is a **proxy for global feature
motion**, NOT a pure camera-only meter.

- Subject motion inside a Static Shot can raise the metric (false FAIL risk).
- Authorized camera verbs (pan/tilt/dolly/…) also raise it by design.
- Distinguishing camera vs subject requires a vision strip / human confirm:
  field camera_vs_subject=ambiguous_without_vision.

CLI intents
-----------
--intent static (default)
  FAIL if drift_pct > threshold (default 8). High subject motion may false-fail
  → vision strip required when status=FAIL but camera was meant locked.

--intent authorized_camera
  Still report drift_pct. Do NOT auto-PASS. Print gate=REPORT_ONLY and
  review_required=true. Exit 0 so CI can parse; human/vision must confirm the
  motion matches the single authorized verb.

Forbidden remediation (operators): vidstab, letterbox/black bars, crop-to-hide.
Re-prompt or re-lock stills instead.

Dependencies: opencv-python (cv2), numpy. If missing, exit 2 with install hint.

Canonical paths:
  - This repo: scripts/measure_frame_drift.py
  - Wiki operators / Mac: <LLM_WIKI_ROOT>/04_projects/Camera_Motion_Language/measure_frame_drift.py
Discovery (wiki): (a) env LLM_WIKI_ROOT (b) locate Leon_LLM_Wiki under OneDrive
  Documents on Mac (c) else sibling of the wiki project note.
Legacy brightness-centroid gate: scripts/measure_frame_drift_brightness_legacy.py
"""
from __future__ import annotations

import argparse
import math
import sys


def main() -> int:
    p = argparse.ArgumentParser(
        description=(
            "CML drift gate: global feature-motion proxy "
            "(NOT pure camera-only). See module docstring."
        )
    )
    p.add_argument("--video", required=True, help="Path to mp4/mov")
    p.add_argument(
        "--threshold-pct",
        type=float,
        default=8.0,
        help="For intent=static: FAIL if drift > this %% of width (default 8)",
    )
    p.add_argument(
        "--sample-frames",
        type=int,
        default=24,
        help="Number of frames to sample across clip",
    )
    p.add_argument(
        "--intent",
        choices=("static", "authorized_camera"),
        default="static",
        help=(
            "static: enforce threshold FAIL; "
            "authorized_camera: REPORT_ONLY + review_required (exit 0)"
        ),
    )
    args = p.parse_args()
    if not math.isfinite(args.threshold_pct) or args.threshold_pct < 0:
        p.error("--threshold-pct must be finite and non-negative")
    if args.sample_frames < 2:
        p.error("--sample-frames must be at least 2")

    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except ImportError:
        print(
            "FAIL: need opencv-python and numpy. "
            "pip install opencv-python-headless numpy",
            file=sys.stderr,
        )
        return 2

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        print(f"FAIL: cannot open {args.video}", file=sys.stderr)
        return 2

    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    if n < 2 or w < 1:
        cap.release()
        print("FAIL: video too short or invalid size", file=sys.stderr)
        return 2

    idxs = np.linspace(0, n - 1, num=min(args.sample_frames, n), dtype=int)
    prev_gray = None
    prev_pts = None
    max_disp = 0.0
    first_gray = None
    sampled_grays = []
    valid_flow_pairs = 0
    orb_pairs = 0
    decoded_frames = 0

    for i in idxs:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(i))
        ok, frame = cap.read()
        if not ok:
            cap.release()
            print("status=NEEDS_REVIEW\nreason=sample_decode_failed", file=sys.stderr)
            return 2
        decoded_frames += 1
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if first_gray is None:
            first_gray = gray
        sampled_grays.append(gray)
        if prev_gray is None:
            prev_gray = gray
            prev_pts = cv2.goodFeaturesToTrack(
                prev_gray, maxCorners=200, qualityLevel=0.01, minDistance=8
            )
            continue
        if prev_pts is None or len(prev_pts) < 8:
            prev_gray = gray
            prev_pts = cv2.goodFeaturesToTrack(
                prev_gray, maxCorners=200, qualityLevel=0.01, minDistance=8
            )
            continue
        nxt, st, _ = cv2.calcOpticalFlowPyrLK(prev_gray, gray, prev_pts, None)
        if nxt is None:
            prev_gray = gray
            continue
        good_prev = prev_pts[st.flatten() == 1]
        good_next = nxt[st.flatten() == 1]
        if len(good_prev) >= 8:
            valid_flow_pairs += 1
            disp = np.linalg.norm(
                good_next.reshape(-1, 2) - good_prev.reshape(-1, 2), axis=1
            )
            max_disp = max(max_disp, float(np.median(disp)))
        prev_gray = gray
        prev_pts = cv2.goodFeaturesToTrack(
            prev_gray, maxCorners=200, qualityLevel=0.01, minDistance=8
        )

    cap.release()

    end_disp = 0.0
    max_reference_disp = 0.0
    orb = cv2.ORB_create(1000)
    if first_gray is not None:
        k1, d1 = orb.detectAndCompute(first_gray, None)
        matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        for gray in sampled_grays[1:]:
            k2, d2 = orb.detectAndCompute(gray, None)
            if d1 is None or d2 is None:
                continue
            matches = matcher.match(d1, d2)
            if len(matches) < 8:
                continue
            matches = sorted(matches, key=lambda m: m.distance)[:50]
            deltas = [np.linalg.norm(np.subtract(k2[m.trainIdx].pt, k1[m.queryIdx].pt))
                      for m in matches]
            end_disp = float(np.median(deltas))
            max_reference_disp = max(max_reference_disp, end_disp)
            orb_pairs += 1

    if decoded_frames < 2 or valid_flow_pairs != len(idxs) - 1 or orb_pairs != len(idxs) - 1:
        print("metric_kind=global_feature_proxy")
        print("status=NEEDS_REVIEW")
        print("gate=INSUFFICIENT_EVIDENCE")
        print("review_required=true")
        print("reason=insufficient_trackable_features")
        return 2

    metric = max(max_disp, max_reference_disp)
    pct = 100.0 * metric / float(w)

    # Always print metric provenance first (machine-parseable).
    print("metric_kind=global_feature_proxy")
    print("camera_vs_subject=ambiguous_without_vision")
    print(f"intent={args.intent}")
    print(f"frame_width={w} height={h} frames={n}")
    print(f"median_flow_disp_px={max_disp:.3f}")
    print(f"first_last_orb_disp_px={end_disp:.3f}")
    print(f"max_first_sample_orb_disp_px={max_reference_disp:.3f}")
    print(f"drift_pct_of_width={pct:.3f}")
    print(f"threshold_pct={args.threshold_pct}")

    if args.intent == "authorized_camera":
        # Report only — never auto-PASS. Human/vision must confirm verb match.
        print("gate=REPORT_ONLY")
        print("review_required=true")
        print("status=NEEDS_REVIEW")
        print(
            "note=authorized_camera intent: confirm motion matches the single "
            "Leon-named verb via vision strip; proxy cannot separate camera vs subject"
        )
        print("forbidden=vidstab,letterbox,black_bars,crop_to_hide")
        return 0

    # intent=static
    status = "PASS" if pct <= args.threshold_pct else "FAIL"
    print(f"status={status}")
    print("gate=ENFORCE")
    print("review_required=false" if status == "PASS" else "review_required=true")
    if status == "FAIL":
        print(
            "note=high subject motion may false-fail a locked Static Shot; "
            "vision strip required before accepting FAIL as camera drift"
        )
        print("remediation=reprompt_or_relock_stills")
        print("forbidden=vidstab,letterbox,black_bars,crop_to_hide")
        return 1
    print("note=static intent PASS on proxy; still optional vision strip for identity")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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
import json
import sys


class CLIError(ValueError):
    pass


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise CLIError(message)


def emit(fields, args=None, *, output_format=None, code=2):
    """One result on stdout; stderr is reserved for dependency diagnostics."""
    result = {
        "schema_version": 1,
        "metric_kind": "global_feature_proxy",
        "camera_vs_subject": "ambiguous_without_vision",
        "status": "NEEDS_REVIEW",
        "gate": "INSUFFICIENT_EVIDENCE",
        "review_required": True,
        **fields,
    }
    result["approved"] = result["status"] == "PASS" and result["gate"] == "ENFORCE"
    if args and args.require_pass and not result["approved"] and code == 0:
        code = 2
    result["exit_code"] = code
    fmt = output_format or (args.format if args else "text")
    if fmt == "json":
        print(json.dumps(result, allow_nan=False, sort_keys=True))
    else:
        for key, value in result.items():
            if isinstance(value, bool):
                value = str(value).lower()
            elif isinstance(value, float):
                value = f"{value:.3f}"
            elif isinstance(value, list):
                value = json.dumps(value)
            print(f"{key}={value}")
    return code


def _run(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    p = Parser(
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
        default=None,
        help="Opt into a sampled preview with N frames (cannot auto-approve)",
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
    p.add_argument("--format", choices=("text", "json"), default="text",
                   help="Stable versioned JSON or human-readable key=value output")
    p.add_argument("--require-pass", action="store_true",
                   help="Exit zero only for an enforced PASS, never for report-only")
    p.add_argument("--all-frames", action="store_true",
                   help="Decode every frame (the default); excludes --sample-frames")
    # Honor JSON even on invalid options; never infer approval from an exception.
    json_requested = "--format=json" in argv or any(
        argv[i:i + 2] == ["--format", "json"] for i in range(len(argv)))
    try:
        args = p.parse_args(argv)
        if not math.isfinite(args.threshold_pct) or args.threshold_pct < 0:
            p.error("--threshold-pct must be finite and non-negative")
        if args.sample_frames is not None and args.sample_frames < 2:
            p.error("--sample-frames must be at least 2")
        if args.all_frames and args.sample_frames is not None:
            p.error("--all-frames and --sample-frames are mutually exclusive")
        args.all_frames = args.all_frames or args.sample_frames is None
    except CLIError as exc:
        return emit({"reason": "invalid_arguments", "error": str(exc)},
                    output_format="json" if json_requested else "text")

    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except ImportError:
        return emit({"reason": "missing_dependency",
                     "error": "Install requirements.txt in this Python environment"}, args)

    cap = cv2.VideoCapture(args.video)
    try:
        return _measure(cap, args, cv2, np)
    finally:
        cap.release()


def _measure(cap, args, cv2, np):
    if not cap.isOpened():
        cap.release()
        return emit({"reason": "video_open_failed"}, args)

    metadata = [cap.get(prop) for prop in (cv2.CAP_PROP_FRAME_COUNT,
                cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT)]
    if any(not math.isfinite(value) for value in metadata):
        return emit({"reason": "invalid_video_metadata"}, args)
    n, w, h = (int(value) for value in metadata)
    if n < 2 or w < 1 or h < 1:
        return emit({"reason": "invalid_video_metadata"}, args)

    idxs = range(n) if args.all_frames else np.linspace(0, n - 1, num=min(args.sample_frames, n), dtype=int)
    prev_gray = None
    prev_pts = None
    max_disp = 0.0
    first_gray = None
    orb = cv2.ORB_create(1000)
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    first_keys = first_desc = None
    end_disp = max_reference_disp = 0.0
    minimum_inlier_ratio = 1.0
    valid_flow_pairs = 0
    orb_pairs = 0
    decoded_frames = 0

    for i in idxs:
        if not args.all_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(i))
        ok, frame = cap.read()
        if not ok:
            cap.release()
            return emit({"reason": "sample_decode_failed", "failed_frame": int(i)}, args)
        decoded_frames += 1
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if first_gray is None:
            first_gray = gray
            first_keys, first_desc = orb.detectAndCompute(gray, None)
        else:
            keys, desc = orb.detectAndCompute(gray, None)
            if first_desc is not None and desc is not None:
                matches = sorted(matcher.match(first_desc, desc), key=lambda m: m.distance)[:50]
                if len(matches) >= 8:
                    source = np.float32([first_keys[m.queryIdx].pt for m in matches])
                    target = np.float32([keys[m.trainIdx].pt for m in matches])
                    transform, inliers = cv2.estimateAffinePartial2D(
                        source, target, method=cv2.RANSAC, ransacReprojThreshold=3.0)
                    if transform is not None and inliers is not None:
                        mask = inliers.ravel().astype(bool)
                        ratio = float(mask.mean())
                        minimum_inlier_ratio = min(minimum_inlier_ratio, ratio)
                        if int(mask.sum()) >= 8 and ratio >= 0.5:
                            end_disp = float(np.median(np.linalg.norm(target[mask] - source[mask], axis=1)))
                            max_reference_disp = max(max_reference_disp, end_disp)
                            orb_pairs += 1
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
        if nxt is None or st is None:
            prev_gray = gray
            prev_pts = cv2.goodFeaturesToTrack(
                prev_gray, maxCorners=200, qualityLevel=0.01, minDistance=8
            )
            continue
        # A solver status flag alone does not prove a valid long-range track.
        # Reject tracks that cannot return to within one pixel of their origin.
        back, back_st, _ = cv2.calcOpticalFlowPyrLK(gray, prev_gray, nxt, None)
        if back is None or back_st is None:
            mask = np.zeros(len(prev_pts), dtype=bool)
        else:
            mask = ((st.ravel() == 1) & (back_st.ravel() == 1)
                    & (np.linalg.norm((back - prev_pts).reshape(-1, 2), axis=1) <= 1.0))
        good_prev = prev_pts[mask]
        good_next = nxt[mask]
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

    # Container frame counts can be stale or corrupt. Never declare the whole
    # clip passed when additional frames remain after its advertised last frame.
    extra_frame, _ = cap.read()
    cap.release()
    if extra_frame:
        return emit({"reason": "metadata_frame_count_mismatch", "declared_frames": n,
                     "decoded_samples": decoded_frames, "all_frames": args.all_frames}, args)

    evidence = {
        "intent": args.intent, "frame_width": w, "height": h, "frames": n,
        "sampled_frame_indices": [int(i) for i in idxs],
        "all_frames": args.all_frames,
        "decoded_frames": decoded_frames, "flow_pairs": valid_flow_pairs,
        "reference_pairs": orb_pairs, "expected_pairs": len(idxs) - 1,
        "minimum_reference_inlier_ratio": minimum_inlier_ratio,
        "threshold_pct": args.threshold_pct,
    }
    if decoded_frames < 2 or valid_flow_pairs != len(idxs) - 1 or orb_pairs != len(idxs) - 1:
        return emit({**evidence, "reason": "insufficient_trackable_features_or_geometry"}, args)

    metric = max(max_disp, max_reference_disp)
    pct = 100.0 * metric / float(w)

    evidence.update({
        "median_flow_disp_px": max_disp,
        "first_last_orb_disp_px": end_disp,
        "max_first_sample_orb_disp_px": max_reference_disp,
        "drift_pct_of_width": pct,
    })
    if args.intent == "authorized_camera":
        return emit({**evidence, "gate": "REPORT_ONLY", "reason": "intent_requires_visual_review"}, args, code=0)
    status = "PASS" if pct <= args.threshold_pct else "FAIL"
    if status == "PASS" and not args.all_frames:
        return emit({**evidence, "gate": "REPORT_ONLY", "sampled_proxy_status": "PASS",
                     "reason": "sampled_preview_cannot_approve_whole_clip"}, args, code=0)
    return emit({**evidence, "status": status, "gate": "ENFORCE",
                 "review_required": status != "PASS",
                 "reason": "within_proxy_threshold" if status == "PASS" else "above_proxy_threshold"},
                args, code=0 if status == "PASS" else 1)


def main(argv=None) -> int:
    """Turn backend faults into a single non-approving machine result."""
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        import cv2
    except ImportError:
        return _run(argv)  # emit the normal dependency diagnostic
    try:
        return _run(argv)
    except cv2.error:
        json_requested = "--format=json" in argv or any(
            argv[i:i + 2] == ["--format", "json"] for i in range(len(argv)))
        return emit({"reason": "vision_backend_error"},
                    output_format="json" if json_requested else "text")


if __name__ == "__main__":
    raise SystemExit(main())

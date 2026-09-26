# Golden clips — Camera Motion Language drift gate

Document type: Operator fixture guide  
Status: SYNTHETIC fixtures only (2026-09-24). **Not** H3 evidence.  
Label: **SYNTHETIC** — do not treat measured numbers below as MiniMax H3 tok/s or real Sampled exports.

## What these prove

The drift script (`scripts/measure_frame_drift.py`) measures a **global feature-motion proxy** (optical-flow median + ORB first/last). It is **not** a pure camera-only meter: subject motion can raise the metric under a locked Static Shot; authorized camera verbs also raise it.

## Three synthetic tests

| Clip | Intent | Expected policy |
|---|---|---|
| `static_hold.mp4` | `--intent static` | near-identical frames → **PASS** ≪8% |
| `subject_wiggle_static_cam.mp4` | `--intent static` | subject moves, cam locked → proxy **may FAIL**; vision must confirm Static Shot |
| `pan_authorized.mp4` | `--intent authorized_camera` | large global shift → high drift; **REPORT_ONLY** (`gate=REPORT_ONLY`, `review_required=true`, exit 0) |

### How to generate

```bash
# From repo root
python3 -m venv .venv && .venv/bin/pip install opencv-python-headless numpy
.venv/bin/python scripts/make_synthetic_goldens.py
```

Requires opencv + numpy. If missing, the generator prints the same install hint and exits 2.

### How to measure

```bash
.venv/bin/python scripts/measure_frame_drift.py --video golden_clips/static_hold.mp4 --intent static --threshold-pct 8
.venv/bin/python scripts/measure_frame_drift.py --video golden_clips/subject_wiggle_static_cam.mp4 --intent static --threshold-pct 8
.venv/bin/python scripts/measure_frame_drift.py --video golden_clips/pan_authorized.mp4 --intent authorized_camera --threshold-pct 8
```

## Measured synthetic evidence (box run 2026-09-24 CST) — SYNTHETIC not H3

### 1) static_hold — intent=static — expect PASS

```
metric_kind=global_feature_proxy
camera_vs_subject=ambiguous_without_vision
intent=static
frame_width=320 height=240 frames=24
median_flow_disp_px=0.000
first_last_orb_disp_px=0.000
drift_pct_of_width=0.000
threshold_pct=8.0
status=PASS
gate=ENFORCE
review_required=false
note=static intent PASS on proxy; still optional vision strip for identity
exit:0
```

### 2) subject_wiggle_static_cam — intent=static — may FAIL proxy (vision confirm Static Shot)

```
metric_kind=global_feature_proxy
camera_vs_subject=ambiguous_without_vision
intent=static
frame_width=320 height=240 frames=24
median_flow_disp_px=0.001
first_last_orb_disp_px=81.216
drift_pct_of_width=25.380
threshold_pct=8.0
status=FAIL
gate=ENFORCE
review_required=true
note=high subject motion may false-fail a locked Static Shot; vision strip required before accepting FAIL as camera drift
remediation=reprompt_or_relock_stills
forbidden=vidstab,letterbox,black_bars,crop_to_hide
exit:1
```

### 3) pan_authorized — intent=authorized_camera — REPORT_ONLY

```
metric_kind=global_feature_proxy
camera_vs_subject=ambiguous_without_vision
intent=authorized_camera
frame_width=320 height=240 frames=24
median_flow_disp_px=10.001
first_last_orb_disp_px=221.450
drift_pct_of_width=69.203
threshold_pct=8.0
gate=REPORT_ONLY
review_required=true
status=NEEDS_REVIEW
note=authorized_camera intent: confirm motion matches the single Leon-named verb via vision strip; proxy cannot separate camera vs subject
forbidden=vidstab,letterbox,black_bars,crop_to_hide
exit:0
```

Control (same pan clip under static — expect FAIL):

```
drift_pct_of_width=69.203
status=FAIL
gate=ENFORCE
exit:1
```

## Explicit non-claims

- These mp4s are colored-rectangle OpenCV synthetics — **not** MiniMax H3 exports.
- Numbers above are **SYNTHETIC** evidence that the gate script + intents behave. Real H3 rows live in the Leon LLM Wiki `04_projects/Camera_Motion_Language/drift_evidence_en.md` (**MEASURED** 2026-09-24). SYNTHETIC ≠ H3.
- Legacy brightness-centroid gate (LOCK pack 8895185) kept at `scripts/measure_frame_drift_brightness_legacy.py` for comparison only.

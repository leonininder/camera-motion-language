# camera-motion-language

Status: **LOCKED** (SOP / review pack). Evidence: **MEASURED**.
Lock: David R2 9.7 PASS / Justin Sun R3 9.5 PASS (2026-09-24).

Leon’s **one** Hermes skill for camera: classify **keyed vs sampled**, default H3 to **static**, fail clips that drift.

This lock is **not** a claim that PlanV2 Static always passes the 8% gate. Measured lock quartet: **3 FAIL / 1 PASS**.

Not a fork of Remotion / GSAP / Lottie / Shotcraft / Pixel2Motion / HyperFrames. Those are cited in `references/sources.md` only.

Wiki entry: `04_projects/Camera_Motion_Language/` and `07_skills/camera_motion_language_skill_en.md`.

## Install (Hermes)

Copy this folder to:

`%LOCALAPPDATA%/hermes/profiles/<profile>/skills/creative/camera-motion-language/`

New session to load. Wiki fallback (any LLM): Leon LLM Wiki `07_skills/camera_motion_language_skill_en.md`.

## Drift gate

```bash
python scripts/measure_frame_drift.py path/to/clip.mp4
# 0 PASS_LOCK  |  2 FAIL_DRIFT  (|delta| > 0.08 of frame width)
```

Needs: Python, numpy, Pillow, ffmpeg on PATH.

## License

MIT for this skill’s text and script. Upstream licenses are not MIT-by-default (Remotion License, GSAP Standard). See `references/sources.md`.

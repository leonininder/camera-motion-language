# camera-motion-language

> Split keyed vs sampled camera; default Static Shot; enforce 8% drift.

Status: **LOCKED** SOP / review pack (2026-09-24). Evidence: **MEASURED**.  
Lock (SOP pack @ `8895185`): David R2 9.7 PASS / Justin Sun R3 9.5 PASS.  
This lock is **not** a claim that PlanV2 Static always passes the 8% gate. Measured lock quartet: **3 FAIL / 1 PASS**.

Launch-shell updates (docs, goldens, proxy gate CLI) ship on branch PRs and need a **fresh** David + Justin Sun independently ≥9.5 before merge to `main`.

Leon’s **one** Hermes skill for camera: classify **keyed vs sampled**, default H3 to **static**, fail clips that drift.

Not a fork of Remotion / GSAP / Lottie / Shotcraft / Pixel2Motion / HyperFrames. Those are cited in `references/sources.md` only.

Wiki entry: `04_projects/Camera_Motion_Language/` and `07_skills/camera_motion_language_skill_en.md`.

## Surfaces

| Surface | What |
|---------|------|
| Skill SOP | [`SKILL.md`](SKILL.md) |
| Drift gate | [`scripts/measure_frame_drift.py`](scripts/measure_frame_drift.py) |
| SYNTHETIC goldens | [`golden_clips/`](golden_clips/) |
| Shot-card schema | [`references/shot_card_schema.md`](references/shot_card_schema.md) |
| Launch checklist | [`docs/LAUNCH_CHECKLIST.md`](docs/LAUNCH_CHECKLIST.md) |
| Features / non-goals | [`FEATURES.md`](FEATURES.md) |

No hero GIF in-repo yet — use the one-command golden demo below (honest terminal output). Do not invent demo media.

## Install (Hermes)

Copy this folder to:

`%LOCALAPPDATA%/hermes/profiles/<profile>/skills/creative/camera-motion-language/`

New session to load. Wiki fallback (any LLM): Leon LLM Wiki `07_skills/camera_motion_language_skill_en.md`.

## Drift gate (&lt;2 min demo)

```bash
python3 -m venv .venv && .venv/bin/pip install opencv-python-headless numpy
.venv/bin/python scripts/measure_frame_drift.py \
  --video golden_clips/static_hold.mp4 \
  --intent static --threshold-pct 8
# expect: status=PASS  gate=ENFORCE  (SYNTHETIC fixture)
```

- `--intent static` — FAIL if drift proxy **> 8% of frame width** (exit 1).
- `--intent authorized_camera` — REPORT_ONLY; never auto-PASS (exit 0).
- Metric is a **global feature-motion proxy**, not pure camera-only. Subject motion can false-FAIL a Static Shot → vision strip required.
- Forbidden “fixes”: vidstab, letterbox/black bars, crop-to-hide.

Goldens are **SYNTHETIC** (see `golden_clips/README.md`). Real H3 rows live in the wiki `drift_evidence_en.md` (**MEASURED**).

Legacy brightness-centroid gate from the initial LOCKED pack: `scripts/measure_frame_drift_brightness_legacy.py`.

## Honesty

- No fake GIF / fabricated stars / sponsor logos.
- SYNTHETIC goldens ≠ MiniMax H3 exports.
- LOCKED SOP ≠ every H3 Static clears 8%.
- CN entry deferred — EN is canonical for now.

## License

MIT for this skill’s text and scripts. Upstream licenses are not MIT-by-default (Remotion License, GSAP Standard). See `references/sources.md`.

---
name: camera-motion-language
description: Lock or key camera; never sample accidental I2V pan.
version: 0.3.0
author: Leon, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [camera, motion, i2v, remotion, gsap, 9:16]
    related_skills: [phone-reel-production, blender-3d-h3-pipeline]
---

# Camera motion language

Status: Experimental public CLI and camera-planning SOP. Run the current regression suite and review real footage before publishing. Historical internal reviews do not certify this CLI revision.

Two universes. Mixing them is how a 9:16 heroine walks out of frame while an agent "fixes black bars."

- **Keyed** (Remotion, GSAP, Lottie, HyperFrames, Pixel2Motion, Shotcraft): the lens is a number you set per frame.
- **Sampled** (MiniMax H3 / Comfy I2V): the lens is guessed. Default is **static**. One named move only if both stills keep the subject in frame.

Source freeze 2026-09-24: `references/sources.md`. Analog mappings are labeled analog; they are not APIs.

## Features (this skill, not the seven upstreams)

1. Universe split: keyed vs sampled before any generate/edit.
2. Sampled default: `Static Shot`. One named move only if both stills keep the subject.
3. Drift gate: `scripts/measure_frame_drift.py` (`--intent static|authorized_camera`), fail static if proxy `> 8%` of width.
4. Complaint routing: subject-exit is not black bars / vidstab.
5. Filename is not evidence (`locked_*.mp4` still FAIL).
6. Upstream licenses stay in `references/sources.md`; none of their runtimes are vendored.

Primary gate metric is already `global_feature_proxy` (`scripts/measure_frame_drift.py`); brightness-centroid kept as legacy only. Roadmap (not in this lock): face/person detector; copy install to 小綠 profile; optional Remotion 9:16 keyed path as a *separate* procedure, still not H3.

## When to Use

- 運鏡, camera pan/zoom/dolly, heroine leaving frame, I2V drift, Remotion/GSAP/Lottie motion.
- After a still is geometry-OK and before I2V.

Don't use for: newspaper explainers; Telegram 9:16 *delivery* (that is `phone-reel-production`); inventing H3 recipes from Shotcraft crash-zooms.

## Procedure

1. **Classify.** Need frame-accurate 2D/3D motion of known pixels → keyed stack. Need organic motion of a photographed/generated plate → H3 I2V. Completion: one universe named in the prompt log.
2. **If sampled I2V:** camera line is `Static Shot` / `stationary camera` / `kitchen NEVER changes`. Do not write pan, truck, orbit, crash-zoom, Ken Burns, or "follow her" unless Leon asked for that move. First and last stills must both show the full subject. Completion: vision on first and last stills — subject inside frame, same seat/stand geometry.
3. **If a move is intentional:** one move, one hero. Both endpoints keep the subject. No competing camera (Shotcraft: one holder of the lens). Completion: the move is named once; a second camera word is absent.
4. **Gate the mp4.** `python scripts/measure_frame_drift.py --video VIDEO --intent static --threshold-pct 8` (this skill). Proxy `drift_pct_of_width > 8` → **FAIL** (exit 1), do not ship. For a Leon-named camera verb use `--intent authorized_camera` → `gate=REPORT_ONLY`, `status=NEEDS_REVIEW` (exit 0; no auto-PASS). Metric is `global_feature_proxy` (not pure camera-only). Completion: printed `status=PASS|FAIL|NEEDS_REVIEW`.
5. **Do not "fix" drift with letterbox crop, vidstab, or black-bar talk** unless Leon named bars. Those are other defects. Redo prompt or stills.

## Keyed notes (do not paste into H3)

- LottieFiles motion-design: 1/3-screen travel; one hero; no linear spatial; staging. MIT.
- story-to-handdrawn-video: no shake; contain not cover; 3:4 not 9:16. MIT.
- Remotion: `interpolate`/`spring`/`useCurrentFrame`; composition WxH is 9:16; **Remotion License** not MIT.
- video-shotcraft: 16:9 Remotion product-UI cameras; vocabulary only; Apache-2.0.
- pixel2motion: final-frame contract; 2–4px wipe drift must return to 0. MIT. Not I2V.
- GSAP: analog truck/punch/path; Standard no-charge license; not executable in H3.
- HyperFrames: authored wrapper Ken Burns; dolly-zoom needs real depth; Apache-2.0. Endpoint-only zoom is a named failure.

## Pitfalls

- Treating GSAP `x` or Remotion `scale` as an H3 camera.
- I2V between independently generated rooms (furniture morphs) — `phone-reel-production`.
- Black-bar diagnosis when the complaint is subject exit.
- Dumping Shotcraft's 157 cards into one I2V prompt.

## Verification

- Drift script on a known-bad / high-motion golden → FAIL or NEEDS_REVIEW as documented in `golden_clips/README.md`; on `static_hold.mp4` → PASS (SYNTHETIC).
- Claims in wiki cite `references/sources.md` files, not invented cinematography.

## Publish / share surface

Distribution pattern: `docs/LAUNCH_CHECKLIST.md` (CML adaptation of the shared Jarvis→Leon checklist in Leon LLM Wiki `03_wiki/process/launch_distribution_checklist_from_jev_jarvis_en.md`).

**Demo artifact:** `golden_clips/` (SYNTHETIC) + one-command gate:

```bash
python scripts/measure_frame_drift.py \
  --video golden_clips/static_hold.mp4 \
  --intent static --threshold-pct 8
```

**Shot-card filled example:** see Worked Sampled-style card in wiki skill, or fill `references/shot_card_schema.md` (`demo-static-01`: `camera_verb: none`, `drift.intent: static`).

**Before/after PASS/FAIL:** run the gate on a golden or an H3 export; record `status=PASS|FAIL` and `drift_pct_of_width`. Cite wiki `drift_evidence_en.md` for MEASURED H3 rows — do not claim goldens are H3. Do not invent a hero GIF.

**Adopt without full wiki:** hand (1) this SOP, (2) `references/shot_card_schema.md`, (3) `scripts/measure_frame_drift.py`, (4) one filled shot-card, (5) one golden + expected gate line. Architecture notes stay optional (wiki).

Traditional Chinese onboarding: [docs/README.zh-TW.md](docs/README.zh-TW.md). The English SOP remains canonical.

## Distribution surface

Launch / share shell follows the shared Jarvis→Leon checklist. Do not rewrite LOCKED architecture claims for virality; keep SYNTHETIC vs MEASURED labels. Skill status LOCKED date ≠ product Release.

### Measurement failures

If sampled frames cannot be decoded or feature coverage is insufficient, the current CLI returns exit 2 and NEEDS_REVIEW. This is not PASS. Historical internal review scores apply only to their original SOP scope, not later CLI changes or public adoption claims.

The proxy compares each sampled frame to the first frame (maximum median ORB displacement), as well as adjacent-sample optical flow. A pan that returns to its start is still measured at intermediate samples. Missing sufficient features in any sampled comparison requires review; motion entirely between samples can still be missed.

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

Status: **LOCKED** (SOP / review pack). Evidence: **MEASURED**. David R2 9.7 PASS / Justin Sun R3 9.5 PASS. Not a claim that PlanV2 Static always passes 8% (lock quartet 3 FAIL / 1 PASS).

Two universes. Mixing them is how a 9:16 heroine walks out of frame while an agent "fixes black bars."

- **Keyed** (Remotion, GSAP, Lottie, HyperFrames, Pixel2Motion, Shotcraft): the lens is a number you set per frame.
- **Sampled** (MiniMax H3 / Comfy I2V): the lens is guessed. Default is **static**. One named move only if both stills keep the subject in frame.

Source freeze 2026-09-24: `references/sources.md`. Analog mappings are labeled analog; they are not APIs.

## Features (this skill, not the seven upstreams)

1. Universe split: keyed vs sampled before any generate/edit.
2. Sampled default: `Static Shot`. One named move only if both stills keep the subject.
3. Drift gate: `scripts/measure_frame_drift.py`, fail if `|delta| > 0.08`.
4. Complaint routing: subject-exit is not black bars / vidstab.
5. Filename is not evidence (`locked_*.mp4` still FAIL_DRIFT).
6. Upstream licenses stay in `references/sources.md`; none of their runtimes are vendored.

Roadmap (not in this lock): face-centroid instead of brightness; copy install to 小綠 profile; optional Remotion 9:16 keyed path as a *separate* procedure, still not H3.

## When to Use

- 運鏡, camera pan/zoom/dolly, heroine leaving frame, I2V drift, Remotion/GSAP/Lottie motion.
- After a still is geometry-OK and before I2V.

Don't use for: newspaper explainers; Telegram 9:16 *delivery* (that is `phone-reel-production`); inventing H3 recipes from Shotcraft crash-zooms.

## Procedure

1. **Classify.** Need frame-accurate 2D/3D motion of known pixels → keyed stack. Need organic motion of a photographed/generated plate → H3 I2V. Completion: one universe named in the prompt log.
2. **If sampled I2V:** camera line is `Static Shot` / `stationary camera` / `kitchen NEVER changes`. Do not write pan, truck, orbit, crash-zoom, Ken Burns, or "follow her" unless Leon asked for that move. First and last stills must both show the full subject. Completion: vision on first and last stills — subject inside frame, same seat/stand geometry.
3. **If a move is intentional:** one move, one hero. Both endpoints keep the subject. No competing camera (Shotcraft: one holder of the lens). Completion: the move is named once; a second camera word is absent.
4. **Gate the mp4.** `python scripts/measure_frame_drift.py VIDEO` (this skill). `|delta upper_cx_frac| > 0.08` → **FAIL_DRIFT**, do not ship. Live: `recentered` frames 0.48→0.63 FAIL; kitchen H3 `seg_AB` delta −0.001 PASS. Completion: printed PASS_LOCK or FAIL_DRIFT.
5. **Do not "fix" drift with letterbox crop, vidstab, or black-bar talk** unless Leon named bars. Those are other defects.

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

- Drift script on a known-bad clip → FAIL_DRIFT; on a locked H3 clip → PASS_LOCK.
- Claims in wiki cite `references/sources.md` files, not invented cinematography.

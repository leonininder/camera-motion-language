# Features — Leon camera-motion-language

This is **one** Leon skill. It does not vendor Remotion, GSAP, Lottie, Shotcraft, Pixel2Motion, or HyperFrames.

## In this pack (v0.3 launch shell)

| Feature | What it does | Done when |
|---|---|---|
| Universe classifier | Keyed vs sampled before generate | Prompt log names one universe |
| Sampled static default | H3 camera is stationary | First/last stills both contain the subject |
| One-move rule | At most one named camera verb | Second camera word absent |
| Drift gate | `measure_frame_drift.py` (`--intent static` or `authorized_camera`) | `status=PASS` / `FAIL` / `NEEDS_REVIEW` printed |
| Misdiagnosis ban | Subject-exit ≠ letterbox | Agent does not talk black bars unless asked |
| Source freeze | Seven repos, licenses, no invented APIs | `references/sources.md` |
| SYNTHETIC goldens | `golden_clips/` + generator | Labeled SYNTHETIC; not H3 |
| Launch checklist | `docs/LAUNCH_CHECKLIST.md` | Honest surfaces; no fake GIF |

## Not in this skill

- Telegram 9:16 *delivery* (`phone-reel-production`)
- Kitchen furniture millimetres (`blender-3d-h3-pipeline`)
- Executing Shotcraft's 157 Remotion cards as I2V

## Later (explicitly unbuilt)

- Face/person detector instead of brightness centroid
- Install copy on default/小綠 Hermes profile
- Optional keyed Remotion 9:16 procedure (separate section, never mixed into H3 prompts)

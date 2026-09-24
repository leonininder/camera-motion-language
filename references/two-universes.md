# Keyed vs sampled camera

## Keyed
Remotion `useCurrentFrame` + `interpolate`/`spring`. GSAP timelines. Lottie. HyperFrames seek. Pixel2Motion SVG. Shotcraft PageCam.
The subject cannot leave frame unless a keyframe puts it there.

## Sampled
MiniMax H3 / Comfy I2V. First/last stills + a text camera line. The model may pan.

Default camera line (character/kitchen 9:16):

```
Static Shot. Stationary camera. Only the person moves. Furniture and set stay fixed.
```

If Leon names a move: put the same subject in **both** stills, inside the frame, then name **one** move. HyperFrames: endpoint-only zoom without middle poses is a named failure — use two H3 segments, not one morph.

## Drift gate
`measure_frame_drift.py`: |end-start| of upper-frame brightness centroid > 0.08 of width → FAIL_DRIFT.
Evidence 2026-09-20: recentered.mp4 0.485 → 0.628. Kitchen H3 seg_AB 2026-09-14: delta −0.001 PASS_LOCK.

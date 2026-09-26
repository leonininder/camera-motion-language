# Shot-card schema — Camera Motion Language

Document type: Machine-checkable template  
Status: SYNTHESIS_V2 + R1 must-fix 2026-09-24  
Rule: **Every shot fills one shot-card before render.**

Canonical paths: this repo `references/shot_card_schema.md`; wiki `<LLM_WIKI_ROOT>/04_projects/Camera_Motion_Language/shot_card_schema_en.md`

## YAML schema

```yaml
lane: keyed            # keyed | sampled
shot_id: "shot-001"    # stable id within the piece
intent_one_liner: "Static hold on hero product; subject may blink"

camera_verb: none      # none | pan | tilt | dolly | zoom | orbit | push-in | pull-out | crash-zoom | other
camera_authorized: false

subject_lock:
  identity: "hero-product-v3"
  anchors: ["logo center", "left edge highlight"]

# Keyed lane only (omit when sampled):
keyed_params:
  start: "Z=4.0"
  end: "Z=2.2"
  duration: "36f"
  ease: "ease-out"
  fps: 24

# Sampled lane only (omit when keyed):
sampled_prompt_path:
  first: "Static Shot, locked tripod; subject matches start still"
  mid: "Subject micro-motion only; camera locked"
  last: "End still identity preserved; no new angle"
  negatives:
    - "no unsolicited pan"
    - "no morphing face"
    - "no crash zoom"

drift:
  intent: static       # static | authorized_camera
  threshold_pct: 8
  result: null         # PASS | FAIL | NEEDS_REVIEW | null pre-render
  drift_pct: null      # filled from measure_frame_drift.py stdout
  script_path: "<LLM_WIKI_ROOT>/04_projects/Camera_Motion_Language/measure_frame_drift.py"

do_not_paste_apis: true
```

## JSON schema (equivalent fields)

```json
{
  "lane": "sampled",
  "shot_id": "shot-001",
  "intent_one_liner": "Static hold on hero product; subject may blink",
  "camera_verb": "none",
  "camera_authorized": false,
  "subject_lock": {
    "identity": "hero-product-v3",
    "anchors": ["logo center", "left edge highlight"]
  },
  "keyed_params": null,
  "sampled_prompt_path": {
    "first": "Static Shot, locked tripod; subject matches start still",
    "mid": "Subject micro-motion only; camera locked",
    "last": "End still identity preserved; no new angle",
    "negatives": ["no unsolicited pan", "no morphing face", "no crash zoom"]
  },
  "drift": {
    "intent": "static",
    "threshold_pct": 8,
    "result": null,
    "drift_pct": null,
    "script_path": "<LLM_WIKI_ROOT>/04_projects/Camera_Motion_Language/measure_frame_drift.py"
  },
  "do_not_paste_apis": true
}
```

## Field notes

| Field | Rule |
|---|---|
| `lane` | Hard split; never mix Remotion/GSAP/HyperFrames APIs into Sampled prompts. |
| `camera_verb` | Sampled default `none` (= Static Shot). If Leon names one verb, set that verb and `camera_authorized: true`. |
| `camera_authorized` | Must be true only when Leon explicitly named the verb for this shot. |
| `subject_lock` | Both stills must keep `identity` + listed `anchors`. |
| `drift.intent` | `static` enforces >8% FAIL; `authorized_camera` is REPORT_ONLY (`review_required=true`). |
| `do_not_paste_apis` | Always `true`. Remotion/GSAP/HyperFrames/pixel2motion internals stay out of H3. |

## Check before render

- [ ] One shot-card instance filled
- [ ] Lane matches tooling
- [ ] Sampled: Static unless one authorized verb
- [ ] Still-pair identity + anchors recorded
- [ ] Drift block points at canonical `measure_frame_drift.py`

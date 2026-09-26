# Camera Motion Language — Launch / distribution checklist

Document type: Project adaptation of shared launch pattern  
Status: Living  
Date: 2026-09-26 (Asia/Taipei)  
Repo: `leonininder/camera-motion-language`

**Shared pattern (Jarvis → Leon mapping):** Leon LLM Wiki  
`03_wiki/process/launch_distribution_checklist_from_jev_jarvis_en.md`  
(also mirrored in remember-me as `docs/LAUNCH_CHECKLIST.md`).

This note adapts that shell to CML (Hermes skill + drift gate + SYNTHETIC goldens), not a consumer APK.

Wiki project mirror: `04_projects/Camera_Motion_Language/launch_distribution_checklist_en.md`

**Honesty rule:** never invent stars, sponsors, live H3 demo GIFs, or “every Static PASS.” Mark missing proof `TODO` or omit. No fake demo media.

---

## CML pitch (≤15 words)

Split keyed vs sampled camera; default Static Shot; enforce 8% drift.

---

## Installable artifact &lt;2 min

Demo artifact = **synthetic goldens** + **one drift command** (not an APK):

```bash
python3 -m venv .venv && .venv/bin/pip install opencv-python-headless numpy
.venv/bin/python scripts/measure_frame_drift.py \
  --video golden_clips/static_hold.mp4 \
  --intent static --threshold-pct 8
```

Above-the-fold media: terminal PASS/FAIL lines + filled shot-card (`references/shot_card_schema.md`) — label **SYNTHETIC** vs **MEASURED H3** honestly. Do **not** invent a hero GIF.

---

## Surfaces (above the fold)

| Surface | Path |
|---------|------|
| Skill SOP | `SKILL.md` |
| Drift gate CLI | `scripts/measure_frame_drift.py` |
| Goldens (SYNTHETIC) | `golden_clips/` |
| Shot-card schema | `references/shot_card_schema.md` |
| Features / non-goals | `FEATURES.md` |
| Launch checklist | this file |
| Wiki home | Leon LLM Wiki `04_projects/Camera_Motion_Language/` |

CML does **not** claim Built-with-Jev unless a future gate literally calls System One.

---

## Sponsor / social-proof

Omit or `TODO` — never invent logos. Review scores (Justin / David) may be cited only as written for the LOCKED SOP pack (David R2 9.7 / Justin Sun R3 9.5 on 2026-09-24). **This launch-shell PR needs a fresh dual ≥9.5** before merge to `main`.

---

## Community funnel

GitHub Issues on this repo. Wiki remains the durable operator home. Optional 公众号 only with a real published funnel.

---

## Fear FAQ (CML)

| Fear | Honest answer |
|------|----------------|
| Does the 8% gate prove every H3 Static PASS? | **No.** MEASURED lock quartet was 3 FAIL / 1 PASS; gate fires. |
| Are goldens H3 outputs? | **No** — `golden_clips/` are SYNTHETIC unless labeled otherwise. |
| Can I “fix” FAIL with vidstab / letterbox / crop? | **Forbidden.** Redo prompt or stills. |
| Is the metric pure camera-only? | **No** — `metric_kind=global_feature_proxy`; subject motion can false-FAIL. |

---

## Contributor / adopter hook (without full wiki)

Minimum pack:

1. `SKILL.md` (SOP)
2. `references/shot_card_schema.md` + one filled example (see Publish / share in `SKILL.md`)
3. `scripts/measure_frame_drift.py`
4. One golden + expected PASS/FAIL line (`golden_clips/README.md`)
5. Pointer to this checklist / shared Jarvis→Leon pattern

---

## Distribution surface (architecture)

Launch / share shell follows the shared Jarvis→Leon checklist. Do not rewrite LOCKED architecture claims for virality; keep SYNTHETIC vs MEASURED labels. Skill status LOCKED date ≠ product Release.

---


---

## GitHub topics (applied 2026-09-26)

Applied via `gh repo edit leonininder/camera-motion-language --add-topic ...`:

`camera-motion`, `keyed-camera`, `sampled-i2v`, `drift-gate`, `minimax-h3`, `shot-card`, `python`, `openai-skill`, `hermes-skill`, `i2v`, `video-generation`, `computer-vision`

## Pre-flight (CML)

- [x] Pitch visible in README / skill header
- [x] One-command drift demo documented
- [x] Goldens labeled SYNTHETIC
- [x] Evidence honesty (MEASURED vs claim)
- [x] Share pack listed for adopters
- [x] Link to shared process checklist (wiki path above)
- [ ] **CN deferred** (2026-09-26): no ZH stub yet — bilingual CN entry postponed; EN SOP + checklist remain canonical
- [ ] Dual review PASS (David + Justin Sun independently ≥9.5) on this launch-shell change set — **required before merge**

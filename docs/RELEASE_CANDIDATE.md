# Conservative video screening: release candidate

Prepared 2026-09-27. This is a candidate on top of public commit
`ec5faf911ceed9f4ae7ebcded03cbe7845b7fa57`. It is not a claim that the changes
below are already on GitHub or that the tool has real-world accuracy validation.

## What changes for users

- **Every frame by default.** `--sample-frames N` becomes an opt-in preview;
  low sampled motion produces NEEDS_REVIEW, never automatic approval.
- **Usable by scripts.** `--format json` emits one versioned object;
  `--require-pass` returns zero only for an enforced PASS.
- **Reject unreliable evidence.** Geometry checks, forward/backward flow checks,
  inconsistent frame counts and backend faults lead to review instead of PASS.
- **Document the misses.** A generated single-frame excursion is missed by
  sparse sampling but detected by the default full decode. Four open-animation
  excerpts all require review; they do not establish an accuracy percentage.

Compatibility change: the old sparse `pan_authorized.mp4` fixture now abstains
with exit 2. Preview-only exit 0 still means execution completed, not approval;
use `--require-pass` for an automated gate. Human-readable frame metadata is now
one key per line. Prefer JSON schema version 1 over parsing the old text layout.

## Run the candidate before publishing

Use the README to create a fresh virtual environment and install requirements.
Windows Python 3.13.14, NumPy 2.5.3 and OpenCV headless 5.0.0 were tested in a new
venv. Package wheels were cached; this was not a new OS installation.

```sh
python -m unittest discover -s tests -v
python scripts/measure_frame_drift.py --video golden_clips/static_hold.mp4 --format json --require-pass
python scripts/evaluate_regressions.py --output regression-results.json
```

Expected: 14 test methods pass; the static command reports `approved: true`,
`all_frames: true`, `status: PASS`, `gate: ENFORCE`, and exit 0. The stress report
contains 16 rows and never auto-approves a sampled preview. See the full
[machine contract](MACHINE_CONTRACT.md) and [raw benchmark records](../benchmarks/README.md).

Not yet tested in this candidate: macOS/Linux, every supported Python version,
a general AI-video accuracy dataset, or a production publishing integration.
The GitHub Actions workflow is a local candidate and has not run remotely;
publication of it needs an appropriately authorized GitHub workflow write path.

Rollback: retain the prior commit above and its CLI behavior. A maintainer can
revert the candidate commit without rewriting history, rerun the old tests, and
announce that sampled approval behavior has returned. Do not silently downgrade
an automation that relies on `--require-pass` or JSON.

## Publication metadata and one targeted share

Suggested About: **Screen video motion locally with a Python CLI, conservative
checks, and reproducible examples.**

Suggested topics: `python`, `computer-vision`, `video-quality`, `opencv`,
`video-tools`, `ai-video`. GitHub metadata must be applied separately; this file
does not change the live About or topics.

Candidate audience: Python developers building a local video review pipeline.
Use the current r/Python Showcase thread; the community directs projects there
and requires the three headings below. Check its current rules before posting:
[r/Python](https://www.reddit.com/r/Python/). A first, earlier-version comment
already exists; prefer updating that discussion when appropriate to duplicating
the announcement. No further post is sent by this checklist.

### English draft

**What My Project Does**

Camera Motion Language is a local Python CLI for screening feature motion in
video. The new candidate decodes every frame by default, exports JSON, and never
approves a clip from a sampled preview. It runs without a GPU or API key.

**Target Audience**

Developers checking video outputs or adding a conservative screening step to a
review pipeline. It cannot distinguish moving subjects from camera movement,
and an inconclusive result requires visual review.

**Comparison**

It gives a repeatable local signal alongside visual inspection; it does not
stabilize or generate video. The repository includes a reproducible case where
sparse sampling misses an excursion, plus current abstention results on open
animation. I would like reproducible failures and reports of where setup gets
stuck. Source: https://github.com/leonininder/camera-motion-language

Publish this draft only after the candidate code and documentation are visible
at that link. Do not describe it as a benchmark winner or proven market fit.

## First-use observations (unfilled, not results)

Success means someone follows the public README, independently obtains the
documented static result, and can explain why review is not approval. Record
permission before including another person's media or identifiers.

| Date / candidate commit | Environment | Task attempted | First run succeeded? | Blocking step / error | Did it help a real task? | Voluntary repeat use? |
| --- | --- | --- | --- | --- | --- | --- |
| Not observed | — | — | — | — | — | — |

Use the issue template for a report. Never fill this table with agent-run tests
as though they were external users, and never equate clone counts with people.

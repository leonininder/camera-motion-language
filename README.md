# Camera Motion Language

**Check unwanted motion in AI video before you publish.**

A local Python CLI and optional agent skill for creators checking image-to-video clips. Measure a global feature-motion proxy, flag clips above your threshold, and send intentional camera moves for review. Runs on your own video files; no API key, GPU, or Hermes installation is needed for the CLI.

[繁體中文](docs/README.zh-TW.md) · [Agent skill](SKILL.md) · [Synthetic examples](golden_clips/README.md)

| Your intent | What the CLI does | Next step |
|---|---|---|
| Keep the shot static | PASS or FAIL against an 8% default threshold | Review the actual subject and framing before publishing |
| Make an intentional pan / tilt / dolly | NEEDS_REVIEW, with the measured motion | Confirm the move matches your shot plan |
| Video cannot be measured reliably | NEEDS_REVIEW, exit 2 | Inspect the file or use a visual review |

The metric tracks **global feature motion**, so a moving subject can trigger a false alarm. It does not detect faces, prove subject containment, stabilize footage, or generate video. The 8% default is a project policy, not a validated universal quality threshold.

## Try the included demo

Install Python 3.10 or newer and Git. From a terminal:

```sh
git clone https://github.com/leonininder/camera-motion-language.git
cd camera-motion-language
python -m venv .venv
```

**Windows PowerShell:**

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/measure_frame_drift.py --video golden_clips/static_hold.mp4 --intent static
```

**macOS / Linux:**

```sh
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/measure_frame_drift.py --video golden_clips/static_hold.mp4 --intent static
```

Expected key lines:

```text
drift_pct_of_width=0.000
status=PASS
gate=ENFORCE
```

The included clips are **synthetic OpenCV fixtures**, not real AI-video outputs. Try `golden_clips/pan_authorized.mp4` with `--intent static` for a FAIL, then use `--intent authorized_camera` for NEEDS_REVIEW. Replace the fixture path with your own MP4 or MOV.

## Read the result correctly

| Exit code | Status | Meaning |
|---|---|---|
| 0 | PASS | The sampled proxy is within the threshold for static intent |
| 0 | NEEDS_REVIEW | Intentional motion is reported, never auto-approved |
| 1 | FAIL | Static intent exceeds the selected threshold |
| 2 | NEEDS_REVIEW or error | Insufficient features, unreadable video, invalid options, or missing dependencies |

**Do not treat exit 0 alone as approval.** Check both `status` and `gate` when integrating with automation. Low texture, failed frame decoding, or insufficient tracked features cannot produce PASS. Each sampled frame after the first needs at least eight ORB matches to the first frame, and each adjacent sample pair needs at least eight flow tracks.

The proxy takes the larger of sampled adjacent-frame median optical flow and maximum first-to-sampled-frame ORB displacement, normalized by frame width. Comparing every sample against the first catches movement that returns to its start. It can still miss motion between samples, and ORB mismatches can inflate results. A PASS is a screening result, not proof of camera lock or identity preservation. Increase `--sample-frames` when useful, and inspect the clip visually.

## Plan the shot before generating

1. For authored animation, key exact camera values in your animation tool.
2. For AI-generated video, start with a static camera unless you want one named move.
3. Keep the subject visible in both endpoint stills; review the entire output afterward.
4. Run the gate, then inspect flagged clips. Rework the prompt or endpoint images when framing is wrong.

A starter camera line: `Static Shot. Stationary camera. Only the person moves. Set stays fixed.` This is prompt guidance, not a guarantee that a video model will obey it. See the [shot-card schema and example](references/shot_card_schema.md).

## Use with an agent

The [self-contained skill](SKILL.md) explains keyed versus sampled camera motion and the review workflow. Read it in any file-capable agent. For Hermes, copy this repository to `%LOCALAPPDATA%/hermes/profiles/<profile>/skills/creative/camera-motion-language/` and start a new session. Private operator notes are optional historical context; the CLI and examples work without them.

## Verification and contributions

Using the Python interpreter from your virtual environment, run:

```sh
python -m unittest discover -s tests -v
```

Substitute `.venv/bin/python` or `.\.venv\Scripts\python.exe` if you have not activated the environment. Tests cover included pass/fail/report-only clips, featureless input, missing files, and invalid CLI settings.

Useful contributions: a redistributable real video with your camera intent, observed framing, CLI output, and permission to publish; a reproducible false positive or false negative; or clearer onboarding. [Open an issue](https://github.com/leonininder/camera-motion-language/issues) with the command, Python/OpenCV versions, and expected result. Never upload private footage without permission.

## Project status and license

Early public tool with synthetic regression fixtures. Real-video accuracy and subject-retention benchmarks remain open work. Earlier internal SOP review scores do not establish public adoption, benchmark accuracy, or independent endorsement. See [release-readiness work](docs/LAUNCH_CHECKLIST.md).

MIT for this repository's original text and scripts. Referenced animation libraries have their own licenses; see [sources](references/sources.md). The historical brightness-centroid implementation remains in `scripts/measure_frame_drift_brightness_legacy.py` for comparison.

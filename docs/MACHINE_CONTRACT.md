# Integrate the drift screen safely

```sh
python scripts/measure_frame_drift.py --video golden_clips/static_hold.mp4 --format json --require-pass --all-frames
```

JSON schema version 1 emits one object on stdout. OpenCV may emit decoding
diagnostics on stderr; parse stdout only. `--help` is ordinary argparse help,
not a measurement. `schema_version`, `status`, `gate`, `approved`,
`review_required`, `reason`, `metric_kind`, `camera_vs_subject`, and `exit_code`
exist for successful measurements and handled argument/input failures.
Metric fields are absent when they cannot be measured; absent is never zero.

| Condition | approved | status / gate | Exit |
| --- | --- | --- | --- |
| Static proxy within threshold | true | PASS / ENFORCE | 0 |
| Static proxy above threshold | false | FAIL / ENFORCE | 1 |
| Intentional motion or sampled preview below threshold | false | NEEDS_REVIEW / REPORT_ONLY | 0; **2 with --require-pass** |
| Decode / dependency / arguments / tracking failure | false | NEEDS_REVIEW / INSUFFICIENT_EVIDENCE | 2 |

`approved` means only **this proxy policy passed**. It does not certify identity,
framing, copyright, safety, or overall publishability. Consumers should require
`schema_version == 1` and `approved is True`; fail closed on unknown schemas,
missing keys, malformed JSON, nonzero exit, process termination or timeout.
Never grant approval because a metric key is missing or an exception occurred.

Example using the same virtual-environment interpreter:

```python
import json, subprocess, sys

run = subprocess.run(
    [sys.executable, "scripts/measure_frame_drift.py", "--video", "clip.mp4",
     "--format", "json", "--require-pass", "--all-frames"],
    capture_output=True, text=True, timeout=120,
)
result = json.loads(run.stdout)  # let errors stop the pipeline
accepted = (run.returncode == 0 and result.get("schema_version") == 1
            and result.get("approved") is True)
```

The default reads every frame sequentially; `--all-frames` is an explicit alias.
Image working memory is constant, while CPU time and the result's index list
grow with clip length. `--sample-frames N` opts into a faster preview and cannot
be combined with `--all-frames`. A below-threshold preview returns NEEDS_REVIEW /
REPORT_ONLY with `sampled_proxy_status=PASS`, **never approved=true**. An observed
above-threshold preview still returns FAIL. Neither mode separates subject from
camera motion. Container frame counts are checked with a read past the declared
last frame; missing or extra frames require review rather than a partial PASS.

OpenCV backend exceptions return one JSON object with reason
`vision_backend_error`, approved=false and exit 2; resources are released.
Non-finite or invalid frame metadata likewise cannot pass. The optical-flow
solver's status flag is checked against a backward track, with disagreement
over one pixel discarded. These confidence checks can increase abstentions.

Reference ORB matches now require at least 8 affine RANSAC inliers and at least
50% inliers among the best 50 cross-checked matches. This is a conservative
consistency check, not a calibrated probability or a background detector.
Every reference pair and adjacent flow pair must be measurable. Inconsistent
geometry abstains, including the sparse legacy `pan_authorized.mp4` fixture.
This deliberately changes that fixture from FAIL/report-only to NEEDS_REVIEW
exit 2. Original fixture bytes are retained; the test expectations and public
examples record the new behavior instead of weakening the check to pass them.

## Reproduce the stress cases

```sh
python scripts/evaluate_regressions.py --output regression-results.json
```

Eight procedurally generated cases are run with sampled and all-frame modes.
The seeded inputs and SHA-256 hashes, package versions, actual elapsed time and
complete results are recorded. The single-frame 20% excursion is deliberately
missed by a 24-frame preview metric and caught by the default full decode. The preview abstains rather than granting approval. This is evidence of
a known boundary and its mitigation, not a real-world accuracy percentage.

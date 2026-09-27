# Reproducible evaluation, including failures

These are local maintainer-agent measurements recorded on 2026-09-27, not
external user validation. Raw JSON includes input hashes, modes and runtime
versions. Do not combine the following two probes into an accuracy score.

## Synthetic stress suite

```sh
python scripts/evaluate_regressions.py --output synthetic-results.json
```

| Generated case | Opt-in 24-frame preview | Default every frame |
| --- | --- | --- |
| Static texture | NEEDS_REVIEW | PASS |
| 20% one-way pan | FAIL | FAIL |
| 20% excursion then return to start | FAIL | FAIL |
| 20% excursion on skipped frame 25 | **NEEDS_REVIEW (preview metric misses motion)** | FAIL |
| Blank frames | NEEDS_REVIEW | NEEDS_REVIEW |
| Mid-clip full occlusion | NEEDS_REVIEW | NEEDS_REVIEW |
| Unrelated scene cut | NEEDS_REVIEW | NEEDS_REVIEW |
| Foreground rectangle on static texture | NEEDS_REVIEW | PASS |

The earlier sampled policy falsely granted PASS for the skipped-frame excursion.
The current default checks every frame, and explicit previews never auto-approve.
This change fixes the policy boundary without claiming that sparse sampling
measures motion it never observed.

The foreground case is deliberately simple and does not validate arbitrary
subject/camera separation. Coverage is eight constructed cases, not a random
sample of production video. Results: [synthetic-results.json](synthetic-results.json).

## Open-animation domain-transfer probe

Source: *Big Buck Bunny*, official 320x180 / 24 fps edition.
[Download](https://download.blender.org/peach/bigbuckbunny_movies/BigBuckBunny_320x180.mp4.zip).
[Source license and attribution](https://peach.blender.org/about/): CC BY 3.0,
**(c) copyright 2008, Blender Foundation / www.bigbuckbunny.org**.
This is authored 3D animation, not real-camera footage or AI-generated video.

The original source MP4 SHA-256 is
`f78f39603e6774907f2faafabf26a667f4a6fc31769ec304a8a8f7c62d280508`.
Download/unzip it separately; the script makes fixed time excerpts, removes
audio and re-encodes MJPG without stabilization or crop. The full film is not
bundled or downloaded automatically.

```sh
python scripts/evaluate_open_movie.py --source /path/to/BigBuckBunny_320x180.mp4 --output-dir movie-evaluation
```

| Source time | Qualitative observation from contact sheet | All-frame output |
| --- | --- | --- |
| 30–34 s | Background changes / transition | NEEDS_REVIEW |
| 61–64 s | Moving character; largely stationary visible background | NEEDS_REVIEW |
| 150–154 s | Moving characters; largely stationary visible background | NEEDS_REVIEW |
| 240–244 s | Character exit / transitions | NEEDS_REVIEW |

All four abstained because at least one reference pair lacked sufficient
geometric consistency. That is **0/4 automatic decisions** on this tiny probe,
not 100% accuracy. It exposes a current usability limit with changing subjects,
low-resolution texture and scene transitions. Contact-sheet observations are
not calibrated ground truth or independently human-labeled camera trajectories.
Results: [open-movie-results.json](open-movie-results.json).

Next useful evaluations should predefine labeled real AI-video cases, separate
camera displacement from subject changes, count abstentions, and report both
false approvals and false alarms. Keep evaluation material that disagrees with
the algorithm; do not select only easy passing examples.

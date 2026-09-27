"""Exercise the public CLI, including cases that previously falsely passed."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


class DriftCLI(unittest.TestCase):
    def run_cli(self, video, *options):
        return subprocess.run(
            [sys.executable, str(ROOT / "scripts/measure_frame_drift.py"),
             "--video", str(video), *options], capture_output=True, text=True,
        )

    def test_synthetic_policy(self):
        for clip, intent, code, status in [
            ("static_hold.mp4", "static", 0, "PASS"),
            ("pan_authorized.mp4", "static", 1, "FAIL"),
            ("pan_authorized.mp4", "authorized_camera", 0, "NEEDS_REVIEW"),
        ]:
            with self.subTest(clip=clip, intent=intent):
                result = self.run_cli(ROOT / "golden_clips" / clip, "--intent", intent)
                self.assertEqual(result.returncode, code, result.stdout + result.stderr)
                self.assertIn("status=" + status, result.stdout)

    def test_featureless_video_requires_review(self):
        with tempfile.TemporaryDirectory() as folder:
            video = Path(folder) / "blank.avi"
            writer = cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*"MJPG"), 10, (96, 96))
            self.assertTrue(writer.isOpened())
            for _ in range(10):
                writer.write(np.zeros((96, 96, 3), dtype=np.uint8))
            writer.release()
            for intent in ("static", "authorized_camera"):
                result = self.run_cli(video, "--intent", intent)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("gate=INSUFFICIENT_EVIDENCE", result.stdout)
                self.assertNotIn("status=PASS", result.stdout)

    def test_pan_returning_to_start_still_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            video = Path(folder) / "return_pan.avi"
            rng = np.random.default_rng(123)
            texture = rng.integers(0, 256, (240, 320, 3), dtype=np.uint8)
            texture = cv2.GaussianBlur(texture, (5, 5), 0)
            writer = cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*"MJPG"), 12, (320, 240))
            self.assertTrue(writer.isOpened())
            for i in range(48):
                x = round(64 * np.sin(np.pi * i / 47))
                frame = cv2.warpAffine(texture, np.float32([[1, 0, x], [0, 1, 0]]), (320, 240), borderMode=cv2.BORDER_REFLECT)
                writer.write(frame)
            writer.release()
            result = self.run_cli(video)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("status=FAIL", result.stdout)

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as folder:
            result = self.run_cli(Path(folder) / "missing.mp4")
            self.assertEqual(result.returncode, 2)

    def test_invalid_settings(self):
        for option, value in [("--sample-frames", "0"), ("--sample-frames", "1"),
                              ("--threshold-pct", "nan"), ("--threshold-pct", "inf"),
                              ("--threshold-pct", "-1")]:
            with self.subTest(option=option, value=value):
                result = self.run_cli(ROOT / "golden_clips/static_hold.mp4", option, value)
                self.assertEqual(result.returncode, 2)
                self.assertNotIn("status=PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()

"""Public process contracts, including automation's approval boundary."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class MachineContract(unittest.TestCase):
    def call(self, *args):
        p = subprocess.run([sys.executable, str(ROOT/'scripts/measure_frame_drift.py'),
                            '--format', 'json', *args], capture_output=True, text=True)
        data = json.loads(p.stdout)
        self.assertEqual(data['schema_version'], 1)
        self.assertEqual(data['exit_code'], p.returncode)
        self.assertIsInstance(data['approved'], bool)
        self.assertEqual(data['approved'], data['status'] == 'PASS' and data['gate'] == 'ENFORCE')
        return p.returncode, data

    def test_json_error_contract(self):
        for args in [[], ['--video','missing.mp4'],
                     ['--video','missing.mp4','--threshold-pct','NaN'],
                     ['--video','missing.mp4','--sample-frames','x'], ['--unknown']]:
            with self.subTest(args=args):
                code, data = self.call(*args)
                self.assertEqual(code, 2)
                self.assertFalse(data['approved'])
                self.assertTrue(data['review_required'])
                self.assertIn('reason', data)

    def test_report_only_never_approved_and_strict_exit(self):
        video = str(ROOT/'golden_clips/static_hold.mp4')
        for extra, code in [([],0), (['--require-pass'],2)]:
            actual, data = self.call('--video',video,'--intent','authorized_camera',*extra)
            self.assertEqual(actual,code)
            self.assertFalse(data['approved'])
            self.assertEqual(data['gate'],'REPORT_ONLY')

    def test_all_frames_contract_and_static_approval(self):
        code, data = self.call('--video',str(ROOT/'golden_clips/static_hold.mp4'),
                               '--all-frames','--require-pass')
        self.assertEqual(code,0)
        self.assertTrue(data['approved'])
        self.assertEqual(data['sampled_frame_indices'],list(range(data['frames'])))
        self.assertEqual(data['reference_pairs'], data['frames']-1)

    def test_default_is_full_decode_and_preview_never_approves(self):
        video = str(ROOT/'golden_clips/static_hold.mp4')
        code, data = self.call('--video',video)
        self.assertEqual(code,0)
        self.assertTrue(data['all_frames'])
        self.assertTrue(data['approved'])
        for extra, code in [([],0), (['--require-pass'],2)]:
            actual, data = self.call('--video',video,'--sample-frames','2',*extra)
            self.assertEqual(actual,code)
            self.assertFalse(data['approved'])
            self.assertEqual(data['sampled_proxy_status'],'PASS')
            self.assertEqual(data['status'],'NEEDS_REVIEW')
        code, data = self.call('--video',video,'--sample-frames','2','--all-frames')
        self.assertEqual(code,2)
        self.assertEqual(data['reason'],'invalid_arguments')

    def test_underreported_frame_count_cannot_approve(self):
        import struct
        import tempfile

        import cv2
        import numpy as np

        with tempfile.TemporaryDirectory() as folder:
            video = Path(folder) / 'underreported.avi'
            base = cv2.GaussianBlur(np.random.default_rng(123).integers(
                0, 256, (240, 320, 3), dtype=np.uint8), (5, 5), 0)
            writer = cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*'MJPG'),
                                     12, (320, 240))
            self.assertTrue(writer.isOpened())
            for i in range(48):
                x = 0 if i < 3 else round(64 * min(i - 3, 20) / 20)
                writer.write(cv2.warpAffine(base, np.float32([[1, 0, x], [0, 1, 0]]),
                                            (320, 240), borderMode=cv2.BORDER_REFLECT))
            writer.release()
            data = bytearray(video.read_bytes())
            for chunk, field in [(b'avih', 16), (b'strh', 32)]:
                struct.pack_into('<I', data, data.index(chunk) + 8 + field, 2)
            video.write_bytes(data)
            for mode in ([], ['--all-frames']):
                code, result = self.call('--video', str(video), '--require-pass', *mode)
                self.assertEqual(code, 2)
                self.assertFalse(result['approved'])
                self.assertEqual(result['reason'], 'metadata_frame_count_mismatch')


if __name__ == '__main__':
    unittest.main()

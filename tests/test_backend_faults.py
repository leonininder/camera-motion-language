"""Inject backend faults: no solver error or untrustworthy track may approve."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('drift', ROOT/'scripts/measure_frame_drift.py')
DRIFT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DRIFT)


class BackendFaults(unittest.TestCase):
    def run_json(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = DRIFT.main(['--video',str(ROOT/'golden_clips/static_hold.mp4'),
                               '--format','json','--require-pass'])
        data=json.loads(stdout.getvalue())
        self.assertEqual(code,2)
        self.assertEqual(data['exit_code'],code)
        self.assertIs(data['approved'],False)
        self.assertIs(data['review_required'],True)
        self.assertEqual(data['status'],'NEEDS_REVIEW')
        return data

    def test_opencv_faults_are_one_json_result(self):
        for name in ('VideoCapture','cvtColor','goodFeaturesToTrack',
                     'calcOpticalFlowPyrLK','ORB_create','estimateAffinePartial2D'):
            with self.subTest(operation=name):
                with patch.object(cv2,name,side_effect=cv2.error('injected backend fault')):
                    self.assertEqual(self.run_json()['reason'],'vision_backend_error')

    def test_forward_status_success_without_backward_consistency_is_rejected(self):
        calls=0
        def flow(previous,current,points,next_points):
            nonlocal calls
            calls+=1
            # A forward solver falsely reports success on unchanged coordinates;
            # its return track disagrees by five pixels. Removing FB validation
            # would produce a false zero-motion PASS on this real static fixture.
            nxt=points.copy() if calls%2 else points+5
            return nxt,np.ones((len(points),1),dtype=np.uint8),None
        with patch.object(cv2,'calcOpticalFlowPyrLK',side_effect=flow):
            data=self.run_json()
        self.assertEqual(data['flow_pairs'],0)
        self.assertIn('insufficient_trackable',data['reason'])

    def test_missing_flow_outputs_are_rejected(self):
        for value in [(None,None,None), (np.zeros((8,1,2),np.float32),None,None)]:
            with self.subTest(value=value[0] is None):
                with patch.object(cv2,'calcOpticalFlowPyrLK',return_value=value):
                    self.assertIn('insufficient_trackable',self.run_json()['reason'])

    def test_invalid_and_overreported_metadata_release_capture(self):
        original=cv2.VideoCapture
        cases=[(cv2.CAP_PROP_FRAME_COUNT,1,'invalid_video_metadata'),
               (cv2.CAP_PROP_FRAME_WIDTH,0,'invalid_video_metadata'),
               (cv2.CAP_PROP_FRAME_HEIGHT,float('nan'),'invalid_video_metadata'),
               (cv2.CAP_PROP_FRAME_COUNT,25,'sample_decode_failed')]
        for prop,value,reason in cases:
            cap=original(str(ROOT/'golden_clips/static_hold.mp4'))
            class Wrapped:
                released=False
                def isOpened(self): return cap.isOpened()
                def get(self,key): return value if key==prop else cap.get(key)
                def read(self): return cap.read()
                def set(self,key,v): return cap.set(key,v)
                def release(self):
                    self.released=True
                    cap.release()
            wrapper=Wrapped()
            with self.subTest(prop=prop,value=value):
                with patch.object(cv2,'VideoCapture',return_value=wrapper):
                    self.assertEqual(self.run_json()['reason'],reason)
                self.assertTrue(wrapper.released)


if __name__=='__main__':
    unittest.main()

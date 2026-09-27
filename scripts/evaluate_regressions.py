#!/usr/bin/env python3
"""Reproducible synthetic stress suite. Not a real-video accuracy benchmark."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def frames(kind, seed=123):
    rng = np.random.default_rng(seed)
    base = cv2.GaussianBlur(rng.integers(0,256,(240,320,3),dtype=np.uint8),(5,5),0)
    for i in range(48):
        x = 0
        if kind == 'pan':
            x = round(64*i/47)
        elif kind == 'return_pan':
            x = round(64*np.sin(np.pi*i/47))
        elif kind == 'single_frame_excursion':
            x = 64 if i == 25 else 0  # default 24 samples skip frame 25
        frame = cv2.warpAffine(base,np.float32([[1,0,x],[0,1,0]]),(320,240),borderMode=cv2.BORDER_REFLECT)
        if kind == 'blank':
            frame[:] = 0
        elif kind == 'occluded' and 12 <= i <= 36:
            frame[:] = 0
        elif kind == 'scene_cut' and i >= 24:
            frame = rng.integers(0,256,(240,320,3),dtype=np.uint8)
        elif kind == 'moving_subject':
            # Static textured background; a foreground rectangle is not camera motion.
            left = round(220*i/47)
            frame[60:140,left:left+70] = (80,160,240)
        yield frame


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',required=True)
    args=p.parse_args()
    rows=[]
    with tempfile.TemporaryDirectory() as folder:
        for kind in ['static','pan','return_pan','single_frame_excursion','blank','occluded','scene_cut','moving_subject']:
            path=Path(folder)/(kind+'.avi')
            writer=cv2.VideoWriter(str(path),cv2.VideoWriter_fourcc(*'MJPG'),12,(320,240))
            if not writer.isOpened():
                raise RuntimeError('MJPG writer unavailable')
            for frame in frames(kind):
                writer.write(frame)
            writer.release()
            for all_frames in (False,True):
                command=[sys.executable,str(ROOT/'scripts/measure_frame_drift.py'),'--video',str(path),'--format','json','--require-pass']
                if all_frames:
                    command.append('--all-frames')
                else:
                    command.extend(['--sample-frames','24'])
                start=time.perf_counter()
                proc=subprocess.run(command,capture_output=True,text=True,check=False)
                result=json.loads(proc.stdout)
                rows.append({'fixture':kind,'synthetic':True,'seed':123,
                             'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                             'all_frames':all_frames,'elapsed_seconds':time.perf_counter()-start,
                             'known_translation_pct':20 if kind in ('pan','return_pan','single_frame_excursion') else None,
                             'result':result})
    output={'scope':'Synthetic regression and sampling-gap demonstration; not real-video accuracy',
            'opencv':cv2.__version__,'numpy':np.__version__,'python':sys.version,
            'rows':rows}
    Path(args.output).write_text(json.dumps(output,indent=2),encoding='utf-8')
    for row in rows:
        print(f"{row['fixture']:24} all_frames={str(row['all_frames']):5} {row['result']['status']:12} {row['result']['reason']}")


if __name__ == '__main__':
    main()

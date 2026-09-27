#!/usr/bin/env python3
"""Measure fixed open-movie excerpts. No accuracy claim or network downloads."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

import cv2

ROOT = Path(__file__).resolve().parents[1]
WINDOWS = [(30,34,'Changing background / shot transition'),
           (61,64,'Moving character, largely stationary visible background'),
           (150,154,'Moving characters, largely stationary visible background'),
           (240,244,'Character exit and shot transitions')]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',required=True,help='Official BigBuckBunny_320x180.mp4')
    parser.add_argument('--output-dir',required=True)
    args=parser.parse_args()
    source=Path(args.source)
    output=Path(args.output_dir)
    output.mkdir(parents=True,exist_ok=True)
    digest_state=hashlib.sha256()
    with source.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):
            digest_state.update(chunk)
    digest=digest_state.hexdigest()
    cap=cv2.VideoCapture(str(source))
    if not cap.isOpened():
        raise RuntimeError('Cannot decode source')
    fps=cap.get(cv2.CAP_PROP_FPS)
    if abs(fps-24)>0.01 or int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) != 320:
        raise ValueError('Expected official 320x180 / 24 fps edition')
    rows=[]
    for start,end,observation in WINDOWS:
        clip=output/f'bbb_{start}_{end}.avi'
        writer=cv2.VideoWriter(str(clip),cv2.VideoWriter_fourcc(*'MJPG'),fps,(320,180))
        if not writer.isOpened():
            raise RuntimeError('MJPG writer unavailable')
        cap.set(cv2.CAP_PROP_POS_FRAMES,round(start*fps))
        for i in range(round((end-start)*fps)):
            ok,frame=cap.read()
            if not ok:
                raise RuntimeError(f'Failed to decode {start}+{i}/{fps}')
            writer.write(frame)
        writer.release()
        t=time.perf_counter()
        proc=subprocess.run([sys.executable,str(ROOT/'scripts/measure_frame_drift.py'),
                             '--video',str(clip),'--all-frames','--require-pass','--format','json'],
                            capture_output=True,text=True)
        rows.append({'start_seconds':start,'end_seconds':end,'clip':clip.name,
                     'sha256':hashlib.sha256(clip.read_bytes()).hexdigest(),
                     'visual_screening_note':observation,
                     'note_basis':'Maintainer-agent inspection of one-frame-per-second contact sheet, not calibrated ground truth',
                     'elapsed_seconds':time.perf_counter()-t,'result':json.loads(proc.stdout)})
    cap.release()
    record={'source_filename':source.name,'source_sha256':digest,
            'source_url':'https://download.blender.org/peach/bigbuckbunny_movies/BigBuckBunny_320x180.mp4.zip',
            'license_url':'https://peach.blender.org/about/',
            'license':'CC BY 3.0',
            'attribution':'(c) copyright 2008, Blender Foundation / www.bigbuckbunny.org',
            'changes':'Fixed temporal excerpts, no audio, re-encoded MJPG. No camera stabilization or crops.',
            'scope':'Authored animation domain-transfer probe, not AI-video accuracy or human user testing',
            'opencv':cv2.__version__,'rows':rows}
    (output/'results.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    for row in rows:
        print(row['clip'],row['result']['status'],row['result']['reason'])


if __name__=='__main__':
    main()

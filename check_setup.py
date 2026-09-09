"""Verify the installed dashboard, actual ONNX inference and OCR without a camera."""
import sys,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def main():
    import cv2,numpy as np
    from yolo_detector import LabelDetector
    from ocr_reader import read_fields
    print('Dashboard Python:',sys.version.split()[0],struct.calcsize('P')*8,'bit; OpenCV:',cv2.__version__,flush=True)
    model=ROOT/'models/parcel_fields.onnx'
    if not model.is_file():raise RuntimeError('Missing models/parcel_fields.onnx. Download/clone the complete repository and extract ZIP files before running.')
    with model.open('rb') as stream:head=stream.read(160)
    if b'git-lfs' in head or model.stat().st_size<1000000:raise RuntimeError('The ONNX file is incomplete or a pointer. Download the actual model from the repository.')
    detector=LabelDetector()
    if detector.net is None or detector.names!=['filled','empty']:raise RuntimeError(getattr(detector,'error',detector.status))
    frame=cv2.imdecode(np.fromfile(str(ROOT/'templates/complete.png'),np.uint8),cv2.IMREAD_COLOR)
    if frame is None:raise RuntimeError('Missing/unreadable templates/complete.png')
    result=detector.inspect_fields(frame)
    if result['status']!='PASS':raise RuntimeError('YOLO demo inference failed: '+result['reason'])
    print('YOLO: PASS',flush=True)
    ocr=read_fields(frame,result)
    if ocr.get('status')!='ok' or not all(row.get('text') for row in ocr.get('fields',[])) or len(ocr.get('fields',[]))!=5:
        raise RuntimeError('OCR demo failed: '+ocr.get('message','No text'))
    print('OCR: PASS (five demo fields read)',flush=True)

if __name__=='__main__':
    try:main()
    except Exception as exc:
        print('SETUP FAILED:',exc,flush=True)
        sys.exit(1)

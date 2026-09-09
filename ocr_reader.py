"""OCR for the supplied fixed template, isolated from the 32-bit dashboard."""
import json,subprocess,tempfile
from pathlib import Path
import cv2,numpy as np
from inspection import FIELDS,MARKERS,W,H,DICT,PARAMETERS
ROOT=Path(__file__).resolve().parent

def read_fields(image,result):
    corners,ids,_=cv2.aruco.ArucoDetector(DICT,PARAMETERS).detectMarkers(image)
    found={} if ids is None else {int(i):c.reshape(4,2) for i,c in zip(ids.flatten(),corners)}
    if not all(i in found for i in MARKERS):
        return {'status':'unavailable','message':'OCR perlukan empat penanda sudut template.','fields':[]}
    source=[];target=[]
    for i,(x,y) in MARKERS.items():
        source.extend(found[i]);target.extend([(x,y),(x+89,y),(x+89,y+89),(x,y+89)])
    hom,mask=cv2.findHomography(np.float32(source),np.float32(target),cv2.RANSAC,3)
    if hom is None or mask is None or mask.sum()<14:
        return {'status':'unavailable','message':'Label senget atau penjajaran tidak jelas.','fields':[]}
    flat=cv2.warpPerspective(image,hom,(W,H))
    python=ROOT/'.venv-train/Scripts/python.exe'
    if not python.exists():raise RuntimeError('Persekitaran OCR belum dipasang. Tutup dashboard dan jalankan setup.bat.')
    with tempfile.TemporaryDirectory(prefix='parcel-ocr-') as directory:
        folder=Path(directory)
        for i,(_, (x1,y1,x2,y2)) in enumerate(FIELDS):
            crop=flat[y1:y2,x1:x2]
            crop=cv2.copyMakeBorder(crop,16,16,16,16,cv2.BORDER_CONSTANT,value=(255,255,255))
            cv2.imencode('.png',crop)[1].tofile(str(folder/f'{i}.png'))
        proc=subprocess.run([str(python),str(ROOT/'ocr_worker.py'),str(folder)],capture_output=True,text=True,encoding='utf-8',timeout=45,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        if proc.returncode:raise RuntimeError('OCR gagal: '+proc.stderr[-400:])
        return json.loads((folder/'result.json').read_text(encoding='utf-8'))

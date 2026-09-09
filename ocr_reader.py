"""OCR for the supplied fixed template, isolated from the 32-bit dashboard."""
import json,subprocess,tempfile
from pathlib import Path
import cv2,numpy as np
from inspection import FIELDS,MARKERS,W,H,DICT,PARAMETERS
ROOT=Path(__file__).resolve().parent

def read_fields(image,result):
    corners,ids,_=cv2.aruco.ArucoDetector(DICT,PARAMETERS).detectMarkers(image)
    found={} if ids is None else {int(i):c.reshape(4,2) for i,c in zip(ids.flatten(),corners)}
    crops=[];method="markers"
    if all(i in found for i in MARKERS):
        source=[];target=[]
        for i,(x,y) in MARKERS.items():
            source.extend(found[i]);target.extend([(x,y),(x+89,y),(x+89,y+89),(x,y+89)])
        hom,mask=cv2.findHomography(np.float32(source),np.float32(target),cv2.RANSAC,3)
        if hom is not None and mask is not None and mask.sum()>=14:
            flat=cv2.warpPerspective(image,hom,(W,H))
            crops=[flat[y1:y2,x1:x2] for _,(x1,y1,x2,y2) in FIELDS]
    if not crops:
        # Only map a complete, validated five-row YOLO result; never shift missing rows.
        detections=result.get('detections',[])
        if result.get('status') not in ('PASS','FAIL') or len(detections)!=5 or len(result.get('fields',[]))!=5:
            return {'status':'unavailable','message':'OCR: tunjuk empat penanda atau lima kotak medan YOLO yang jelas.','fields':[]}
        method="yolo_boxes"
        height,width=image.shape[:2]
        for detection in sorted(detections,key=lambda d:d['box'][1]+d['box'][3]/2):
            x,y,w,h=detection['box']
            # Remove the printed border, retaining the single line of field content.
            px,py=max(2,round(w*.015)),max(2,round(h*.10))
            crop=image[max(0,y+py):min(height,y+h-py),max(0,x+px):min(width,x+w-px)]
            if crop.size==0:return {'status':'unavailable','message':'OCR: kotak medan di luar gambar.','fields':[]}
            if crop.shape[0]<64:
                scale=min(3.,64/crop.shape[0]);crop=cv2.resize(crop,None,fx=scale,fy=scale,interpolation=cv2.INTER_CUBIC)
            crops.append(crop)
    python=ROOT/'.venv-train/Scripts/python.exe'
    if not python.exists():raise RuntimeError('Persekitaran OCR belum dipasang. Tutup dashboard dan jalankan setup.bat.')
    with tempfile.TemporaryDirectory(prefix='parcel-ocr-') as directory:
        folder=Path(directory)
        for i,crop in enumerate(crops):
            crop=cv2.copyMakeBorder(crop,16,16,16,16,cv2.BORDER_CONSTANT,value=(255,255,255))
            cv2.imencode('.png',crop)[1].tofile(str(folder/f'{i}.png'))
        proc=subprocess.run([str(python),str(ROOT/'ocr_worker.py'),str(folder)],capture_output=True,text=True,encoding='utf-8',timeout=45,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        if proc.returncode:raise RuntimeError('OCR gagal: '+proc.stderr[-400:])
        output=json.loads((folder/'result.json').read_text(encoding='utf-8'))
        output['alignment']=method
        return output

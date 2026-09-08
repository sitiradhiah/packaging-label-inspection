"""Local pretrained RapidOCR worker. No network calls or model training."""
import json,sys
from pathlib import Path
import cv2,numpy as np
from rapidocr_onnxruntime import RapidOCR
from inspection import FIELDS
if __name__=='__main__':
    folder=Path(sys.argv[1])
    engine=RapidOCR(intra_op_num_threads=2,inter_op_num_threads=1,det_limit_type="max",det_limit_side_len=960)
    rows=[]
    for i,(name,_) in enumerate(FIELDS):
        image=cv2.imdecode(np.fromfile(str(folder/f'{i}.png'),np.uint8),cv2.IMREAD_COLOR)
        found,_=engine(image,use_cls=False)
        # Each supplied field is one line: recognise its whole text region together.
        text="";confidence=None
        if found:
            points=np.concatenate([np.asarray(r[0]) for r in found])
            x1,y1=np.maximum(0,np.floor(points.min(axis=0)).astype(int)-4)
            x2,y2=np.minimum([image.shape[1],image.shape[0]],np.ceil(points.max(axis=0)).astype(int)+4)
            line=image[y1:y2,x1:x2]
            recognised,_=engine(line,use_det=False,use_cls=False)
            if recognised and float(recognised[0][1])>=.5:
                text=str(recognised[0][0]).strip();confidence=float(recognised[0][1])
        rows.append({'name':name,'text':text,'confidence':confidence})
    (folder/'result.json').write_text(json.dumps({'status':'ok','message':'Bacaan OCR; bukan pengesahan maklumat.','fields':rows},ensure_ascii=False),encoding='utf-8')

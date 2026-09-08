from pathlib import Path
import cv2, torch, json
from ultralytics import YOLO
if __name__=='__main__':
 torch.set_num_threads(2)
 model=YOLO('training_runs/fields_v2/weights/best.pt')
 for file in ['complete.png','missing_date.png','missing_id_postcode.png','blank.png']:
  im=cv2.imread('templates/'+file)
  for padded in [False,True]:
   f=cv2.copyMakeBorder(im,270,270,360,360,cv2.BORDER_CONSTANT,value=(160,160,160)) if padded else im
   r=model.predict(f,imgsz=640,conf=.5,agnostic_nms=True,device='cpu',verbose=False)[0]
   rows=sorted([(round(float(b.xyxy[0][1])),model.names[int(b.cls[0])],round(float(b.conf[0]),3)) for b in r.boxes])
   print(file,'padded' if padded else 'direct',rows,flush=True)
 f=cv2.imread('work/current-diagnostic.jpg')
 if f is not None:
  r=model.predict(f,imgsz=640,conf=.5,agnostic_nms=True,device='cpu',verbose=False)[0]
  print('camera',[(model.names[int(b.cls[0])],round(float(b.conf[0]),3)) for b in r.boxes],flush=True)

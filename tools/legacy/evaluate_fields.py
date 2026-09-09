
# Locate shared application modules after moving this development script.
import sys
from pathlib import Path
_PROJECT_ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(_PROJECT_ROOT))
if __name__=="__main__":
    import os
    os.chdir(_PROJECT_ROOT)
import json
from pathlib import Path
import cv2
from ultralytics import YOLO
ROOT=Path(__file__).resolve().parents[2]
if __name__=="__main__":
 model=YOLO(str(ROOT/"training_runs/fields_v1/weights/best.pt"))
 for filename in ["complete.png","missing_date.png","missing_id_postcode.png","blank.png"]:
  results=model.predict(str(ROOT/"templates"/filename),imgsz=640,conf=.35,device="cpu",verbose=False)[0]
  detections=sorted([(float(b.xyxy[0][1]),model.names[int(b.cls[0])],round(float(b.conf[0]),3)) for b in results.boxes])
  print(filename,detections,flush=True)

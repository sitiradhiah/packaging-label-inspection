
# Locate shared application modules after moving this development script.
import sys
from pathlib import Path
_PROJECT_ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(_PROJECT_ROOT))
if __name__=="__main__":
    import os
    os.chdir(_PROJECT_ROOT)
from pathlib import Path
import shutil,torch
from ultralytics import YOLO
if __name__=='__main__':
 torch.set_num_threads(2)
 p=Path('work/fields-candidate.pt')
 shutil.copy2('training_runs/fields_v2/weights/best.pt',p)
 out=YOLO(str(p)).export(format='onnx',imgsz=640,opset=12,simplify=False,dynamic=False,nms=False,device='cpu')
 shutil.copy2(out,'models/parcel_fields.onnx')
 shutil.copy2(p,'models/parcel_fields.pt')

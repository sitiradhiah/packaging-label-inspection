
# Locate shared application modules after moving this development script.
import sys
from pathlib import Path
_PROJECT_ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(_PROJECT_ROOT))
if __name__=="__main__":
    import os
    os.chdir(_PROJECT_ROOT)
import os
os.environ['OMP_NUM_THREADS']='4'
from pathlib import Path
import shutil
import torch
from ultralytics import YOLO
ROOT=Path(__file__).resolve().parents[2]
if __name__=='__main__':
 torch.set_num_threads(4)
 model=YOLO(str(ROOT/'models/fields-stage1.pt'))
 model.train(data=str(ROOT/'datasets/parcel_fields_v3/data.yaml'),epochs=12,imgsz=512,batch=8,device=0 if torch.cuda.is_available() else 'cpu',workers=0,freeze=10,lr0=.001,cache=False,plots=False,project=str(ROOT/'training_runs'),name='fields_v2',exist_ok=True,mosaic=0,close_mosaic=0,fliplr=0,translate=.05,scale=.2,verbose=False)
 best=Path(model.trainer.best)
 net=YOLO(str(best))
 output=net.export(format='onnx',imgsz=640,opset=12,simplify=False,dynamic=False,nms=False,device='cpu')
 shutil.copy2(best,ROOT/'models/parcel_fields.pt')
 shutil.copy2(output,ROOT/'models/parcel_fields.onnx')
 print('FIELD MODEL READY',flush=True)

import os
os.environ['OMP_NUM_THREADS']='4'
from pathlib import Path
import shutil
import torch
from ultralytics import YOLO
ROOT=Path(__file__).resolve().parent
if __name__=='__main__':
 torch.set_num_threads(4)
 model=YOLO('yolo11n.pt')
 model.train(data=str(ROOT/'datasets/parcel_fields_v1/data.yaml'),epochs=25,imgsz=512,batch=8,device=0 if torch.cuda.is_available() else 'cpu',workers=0,freeze=10,cache=False,plots=False,project=str(ROOT/'training_runs'),name='fields_v1',exist_ok=True,mosaic=.3,close_mosaic=5,fliplr=0,translate=.05,scale=.2,verbose=False)
 best=Path(model.trainer.best)
 net=YOLO(str(best))
 output=net.export(format='onnx',imgsz=640,opset=12,simplify=False,dynamic=False,nms=False,device='cpu')
 shutil.copy2(best,ROOT/'models/parcel_fields.pt')
 shutil.copy2(output,ROOT/'models/parcel_fields.onnx')
 print('FIELD MODEL READY',flush=True)

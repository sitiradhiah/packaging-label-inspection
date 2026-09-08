"""Run with a separate 64-bit Python environment, not the existing 32-bit .venv."""
import argparse
import shutil
import struct
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--data",required=True,help="YOLO dataset YAML with separate real validation data")
    p.add_argument("--epochs",type=int,default=40)
    p.add_argument("--device",default="0",help="0 for NVIDIA GPU; cpu for CPU")
    args=p.parse_args()
    if struct.calcsize("P")!=8:raise SystemExit("Training requires 64-bit Python. Existing .venv is 32-bit.")
    from ultralytics import YOLO
    data=Path(args.data).resolve()
    if not data.exists():raise SystemExit("Dataset YAML missing")
    model=YOLO("yolo11n.pt")
    model.train(data=str(data),epochs=args.epochs,imgsz=640,batch=4,device=args.device,workers=0,project=str(ROOT/"training_runs"),name="parcel_label")
    best=Path(model.trainer.best)
    trained=YOLO(str(best))
    if len(trained.names)!=1 or trained.names[0]!="parcel_label":
        raise RuntimeError("Expected one class named parcel_label")
    exported=trained.export(format="onnx",imgsz=640,opset=12,simplify=False,dynamic=False,nms=False,device="cpu")
    target=ROOT/"models";target.mkdir(exist_ok=True)
    shutil.copy2(best,target/"parcel_label.pt")
    shutil.copy2(exported,target/"parcel_label.onnx")
    print("Model exported. Restart dashboard.")
if __name__=="__main__":main()


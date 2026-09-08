"""Parcel Label Field Completeness Inspection Using OpenCV."""
import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
import time
import cv2
import numpy as np
from inspection import inspect,FIELDS

ROOT=Path(__file__).resolve().parent

def save(result,frame):
    folder=ROOT/"results_fields";folder.mkdir(exist_ok=True)
    stamp=datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    photo=folder/(stamp+".jpg")
    if not cv2.imwrite(str(photo),frame): raise OSError("Image save failed")
    (folder/(stamp+".json")).write_text(json.dumps(result,indent=2),encoding="utf-8")
    log=folder/"inspections.csv"
    new=not log.exists()
    with log.open("a",newline="",encoding="utf-8") as stream:
        writer=csv.writer(stream)
        if new: writer.writerow(["time","status","reason"]+[name for name,_ in FIELDS]+["image"])
        texts={r["name"]:r.get("text","") for r in result.get("ocr",{}).get("fields",[])}
        writer.writerow([stamp,result["status"],result["reason"]]+[texts.get(n,"") for n,_ in FIELDS]+[photo.name])

def export_ocr_csv():
    """Rebuild the Excel-readable export from the exact saved OCR records."""
    folder=ROOT/"results_fields";folder.mkdir(exist_ok=True)
    log=folder/"inspections.csv"
    headers=["time","status","reason"]+[name for name,_ in FIELDS]+["image"]
    rows=[]
    if log.exists():
        with log.open(encoding="utf-8-sig",newline="") as stream:
            reader=csv.DictReader(stream);headers=reader.fieldnames or headers;rows=list(reader)
    for row in rows:
        record=folder/Path(row.get("image","")).with_suffix(".json").name
        if record.is_file():
            result=json.loads(record.read_text(encoding="utf-8"))
            texts={f["name"]:f.get("text","") for f in result.get("ocr",{}).get("fields",[])}
            for name,_ in FIELDS:row[name]=texts.get(name,"")
    output=folder/"inspections_ocr.csv"
    try:stream=output.open("w",encoding="utf-8-sig",newline="")
    except PermissionError:
        output=folder/("inspections_ocr_"+datetime.now().strftime("%Y%m%d_%H%M%S_%f")+".csv")
        stream=output.open("w",encoding="utf-8-sig",newline="")
    with stream:
        writer=csv.DictWriter(stream,fieldnames=headers);writer.writeheader();writer.writerows(rows)
    return output


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--camera",type=int,default=0)
    parser.add_argument("--image",help="Inspect a saved image without opening webcam")
    args=parser.parse_args()
    if args.image:
        frame=cv2.imread(args.image)
        if frame is None: raise ValueError("Image could not be opened")
        result,_=inspect(frame); print(json.dumps(result,indent=2)); return
    cap=cv2.VideoCapture(args.camera,cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap.release();cap=cv2.VideoCapture(args.camera)
    if not cap.isOpened(): raise RuntimeError("Camera unavailable. Close other camera apps or try --camera 1.")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280);cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
    title="Parcel Label Field Completeness Inspection"
    cv2.namedWindow(title,cv2.WINDOW_NORMAL)
    cv2.resizeWindow(title,1180,850)
    last="No inspection saved"
    last_time=0
    try:
        while True:
            ok,frame=cap.read()
            if not ok: raise RuntimeError("Cannot read camera frame")
            result,flat=inspect(frame)
            display=cv2.resize(frame,(720,480))
            panel=np.full((850,1180,3),(30,26,20),np.uint8)
            panel[80:560,20:740]=display
            def text(value,x,y,size=0.65,ink=(230,230,230)):
                cv2.putText(panel,value,(x,y),cv2.FONT_HERSHEY_SIMPLEX,size,ink,1,cv2.LINE_AA)
            text("PARCEL LABEL | FIELD COMPLETENESS",20,40,0.95)
            text("LIVE: "+result["status"],765,100,0.85,(80,210,240))
            for index,row in enumerate(result["fields"]):
                text(row["name"],765,150+index*65,0.57)
                text(row["state"],765,177+index*65,0.65,(70,220,70) if row["state"]=="FILLED" else (80,140,255))
            if flat is not None:
                thumb=cv2.resize(flat,(300,225));panel[590:815,20:320]=thumb
            # Wrap long messages to stay inside panel.
            import textwrap
            for j,line in enumerate(textwrap.wrap(result["reason"],72)):
                text(line,345,610+j*25,0.55)
            text("SPACE: inspect + save | Q: quit",345,695,0.65)
            text("Use supplied template. Keep 4 markers visible.",345,735,0.55)
            text("Checks marks only, not meaning or valid text.",345,765,0.55)
            text(last,345,805,0.52)
            cv2.imshow(title,panel)
            key=cv2.waitKey(1)&0xff
            if key==ord("q") or cv2.getWindowProperty(title,cv2.WND_PROP_VISIBLE)<1: break
            if key==32 and time.monotonic()-last_time>1:
                try:
                    save(result,frame)
                    last="Last saved: "+result["status"]+" at "+datetime.now().strftime("%H:%M:%S")
                except OSError as exc:
                    last="Save failed - see terminal";print(exc)
                last_time=time.monotonic()
    finally:
        cap.release();cv2.destroyAllWindows()

if __name__=="__main__": main()


"""YOLO11 ONNX inference via OpenCV; field classes: filled and empty."""
from pathlib import Path
import threading
import cv2
import numpy as np
ROOT=Path(__file__).resolve().parent
COCO="person,bicycle,car,motorcycle,airplane,bus,train,truck,boat,traffic light,fire hydrant,stop sign,parking meter,bench,bird,cat,dog,horse,sheep,cow,elephant,bear,zebra,giraffe,backpack,umbrella,handbag,tie,suitcase,frisbee,skis,snowboard,sports ball,kite,baseball bat,baseball glove,skateboard,surfboard,tennis racket,bottle,wine glass,cup,fork,knife,spoon,bowl,banana,apple,sandwich,orange,broccoli,carrot,hot dog,pizza,donut,cake,chair,couch,potted plant,bed,dining table,toilet,tv,laptop,mouse,remote,keyboard,cell phone,microwave,oven,toaster,sink,refrigerator,book,clock,vase,scissors,teddy bear,hair drier,toothbrush".split(",")
class LabelDetector:
    def __init__(self):
        self.net=None;self.lock=threading.Lock()
        path=ROOT/"models"/"parcel_label.onnx"
        self.names=["parcel_label"]
        if not path.exists():
            path=ROOT/"models"/"yolo11n-coco.onnx";self.names=COCO
        if (ROOT/"models"/"parcel_fields.onnx").exists():
            path=ROOT/"models"/"parcel_fields.onnx";self.names=["filled","empty"]
        self.status="YOLO: model belum tersedia"
        if path.exists():
            try:
                self.net=cv2.dnn.readNetFromONNX(str(path))
                self.status="YOLO11n aktif: objek umum, bukan kelengkapan label" if self.names==COCO else "YOLO11n parcel_label aktif"
                if self.names==["filled","empty"]:self.status="YOLO filled/empty | model prototaip"
            except cv2.error:
                self.status="YOLO: model tidak dapat dibuka"
    def detect(self,frame):
        # Match the training framing when a demo label fills almost the whole image.
        # Only framing changes here; filled/empty and confidence come from YOLO.
        pad_x=pad_y=0
        if self.names==["filled","empty"]:
            from inspection import DICT, PARAMETERS
            corners,ids,_=cv2.aruco.ArucoDetector(DICT,PARAMETERS).detectMarkers(frame)
            if ids is not None and {0,1,2,3}.issubset(set(ids.flatten())):
                points=np.concatenate([c.reshape(-1,2) for c,i in zip(corners,ids.flatten()) if int(i) in (0,1,2,3)])
                h,w=frame.shape[:2]
                if np.ptp(points[:,0])>w*.80 or np.ptp(points[:,1])>h*.90:
                    pad_x,pad_y=round(w*.30),round(h*.30)
        if not pad_x:return self._detect(frame)
        padded=cv2.copyMakeBorder(frame,pad_y,pad_y,pad_x,pad_x,cv2.BORDER_CONSTANT,value=(160,160,160))
        detections=self._detect(padded)
        h,w=frame.shape[:2];mapped=[]
        for detection in detections:
            x,y,bw,bh=detection["box"]
            x1,y1=max(0,x-pad_x),max(0,y-pad_y)
            x2,y2=min(w,x+bw-pad_x),min(h,y+bh-pad_y)
            if x2>x1 and y2>y1:
                detection["box"]=[x1,y1,x2-x1,y2-y1];mapped.append(detection)
        return mapped

    def _detect(self,frame):
        if self.net is None:return []
        threshold=0.65 if self.names==["filled","empty"] else 0.35
        height,width=frame.shape[:2];scale=min(640/width,640/height)
        nw,nh=round(width*scale),round(height*scale)
        left,top=(640-nw)//2,(640-nh)//2
        canvas=np.full((640,640,3),114,np.uint8)
        canvas[top:top+nh,left:left+nw]=cv2.resize(frame,(nw,nh))
        blob=cv2.dnn.blobFromImage(canvas,1/255.,(640,640),swapRB=True,crop=False)
        with self.lock:
            self.net.setInput(blob);output=self.net.forward()
        # YOLO11 exported without NMS: [1, 4 + number_of_classes, anchors].
        if output.ndim!=3 or output.shape[1]!=4+len(self.names):
            raise RuntimeError("Unexpected YOLO output shape; check model classes and export with nms=False.")
        boxes=[];scores=[];classes=[]
        for row in output[0].T:
            cx,cy,bw,bh=row[:4];cls=int(np.argmax(row[4:]));score=float(row[4+cls])
            if score<threshold:continue
            x1=max(0,min(width-1,float((cx-bw/2-left)/scale)))
            y1=max(0,min(height-1,float((cy-bh/2-top)/scale)))
            x2=max(0,min(width,float((cx+bw/2-left)/scale)))
            y2=max(0,min(height,float((cy+bh/2-top)/scale)))
            if x2<=x1 or y2<=y1:continue
            boxes.append([int(x1),int(y1),int(x2-x1),int(y2-y1)]);scores.append(float(score));classes.append(cls)
        keep=[]
        for cls in set(classes):
            indices=[i for i,c in enumerate(classes) if c==cls]
            selected=cv2.dnn.NMSBoxes([boxes[i] for i in indices],[scores[i] for i in indices],threshold,0.45)
            keep.extend(indices[int(j)] for j in np.asarray(selected).flatten())
        if self.names==["filled","empty"]:
            keep=list(np.asarray(cv2.dnn.NMSBoxes(boxes,scores,threshold,0.45)).flatten())
        return [{"class":self.names[classes[i]],"confidence":scores[i],"box":boxes[i]} for i in keep]
    def inspect_fields(self,frame):
        detections=self.detect(frame)
        if self.names!=["filled","empty"]:
            from inspection import inspect
            result,_=inspect(frame);result["detections"]=detections
            return result
        result={"status":"RETAKE","reason":"YOLO: %d/5 medan; tunjuk satu label tegak"%len(detections),"fields":[],"detections":detections,"engine":"YOLO filled/empty"}
        if len(detections)!=5:return result
        ordered=sorted(detections,key=lambda d:d["box"][1]+d["box"][3]/2)
        # Fixed upright template only: five separate rows with similar widths.
        boxes=[d["box"] for d in ordered]
        centers=[y+h/2 for x,y,w,h in boxes]
        if any(centers[i+1]-centers[i]<min(boxes[i][3],boxes[i+1][3])*.5 for i in range(4)):return result
        if max(b[2] for b in boxes)>2*max(1,min(b[2] for b in boxes)):return result
        from inspection import FIELDS
        for (name,_),d in zip(FIELDS,ordered):
            result["fields"].append({"name":name,"state":"FILLED" if d["class"]=="filled" else "EMPTY","confidence":d["confidence"]})
        result["status"]="FAIL" if any(d["class"]=="empty" for d in ordered) else "PASS"
        result["reason"]="YOLO: semua medan berisi" if result["status"]=="PASS" else "YOLO kosong: "+", ".join(r["name"] for r in result["fields"] if r["state"]=="EMPTY")
        return result

def draw(frame,detections):
    image=frame.copy()
    font_scale=max(.7,frame.shape[1]/900.)
    text_width=max(2,round(frame.shape[1]/600))
    for detection in detections:
        x,y,w,h=detection["box"]
        colour=(40,40,230) if detection["class"]=="empty" else (40,210,40)
        cv2.rectangle(image,(x,y),(x+w,y+h),colour,3)
        text="%s %.2f"%(detection["class"],detection["confidence"])
        cv2.putText(image,text,(x,max(22,y-8)),cv2.FONT_HERSHEY_SIMPLEX,font_scale,(20,20,20),text_width+2,cv2.LINE_AA)
        cv2.putText(image,text,(x,max(22,y-8)),cv2.FONT_HERSHEY_SIMPLEX,font_scale,colour,text_width,cv2.LINE_AA)
    return image


from pathlib import Path
import cv2
import numpy as np
from inspection import W,H,MARKERS,FIELDS,DICT
ROOT=Path(__file__).resolve().parent

def make(values):
    img=np.full((H,W,3),255,np.uint8)
    navy=(65,40,20)
    for i,(x,y) in MARKERS.items():
        img[y:y+90,x:x+90]=cv2.cvtColor(cv2.aruco.generateImageMarker(DICT,i,90),cv2.COLOR_GRAY2BGR)
    cv2.putText(img,"PARCEL LABEL",(170,85),cv2.FONT_HERSHEY_SIMPLEX,1.6,navy,3,cv2.LINE_AA)
    cv2.putText(img,"COMPANY: SAMPLE LOGISTICS",(170,135),cv2.FONT_HERSHEY_SIMPLEX,0.8,navy,2,cv2.LINE_AA)
    cv2.putText(img,"FIXED TEMPLATE 01 | CLASS DEMO",(170,174),cv2.FONT_HERSHEY_SIMPLEX,0.65,navy,1,cv2.LINE_AA)
    for name,(x1,y1,x2,y2) in FIELDS:
        labels={"Parcel ID":["Parcel ID"],"Nama penerima":["Nama","penerima"],"Alamat":["Alamat"],"Poskod":["Poskod"],"Tarikh penghantaran":["Tarikh","penghantaran"]}
        lines=labels[name]
        for index,line in enumerate(lines):
            scale=1.08
            width=cv2.getTextSize(line,cv2.FONT_HERSHEY_SIMPLEX,scale,3)[0][0]
            scale*=min(1.0,(x1-66)/max(1,width))
            baseline=y1+42 if len(lines)==1 else y1+23+index*34
            cv2.putText(img,line,(36,baseline),cv2.FONT_HERSHEY_SIMPLEX,scale,(0,0,0),3,cv2.LINE_AA)
        cv2.rectangle(img,(x1-12,y1-12),(x2+12,y2+12),navy,2)
        if values.get(name):
            text=values[name]
            scale=1.35
            text_width=cv2.getTextSize(text,cv2.FONT_HERSHEY_SIMPLEX,scale,3)[0][0]
            scale*=min(1.0,(x2-x1-24)/max(1,text_width))
            cv2.putText(img,text,(x1+10,y1+46),cv2.FONT_HERSHEY_SIMPLEX,scale,(0,0,0),3,cv2.LINE_AA)
    cv2.putText(img,"DEMO ONLY - FICTIONAL DATA",(180,804),cv2.FONT_HERSHEY_SIMPLEX,0.8,navy,2,cv2.LINE_AA)
    cv2.putText(img,"Keep all four corner markers visible",(180,847),cv2.FONT_HERSHEY_SIMPLEX,0.65,navy,1,cv2.LINE_AA)
    return img

VALUES={"Parcel ID":"PKG-000123","Nama penerima":"NAMA CONTOH","Alamat":"12 JALAN DEMO, BANDAR CONTOH","Poskod":"12345","Tarikh penghantaran":"08/09/2026"}
if __name__=="__main__":
    folder=ROOT/"templates";folder.mkdir(exist_ok=True)
    examples={"complete":VALUES,"missing_date":{**VALUES,"Tarikh penghantaran":""},"missing_id_postcode":{**VALUES,"Parcel ID":"","Poskod":""},"blank":{}}
    for name,values in examples.items():
        cv2.imwrite(str(folder/(name+".png")),make(values))
    print("Created four label templates.")


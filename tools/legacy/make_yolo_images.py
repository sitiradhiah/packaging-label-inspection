"""Generate synthetic starter images; real validation images must be collected separately."""

# Locate shared application modules after moving this development script.
import sys
from pathlib import Path
_PROJECT_ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(_PROJECT_ROOT))
if __name__=="__main__":
    import os
    os.chdir(_PROJECT_ROOT)
from pathlib import Path
import csv,json
import cv2
import numpy as np
from make_templates import make,VALUES
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"datasets"/"parcel_label_starter"
rng=np.random.default_rng(830)
def main():
    if OUT.exists():raise SystemExit("Dataset exists. Preserve existing data; choose a new output name.")
    images=OUT/"images"/"train";labels=OUT/"labels"/"train"
    images.mkdir(parents=True);labels.mkdir(parents=True)
    manifest=[];thumbs=[]
    for i in range(120):
        bg=np.full((720,960,3),rng.integers(65,230,size=3),np.float32)
        gradient=np.linspace(float(rng.uniform(.75,1)),float(rng.uniform(1,1.2)),960)[None,:,None]
        bg=np.clip(bg*gradient,0,255).astype(np.uint8)
        # Background props provide simple negative regions, not photorealistic scenes.
        for j in range(3):
            x,y=rng.integers(0,750),rng.integers(0,570)
            cv2.rectangle(bg,(int(x),int(y)),(int(x+120),int(y+90)),tuple(int(v) for v in rng.integers(30,225,3)),-1)
        negative=i>=108
        kind=["complete","missing_date","missing_id_postcode","blank"][i%4]
        annotation=""
        if not negative:
            values=dict(VALUES)
            values["Parcel ID"]=f"PKG-{i+120:06d}"
            if kind=="missing_date":values["Tarikh penghantaran"]=""
            if kind=="missing_id_postcode":values["Parcel ID"]="";values["Poskod"]=""
            if kind=="blank":values={}
            template=make(values)
            width=float(rng.uniform(340,650));height=width*.75
            angle=float(rng.uniform(-22,22))*np.pi/180
            corners=np.float32([[-width/2,-height/2],[width/2,-height/2],[width/2,height/2],[-width/2,height/2]])
            rot=np.float32([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])
            dest=corners@rot.T+rng.uniform(-12,12,(4,2))
            lo=dest.min(axis=0);hi=dest.max(axis=0)
            offset=np.array([rng.uniform(25-lo[0],935-hi[0]),rng.uniform(25-lo[1],695-hi[1])])
            dest=np.float32(dest+offset)
            h=cv2.getPerspectiveTransform(np.float32([[0,0],[1199,0],[1199,899],[0,899]]),dest)
            warped=cv2.warpPerspective(template,h,(960,720))
            mask=cv2.warpPerspective(np.full((900,1200),255,np.uint8),h,(960,720))
            alpha=mask[:,:,None]/255.
            bg=np.uint8(bg*(1-alpha)+warped*alpha)
            lo=dest.min(axis=0);hi=dest.max(axis=0)
            cx,cy=(lo+hi)/2/[960,720];bw,bh=(hi-lo)/[960,720]
            annotation=f"0 {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}\n"
        if i%5==0:bg=cv2.GaussianBlur(bg,(3,3),.7)
        bg=np.uint8(np.clip(bg.astype(np.float32)*rng.uniform(.8,1.1)+rng.normal(0,1.5,bg.shape),0,255))
        stem=f"parcel_{i:03d}"
        cv2.imwrite(str(images/(stem+".jpg")),bg,[cv2.IMWRITE_JPEG_QUALITY,92])
        (labels/(stem+".txt")).write_text(annotation,encoding="utf-8")
        manifest.append({"image":stem+".jpg","type":"negative" if negative else kind,"synthetic":True})
        if i in list(range(0,108,10))+[108]:
            preview=bg.copy()
            if annotation:
                cv2.polylines(preview,[dest.astype(np.int32)],True,(0,190,0),3)
            preview=cv2.resize(preview,(320,240))
            cv2.rectangle(preview,(0,215),(320,240),(245,245,245),-1)
            cv2.putText(preview,stem+" "+("negative" if negative else kind),(7,232),cv2.FONT_HERSHEY_SIMPLEX,.4,(20,20,20),1)
            thumbs.append(preview)
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    (OUT/"classes.txt").write_text("parcel_label\n",encoding="utf-8")
    (OUT/"README.md").write_text("""# Parcel label synthetic starter images
120 synthetic training images: 108 labels (27 each complete, missing date, missing ID/postcode, blank) and 12 backgrounds without labels.
One detection class: 0 = parcel_label. Completeness is NOT a YOLO class in this dataset.
Each JPEG has a matching YOLO TXT: class center_x center_y width height normalized to 0..1. Negative image TXT files are empty.
Dataset includes scale, rotation, perspective, background, brightness, mild blur and noise changes. Images are derived from one fixed template family, not real camera photographs.
All images are training-only. Do not split near-identical generated variants to report camera accuracy. Collect independent real RB3/webcam captures for validation and testing, including negatives.
No model has been trained. No training YAML provided yet because the independent validation set is missing.
Green outlines appear only in contact-sheet preview, never in training images.
""",encoding="utf-8")
    sheet=np.vstack([np.hstack(thumbs[i:i+3]) for i in range(0,12,3)])
    cv2.imwrite(str(OUT/"preview.jpg"),sheet)
    # Check files, decoded images and annotation bounds.
    for entry in manifest:
        path=images/entry["image"]
        assert cv2.imread(str(path)).shape==(720,960,3)
        text=(labels/(path.stem+".txt")).read_text().strip()
        if text:
            cls,x,y,w,h=map(float,text.split())
            assert cls==0 and w>0 and h>0 and x-w/2>=-1e-5 and x+w/2<=1.00001 and y-h/2>=-1e-5 and y+h/2<=1.00001
        else:assert entry["type"]=="negative"
    print("Verified: 120 images, 120 annotations; 108 label samples + 12 negatives.")
if __name__=="__main__":main()

"""Generate synthetic starter images; real validation images must be collected separately."""
from pathlib import Path
import csv,json
import cv2
import numpy as np
from make_templates import make,VALUES
from inspection import FIELDS
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"datasets"/"parcel_fields_v3"
rng=np.random.default_rng(1942)
def main():
    if OUT.exists():raise SystemExit("Dataset exists. Preserve existing data; choose a new output name.")

    manifest=[];thumbs=[]
    for i in range(240):
        split="train" if i<200 else "val"
        images=OUT/"images"/split;labels=OUT/"labels"/split
        images.mkdir(parents=True,exist_ok=True);labels.mkdir(parents=True,exist_ok=True)
        bg=np.full((720,960,3),rng.integers(65,230,size=3),np.float32)
        gradient=np.linspace(float(rng.uniform(.75,1)),float(rng.uniform(1,1.2)),960)[None,:,None]
        bg=np.clip(bg*gradient,0,255).astype(np.uint8)
        # Background props provide simple negative regions, not photorealistic scenes.
        for j in range(3):
            x,y=rng.integers(0,750),rng.integers(0,570)
            cv2.rectangle(bg,(int(x),int(y)),(int(x+120),int(y+90)),tuple(int(v) for v in rng.integers(30,225,3)),-1)
        negative=i%12==11
        kind=["complete","missing_date","missing_id_postcode","blank"][i%4]
        annotation=""
        if not negative:
            values=dict(VALUES)
            values["Parcel ID"]=f"PKG-{i+120:06d}"
            if kind=="missing_date":values["Tarikh penghantaran"]=""
            if kind=="missing_id_postcode":values["Parcel ID"]="";values["Poskod"]=""
            if kind=="blank":values={}
            if i%4==2:
                for name,_ in FIELDS:
                    if rng.random()<.5:values[name]=""
            values=dict(VALUES)
            values["Parcel ID"]=f"PKG-{i+700:06d}"
            for index,(name,_) in enumerate(FIELDS):
                if not (i%32)&(1<<index):values[name]=""
            template=make(values)
            width=float(rng.uniform(460,740));height=width*.75
            angle=float(rng.uniform(-7,7))*np.pi/180
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
            for name,(x1,y1,x2,y2) in FIELDS:
                points=np.float32([[[x1-12,y1-12],[x2+12,y1-12],[x2+12,y2+12],[x1-12,y2+12]]])
                projected=cv2.perspectiveTransform(points,h)[0]
                lo=projected.min(axis=0);hi=projected.max(axis=0)
                cx,cy=(lo+hi)/2/[960,720];bw,bh=(hi-lo)/[960,720]
                cls=0 if values.get(name) else 1
                annotation+=f"{cls} {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}\n"
        if i%5==0:bg=cv2.GaussianBlur(bg,(3,3),.7)
        bg=np.uint8(np.clip(bg.astype(np.float32)*rng.uniform(.8,1.1)+rng.normal(0,1.5,bg.shape),0,255))
        stem=f"parcel_{i:03d}"
        cv2.imwrite(str(images/(stem+".jpg")),bg,[cv2.IMWRITE_JPEG_QUALITY,92])
        (labels/(stem+".txt")).write_text(annotation,encoding="utf-8")
        manifest.append({"image":stem+".jpg","type":"negative" if negative else kind,"synthetic":True,"split":split})
        if i in list(range(0,108,10))+[108]:
            preview=bg.copy()
            if annotation:
                cv2.polylines(preview,[dest.astype(np.int32)],True,(0,190,0),3)
            preview=cv2.resize(preview,(320,240))
            cv2.rectangle(preview,(0,215),(320,240),(245,245,245),-1)
            cv2.putText(preview,stem+" "+("negative" if negative else kind),(7,232),cv2.FONT_HERSHEY_SIMPLEX,.4,(20,20,20),1)
            thumbs.append(preview)
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    (OUT/"data.yaml").write_text("path: "+OUT.as_posix()+"\ntrain: images/train\nval: images/val\nnames:\n  0: filled\n  1: empty\n",encoding="utf-8")
    (OUT/"README.md").write_text("Synthetic-only prototype: 200 train / 40 validation scenes from one template family. Validation is for training diagnostics, NOT evidence of real camera accuracy. Classes 0 filled, 1 empty. 20 negative images. Need independent real-world test data.",encoding="utf-8")
    for entry in manifest:
        label=OUT/"labels"/entry["split"]/(Path(entry["image"]).stem+".txt")
        rows=label.read_text().splitlines()
        assert len(rows)==(0 if entry["type"]=="negative" else 5)
        for row in rows:
            cls,x,y,w,h=map(float,row.split())
            assert cls in (0,1) and 0<x<1 and 0<y<1 and 0<w<1 and 0<h<1
    print("240 synthetic images and field annotations verified.")
if __name__=="__main__":main()


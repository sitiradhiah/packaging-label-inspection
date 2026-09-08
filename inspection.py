"""Fixed-template field occupancy inspection; no OCR."""
import cv2
import numpy as np

W,H = 1200,900
MARKERS = {0:(30,30),1:(1080,30),2:(1080,780),3:(30,780)}
FIELDS = [(name,(340, y+12,1035,y+80)) for name,y in
          [("Parcel ID",205),("Nama penerima",310),("Alamat",415),("Poskod",520),("Tarikh penghantaran",625)]]
DICT = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
PARAMETERS = cv2.aruco.DetectorParameters()
PARAMETERS.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
DETECTOR = cv2.aruco.ArucoDetector(DICT, PARAMETERS)

def inspect(image):
    corners,ids,_ = DETECTOR.detectMarkers(image)
    if ids is None:
        return {"status":"RETAKE","reason":"Show all four corner markers","fields":[]},None
    found = {int(i):c.reshape(4,2) for i,c in zip(ids.flatten(),corners)}
    if not all(i in found for i in MARKERS):
        return {"status":"RETAKE","reason":"Only %d/4 markers detected; enlarge label / avoid glare" % sum(i in found for i in MARKERS),"fields":[]},None
    source=[]; target=[]
    for i,(x,y) in MARKERS.items():
        source.extend(found[i])
        target.extend([(x,y),(x+89,y),(x+89,y+89),(x,y+89)])
    source=np.float32(source); target=np.float32(target)
    inverse,mask=cv2.findHomography(target,source,cv2.RANSAC,3)
    if inverse is None or mask is None or int(mask.sum())<14:
        return {"status":"RETAKE","reason":"Alignment uncertain","fields":[]},None
    hom=np.linalg.inv(inverse)
    outline=cv2.perspectiveTransform(np.float32([[[0,0],[W-1,0],[W-1,H-1],[0,H-1]]]),inverse)[0]
    ih,iw=image.shape[:2]
    if not cv2.isContourConvex(outline) or np.any(outline[:,0]<-5) or np.any(outline[:,0]>iw+5) or np.any(outline[:,1]<-5) or np.any(outline[:,1]>ih+5):
        return {"status":"RETAKE","reason":"Keep whole label inside camera","fields":[]},None
    if cv2.contourArea(outline)<220000:
        return {"status":"RETAKE","reason":"Label too small (%d%% of required pixels); enlarge on phone or use larger print" % (100*cv2.contourArea(outline)/220000),"fields":[]},None
    flat=cv2.warpPerspective(image,hom,(W,H),borderValue=(255,255,255))
    gray=cv2.cvtColor(flat,cv2.COLOR_BGR2GRAY)
    # Evaluate known printed detail, not the mostly blank label background.
    marker_sharpness=[cv2.Laplacian(gray[y:y+90,x:x+90],cv2.CV_64F).var() for x,y in MARKERS.values()]
    if min(marker_sharpness)<75:
        return {"status":"RETAKE","reason":"Image blurred; hold steady","fields":[]},flat
    rows=[]
    for name,(x1,y1,x2,y2) in FIELDS:
        crop=gray[y1:y2,x1:x2]
        if np.median(crop)<125:
            return {"status":"RETAKE","reason":"Lighting too dark","fields":[]},flat
        # Local background normalization suppresses gentle shadows.
        background=cv2.GaussianBlur(crop,(0,0),9)
        ink=((background.astype(np.int16)-crop.astype(np.int16)>28)&(crop<180)).astype(np.uint8)*255
        count,labels,stats,_=cv2.connectedComponentsWithStats(ink,8)
        area=sum(int(s[cv2.CC_STAT_AREA]) for s in stats[1:] if s[cv2.CC_STAT_AREA]>=10 and s[cv2.CC_STAT_HEIGHT]>=4)
        ratio=area/crop.size
        state="FILLED" if ratio>=0.008 else ("EMPTY" if ratio<=0.002 else "UNCERTAIN")
        rows.append({"name":name,"state":state,"ink_ratio":round(ratio,5)})
    status="RETAKE" if any(r["state"]=="UNCERTAIN" for r in rows) else ("PASS" if all(r["state"]=="FILLED" for r in rows) else "FAIL")
    reason="Unclear marks; retake" if status=="RETAKE" else ("All fields contain marks" if status=="PASS" else "Empty: "+", ".join(r["name"] for r in rows if r["state"]=="EMPTY"))
    return {"status":status,"reason":reason,"fields":rows},flat


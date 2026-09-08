"""Run inference through the actual dashboard model; synthetic smoke checks only."""
import json,time
from pathlib import Path
import cv2,numpy as np
from yolo_detector import LabelDetector,draw
from inspection import FIELDS
ROOT=Path(__file__).resolve().parent
if __name__=='__main__':
 detector=LabelDetector()
 assert detector.net is not None and detector.names==['filled','empty'],detector.status
 expected={'complete.png':['FILLED']*5,'missing_date.png':['FILLED']*4+['EMPTY'],'missing_id_postcode.png':['EMPTY','FILLED','FILLED','EMPTY','FILLED'],'blank.png':['EMPTY']*5}
 reports=[]
 for file,states in expected.items():
  image=cv2.imread(str(ROOT/'templates'/file));start=time.perf_counter()
  result=detector.inspect_fields(image)
  elapsed=time.perf_counter()-start
  actual=[r['state'] for r in result['fields']]
  ok=actual==states
  reports.append({'image':file,'expected':states,'actual':actual,'status':result['status'],'passed':ok,'seconds':round(elapsed,3),'detections':result['detections']})
  cv2.imwrite(str(ROOT/'work'/('yolo-'+file)),draw(image,result['detections']))
  print(file,ok,result['status'],actual,flush=True)
 image=cv2.imread(str(ROOT/'work/current-diagnostic.jpg'))
 if image is not None:
  result=detector.inspect_fields(image)
  reports.append({'image':'saved camera frame','status':result['status'],'actual':[r['state'] for r in result['fields']],'detections':result['detections']})
  print('saved camera frame',result['status'],reports[-1]['actual'],flush=True)
 negative=detector.inspect_fields(np.full((720,960,3),160,np.uint8))
 assert negative['status']=='RETAKE',negative
 (ROOT/'work/field-model-verification.json').write_text(json.dumps(reports,indent=2))
 assert all(r['passed'] for r in reports if 'passed' in r), 'Demo checks failed; see report'
 print('MODEL DEMO CHECKS PASS (not independent real-world accuracy)')

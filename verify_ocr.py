import cv2,json,time
from pathlib import Path
from yolo_detector import LabelDetector
from ocr_reader import read_fields
from make_templates import VALUES
if __name__=='__main__':
 d=LabelDetector();report=[]
 for file in ['complete.png','missing_date.png','missing_id_postcode.png','blank.png']:
  im=cv2.imread('templates/'+file);start=time.perf_counter();r=read_fields(im,d.inspect_fields(im))
  actual={f['name']:f['text'] for f in r['fields']}
  expected=dict(VALUES)
  if file=='missing_date.png':expected['Tarikh penghantaran']=''
  if file=='missing_id_postcode.png':expected['Parcel ID']='';expected['Poskod']=''
  if file=='blank.png':expected={k:'' for k in VALUES}
  ok=actual==expected;report.append({'file':file,'ocr':r,'passed':ok,'seconds':round(time.perf_counter()-start,2)})
  print(file,ok,actual,report[-1]['seconds'],flush=True)
 im=cv2.imread('work/current-diagnostic.jpg')
 if im is not None:
  r=read_fields(im,d.inspect_fields(im));report.append({'file':'saved camera','ocr':r});print('camera',r,flush=True)
 Path('work/ocr-verification.json').write_text(json.dumps(report,indent=2))
 assert all(r['passed'] for r in report if 'passed' in r)

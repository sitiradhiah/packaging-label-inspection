from pathlib import Path
import cv2,json
from make_templates import make,VALUES
from inspection import FIELDS
from yolo_detector import LabelDetector
if __name__=='__main__':
 d=LabelDetector();rows=[]
 for mask in range(32):
  values={name:VALUES[name] for i,(name,_) in enumerate(FIELDS) if mask&(1<<i)}
  expected=['FILLED' if mask&(1<<i) else 'EMPTY' for i in range(5)]
  r=d.inspect_fields(make(values));actual=[f['state'] for f in r['fields']]
  rows.append({'combination':mask,'expected':expected,'actual':actual,'passed':actual==expected})
 Path('work/combination-verification.json').write_text(json.dumps(rows,indent=2))
 print('Synthetic combinations correct:',sum(r['passed'] for r in rows),'/ 32')
 print('Failed combinations:',[r['combination'] for r in rows if not r['passed']])

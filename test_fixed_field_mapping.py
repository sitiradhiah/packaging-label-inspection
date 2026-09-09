import unittest
import numpy as np
from make_templates import make,VALUES
from inspection import FIELDS
from yolo_detector import LabelDetector
from ocr_reader import read_fields
class FixedFieldMapping(unittest.TestCase):
 def test_missing_middle_field_does_not_shift_names(self):
  frame=make(VALUES)
  frame[200:730,20:320]=255 # Remove all headings, preserve markers and field contents.
  d=LabelDetector.__new__(LabelDetector);d.names=['filled','empty']
  detections=[]
  for i,(_, (x1,y1,x2,y2)) in enumerate(FIELDS):
   if i==1:continue
   detections.append({'class':'filled','confidence':.9,'box':[x1,y1,x2-x1,y2-y1]})
  d.detect=lambda image:detections
  result=d.inspect_fields(frame)
  self.assertEqual(result['status'],'RETAKE')
  self.assertEqual([r['name'] for r in result['fields']],[name for name,_ in FIELDS])
  self.assertEqual(result['fields'][1],{'name':'Nama penerima','state':'NOT_DETECTED'})
  self.assertEqual(result['fields'][2]['state'],'FILLED')
  ocr=read_fields(frame,result)
  self.assertEqual({r['name']:r['text'] for r in ocr['fields']},VALUES)
if __name__=='__main__':unittest.main()

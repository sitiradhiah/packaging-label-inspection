import unittest
import numpy as np
from yolo_detector import LabelDetector

class ResultRules(unittest.TestCase):
 def model(self,classes):
  detector=LabelDetector.__new__(LabelDetector);detector.names=['filled','empty']
  detector.detect=lambda frame:[{'class':name,'confidence':.8,'box':[100,50+i*90,300,60]} for i,name in enumerate(classes)]
  return detector
 def test_missing_detection_is_not_empty(self):
  result=self.model(['filled']*4).inspect_fields(np.zeros((1,1,3),np.uint8))
  self.assertEqual(result['status'],'RETAKE')
 def test_empty_detection_fails(self):
  result=self.model(['filled']*4+['empty']).inspect_fields(np.zeros((1,1,3),np.uint8))
  self.assertEqual(result['status'],'FAIL')
  self.assertEqual(result['fields'][-1]['state'],'EMPTY')
 def test_full_label_passes(self):
  self.assertEqual(self.model(['filled']*5).inspect_fields(np.zeros((1,1,3),np.uint8))['status'],'PASS')
 def test_extra_fields_require_retake(self):
  self.assertEqual(self.model(['filled']*6).inspect_fields(np.zeros((1,1,3),np.uint8))['status'],'RETAKE')
if __name__=='__main__':unittest.main()

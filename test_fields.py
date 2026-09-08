import unittest
import cv2
import numpy as np
from inspection import inspect,FIELDS,W,H
from make_templates import make,VALUES

class FieldTests(unittest.TestCase):
    def test_complete(self):
        self.assertEqual(inspect(make(VALUES))[0]["status"],"PASS")
    def test_each_field_missing(self):
        for name,_ in FIELDS:
            result,_=inspect(make({**VALUES,name:""}))
            self.assertEqual(result["status"],"FAIL",name)
            self.assertEqual(next(r["state"] for r in result["fields"] if r["name"]==name),"EMPTY")
    def test_blank(self):
        r,_=inspect(make({}))
        self.assertEqual(r["status"],"FAIL")
        self.assertTrue(all(f["state"]=="EMPTY" for f in r["fields"]))
    def test_no_label(self):
        self.assertEqual(inspect(np.full((900,1200,3),255,np.uint8))[0]["status"],"RETAKE")
    def test_blurred(self):
        self.assertEqual(inspect(cv2.GaussianBlur(make(VALUES),(51,51),15))[0]["status"],"RETAKE")
    def test_perspective(self):
        transform=cv2.getPerspectiveTransform(np.float32([[0,0],[1199,0],[1199,899],[0,899]]),np.float32([[100,80],[1100,120],[1070,820],[130,800]]))
        moved=cv2.warpPerspective(make(VALUES),transform,(1200,900),borderValue=(190,190,190))
        self.assertEqual(inspect(moved)[0]["status"],"PASS")
    def test_small(self):
        self.assertEqual(inspect(cv2.resize(make(VALUES),(480,360)))[0]["status"],"RETAKE")
if __name__=="__main__":unittest.main()


"""Test actual image, JSON and CSV writes including Unicode Windows folders."""
import csv,json,tempfile,unittest
from pathlib import Path
import cv2,numpy as np
import app
class SaveRecords(unittest.TestCase):
 def test_image_json_csv_and_ocr_export(self):
  original=app.ROOT
  try:
   with tempfile.TemporaryDirectory() as tmp:
    for name in ['normal','folder with spaces','label_\u6d4b\u8bd5_\u00e9']:
     app.ROOT=Path(tmp)/name;app.ROOT.mkdir()
     image=np.full((64,96,3),180,np.uint8)
     result={'status':'PASS','reason':'test','fields':[], 'ocr':{'status':'ok','fields':[{'name':'Parcel ID','text':'PKG-0123'},{'name':'Nama penerima','text':'NAMA CONTOH'}]}}
     app.save(result,image)
     folder=app.ROOT/'results_fields'
     with (folder/'inspections.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
     self.assertEqual(len(rows),1);self.assertEqual(rows[0]['Parcel ID'],'PKG-0123')
     photo=folder/rows[0]['image']
     decoded=cv2.imdecode(np.frombuffer(photo.read_bytes(),np.uint8),cv2.IMREAD_COLOR)
     self.assertEqual(decoded.shape,image.shape)
     record=json.loads(photo.with_suffix('.json').read_text(encoding='utf-8'))
     self.assertEqual(record['ocr'],result['ocr'])
     with app.export_ocr_csv().open(encoding='utf-8-sig',newline='') as f:export=list(csv.DictReader(f))
     self.assertEqual(export[0]['Nama penerima'],'NAMA CONTOH')
  finally:app.ROOT=original
if __name__=='__main__':unittest.main()

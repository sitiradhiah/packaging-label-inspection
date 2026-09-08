"""Actual automatic OCR integration, no camera and no real history writes."""
import time,tkinter as tk
import cv2,numpy as np
import dashboard
root=tk.Tk();app=dashboard.Dashboard(root,rb3=False);root.geometry('900x680');root.update()
saved=[];dashboard.save=lambda result,frame:saved.append((result,frame.copy()))
def wait_for(test):
 end=time.monotonic()+35
 while not test() and time.monotonic()<end:root.update();time.sleep(.02)
 assert test(),'Timed out'
try:
 full=cv2.imread('templates/complete.png');blank=cv2.imread('templates/blank.png')
 app.show(full,app.detector.inspect_fields(full))
 # No CHECK call: poll must start OCR and populate the combined fields.
 wait_for(lambda:app.ocr_values['Parcel ID'].get()=='PKG-000123')
 assert not saved,'Live OCR must not write history'
 app.clear_ocr();app.show(blank,app.detector.inspect_fields(blank))
 wait_for(lambda:all(v.get()=='Tiada teks dapat dibaca' for v in app.ocr_values.values()))
 app.clear_ocr();app.show(full,app.detector.inspect_fields(full));app.record()
 app.frame=blank.copy()
 wait_for(lambda:len(saved)==1)
 assert np.array_equal(saved[0][1],full)
 assert saved[0][0]['ocr']['fields'][0]['text']=='PKG-000123'
 root.update_idletasks()
 assert app.table.winfo_rooty()+app.table.winfo_height()<=root.winfo_rooty()+root.winfo_height()
 assert app.check_button.winfo_rooty()+app.check_button.winfo_height()<app.table.winfo_rooty()
 app.clear_ocr();assert all(v.get()=='Menunggu bacaan...' for v in app.ocr_values.values())
 print('PASS: automatic full-to-blank OCR, no automatic saves, exact saved snapshot, clearing and compact layout')
finally:
 app.frame=None;app.result=None;app.close()
 while app.ocr_busy:root.update();time.sleep(.02)

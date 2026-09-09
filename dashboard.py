"""Desktop dashboard. OpenCV processes images; Tkinter displays controls."""
import argparse
import base64
import csv
import copy
import os
import queue
import threading
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
from inspection import inspect, FIELDS
from app import save, export_ocr_csv
from ocr_reader import read_fields
from yolo_detector import LabelDetector, draw

ROOT=Path(__file__).resolve().parent
COLOURS={"PASS":"#15805b","FAIL":"#c34848","RETAKE":"#a66d16"}
class Dashboard:
    def __init__(self,root,camera=0,rb3=True):
        self.root=root;self.camera=camera;self.rb3=rb3
        self.detector=LabelDetector()
        self.frame=None;self.result=None;self.photo=None
        self.stop_event=None;self.worker=None;self.events=queue.Queue(maxsize=2)
        self.last_save=0;self.closing=False
        self.ocr_busy=False;self.ocr_events=queue.Queue();self.ocr_generation=0
        self.ocr_due=0;self.save_pending=None;self.saving=False
        root.title("Parcel Label Checker Dashboard Using OpenCV")
        root.geometry("%dx%d"%(min(1180,root.winfo_screenwidth()-80),min(820,root.winfo_screenheight()-100)))
        root.minsize(640,480);root.configure(bg="#edf2f7")
        style=ttk.Style();style.theme_use("clam")
        style.configure("TFrame",background="#edf2f7")
        style.configure("TLabel",background="#edf2f7",foreground="#18324d",font=("Segoe UI",10))
        style.configure("Title.TLabel",font=("Segoe UI",21,"bold"))
        style.configure("TButton",font=("Segoe UI",10),padding=8)
        style.configure("Treeview",rowheight=27,font=("Segoe UI",9))
        outer=ttk.Frame(root);outer.pack(fill="both",expand=True)
        outer.rowconfigure(0,weight=1);outer.columnconfigure(0,weight=1)
        self.page=tk.Canvas(outer,bg="#edf2f7",highlightthickness=0)
        self.page.grid(row=0,column=0,sticky="nsew")
        vertical=ttk.Scrollbar(outer,orient="vertical",command=self.page.yview)
        vertical.grid(row=0,column=1,sticky="ns")
        horizontal=ttk.Scrollbar(outer,orient="horizontal",command=self.page.xview)
        horizontal.grid(row=1,column=0,sticky="ew")
        self.page.configure(yscrollcommand=vertical.set,xscrollcommand=horizontal.set)
        shell=ttk.Frame(self.page,padding=12)
        self.page_window=self.page.create_window(0,0,window=shell,anchor="nw")
        self.shell=shell

        shell.columnconfigure(0,weight=1);shell.rowconfigure(3,weight=1)
        ttk.Label(shell,text="Parcel Label Checker Dashboard",style="Title.TLabel").grid(row=0,column=0,sticky="w")
        ttk.Label(shell,text="YOLO + OpenCV  |  Filled / Empty + confidence  |  Baca teks dengan OCR").grid(row=1,column=0,sticky="w",pady=(2,8))
        cards=ttk.Frame(shell);cards.grid(row=2,column=0,sticky="ew")
        self.metrics={}
        for i,(key,label) in enumerate([("TOTAL","JUMLAH"),("PASS","PASS"),("FAIL","FAIL"),("RETAKE","RETAKE")]):
            cards.columnconfigure(i,weight=1)
            card=tk.Frame(cards,bg="white",padx=14,pady=8);card.grid(row=0,column=i,sticky="ew",padx=(0,8))
            tk.Label(card,text=label,bg="white",fg="#596b7e",font=("Segoe UI",9)).pack(anchor="w")
            var=tk.StringVar(value="0");self.metrics[key]=var
            tk.Label(card,textvariable=var,bg="white",fg=COLOURS.get(key,"#18324d"),font=("Segoe UI",22,"bold")).pack(anchor="w")
        body=ttk.Frame(shell);body.grid(row=3,column=0,sticky="nsew",pady=8)
        body.columnconfigure(0,weight=3,uniform="body");body.columnconfigure(1,weight=2,uniform="body");body.rowconfigure(0,weight=1)
        left=ttk.Frame(body);left.grid(row=0,column=0,sticky="nsew",padx=(0,16))
        viewport=tk.Frame(left,bg="#142d45",height=260)
        viewport.pack(fill="both",expand=True)
        viewport.pack_propagate(False)
        self.preview=tk.Label(viewport,text="Klik Mula RB3 atau Buka Gambar Demo" if self.rb3 else "Klik Mula Webcam atau Buka Gambar Demo",bg="#142d45",fg="white",font=("Segoe UI",12))
        self.preview.place(x=0,y=0,relwidth=1,relheight=1)
        camera_row=ttk.Frame(left);camera_row.pack(fill="x",pady=(6,0))
        ttk.Label(camera_row,text="Kamera:").pack(side="left",padx=(0,8))
        self.camera_choice=tk.StringVar(value="Qualcomm RB3 USB" if self.rb3 else "Built-in Webcam")
        self.camera_selector=ttk.Combobox(camera_row,textvariable=self.camera_choice,values=("Qualcomm RB3 USB","Built-in Webcam"),state="readonly",width=23)
        self.camera_selector.pack(side="left")
        self.camera_selector.bind("<<ComboboxSelected>>",self.select_camera)
        buttons=ttk.Frame(left);buttons.pack(fill="x",pady=(6,0))
        self.start_button=ttk.Button(buttons,text="Mula RB3" if self.rb3 else "Mula Webcam",command=self.start);self.start_button.pack(side="left")
        self.stop_button=ttk.Button(buttons,text="Henti",command=self.stop,state="disabled");self.stop_button.pack(side="left",padx=5)
        self.load_button=ttk.Button(buttons,text="Buka Gambar Demo",command=self.load);self.load_button.pack(side="left")
        right=ttk.Frame(body);right.grid(row=0,column=1,sticky="nsew")
        self.source=tk.StringVar(value="Sumber: belum dipilih")
        ttk.Label(right,textvariable=self.source).pack(anchor="w")
        self.badge=tk.Label(right,text="READY",bg="#dce5ef",fg="#18324d",font=("Segoe UI",20,"bold"),pady=4)
        self.badge.pack(fill="x",pady=4)
        self.reason=tk.StringVar(value="Letakkan keseluruhan label dan empat penanda dalam kamera.")
        ttk.Label(right,textvariable=self.reason,wraplength=345).pack(anchor="w",pady=(0,10))
        self.ocr_message=tk.StringVar(value="OCR automatik: menunggu gambar label.")
        ttk.Label(right,textvariable=self.ocr_message,wraplength=345).pack(anchor="w")
        panel=ttk.Frame(right,height=160);panel.pack(fill="both",expand=True,pady=3);panel.pack_propagate(False)
        canvas=tk.Canvas(panel,bg="#edf2f7",highlightthickness=0,height=160)
        scroll=ttk.Scrollbar(panel,orient="vertical",command=canvas.yview)
        scroll.pack(side="right",fill="y");canvas.pack(side="left",fill="both",expand=True)
        canvas.configure(yscrollcommand=scroll.set)
        state_panel=ttk.Frame(canvas);window=canvas.create_window(0,0,window=state_panel,anchor="nw")
        state_panel.bind("<Configure>",lambda e:canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",lambda e:canvas.itemconfigure(window,width=e.width))
        self.states={};self.ocr_values={}
        for name,_ in FIELDS:
            row=ttk.Frame(state_panel);row.pack(fill="x",pady=(1,3))
            heading=ttk.Frame(row);heading.pack(fill="x")
            ttk.Label(heading,text=name).pack(side="left")
            var=tk.StringVar(value="Belum diperiksa");self.states[name]=var
            ttk.Label(heading,textvariable=var).pack(side="right")
            value=tk.StringVar(value="Menunggu bacaan...");self.ocr_values[name]=value
            ttk.Entry(row,textvariable=value,state="readonly").pack(fill="x")
        self.check_button=ttk.Button(right,text="CHECK & SIMPAN",command=self.record,state="disabled")
        self.check_button.pack(fill="x",pady=(6,3))
        ttk.Label(right,text="PASS = ada tanda, bukan pengesahan isi betul.",wraplength=345).pack(anchor="w")
        ttk.Label(shell,text="SEJARAH PEMERIKSAAN TERSIMPAN (klik dua kali untuk gambar)").grid(row=4,column=0,sticky="w")
        table_frame=ttk.Frame(shell);table_frame.grid(row=5,column=0,sticky="ew",pady=4)
        self.table=ttk.Treeview(table_frame,columns=("time","status","reason","image"),show="headings",height=4)
        for name,label,width in [("time","Masa",180),("status","Keputusan",85),("reason","Butiran",490),("image","Gambar",180)]:
            self.table.heading(name,text=label);self.table.column(name,width=width,minwidth=60)
        self.table.pack(side="left",fill="x",expand=True)
        scroll=ttk.Scrollbar(table_frame,orient="vertical",command=self.table.yview);scroll.pack(side="right",fill="y")
        self.table.configure(yscrollcommand=scroll.set)
        self.table.bind("<Double-1>",self.open_record)
        footer=ttk.Frame(shell);footer.grid(row=6,column=0,sticky="ew")
        self.notice=tk.StringVar(value="Klik dua kali rekod untuk buka gambar. Kamera belum diaktifkan.")
        footer.columnconfigure(0,weight=1)
        actions=ttk.Frame(footer);actions.grid(row=0,column=0,sticky="w")
        self.excel_button=ttk.Button(actions,text="Buka Excel (OCR)",command=self.open_excel)
        self.excel_button.pack(side="left",padx=(0,5))
        self.folder_button=ttk.Button(actions,text="Folder Keputusan",command=self.open_folder)
        self.folder_button.pack(side="left")
        notice_label=ttk.Label(footer,textvariable=self.notice,wraplength=700)
        notice_label.grid(row=1,column=0,sticky="w",pady=(4,0))
        def fit_page(event=None):
            # Preserve each column's requested size; scroll instead of clipping controls.
            minimum_width=max(shell.winfo_reqwidth(),int(left.winfo_reqwidth()*5/3)+44,int(right.winfo_reqwidth()*5/2)+44)
            width=max(self.page.winfo_width(),minimum_width)
            height=max(self.page.winfo_height(),shell.winfo_reqheight())
            self.page.itemconfigure(self.page_window,width=width,height=height)
            self.page.configure(scrollregion=(0,0,width,height))
            notice_label.configure(wraplength=max(300,width-30))
        self.page.bind("<Configure>",fit_page)
        shell.bind("<Configure>",fit_page)

        self.refresh_history()
        root.protocol("WM_DELETE_WINDOW",self.close)
        root.after(33,self.poll)

    def refresh_history(self):
        rows=[];path=ROOT/"results_fields"/"inspections.csv"
        if path.exists():
            try:
                with path.open(newline="",encoding="utf-8-sig") as f: rows=list(csv.DictReader(f))
            except (OSError,csv.Error) as exc:
                self.notice.set("Sejarah tidak dapat dibaca: "+str(exc))
        for key,var in self.metrics.items():
            var.set(str(len(rows) if key=="TOTAL" else sum(r.get("status")==key for r in rows)))
        self.table.delete(*self.table.get_children())
        for r in reversed(rows[-200:]):
            self.table.insert("","end",values=(r.get("time",""),r.get("status",""),r.get("reason",""),r.get("image","")))

    def emit(self,item):
        try:self.events.put_nowait(item)
        except queue.Full:
            try:self.events.get_nowait()
            except queue.Empty:pass
            try:self.events.put_nowait(item)
            except queue.Full:pass

    def capture(self,event):
        cap=None
        try:
            if self.rb3:
                from rb3_camera import RB3Camera
                cap=RB3Camera()
            else:
                cap=cv2.VideoCapture(self.camera,cv2.CAP_DSHOW)
                if not cap.isOpened():
                    cap.release();cap=cv2.VideoCapture(self.camera)
                if not cap.isOpened():raise RuntimeError("Webcam tidak tersedia. Tutup aplikasi kamera lain.")
                cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280);cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
            checked_at=0;result=None
            while not event.is_set():
                ok,frame=cap.read()
                if not ok:raise RuntimeError("Bacaan webcam terhenti.")
                updated=False
                if result is None or time.monotonic()-checked_at>=0.30:
                    result=self.detector.inspect_fields(frame)
                    checked_at=time.monotonic();updated=True
                if self.detector.net is None or updated:
                    self.emit(("frame",frame,result))
        except Exception as exc:self.emit(("error",str(exc),None))
        finally:
            if cap is not None:cap.release()

    def select_camera(self,event=None):
        if self.worker and self.worker.is_alive():return
        self.rb3=self.camera_choice.get()=="Qualcomm RB3 USB"
        self.clear_ocr()
        self.frame=None;self.result=None;self.photo=None
        self.check_button.configure(state="disabled")
        self.start_button.configure(text="Mula RB3" if self.rb3 else "Mula Webcam")
        self.preview.configure(image="",text="Klik Mula untuk " + self.camera_choice.get())
        self.source.set("Sumber dipilih: " + self.camera_choice.get())
        self.badge.configure(text="READY",bg="#dce5ef",fg="#18324d")
        self.reason.set("Klik Mula untuk aktifkan kamera pilihan.")
        for var in self.states.values():var.set("Belum diperiksa")
        self.notice.set("Kamera ditukar. Hentikan kamera sebelum memilih sumber lain.")

    def start(self):
        if self.worker and self.worker.is_alive():return
        while not self.events.empty():
            try:self.events.get_nowait()
            except queue.Empty:break
        self.clear_ocr()
        self.frame=None;self.result=None;self.check_button.configure(state="disabled")
        self.rb3=self.camera_choice.get()=="Qualcomm RB3 USB"
        self.camera_selector.configure(state="disabled")
        self.stop_event=threading.Event()
        self.worker=threading.Thread(target=self.capture,args=(self.stop_event,),daemon=True)
        self.start_button.configure(state="disabled");self.load_button.configure(state="disabled");self.stop_button.configure(state="normal")
        self.source.set("Sumber: Qualcomm RB3 USB" if self.rb3 else "Sumber: webcam langsung")
        self.notice.set("Connecting Qualcomm RB3 over USB..." if self.rb3 else "Membuka webcam...")
        self.worker.start()

    def stop(self):
        if self.stop_event:self.stop_event.set()
        self.clear_ocr()
        self.frame=None;self.result=None;self.check_button.configure(state="disabled")
        self.badge.configure(text="STOPPED",bg="#dce5ef",fg="#18324d")
        self.reason.set("Kamera dihentikan. Pilih kamera lain atau buka gambar.")
        for var in self.states.values():var.set("Belum diperiksa")
        self.preview.configure(image="",text="Webcam dihentikan");self.photo=None
        self.stop_button.configure(state="disabled")

    def show(self,frame,result):
        self.frame=frame;self.result=result
        # Fit without stretching the camera image.
        width=max(1,min(720,self.preview.winfo_width()-4));height=max(1,min(360,self.preview.winfo_height()-4))
        scale=min(width/frame.shape[1],height/frame.shape[0])
        small=cv2.resize(draw(frame,result.get("detections",[])),(max(1,int(frame.shape[1]*scale)),max(1,int(frame.shape[0]*scale))))
        rgb=cv2.cvtColor(small,cv2.COLOR_BGR2RGB)
        ppm=("P6\n%d %d\n255\n" % (rgb.shape[1],rgb.shape[0])).encode()+rgb.tobytes()
        self.photo=tk.PhotoImage(data=ppm,format="PPM")
        self.preview.configure(image=self.photo,text="")
        status=result["status"];self.badge.configure(text=status,bg=COLOURS[status],fg="white")
        self.reason.set(result["reason"]+" | "+self.detector.status)
        states={r["name"]:r["state"] for r in result["fields"]}
        words={"FILLED":"Berisi","EMPTY":"Kosong","UNCERTAIN":"Tidak pasti"}
        for name,var in self.states.items():
            row=next((r for r in result["fields"] if r["name"]==name),{})
            label=words.get(states.get(name),"Belum diperiksa")
            if "confidence" in row:label+=" %.2f"%row["confidence"]
            var.set(label)
        self.check_button.configure(state="disabled" if self.save_pending or self.saving else "normal")

    def load(self):
        path=filedialog.askopenfilename(initialdir=ROOT/"templates",filetypes=[("Images","*.png *.jpg *.jpeg *.bmp")])
        if not path:return
        try:
            # Unicode-safe Windows image loading.
            import numpy as np
            frame=cv2.imdecode(np.fromfile(path,dtype=np.uint8),cv2.IMREAD_COLOR)
            if frame is None:raise ValueError("Gambar tidak dapat dibaca")
            result=self.detector.inspect_fields(frame)
            self.clear_ocr()
            self.source.set("Sumber: gambar demo")
            self.show(frame,result);self.notice.set(Path(path).name)
        except Exception as exc:messagebox.showerror("Gambar",str(exc))

    def clear_ocr(self):
        self.ocr_generation+=1;self.ocr_due=0
        self.ocr_message.set("OCR automatik: menunggu gambar label.")
        for var in self.ocr_values.values():var.set("Menunggu bacaan...")

    def record(self):
        if self.frame is None or self.result is None or self.save_pending or self.saving:return
        if time.monotonic()-self.last_save<1:return
        self.save_pending=(self.frame.copy(),copy.deepcopy(self.result),self.source.get(),self.ocr_generation,time.strftime("%H:%M:%S"))
        self.check_button.configure(state="disabled")
        self.notice.set("Sedang menyediakan rekod gambar ini...")

    def launch_ocr(self,job,is_save=False):
        frame,result,source,generation,captured_at=job
        self.ocr_busy=True;self.saving=is_save
        self.ocr_message.set("OCR sedang membaca... (automatik)")
        def work():
            try:
                try:result['ocr']=read_fields(frame,result)
                except Exception as exc:result['ocr']={'status':'error','message':str(exc),'fields':[]}
                result['ocr']['captured_at']=captured_at
                if is_save:
                    result['reason']="["+source.replace("Sumber: ","")+"] "+result['reason']
                    save(result,frame)
                self.ocr_events.put((generation,result,None,is_save))
            except Exception as exc:self.ocr_events.put((generation,None,str(exc),is_save))
        threading.Thread(target=work,daemon=True).start()

    def finish_ocr(self,result):
        ocr=result['ocr']
        self.ocr_message.set("OCR "+ocr['captured_at']+" | "+("Bacaan automatik" if ocr['status']=='ok' else ocr['message']))
        texts={r['name']:r['text'] for r in ocr['fields']}
        for name,var in self.ocr_values.items():
            var.set((texts.get(name) or "Tiada teks dapat dibaca") if ocr['status']=='ok' else "Belum dapat dibaca")

    def poll(self):
        try:
            generation,result,error,is_save=self.ocr_events.get_nowait()
            self.ocr_busy=False;self.saving=False;self.ocr_due=time.monotonic()+.5
            if is_save:self.last_save=time.monotonic()
            if not self.closing:
                if error:self.notice.set("Proses gagal: "+error)
                else:
                    if is_save:
                        self.refresh_history();self.notice.set("Disimpan: "+result['status']+" | OCR "+result['ocr']['status'])
                    if generation==self.ocr_generation:self.finish_ocr(result)
                self.check_button.configure(state="normal" if self.frame is not None and not self.save_pending else "disabled")
        except queue.Empty:pass
        if self.closing:
            if self.save_pending and not self.ocr_busy:
                job=self.save_pending;self.save_pending=None;self.launch_ocr(job,True)
            if self.ocr_busy or self.save_pending or (self.worker and self.worker.is_alive()):self.root.after(33,self.poll)
            else:self.root.destroy()
            return
        newest=None
        while True:
            try:newest=self.events.get_nowait()
            except queue.Empty:break
        if newest and self.stop_event and not self.stop_event.is_set():
            if newest[0]=="frame":
                self.show(newest[1],newest[2])
            else:
                self.stop();self.notice.set(newest[1])
        if self.worker and not self.worker.is_alive():
            self.worker=None
            self.camera_selector.configure(state="readonly")
            self.start_button.configure(state="normal");self.load_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
        if not self.ocr_busy:
            if self.save_pending:
                job=self.save_pending;self.save_pending=None;self.launch_ocr(job,True)
            elif self.frame is not None and self.result is not None and time.monotonic()>=self.ocr_due:
                self.launch_ocr((self.frame.copy(),copy.deepcopy(self.result),self.source.get(),self.ocr_generation,time.strftime("%H:%M:%S")))
        self.root.after(33,self.poll)

    def open_record(self,event=None):
        chosen=self.table.selection()
        if not chosen:return
        filename=self.table.item(chosen[0],"values")[3]
        folder=(ROOT/"results_fields").resolve();path=(folder/filename).resolve()
        if path.parent!=folder or not path.is_file():return
        os.startfile(str(path))

    def open_excel(self):
        try:os.startfile(str(export_ocr_csv()))
        except Exception as exc:messagebox.showerror("Excel OCR",str(exc))

    def open_folder(self):
        folder=ROOT/"results_fields";folder.mkdir(exist_ok=True);os.startfile(str(folder))

    def close(self):
        self.closing=True
        if self.stop_event:self.stop_event.set()
        self.root.title("Menutup webcam...")
        if not self.ocr_busy and not self.save_pending and (not self.worker or not self.worker.is_alive()):self.root.destroy()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--camera",type=int,default=0)
    sources=parser.add_mutually_exclusive_group()
    sources.add_argument("--rb3",dest="rb3",action="store_true",help="Use Qualcomm RB3 over USB (default)")
    sources.add_argument("--webcam",dest="rb3",action="store_false",help="Use laptop webcam instead")
    parser.set_defaults(rb3=True)
    parser.add_argument("--smoke-test",action="store_true",help="Test GUI with demo images; no webcam")
    args=parser.parse_args()
    root=tk.Tk();app=Dashboard(root,args.camera,args.rb3)
    if args.rb3 and not args.smoke_test:root.after(300,app.start)
    if args.smoke_test:
        def verify():
            try:
                for filename,expected in [("complete.png","PASS"),("missing_date.png","FAIL"),("blank.png","FAIL")]:
                    frame=cv2.imread(str(ROOT/"templates"/filename))
                    result=app.detector.inspect_fields(frame);app.show(frame,result);root.update_idletasks()
                    assert result["status"]==expected
                    assert app.badge.cget("text")==expected
                assert app.states["Tarikh penghantaran"].get().startswith("Kosong")
                print("Dashboard smoke test: PASS; image preview, field status and history load checked.")
            finally:app.close()
        root.after(250,verify)
    root.mainloop()
if __name__=="__main__":main()



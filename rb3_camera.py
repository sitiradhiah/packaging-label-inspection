"""RB3 camera via localhost-only JPEG stream forwarded over USB ADB."""
import os
from pathlib import Path
import shutil
import socket
import subprocess
import time
import threading
import cv2
import numpy as np

class RB3Camera:
    def __init__(self):
        self.sock=None;self.pid=None;self.buffer=b"";self.port=None
        self.adb=shutil.which("adb") or str(Path(os.environ["LOCALAPPDATA"])/"Android/Sdk/platform-tools/adb.exe")
        self.serial=None
        self.condition=threading.Condition();self.latest=None;self.failure=None
        self.receiver=None;self.halt=threading.Event()
        try:
            devices=self.run("devices").splitlines()
            ready=[line.split()[0] for line in devices if line.endswith("\tdevice")]
            if len(ready)!=1:raise RuntimeError("Connect exactly one authorized RB3 ADB device.")
            self.serial=ready[0]
            # ADB allocates an unused local port. Remote listens on loopback only.
            self.port=int(self.run("forward","tcp:0","tcp:18763").strip())
            cmd="nohup gst-launch-1.0 -q -e qtiqmmfsrc camera=0 control-mode=auto focus-mode=off name=cam cam.video_0 ! video/x-raw,format=NV12,width=1920,height=1080,framerate=15/1 ! videoconvert ! jpegenc quality=90 ! tcpserversink host=127.0.0.1 port=18763 sync=false > /tmp/parcel-camera-stream.log 2>&1 < /dev/null & stream_pid=$!; sleep 2; echo $stream_pid"
            self.pid=int(self.run("shell",cmd).strip().splitlines()[-1])
            deadline=time.monotonic()+12
            while time.monotonic()<deadline:
                try:
                    self.sock=socket.create_connection(("127.0.0.1",self.port),timeout=2)
                    self.sock.settimeout(5)
                    ok,frame=self.read_packet()
                    if ok:
                        self.receiver=threading.Thread(target=self.receive_latest,daemon=True)
                        self.receiver.start()
                        return
                except (OSError,RuntimeError):
                    if self.sock:self.sock.close()
                    self.sock=None
                    time.sleep(.3)
            raise RuntimeError("RB3 connected but camera stream unavailable. Check camera module/power.")
        except Exception:
            self.release();raise

    def run(self,*args):
        prefix=[self.adb]+(["-s",self.serial] if self.serial else [])
        return subprocess.check_output(prefix+list(args),stderr=subprocess.STDOUT,timeout=15,creationflags=subprocess.CREATE_NO_WINDOW).decode(errors="replace")

    def read_packet(self):
        while self.sock:
            start=self.buffer.find(b"\xff\xd8")
            end=self.buffer.find(b"\xff\xd9",max(0,start))
            if start>=0 and end>start:
                packet=self.buffer[start:end+2];self.buffer=self.buffer[end+2:]
                image=cv2.imdecode(np.frombuffer(packet,np.uint8),cv2.IMREAD_COLOR)
                if image is not None:return True,image
            chunk=self.sock.recv(65536)
            if not chunk:raise RuntimeError("RB3 stream ended.")
            self.buffer+=chunk
            if len(self.buffer)>8000000:raise RuntimeError("Invalid RB3 camera stream.")
        return False,None

    def receive_latest(self):
        try:
            while not self.halt.is_set():
                ok,frame=self.read_packet()
                if not ok:raise RuntimeError("RB3 stream stopped")
                with self.condition:
                    self.latest=frame
                    self.condition.notify_all()
        except Exception as exc:
            if not self.halt.is_set():
                with self.condition:
                    self.failure=exc
                    self.condition.notify_all()

    def read(self):
        with self.condition:
            ready=self.condition.wait_for(lambda: self.latest is not None or self.failure is not None or self.halt.is_set(),timeout=6)
            if self.failure:raise RuntimeError(str(self.failure))
            if not ready or self.halt.is_set():return False,None
            frame=self.latest;self.latest=None
            return True,frame

    def release(self):
        self.halt.set()
        with self.condition:self.condition.notify_all()
        if self.sock:
            try:self.sock.shutdown(socket.SHUT_RDWR)
            except OSError:pass
            self.sock.close()
        if self.receiver:self.receiver.join(timeout=2)
        self.sock=None
        if self.pid:
            try:self.run("shell","kill -INT "+str(self.pid))
            except Exception:pass
            self.pid=None
        if self.port:
            try:self.run("forward","--remove","tcp:"+str(self.port))
            except Exception:pass
            self.port=None

if __name__=="__main__":
    camera=RB3Camera()
    try:
        for i in range(5):
            ok,frame=camera.read()
            print("Frame",i+1,frame.shape,"mean",round(float(frame.mean()),1))
    finally:camera.release()





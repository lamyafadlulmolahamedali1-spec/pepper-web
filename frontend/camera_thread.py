"""Camera worker thread — opens via button, high FPS, multi-index.
© 2026 Lamya F. H. Ali"""
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage

try:
    import cv2
    _HAS=True
except Exception:
    _HAS=False


class CameraThread(QThread):
    frame_ready=pyqtSignal(QImage)
    results_ready=pyqtSignal(dict)
    pose_ready=pyqtSignal(object, tuple)  # pose_landmarks, (w,h) for precise touch
    error=pyqtSignal(str)

    def __init__(self, cam_index=0):
        super().__init__()
        self._run=False; self.cam_index=cam_index; self.engine=None

    def run(self):
        if not _HAS:
            self.error.emit("OpenCV not installed."); return
        try:
            from vision_engine import VisionEngine
            self.engine=VisionEngine()
        except Exception as e:
            self.error.emit(f"Vision engine failed: {e}"); return
        cap=None
        backends=[]
        try: backends=[cv2.CAP_V4L2, cv2.CAP_ANY]
        except Exception: backends=[0]
        for idx in [1,0,2,3]:  # CAM_ORDER: index 1 works on this machine
            for be in backends:
                try: c=cv2.VideoCapture(idx,be)
                except Exception: c=cv2.VideoCapture(idx)
                if c is not None and c.isOpened():
                    ok,_=c.read()
                    if ok: cap=c; break
                    c.release()
            if cap is not None: break
        if cap is None:
            self.error.emit("No camera found. Check it's connected and not used by another app.\n"
                            "Linux: sudo usermod -a -G video $USER  then re-login."); return
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,640); cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
        cap.set(cv2.CAP_PROP_FPS,30); cap.set(cv2.CAP_PROP_BUFFERSIZE,1)
        self._run=True; fail=0
        while self._run:
            ok,frame=cap.read()
            if not ok:
                fail+=1
                if fail>60: self.error.emit("Camera stopped sending frames."); break
                self.msleep(20); continue
            fail=0; frame=cv2.flip(frame,1)
            try:
                annotated,res=self.engine.process(frame,draw=True)
                # also surface raw pose landmarks for precise body-touch checks
                pl=getattr(self.engine,"_last_pose",None)
            except Exception:
                annotated,res,pl=frame,{},None
            rgb=cv2.cvtColor(annotated,cv2.COLOR_BGR2RGB)
            h,w,ch=rgb.shape
            img=QImage(rgb.data,w,h,ch*w,QImage.Format.Format_RGB888).copy()
            self.frame_ready.emit(img)
            if res: self.results_ready.emit(res)
            self.msleep(12)
        cap.release()
        if self.engine: self.engine.close()

    def stop(self):
        self._run=False; self.wait(1500)

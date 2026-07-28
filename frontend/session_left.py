"""Live session LEFT column: camera feed + theme selector + metrics + emotion bars.
Matches screenshot 6 left side. © 2026 Lamya F. H. Ali"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGridLayout, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPainter, QPixmap
import theme as T
from frame_bridge import FRAMES


class EmotionBars(QWidget):
    """Horizontal emotion bar chart (7 emotions) — bottom-left of screenshot 6."""
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(150)
        self.data={e:0.0 for e in ["happy","joyful","sad","angry","fear","surprise","neutral"]}
    def set_data(self,emotions):
        for k in self.data: self.data[k]=emotions.get(k,0.0)
        self.update()
    def paintEvent(self,e):
        qp=QPainter(self); qp.setRenderHint(QPainter.RenderHint.Antialiasing)
        qp.fillRect(self.rect(), QColor(T.DARK_BG))
        rows=list(self.data.items()); n=len(rows); pad=6
        rh=(self.height()-pad*2)/n; x0=70; bw=self.width()-x0-50
        qp.setFont(QFont("Arial",8))
        for i,(name,val) in enumerate(rows):
            y=pad+i*rh
            qp.setPen(QColor(T.DARK_MUTE))
            qp.drawText(4,int(y+rh*0.7),name)
            qp.setBrush(QColor(40,52,80)); qp.setPen(Qt.PenStyle.NoPen)
            qp.drawRoundedRect(x0,int(y+4),bw,int(rh-8),4,4)
            col=T.GREEN if name in("happy","joyful") else (T.GOLD if name=="neutral" else T.RED)
            qp.setBrush(QColor(col))
            qp.drawRoundedRect(x0,int(y+4),int(bw*min(1,val)),int(rh-8),4,4)
            qp.setPen(QColor(T.DARK_TEXT))
            qp.drawText(x0+bw+6,int(y+rh*0.7),f"{int(val*100)}%")


class SessionLeft(QWidget):
    def __init__(self, on_theme=None):
        super().__init__()
        self.on_theme=on_theme
        self._build()

    def _build(self):
        lay=QHBoxLayout(self); lay.setContentsMargins(6,6,6,6); lay.setSpacing(6)

        # vertical theme selector (Blue/White/Green/Gray/Colorful/Pink)
        themecol=QVBoxLayout(); themecol.setSpacing(4)
        dots={"Blue":"🔵","White":"⬜","Green":"🟢","Gray":"🩶","Colorful":"🌈","Pink":"💗"}
        for name in T.THEME_NAMES:
            b=QPushButton(f"{dots.get(name,'●')} {name}")
            b.setFixedWidth(86); b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(f"background:{T.DARK_PANEL2};color:{T.DARK_TEXT};border:1px solid {T.DARK_BORDER};"
                            f"border-radius:6px;padding:5px;font-size:11px;font-weight:bold;text-align:left;")
            b.clicked.connect(lambda _,nm=name: self.on_theme(nm) if self.on_theme else None)
            themecol.addWidget(b)
        themecol.addStretch()
        lay.addLayout(themecol)

        # camera + metrics + emotion column
        cam=QVBoxLayout(); cam.setSpacing(6)

        # status bar over video (e.g. NEUTRAL 100%)
        self.statusLbl=QLabel("● LIVE   —   NEUTRAL 0%")
        self.statusLbl.setStyleSheet(f"background:rgba(16,185,129,0.2);color:{T.GREEN};"
                                     f"border-radius:6px;padding:4px 8px;font-weight:bold;font-size:12px;")
        cam.addWidget(self.statusLbl)

        # video feed
        self.view=QLabel("Camera off — press Start Camera")
        self.view.setMinimumSize(360,300); self.view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.view.setStyleSheet(f"background:#06090f;border:1px solid {T.DARK_BORDER};"
                                f"border-radius:10px;color:{T.DARK_MUTE};")
        cam.addWidget(self.view,1)

        # start camera button
        self.btnCam=QPushButton("📷 Start Camera")
        self.btnCam.setStyleSheet(f"background:{T.TEAL};color:white;border:none;border-radius:8px;"
                                  f"padding:8px;font-weight:bold;")
        cam.addWidget(self.btnCam)

        # 4 metric boxes: Score / Att / Fingers / Face
        mgrid=QGridLayout(); mgrid.setSpacing(6)
        self.mScore=self._metric("Score","0",T.GOLD)
        self.mAtt=self._metric("Att","0%",T.TEAL)
        self.mFing=self._metric("Fingers","0",T.PURPLE3)
        self.mFace=self._metric("Face","—",T.GREEN)
        for i,m in enumerate([self.mScore,self.mAtt,self.mFing,self.mFace]):
            mgrid.addWidget(m["box"],i//2,i%2)
        cam.addLayout(mgrid)

        # emotion bars
        elbl=QLabel("Emotion Analysis")
        elbl.setStyleSheet(f"color:{T.DARK_MUTE};font-size:11px;font-weight:bold;")
        cam.addWidget(elbl)
        self.emoBars=EmotionBars(); cam.addWidget(self.emoBars)

        lay.addLayout(cam,1)

    def _metric(self,label,val,color):
        box=QFrame()
        box.setStyleSheet(f"background:{T.DARK_PANEL2};border:1px solid {T.DARK_BORDER};border-radius:8px;")
        v=QVBoxLayout(box); v.setContentsMargins(8,6,8,6); v.setSpacing(0)
        value=QLabel(val); value.setStyleSheet(f"color:{color};font-size:20px;font-weight:bold;")
        value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name=QLabel(label); name.setStyleSheet(f"color:{T.DARK_MUTE};font-size:10px;")
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(value); v.addWidget(name)
        return {"box":box,"value":value}

    def show_frame(self,img):
        pix=QPixmap.fromImage(img).scaled(self.view.width(),self.view.height(),
            Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.view.setPixmap(pix)
        # share this frame to the parent dashboard (live monitor)
        try:
            from PyQt6.QtCore import QByteArray, QBuffer, QIODevice
            small=img.scaled(480,360, Qt.AspectRatioMode.KeepAspectRatio,
                             Qt.TransformationMode.SmoothTransformation)
            ba=QByteArray(); buf=QBuffer(ba); buf.open(QIODevice.OpenModeFlag.WriteOnly)
            small.save(buf, "JPEG", 70); buf.close()
            FRAMES.put(bytes(ba))
        except Exception: pass

    def update_metrics(self,res,score):
        self.mScore["value"].setText(str(score))
        self.mAtt["value"].setText(f"{int(res.get('attention',0))}%")
        self.mFing["value"].setText(str(res.get("fingers",0)))
        face_ok=res.get("face_detected",False)
        self.mFace["value"].setText("Ok" if face_ok else "No")
        self.mFace["value"].setStyleSheet(f"color:{T.GREEN if face_ok else T.RED};font-size:20px;font-weight:bold;")
        emo=res.get("emotion","neutral").upper(); conf=int(res.get("emotion_conf",0)*100)
        self.statusLbl.setText(f"● LIVE   —   {emo} {conf}%")
        self.emoBars.set_data(res.get("emotions",{}))

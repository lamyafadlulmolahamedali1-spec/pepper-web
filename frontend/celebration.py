"""Spatial celebration overlay (stars + crown) + clap sound every 10 tasks.
© 2026 Lamya F. H. Ali"""
import math, random, struct, wave, io, os, tempfile
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QFont, QPainterPath, QBrush

# ---- Generate a clap-like sound (no external file needed) ----
def _make_clap_wav(path):
    sr=22050; dur=0.12; frames=[]
    for n in range(3):  # three quick claps
        for i in range(int(sr*dur)):
            t=i/sr
            # noise burst with fast decay = clap
            amp=math.exp(-30*t)*(random.random()*2-1)
            frames.append(int(amp*32767*0.8))
        for _ in range(int(sr*0.05)): frames.append(0)  # gap
    with wave.open(path,"w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(b"".join(struct.pack("<h",max(-32768,min(32767,f))) for f in frames))

_CLAP_PATH=os.path.join(tempfile.gettempdir(),"pepper_clap.wav")
try:
    if not os.path.exists(_CLAP_PATH): _make_clap_wav(_CLAP_PATH)
except Exception: _CLAP_PATH=None

def play_clap():
    if not _CLAP_PATH: return
    try:
        from PyQt6.QtMultimedia import QSoundEffect
        from PyQt6.QtCore import QUrl
        global _eff
        _eff=QSoundEffect()
        _eff.setSource(QUrl.fromLocalFile(_CLAP_PATH))
        _eff.setVolume(0.9); _eff.play()
    except Exception:
        try:
            import subprocess
            subprocess.Popen(["aplay", _CLAP_PATH],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception: pass


class Celebration(QWidget):
    """Full-screen spatial celebration: falling stars + crown + 'You are a STAR!'"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.hide()
        self.parts=[]; self.frames=0
        self.t=QTimer(self); self.t.timeout.connect(self._tick)

    def celebrate(self):
        self._mini=False
        play_clap()
        w=self.width() or 1200
        self.parts=[]
        emojis=["⭐","🌟","✨","🎉","🎊","💫","🏆","🎈","👑"]
        for _ in range(60):
            self.parts.append({
                "x":random.uniform(0,w),"y":random.uniform(-300,0),
                "vy":random.uniform(4,11),"vx":random.uniform(-2,2),
                "sz":random.uniform(18,44),"rot":random.uniform(0,360),
                "vr":random.uniform(-8,8),
                "color":random.choice(["#fbbf24","#f472b6","#a78bfa","#34d399","#60a5fa","#fb923c"]),
                "emoji":random.choice(emojis)})
        self.frames=0; self.raise_(); self.show(); self.t.start(28)

    def _tick(self):
        self.frames+=1
        for p in self.parts:
            p["y"]+=p["vy"]; p["x"]+=p["vx"]; p["rot"]+=p["vr"]
        self.update()
        lim=40 if getattr(self,'_mini',False) else 95
        if self.frames>lim: self.t.stop(); self.hide(); self._mini=False


    def mini(self):
        """Small celebration for every correct task — a few quick stars, no dark overlay."""
        w=self.width() or 800
        self.parts=[]
        for _ in range(14):
            self.parts.append({
                "x":random.uniform(w*0.2,w*0.8),"y":random.uniform(0,80),
                "vy":random.uniform(3,7),"vx":random.uniform(-2,2),
                "sz":random.uniform(14,26),"rot":random.uniform(0,360),
                "vr":random.uniform(-6,6),
                "color":random.choice(["#fbbf24","#f472b6","#34d399","#60a5fa"]),
                "emoji":random.choice(["⭐","🌟","✨","💫"])})
        self._mini=True; self.frames=0; self.raise_(); self.show(); self.t.start(28)

    def paintEvent(self,e):
        if not self.isVisible(): return
        qp=QPainter(self); qp.setRenderHint(QPainter.RenderHint.Antialiasing)
        if not getattr(self,'_mini',False):
            qp.fillRect(self.rect(), QColor(10,14,26,120))
        if getattr(self,'_mini',False):
            for p in self.parts:
                qp.save(); qp.translate(p["x"],p["y"]); qp.rotate(p["rot"])
                qp.setFont(QFont("Arial",int(p["sz"]))); qp.drawText(0,0,p["emoji"]); qp.restore()
            return
        # Crown + message center
        qp.setFont(QFont("Arial",72))
        qp.drawText(self.rect().adjusted(0,-60,0,-60), Qt.AlignmentFlag.AlignCenter,"👑")
        qp.setFont(QFont("Arial",30,QFont.Weight.Bold))
        qp.setPen(QColor("#fde047"))
        qp.drawText(self.rect().adjusted(0,40,0,40), Qt.AlignmentFlag.AlignCenter,
                    "🎉 You are a STAR! 🎉")
        qp.setFont(QFont("Arial",16))
        qp.setPen(QColor("#e8edf7"))
        qp.drawText(self.rect().adjusted(0,100,0,100), Qt.AlignmentFlag.AlignCenter,
                    "Clap your hands! 👏👏👏")
        # Falling emoji/stars
        for p in self.parts:
            qp.save(); qp.translate(p["x"],p["y"]); qp.rotate(p["rot"])
            qp.setFont(QFont("Arial",int(p["sz"])))
            qp.drawText(0,0,p["emoji"]); qp.restore()

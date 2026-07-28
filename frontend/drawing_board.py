"""Drawing board — gray target item, child traces over it. © 2026 Lamya F. H. Ali"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QPainterPath, QImage
class _Canvas(QWidget):
    progress=pyqtSignal(int)
    def __init__(self):
        super().__init__(); self.setMinimumSize(360,360)
        self.setStyleSheet("background:white;border-radius:12px;")
        self.target="A"; self.kind="letter"; self.pen_color=QColor("#7c3aed"); self.pen_width=14
        self._drawing=False; self._last=None
        self._strokes=QImage(700,700,QImage.Format.Format_ARGB32); self._strokes.fill(Qt.GlobalColor.transparent)
        self._template_points=[]; self._covered=set()
    def set_target(self,target,kind="letter",color="#7c3aed"):
        self.target=str(target); self.kind=kind; self.pen_color=QColor(color)
        self.clear(); self._build_template_points(); self.update()
    def clear(self):
        self._strokes.fill(Qt.GlobalColor.transparent); self._covered=set(); self._last=None
        self.progress.emit(0); self.update()
    def _template_rect(self):
        m=60; s=min(self.width(),self.height())-m*2
        return QRectF((self.width()-s)/2,(self.height()-s)/2,s,s)
    def _build_template_points(self):
        self._template_points=[]; r=self._template_rect(); path=self._template_path(r)
        if path is None: return
        length=path.length(); n=max(40,int(length/8))
        for i in range(n+1):
            pt=path.pointAtPercent(i/n); self._template_points.append((int(pt.x()),int(pt.y())))
    def _template_path(self,r):
        path=QPainterPath()
        if self.kind=="shape":
            t=self.target.lower()
            if "circle" in t: path.addEllipse(r)
            elif "square" in t: path.addRect(r)
            elif "triangle" in t:
                path.moveTo(r.center().x(),r.top()); path.lineTo(r.left(),r.bottom())
                path.lineTo(r.right(),r.bottom()); path.closeSubpath()
            elif "star" in t:
                import math; cx,cy=r.center().x(),r.center().y(); R=r.width()/2
                for i in range(11):
                    ang=-math.pi/2+i*math.pi/5; rad=R if i%2==0 else R*0.42
                    x=cx+rad*math.cos(ang); y=cy+rad*math.sin(ang)
                    path.lineTo(x,y) if i else path.moveTo(x,y)
                path.closeSubpath()
            else: path.addEllipse(r)
        else:
            f=QFont("Arial",1); f.setPixelSize(int(r.height())); f.setBold(True)
            path.addText(r.left()+r.width()*0.18, r.bottom()-r.height()*0.12, f,
                         self.target[:1] if self.kind=="letter" else self.target)
        return path
    def paintEvent(self,e):
        qp=QPainter(self); qp.setRenderHint(QPainter.RenderHint.Antialiasing)
        qp.fillRect(self.rect(),QColor("white"))
        r=self._template_rect(); path=self._template_path(r)
        if path is not None:
            qp.setPen(QPen(QColor(200,205,215),max(8,self.pen_width+2)))
            qp.setBrush(Qt.BrushStyle.NoBrush); qp.drawPath(path)
        qp.drawImage(0,0,self._strokes)
    def mousePressEvent(self,e):
        self._drawing=True; self._last=e.position().toPoint(); self._paint_to(self._last)
    def mouseMoveEvent(self,e):
        if self._drawing: self._paint_to(e.position().toPoint())
    def mouseReleaseEvent(self,e): self._drawing=False; self._last=None
    def _paint_to(self,pt):
        p=QPainter(self._strokes); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QPen(self.pen_color,self.pen_width,Qt.PenStyle.SolidLine,
                 Qt.PenCapStyle.RoundCap,Qt.PenJoinStyle.RoundJoin))
        if self._last is not None: p.drawLine(self._last,pt)
        else: p.drawPoint(pt)
        p.end(); self._last=pt; self._update_coverage(pt); self.update()
    def _update_coverage(self,pt):
        px,py=pt.x(),pt.y(); thr=self.pen_width+8
        for i,(tx,ty) in enumerate(self._template_points):
            if i in self._covered: continue
            if abs(tx-px)<=thr and abs(ty-py)<=thr: self._covered.add(i)
        if self._template_points:
            self.progress.emit(int(len(self._covered)/len(self._template_points)*100))
class DrawingBoard(QWidget):
    done=pyqtSignal(bool)
    def __init__(self):
        super().__init__(); self._pct=0; self._build()
    def _build(self):
        v=QVBoxLayout(self); v.setContentsMargins(8,8,8,8); v.setSpacing(6)
        self.title=QLabel("✏️ Trace the gray shape!")
        self.title.setStyleSheet("color:#2d2b69;font-size:16px;font-weight:bold;")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter); v.addWidget(self.title)
        self.canvas=_Canvas(); self.canvas.progress.connect(self._on_progress); v.addWidget(self.canvas,1)
        self.bar=QLabel("Coverage: 0%"); self.bar.setStyleSheet("color:#6b7280;font-size:12px;")
        self.bar.setAlignment(Qt.AlignmentFlag.AlignCenter); v.addWidget(self.bar)
        row=QHBoxLayout()
        clr=QPushButton("🧹 Clear"); clr.setStyleSheet("background:#e5e7eb;color:#374151;border:none;border-radius:8px;padding:8px;")
        clr.clicked.connect(self.canvas.clear)
        dn=QPushButton("✅ Done"); dn.setStyleSheet("background:#10b981;color:white;border:none;border-radius:8px;padding:8px;font-weight:bold;")
        dn.clicked.connect(lambda: self.done.emit(self._pct>=55))
        row.addWidget(clr); row.addWidget(dn); v.addLayout(row)
    def set_task(self,target,kind="letter",color="#7c3aed"):
        labels={"letter":f"✏️ Trace the letter  {target}","shape":f"✏️ Trace the {target}","word":f"✏️ Trace the word  {target}"}
        self.title.setText(labels.get(kind,"✏️ Trace it!"))
        self.canvas.set_target(target,kind,color); self._pct=0; self.bar.setText("Coverage: 0%")
    def _on_progress(self,pct):
        self._pct=pct; self.bar.setText(f"Coverage: {pct}%")
        if pct>=55: self.bar.setText(f"Coverage: {pct}%  ✅ great tracing!"); self.done.emit(True)

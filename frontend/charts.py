"""Pure-Qt charts: Line, Bar, Donut, Radar — matches screenshots 1-2.
© 2026 Lamya F. H. Ali"""
import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPainterPath
import theme as T


class LineChart(QWidget):
    def __init__(self, title="", color=T.BLUE):
        super().__init__(); self.title=title; self.color=color
        self.values=[]; self.setMinimumHeight(220)
    def set_values(self,v): self.values=v; self.update()
    def paintEvent(self,e):
        qp=QPainter(self); qp.setRenderHint(QPainter.RenderHint.Antialiasing)
        qp.fillRect(self.rect(),QColor(T.CARD))
        w,h=self.width(),self.height(); top,bot,left,right=34,h-26,40,w-16
        qp.setPen(QColor(T.INK)); qp.setFont(QFont("Arial",11,QFont.Weight.Bold))
        qp.drawText(10,20,self.title)
        # grid
        qp.setPen(QPen(QColor(T.CARD_BORDER),1))
        for i in range(6):
            y=top+(bot-top)*i/5; qp.drawLine(left,int(y),right,int(y))
            qp.setPen(QColor(T.MUTE)); qp.setFont(QFont("Arial",7))
            qp.drawText(8,int(y)+3,str(100-i*20)); qp.setPen(QPen(QColor(T.CARD_BORDER),1))
        if len(self.values)<2:
            qp.setPen(QColor(T.MUTE)); qp.drawText(self.rect(),Qt.AlignmentFlag.AlignCenter,"Need more data")
            return
        n=len(self.values); mx=max(max(self.values),1)
        pts=[(left+(right-left)*i/(n-1), bot-(v/mx)*(bot-top)) for i,v in enumerate(self.values)]
        # area
        path=QPainterPath(); path.moveTo(pts[0][0],bot)
        for x,y in pts: path.lineTo(x,y)
        path.lineTo(pts[-1][0],bot); path.closeSubpath()
        qp.setBrush(QColor(124,58,237,40)); qp.setPen(Qt.PenStyle.NoPen); qp.drawPath(path)
        qp.setPen(QPen(QColor(self.color),3))
        for i in range(1,len(pts)):
            qp.drawLine(int(pts[i-1][0]),int(pts[i-1][1]),int(pts[i][0]),int(pts[i][1]))
        qp.setBrush(QColor(self.color))
        for x,y in pts: qp.drawEllipse(int(x-3),int(y-3),6,6)


class BarChart(QWidget):
    def __init__(self,title=""):
        super().__init__(); self.title=title; self.values=[]; self.setMinimumHeight(220)
    def set_values(self,v): self.values=v; self.update()
    def paintEvent(self,e):
        qp=QPainter(self); qp.setRenderHint(QPainter.RenderHint.Antialiasing)
        qp.fillRect(self.rect(),QColor(T.CARD))
        w,h=self.width(),self.height(); top,bot,left=34,h-24,36
        qp.setPen(QColor(T.INK)); qp.setFont(QFont("Arial",11,QFont.Weight.Bold))
        qp.drawText(10,20,self.title)
        if not self.values:
            qp.setPen(QColor(T.MUTE)); qp.drawText(self.rect(),Qt.AlignmentFlag.AlignCenter,"No data")
            return
        n=len(self.values); mx=max(max(self.values),1); gap=8
        bw=max(8,(w-left-16-gap*n)/n)
        for i,v in enumerate(self.values):
            x=left+i*(bw+gap); bh=(v/mx)*(bot-top)
            qp.setBrush(QColor(T.PURPLE3)); qp.setPen(Qt.PenStyle.NoPen)
            qp.drawRoundedRect(int(x),int(bot-bh),int(bw),int(bh),3,3)


class DonutChart(QWidget):
    def __init__(self,title=""):
        super().__init__(); self.title=title
        self.parts=[]  # (label,value,color)
        self.setMinimumHeight(240)
    def set_parts(self,parts): self.parts=parts; self.update()
    def paintEvent(self,e):
        qp=QPainter(self); qp.setRenderHint(QPainter.RenderHint.Antialiasing)
        qp.fillRect(self.rect(),QColor(T.CARD))
        qp.setPen(QColor(T.INK)); qp.setFont(QFont("Arial",11,QFont.Weight.Bold))
        qp.drawText(10,20,self.title)
        total=sum(p[1] for p in self.parts) or 1
        cx,cy=self.width()//2,self.height()//2+10; r=min(self.width(),self.height())//3
        rect=QRectF(cx-r,cy-r,2*r,2*r); start=90*16
        for label,val,col in self.parts:
            span=-int(360*16*val/total)
            qp.setBrush(QColor(col)); qp.setPen(Qt.PenStyle.NoPen)
            qp.drawPie(rect,start,span); start+=span
        # hole
        qp.setBrush(QColor(T.CARD)); qp.drawEllipse(QPointF(cx,cy),r*0.55,r*0.55)
        # legend
        qp.setFont(QFont("Arial",8)); lx=10; ly=self.height()-12
        for label,val,col in self.parts:
            qp.setBrush(QColor(col)); qp.setPen(Qt.PenStyle.NoPen)
            qp.drawRect(lx,ly-8,10,10)
            qp.setPen(QColor(T.MUTE)); qp.drawText(lx+14,ly,label); lx+=80


class RadarChart(QWidget):
    def __init__(self,title=""):
        super().__init__(); self.title=title
        self.data={}  # name->0..100
        self.setMinimumHeight(240)
    def set_data(self,d): self.data=d; self.update()
    def paintEvent(self,e):
        qp=QPainter(self); qp.setRenderHint(QPainter.RenderHint.Antialiasing)
        qp.fillRect(self.rect(),QColor(T.CARD))
        qp.setPen(QColor(T.INK)); qp.setFont(QFont("Arial",11,QFont.Weight.Bold))
        qp.drawText(10,20,self.title)
        if not self.data:
            qp.setPen(QColor(T.MUTE)); qp.drawText(self.rect(),Qt.AlignmentFlag.AlignCenter,"No data")
            return
        names=list(self.data.keys()); n=len(names)
        cx,cy=self.width()//2,self.height()//2+10; R=min(self.width(),self.height())//3
        # rings
        qp.setPen(QPen(QColor(T.CARD_BORDER),1))
        for ring in (0.25,0.5,0.75,1.0):
            pts=[QPointF(cx+R*ring*math.cos(-math.pi/2+2*math.pi*i/n),
                         cy+R*ring*math.sin(-math.pi/2+2*math.pi*i/n)) for i in range(n)]
            for i in range(n): qp.drawLine(pts[i],pts[(i+1)%n])
        # axes + labels
        qp.setFont(QFont("Arial",8))
        for i,name in enumerate(names):
            a=-math.pi/2+2*math.pi*i/n
            ex,ey=cx+R*math.cos(a),cy+R*math.sin(a)
            qp.setPen(QPen(QColor(T.CARD_BORDER),1)); qp.drawLine(QPointF(cx,cy),QPointF(ex,ey))
            qp.setPen(QColor(T.MUTE))
            qp.drawText(int(cx+(R+12)*math.cos(a))-14,int(cy+(R+12)*math.sin(a)),name)
        # polygon
        poly=QPainterPath()
        for i,name in enumerate(names):
            a=-math.pi/2+2*math.pi*i/n; v=self.data[name]/100
            x,y=cx+R*v*math.cos(a),cy+R*v*math.sin(a)
            if i==0: poly.moveTo(x,y)
            else: poly.lineTo(x,y)
        poly.closeSubpath()
        qp.setBrush(QColor(124,58,237,90)); qp.setPen(QPen(QColor(T.PURPLE),2))
        qp.drawPath(poly)

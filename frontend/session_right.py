"""Live session RIGHT column: chat log + quick-action buttons + Next + PDF.
Matches screenshot 6 right side. © 2026 Lamya F. H. Ali"""
import webbrowser
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal
import theme as T

GAMES_URL="https://lamyafadlulmolahamedali.pythonanywhere.com/"


class SessionRight(QWidget):
    next_task=pyqtSignal()
    pause=pyqtSignal()
    cheer=pyqtSignal(str)
    save_pdf=pyqtSignal()

    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        lay=QVBoxLayout(self); lay.setContentsMargins(8,8,8,8); lay.setSpacing(6)
        title=QLabel("💬 CHAT & CONTROLS")
        title.setStyleSheet(f"color:{T.PURPLE3};font-size:12px;font-weight:bold;")
        lay.addWidget(title)

        self.chat=QTextEdit(); self.chat.setReadOnly(True)
        self.chat.setStyleSheet(f"background:{T.DARK_PANEL};color:{T.DARK_TEXT};"
            f"border:1px solid {T.DARK_BORDER};border-radius:8px;font-size:11px;")
        lay.addWidget(self.chat,1)

        # Next + Pause
        row1=QHBoxLayout()
        self.btnNext=QPushButton("➡ Next")
        self.btnNext.setStyleSheet(f"background:{T.GREEN};color:white;border:none;"
            f"border-radius:8px;padding:9px;font-weight:bold;")
        self.btnNext.clicked.connect(self.next_task.emit)
        self.btnPause=QPushButton("⏸ Pause")
        self.btnPause.setStyleSheet(f"background:{T.GOLD};color:white;border:none;"
            f"border-radius:8px;padding:9px;font-weight:bold;")
        self.btnPause.clicked.connect(self.pause.emit)
        row1.addWidget(self.btnNext); row1.addWidget(self.btnPause)
        lay.addLayout(row1)

        # Yay / Cheer / Bravo
        row2=QHBoxLayout()
        for label,msg,col in [("🎉 Yay!","Yay! You did it!",T.PINK),
                              ("👏 Cheer","Cheer! Well done!",T.TEAL),
                              ("⭐ Bravo","Bravo! Superstar!",T.PURPLE)]:
            b=QPushButton(label)
            b.setStyleSheet(f"background:{col};color:white;border:none;border-radius:8px;"
                f"padding:8px;font-weight:bold;font-size:11px;")
            b.clicked.connect(lambda _,m=msg: self.cheer.emit(m))
            row2.addWidget(b)
        lay.addLayout(row2)

        # Clear chat + Games + PDF
        row3=QHBoxLayout()
        bClear=QPushButton("🧹 Clear")
        bClear.setStyleSheet(f"background:{T.DARK_PANEL2};color:{T.DARK_TEXT};"
            f"border:1px solid {T.DARK_BORDER};border-radius:8px;padding:8px;font-size:11px;")
        bClear.clicked.connect(lambda: self.chat.clear())
        bGames=QPushButton("🎮 Games")
        bGames.setStyleSheet(f"background:{T.PURPLE};color:white;border:none;"
            f"border-radius:8px;padding:8px;font-size:11px;font-weight:bold;")
        bGames.clicked.connect(lambda: webbrowser.open(GAMES_URL))
        bPDF=QPushButton("📄 PDF")
        bPDF.setStyleSheet(f"background:{T.BLUE};color:white;border:none;"
            f"border-radius:8px;padding:8px;font-size:11px;font-weight:bold;")
        bPDF.clicked.connect(self.save_pdf.emit)
        row3.addWidget(bClear); row3.addWidget(bGames); row3.addWidget(bPDF)
        lay.addLayout(row3)

    def log(self, who, text):
        ts=datetime.now().strftime("%H:%M:%S")
        color=T.PURPLE3 if who=="Pepper" else (T.GREEN if who=="System" else T.DARK_TEXT)
        self.chat.append(f'<div style="margin-bottom:4px">'
            f'<span style="color:{T.DARK_MUTE};font-size:9px">🤖 {ts}</span><br>'
            f'<span style="color:{color}">{text}</span></div>')
        sb=self.chat.verticalScrollBar(); sb.setValue(sb.maximum())

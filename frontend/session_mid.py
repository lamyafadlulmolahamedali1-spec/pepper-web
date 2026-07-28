"""Live session MIDDLE column: robot prompt + 2x2 task grid / video + audio controls.
Matches screenshot 6 center. © 2026 Lamya F. H. Ali"""
import urllib.parse, webbrowser
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGridLayout, QFrame, QLineEdit, QSlider, QButtonGroup, QRadioButton)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import theme as T


class SessionMid(QWidget):
    answer=pyqtSignal(bool)         # correct / wrong from a grid choice
    speak_toggle=pyqtSignal(bool)   # TAP TO SPEAK pressed/released
    volume=pyqtSignal(int)
    voice=pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.cur=None; self._build()

    def _build(self):
        lay=QVBoxLayout(self); lay.setContentsMargins(10,10,10,10); lay.setSpacing(8)

        # ---- robot prompt ----
        top=QHBoxLayout()
        robot=QLabel("🤖"); robot.setStyleSheet("font-size:40px;")
        top.addWidget(robot)
        pcol=QVBoxLayout()
        self.badge=QLabel("TEACCH  L1")
        self.badge.setStyleSheet(f"background:{T.DARK_PANEL2};color:{T.TEAL};border-radius:6px;"
                                 f"padding:2px 8px;font-size:10px;font-weight:bold;")
        self.badge.setFixedWidth(90)
        self.prompt=QLabel("Press Start to begin")
        self.prompt.setStyleSheet(f"color:{T.DARK_TEXT};font-size:20px;font-weight:bold;")
        self.prompt.setWordWrap(True)
        self.sub=QLabel("")
        self.sub.setStyleSheet(f"color:{T.DARK_MUTE};font-size:11px;")
        pcol.addWidget(self.badge); pcol.addWidget(self.prompt); pcol.addWidget(self.sub)
        top.addLayout(pcol,1)
        lay.addLayout(top)

        # ---- active task area (grid OR big instruction OR video) ----
        self.area=QFrame()
        self.area.setStyleSheet(f"background:{T.DARK_PANEL};border:1px solid {T.DARK_BORDER};border-radius:12px;")
        self.areaLay=QVBoxLayout(self.area)
        self.areaLay.setContentsMargins(20,20,20,20)
        self.bigEm=QLabel("🎯"); self.bigEm.setStyleSheet("font-size:72px;")
        self.bigEm.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bigTxt=QLabel("Ready when you are!")
        self.bigTxt.setStyleSheet(f"color:{T.DARK_TEXT};font-size:18px;font-weight:bold;")
        self.bigTxt.setAlignment(Qt.AlignmentFlag.AlignCenter); self.bigTxt.setWordWrap(True)
        self.doNow=QLabel("")
        self.doNow.setStyleSheet(f"color:{T.GOLD};font-size:13px;")
        self.doNow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid=QWidget(); self.gridLay=QGridLayout(self.grid)
        self.areaLay.addStretch()
        self.areaLay.addWidget(self.bigEm)
        self.areaLay.addWidget(self.bigTxt)
        self.areaLay.addWidget(self.doNow)
        self.areaLay.addWidget(self.grid)
        self.areaLay.addStretch()
        lay.addWidget(self.area,1)

        # ---- YouTube search bar ----
        yt=QHBoxLayout()
        self.ytInput=QLineEdit(); self.ytInput.setPlaceholderText("🔎 Search YouTube...")
        self.ytInput.setStyleSheet(f"background:{T.DARK_PANEL2};color:{T.DARK_TEXT};"
            f"border:1px solid {T.DARK_BORDER};border-radius:8px;padding:7px;")
        btnYt=QPushButton("Search"); btnYt.setStyleSheet(f"background:{T.RED};color:white;"
            f"border:none;border-radius:8px;padding:7px 14px;font-weight:bold;")
        btnYt.clicked.connect(self._yt)
        self.ytInput.returnPressed.connect(self._yt)
        btnGames=QPushButton("🎮 Games"); btnGames.setStyleSheet(f"background:{T.PURPLE};color:white;"
            f"border:none;border-radius:8px;padding:7px 14px;font-weight:bold;")
        btnGames.clicked.connect(lambda: webbrowser.open(
            "https://www.youtube.com/results?search_query="+urllib.parse.quote("fun learning games for kids")))
        yt.addWidget(self.ytInput,1); yt.addWidget(btnYt); yt.addWidget(btnGames)
        lay.addLayout(yt)

        # ---- audio + voice controls ----
        au=QHBoxLayout()
        self.btnSpeak=QPushButton("🎙 TAP TO SPEAK")
        self.btnSpeak.setCheckable(True)
        self.btnSpeak.setStyleSheet(f"background:{T.DARK_PANEL2};color:{T.DARK_TEXT};"
            f"border:1px solid {T.DARK_BORDER};border-radius:8px;padding:8px 14px;font-weight:bold;")
        self.btnSpeak.clicked.connect(lambda: self.speak_toggle.emit(self.btnSpeak.isChecked()))
        au.addWidget(self.btnSpeak)
        au.addWidget(QLabel("🔊"))
        self.vol=QSlider(Qt.Orientation.Horizontal); self.vol.setRange(0,100); self.vol.setValue(85)
        self.vol.setFixedWidth(110)
        self.vol.valueChanged.connect(self.volume.emit)
        au.addWidget(self.vol)
        # voice radio
        self.vgroup=QButtonGroup(self)
        for i,name in enumerate(T.VOICES):
            rb=QRadioButton(name); rb.setStyleSheet(f"color:{T.DARK_TEXT};font-size:11px;")
            if i==0: rb.setChecked(True)
            rb.toggled.connect(lambda c,n=name: self.voice.emit(n) if c else None)
            self.vgroup.addButton(rb); au.addWidget(rb)
        au.addStretch()
        lay.addLayout(au)

    def _yt(self):
        q=self.ytInput.text().strip() or "learning for kids"
        webbrowser.open("https://www.youtube.com/results?search_query="+urllib.parse.quote(q))

    def show_task(self, task):
        self.cur=task
        self.badge.setText(f"{task.get('protocol','ABA')}  L1")
        self.prompt.setText(task.get("instruction",""))
        self.sub.setText(f"{task.get('name','')} · {task.get('domain','')}")
        # clear grid
        while self.gridLay.count():
            it=self.gridLay.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        if task.get("type") in ("grid","obj_grid","color_grid","letter"):
            self.bigEm.hide(); self.bigTxt.hide(); self.doNow.hide(); self.grid.show()
            for i,o in enumerate(task["options"]):
                b=QPushButton()
                if isinstance(o,dict):
                    b.setText(f"{o.get('em','')}\n{o.get('label','')}")
                else:
                    b.setText(str(o))
                b.setMinimumHeight(110)
                b.setStyleSheet("QPushButton{background:#1a2236;color:#e8edf7;border:2px solid #2d3a52;"
                    "border-radius:16px;font-size:30px;font-weight:bold;}"
                    "QPushButton:hover{background:#7c3aed;border-color:#a855f7;}")
                b.clicked.connect(lambda _,idx=i: self.answer.emit(idx==task["correct"]))
                self.gridLay.addWidget(b,i//2,i%2)
        else:
            self.grid.hide()
            self.bigEm.show(); self.bigTxt.show(); self.doNow.show()
            self.bigEm.setText(task.get("em","🎯"))
            self.bigTxt.setText(task.get("instruction",""))
            self.doNow.setText("👉 DO IT NOW!")

"""AAC Sentence Builder + Visual First-Then Schedule for ASD.
© 2026 Lamya Fadlulmola Hamed Ali"""
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
                             QFrame, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal
CORE_WORDS=[("I","👤"),("want","🤲"),("more","➕"),("help","🆘"),("go","🏃"),("stop","✋"),
("eat","🍽"),("drink","🥤"),("play","🧸"),("yes","✅"),("no","❌"),("please","🙏")]
FRINGE_WORDS=[("water","💧"),("food","🍎"),("toy","🧸"),("book","📖"),("music","🎵"),("break","⏸"),
("toilet","🚽"),("home","🏠"),("mum","👩"),("dad","👨"),("ball","⚽"),("hug","🤗")]
class AACSentenceBuilder(QWidget):
    speak_sentence=pyqtSignal(str)
    def __init__(self):
        super().__init__(); self.words=[]; self._build()
    def _build(self):
        self.setStyleSheet("background:#0a0e1a;")
        v=QVBoxLayout(self); v.setContentsMargins(10,10,10,10); v.setSpacing(8)
        title=QLabel("🗣️ Build a Sentence — tap the words")
        title.setStyleSheet("color:#e8edf7;font-size:16px;font-weight:bold;"); v.addWidget(title)
        self.strip=QLabel("…"); self.strip.setMinimumHeight(56)
        self.strip.setStyleSheet("background:#121829;color:#fde047;border:1px solid #243049;"
            "border-radius:10px;padding:10px;font-size:20px;font-weight:bold;"); v.addWidget(self.strip)
        row=QHBoxLayout()
        spk=QPushButton("🔊 Speak"); spk.setStyleSheet("background:#10b981;color:white;border:none;border-radius:8px;padding:8px 16px;font-weight:bold;")
        spk.clicked.connect(self._speak)
        back=QPushButton("⌫ Back"); back.setStyleSheet("background:#1a2236;color:#e8edf7;border:1px solid #243049;border-radius:8px;padding:8px 14px;")
        back.clicked.connect(self._back)
        clr=QPushButton("🧹 Clear"); clr.setStyleSheet("background:#1a2236;color:#e8edf7;border:1px solid #243049;border-radius:8px;padding:8px 14px;")
        clr.clicked.connect(self._clear)
        row.addWidget(spk); row.addWidget(back); row.addWidget(clr); row.addStretch(); v.addLayout(row)
        cl=QLabel("Core words"); cl.setStyleSheet("color:#8b96ad;font-size:11px;"); v.addWidget(cl)
        cg=QGridLayout(); cg.setSpacing(5)
        for i,(w,em) in enumerate(CORE_WORDS): cg.addWidget(self._word_btn(w,em,"#1e3a5f"),i//6,i%6)
        v.addLayout(cg)
        fl=QLabel("Things"); fl.setStyleSheet("color:#8b96ad;font-size:11px;"); v.addWidget(fl)
        fg=QGridLayout(); fg.setSpacing(5)
        for i,(w,em) in enumerate(FRINGE_WORDS): fg.addWidget(self._word_btn(w,em,"#3b2f5f"),i//6,i%6)
        v.addLayout(fg)
    def _word_btn(self,word,em,color):
        b=QPushButton(f"{em}\n{word}"); b.setFixedSize(72,64)
        b.setStyleSheet(f"background:{color};color:#e8edf7;border:1px solid #243049;border-radius:10px;font-size:11px;font-weight:bold;")
        b.clicked.connect(lambda: self._add(word)); return b
    def _add(self,word): self.words.append(word); self.strip.setText(" ".join(self.words))
    def _back(self):
        if self.words: self.words.pop(); self.strip.setText(" ".join(self.words) or "…")
    def _clear(self): self.words=[]; self.strip.setText("…")
    def _speak(self):
        if self.words: self.speak_sentence.emit(" ".join(self.words))
class FirstThenBoard(QWidget):
    def __init__(self): super().__init__(); self._build()
    def _build(self):
        self.setStyleSheet("background:transparent;")
        h=QHBoxLayout(self); h.setContentsMargins(4,4,4,4); h.setSpacing(8)
        self.first=self._slot("First","#1a2236")
        arrow=QLabel("➡"); arrow.setStyleSheet("color:#7c3aed;font-size:22px;font-weight:bold;")
        self.then=self._slot("Then","#1a2236")
        h.addWidget(self.first["box"]); h.addWidget(arrow); h.addWidget(self.then["box"])
    def _slot(self,label,color):
        box=QFrame(); box.setStyleSheet(f"background:{color};border:1px solid #243049;border-radius:10px;")
        box.setFixedSize(130,76); v=QVBoxLayout(box); v.setContentsMargins(6,4,6,4); v.setSpacing(0)
        lab=QLabel(label); lab.setStyleSheet("color:#8b96ad;font-size:10px;font-weight:bold;")
        lab.setAlignment(Qt.AlignmentFlag.AlignCenter)
        em=QLabel("🎯"); em.setStyleSheet("font-size:24px;"); em.setAlignment(Qt.AlignmentFlag.AlignCenter)
        txt=QLabel("—"); txt.setStyleSheet("color:#e8edf7;font-size:10px;")
        txt.setAlignment(Qt.AlignmentFlag.AlignCenter); txt.setWordWrap(True)
        v.addWidget(lab); v.addWidget(em); v.addWidget(txt)
        return {"box":box,"em":em,"txt":txt}
    def set_schedule(self,current_task,next_task):
        if current_task:
            self.first["em"].setText(current_task.get("em","🎯")); self.first["txt"].setText(current_task.get("name","")[:18])
        if next_task:
            self.then["em"].setText(next_task.get("em","🎁")); self.then["txt"].setText(next_task.get("name","")[:18])
        else:
            self.then["em"].setText("🎉"); self.then["txt"].setText("Reward!")

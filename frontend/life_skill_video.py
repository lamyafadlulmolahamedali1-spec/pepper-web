"""Daily life-skill step-by-step videos for ASD kids. Shown every 7 tasks.
Kid-safe YouTube (SafeSearch). © 2026 Lamya F. H. Ali"""
import random, urllib.parse, webbrowser
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt
LIFE_SKILLS=[
 ("🦷 Brush Teeth","brushing teeth step by step song for kids",
  ["Wet the toothbrush","Add a pea-size toothpaste","Brush top teeth in small circles",
   "Brush bottom teeth","Brush the tongue gently","Spit and rinse"]),
 ("🧼 Wash Hands","washing hands step by step song for kids",
  ["Wet hands with water","Add soap","Rub palms together","Wash between fingers","Rinse","Dry with a towel"]),
 ("😊 Wash Face","washing face step by step for kids",
  ["Wet your face","Add gentle soap","Rub in circles","Rinse with water","Pat dry"]),
 ("🍽 Eat with a Spoon","using a spoon to eat step by step toddler",
  ["Hold the spoon","Scoop the food","Lift slowly","Open mouth","Eat","Chew well"]),
 ("📖 Read a Book","how to read a picture book for kids",
  ["Open the book","Look at the picture","Point to the word","Say the word","Turn the page"]),
 ("🧥 Get Dressed","getting dressed step by step for kids",
  ["Pick your shirt","Put arms in","Pull over head","Put on pants","One leg then the other"]),
 ("👟 Put on Shoes","putting on shoes step by step for kids",
  ["Loosen the shoe","Slide your foot in","Pull the back up","Fix the straps"]),
 ("🚽 Use the Toilet","potty training steps for kids song",
  ["Go to the toilet","Pull pants down","Sit or stand","Use toilet","Wipe","Flush","Wash hands"]),
 ("💧 Drink from a Cup","drinking from a cup step by step toddler",
  ["Hold the cup","Lift to your mouth","Sip slowly","Put it down"]),
 ("🧹 Clean Up Toys","clean up toys song for kids",
  ["Pick up a toy","Put it in the box","Repeat","All done!"]),
 ("👋 Say Hello","greeting people social skills for kids",
  ["Look at the person","Smile","Wave","Say hello"]),
 ("✋ Ask for Help","teaching kids to ask for help social story",
  ["Raise your hand","Look at the helper","Say: help please","Wait calmly"]),
]
def _safe_youtube(q):
    return ("https://www.youtube.com/results?search_query="+urllib.parse.quote(q+" for kids")+"&safe=active")
class LifeSkillVideoDialog(QDialog):
    def __init__(self, parent=None, skill=None):
        super().__init__(parent)
        self.setWindowTitle("Daily Life Skill — Step by Step")
        self.resize(620,540); self.skill=skill or random.choice(LIFE_SKILLS); self._build()
    def _build(self):
        self.setStyleSheet("background:#0a0e1a;")
        v=QVBoxLayout(self); v.setContentsMargins(16,16,16,16); v.setSpacing(10)
        title=QLabel(f"{self.skill[0]} — let's learn together!")
        title.setStyleSheet("color:#e8edf7;font-size:20px;font-weight:bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter); v.addWidget(title)
        hint=QLabel("Watch the steps, then try it yourself! 🌟")
        hint.setStyleSheet("color:#8b96ad;font-size:12px;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter); v.addWidget(hint)
        steps=QListWidget()
        steps.setStyleSheet("background:#121829;color:#e8edf7;border:1px solid #243049;"
            "border-radius:10px;font-size:15px;padding:6px;")
        for i,step in enumerate(self.skill[2],1): steps.addItem(QListWidgetItem(f"  {i}.  {step}"))
        v.addWidget(steps,1)
        try:
            from PyQt6.QtWebEngineWidgets import QWebEngineView
            from PyQt6.QtCore import QUrl
            self._web=QWebEngineView(); self._web.setMinimumHeight(180)
            self._web.setUrl(QUrl(_safe_youtube(self.skill[1]))); v.addWidget(self._web,1)
        except Exception:
            note=QLabel("Tap 'Watch Video' to open a kid-safe video in your browser.")
            note.setStyleSheet("color:#8b96ad;font-size:11px;")
            note.setAlignment(Qt.AlignmentFlag.AlignCenter); v.addWidget(note)
        watch=QPushButton("▶ Watch Video (kid-safe)")
        watch.setStyleSheet("background:#ef4444;color:white;border:none;border-radius:8px;padding:10px;font-weight:bold;")
        watch.clicked.connect(lambda: webbrowser.open(_safe_youtube(self.skill[1]))); v.addWidget(watch)
        row=QHBoxLayout()
        another=QPushButton("🔀 Another Skill")
        another.setStyleSheet("background:#1a2236;color:#e8edf7;border:1px solid #243049;border-radius:8px;padding:8px;")
        another.clicked.connect(self._another)
        close=QPushButton("✅ Got it — back to tasks")
        close.setStyleSheet("background:#10b981;color:white;border:none;border-radius:8px;padding:10px;font-weight:bold;")
        close.clicked.connect(self.accept)
        row.addWidget(another); row.addWidget(close); v.addLayout(row)
        cr=QLabel("© 2026 Lamya Fadlulmola Hamed Ali — Pepper Clinical Infinity V6")
        cr.setStyleSheet("color:#5b6478;font-size:8px;")
        cr.setAlignment(Qt.AlignmentFlag.AlignCenter); v.addWidget(cr)
    def _another(self):
        self.skill=random.choice(LIFE_SKILLS)
        for i in reversed(range(self.layout().count())):
            w=self.layout().itemAt(i).widget()
            if w: w.deleteLater()
        self._build()

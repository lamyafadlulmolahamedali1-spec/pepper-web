"""Calm-music button with a popup track MENU. © 2026 Lamya F. H. Ali"""
from PyQt6.QtWidgets import QPushButton, QMenu
from PyQt6.QtGui import QAction
from calm_music import CalmMusic
class MusicButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__("🎵 Calm Music", parent)
        self.music=CalmMusic()
        self.setStyleSheet("background:#1a2236;color:#e8edf7;border:1px solid #243049;"
            "border-radius:10px;padding:8px 14px;font-weight:bold;")
        self.clicked.connect(self._open_menu)
    def _open_menu(self):
        menu=QMenu(self)
        menu.setStyleSheet("QMenu{background:#121829;color:#e8edf7;border:1px solid #243049;}"
            "QMenu::item:selected{background:#7c3aed;}")
        for name in self.music.tracks():
            act=QAction(("🔊 " if self.music.current==name else "🎵 ")+name, self)
            act.triggered.connect(lambda _,n=name: self._choose(n)); menu.addAction(act)
        menu.addSeparator()
        stop=QAction("⏹ Stop music", self); stop.triggered.connect(self._stop); menu.addAction(stop)
        menu.exec(self.mapToGlobal(self.rect().topLeft()))
    def _choose(self,name):
        ok=self.music.play(name); self.setText(f"🎵 {name}" if ok else "🎵 Calm Music")
    def _stop(self):
        self.music.stop(); self.setText("🎵 Calm Music")

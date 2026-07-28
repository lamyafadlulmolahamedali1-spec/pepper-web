"""
Pepper Clinical Infinity V6 — Main Desktop App (PyQt6)
© 2026 Lamya Fadlulmola Hamed Ali — All Rights Reserved
Login → Home (children) → Live Session → Dashboard
"""
import os, sys

# _ASD_IMAGES_INJECTED
def _asd_image_strip_app():
    row = QHBoxLayout(); row.setSpacing(8)
    here = os.path.dirname(os.path.abspath(__file__))
    for fn in ('autism.jpeg', 'images.jpeg', 'images1.jpeg'):
        path = os.path.join(here, fn)
        lbl = QLabel()
        if os.path.exists(path):
            pix = QPixmap(path)
            if not pix.isNull():
                pix = pix.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                  Qt.TransformationMode.SmoothTransformation)
                lbl.setPixmap(pix)
        lbl.setFixedSize(80, 80)
        lbl.setStyleSheet('border-radius:10px;border:1px solid #ddd;')
        lbl.setScaledContents(True)
        row.addWidget(lbl)
    row.addStretch()
    return row
from PyQt6.QtGui import QPixmap

# safety env guards (prevent TF/Qt clashes seen with mediapipe)
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("MEDIAPIPE_DISABLE_GPU", "1")
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("QT_LOGGING_RULES", "*.debug=false")

from PyQt6.QtWidgets import (QApplication, QMainWindow, QStackedWidget, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QScrollArea, QInputDialog,
    QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

import theme as T
from api_client import ApiClient
from login_screen import LoginScreen
from session_screen import SessionScreen
from dashboard import Dashboard

try:
    from pecs_bar import probe_tts
    probe_tts()  # disable TTS safely if espeak is broken
except Exception:
    pass


class HomeScreen(QWidget):
    def __init__(self, app_state, api, on_session, on_dashboard, on_logout):
        super().__init__()
        self.api=api; self.on_session=on_session
        self.on_dashboard=on_dashboard; self.on_logout=on_logout
        self._build()

    def _build(self):
        self.setStyleSheet(f"background:{T.LIGHT_BG};")
        v=QVBoxLayout(self); v.setContentsMargins(20,18,20,18); v.setSpacing(12)
        top=QHBoxLayout()
        t=QLabel("🤖 Pepper Clinical V6 — Children")
        t.setStyleSheet(f"color:{T.INK};font-size:20px;font-weight:bold;")
        top.addWidget(t); top.addStretch()
        bAdd=QPushButton("➕ Add Child")
        bAdd.setStyleSheet(f"background:{T.TEAL};color:white;border:none;border-radius:8px;padding:8px 16px;font-weight:bold;")
        bAdd.clicked.connect(self._add)
        bOut=QPushButton("Logout")
        bOut.setStyleSheet(f"background:white;color:{T.RED};border:1px solid {T.RED};border-radius:8px;padding:8px 16px;")
        bOut.clicked.connect(self.on_logout)
        top.addWidget(bAdd); top.addWidget(bOut)
        v.addLayout(top)
        v.addLayout(_asd_image_strip_app())
        self.scroll=QScrollArea(); self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border:none;")
        v.addWidget(self.scroll,1)
        cr=QLabel(T.COPYRIGHT); cr.setStyleSheet(f"color:{T.MUTE};font-size:9px;")
        v.addWidget(cr)

    def refresh(self):
        inner=QWidget(); lay=QVBoxLayout(inner); lay.setSpacing(8)
        kids=self.api.list_children()
        if not kids:
            lay.addWidget(QLabel("No children yet — click 'Add Child'."))
        for c in kids:
            f=QFrame(); f.setStyleSheet(f"background:{T.CARD};border:1px solid {T.CARD_BORDER};border-radius:12px;")
            h=QHBoxLayout(f)
            nm=QLabel(f"  {c['name']}")
            nm.setStyleSheet(f"color:{T.INK};font-size:16px;font-weight:bold;")
            info=QLabel(f"Age {c.get('age','')} · {c.get('total_sessions',0)} sessions · {c.get('total_score',0)} pts")
            info.setStyleSheet(f"color:{T.MUTE};font-size:12px;")
            h.addWidget(nm); h.addWidget(info,1)
            bSess=QPushButton("▶ Start Session")
            bSess.setStyleSheet(f"background:{T.PURPLE};color:white;border:none;border-radius:8px;padding:7px 14px;font-weight:bold;")
            bSess.clicked.connect(lambda _,ch=c: self.on_session(ch))
            bDash=QPushButton("📊 Dashboard")
            bDash.setStyleSheet(f"background:white;color:{T.PURPLE};border:1px solid {T.PURPLE};border-radius:8px;padding:7px 14px;font-weight:bold;")
            bDash.clicked.connect(lambda _,ch=c: self.on_dashboard(ch))
            h.addWidget(bSess); h.addWidget(bDash)
            lay.addWidget(f)
        lay.addStretch()
        self.scroll.setWidget(inner)

    def _add(self):
        name,ok=QInputDialog.getText(self,"Add Child","Child name:")
        if not ok or not name.strip(): return
        age,ok2=QInputDialog.getInt(self,"Add Child","Age:",6,2,18)
        if not ok2: return
        self.api.add_child(name.strip(), age)
        self.refresh()


class PepperMain(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pepper Clinical Infinity V6")
        self.resize(1280, 800)
        self.live={}; self.last_summary={}
        self.api=ApiClient()

        self.stack=QStackedWidget(); self.setCentralWidget(self.stack)
        self.login=LoginScreen(self.api)
        self.home=HomeScreen(self, self.api, self._open_session, self._open_dashboard, self._logout)
        self.session=SessionScreen(self, self.api)
        self.dash=Dashboard(self, self.api)
        for w in (self.login, self.home, self.session, self.dash):
            self.stack.addWidget(w)

        self.login.logged_in.connect(self._after_login)
        self.session.finished.connect(self._after_session)
        self.dash.back.connect(lambda: self.stack.setCurrentWidget(self.home))
        self.stack.setCurrentWidget(self.login)

    def _after_login(self):
        self.home.refresh(); self.stack.setCurrentWidget(self.home)
    def _open_session(self, child):
        active_child = getattr(self.session, "child", None)
        is_same_active = (active_child is not None and
                           active_child.get("id") == child.get("id") and
                           getattr(self.session, "_active", False))
        self.stack.setCurrentWidget(self.session)
        if not is_same_active:
            self.session.start(child)
        # else: resume — just show the running session, no reset
    def _after_session(self):
        self.last_summary=self.session._summary()
        self.home.refresh(); self.stack.setCurrentWidget(self.home)
    def _open_dashboard(self, child):
        self.dash.open_for(child); self.stack.setCurrentWidget(self.dash)
    def _logout(self):
        self.api.token=None; self.api.user=None
        self.stack.setCurrentWidget(self.login)


def main():
    app=QApplication(sys.argv)
    app.setFont(QFont("Arial",10))
    win=PepperMain(); win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

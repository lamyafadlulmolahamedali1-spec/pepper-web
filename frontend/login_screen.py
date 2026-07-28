"""Login / Trial / Subscribe screen. © 2026 Lamya F. H. Ali"""
import webbrowser
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QSpinBox, QComboBox, QMessageBox, QTabWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
import os as _os

# _ASD_IMAGES_INJECTED
def _asd_image_strip(parent_width=460):
    row = QHBoxLayout(); row.setSpacing(8)
    here = _os.path.dirname(_os.path.abspath(__file__))
    for fn in ('autism.jpeg', 'images.jpeg'):  # only 2 images, dedicated space
        path = _os.path.join(here, fn)
        lbl = QLabel()
        if _os.path.exists(path):
            pix = QPixmap(path)
            if not pix.isNull():
                pix = pix.scaled(90, 90, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                  Qt.TransformationMode.SmoothTransformation)
                lbl.setPixmap(pix)
        lbl.setFixedSize(90, 90)
        lbl.setStyleSheet('border-radius:10px;border:1px solid #ddd;')
        lbl.setScaledContents(True)
        row.addWidget(lbl)
    return row
import theme as T


class LoginScreen(QWidget):
    logged_in=pyqtSignal()

    def __init__(self, api):
        super().__init__()
        self.api=api; self._build()

    def _build(self):
        self.setStyleSheet(f"background:{T.LIGHT_BG};")
        outer=QVBoxLayout(self); outer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        box=QFrame(); box.setFixedWidth(460)
        box.setStyleSheet(f"background:{T.CARD};border:1px solid {T.CARD_BORDER};border-radius:18px;")
        v=QVBoxLayout(box); v.setContentsMargins(34,30,34,30); v.setSpacing(12)

        logo=QLabel("🤖"); logo.setStyleSheet("font-size:52px;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter); v.addWidget(logo)
        v.addLayout(_asd_image_strip())
        title=QLabel("Pepper Clinical Infinity V6")
        title.setStyleSheet(f"color:{T.INK};font-size:20px;font-weight:bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter); v.addWidget(title)

        tabs=QTabWidget()
        tabs.setStyleSheet("QTabBar::tab{padding:8px 16px;}")

        # ---- Login ----
        lw=QWidget(); lv=QVBoxLayout(lw)
        self.lEmail=self._inp("Email"); self.lPin=self._inp("PIN", pw=True)
        lv.addWidget(self.lEmail); lv.addWidget(self.lPin)
        bLogin=QPushButton("Login")
        bLogin.setStyleSheet(self._btn(T.PURPLE)); bLogin.clicked.connect(self._login)
        lv.addWidget(bLogin)
        tabs.addTab(lw,"Login")

        # ---- Free Trial ----
        tw=QWidget(); tv=QVBoxLayout(tw)
        self.tName=self._inp("Your name"); self.tEmail=self._inp("Email")
        self.tChild=self._inp("Child name")
        self.tAge=QSpinBox(); self.tAge.setRange(2,18); self.tAge.setValue(6)
        self.tAge.setStyleSheet(f"padding:8px;border:1px solid {T.CARD_BORDER};border-radius:8px;")
        tv.addWidget(self.tName); tv.addWidget(self.tEmail); tv.addWidget(self.tChild)
        tv.addWidget(QLabel("Child age")); tv.addWidget(self.tAge)
        bTrial=QPushButton("Start 15-Day Free Trial")
        bTrial.setStyleSheet(self._btn(T.TEAL)); bTrial.clicked.connect(self._trial)
        tv.addWidget(bTrial)
        tabs.addTab(tw,"Free Trial")

        # ---- Subscribe ----
        sw=QWidget(); sv=QVBoxLayout(sw)
        self.sEmail=self._inp("Email")
        self.sPlan=QComboBox()
        self.sPlan.addItems(["Individual — Monthly (£49)","Individual — Yearly (£399)",
            "Institution 10 — Monthly (£399)","Institution 10 — Yearly (£3990)"])
        self.sPlan.setStyleSheet(f"padding:8px;border:1px solid {T.CARD_BORDER};border-radius:8px;")
        sv.addWidget(self.sEmail); sv.addWidget(QLabel("Plan")); sv.addWidget(self.sPlan)
        bSub=QPushButton("Subscribe with Stripe 💳")
        bSub.setStyleSheet(self._btn(T.PURPLE2)); bSub.clicked.connect(self._subscribe)
        sv.addWidget(bSub)
        tabs.addTab(sw,"Subscribe")

        v.addWidget(tabs)
        cr=QLabel(T.COPYRIGHT); cr.setStyleSheet(f"color:{T.MUTE};font-size:8px;")
        cr.setAlignment(Qt.AlignmentFlag.AlignCenter); v.addWidget(cr)
        outer.addWidget(box)

    def _inp(self, ph, pw=False):
        e=QLineEdit(); e.setPlaceholderText(ph)
        if pw: e.setEchoMode(QLineEdit.EchoMode.Password)
        e.setStyleSheet(f"padding:9px;border:1px solid {T.CARD_BORDER};border-radius:8px;font-size:13px;")
        return e
    def _btn(self,c): return (f"background:{c};color:white;border:none;border-radius:8px;"
                              f"padding:10px;font-weight:bold;font-size:14px;")

    def _login(self):
        d=self.api.login(self.lEmail.text().strip(), self.lPin.text().strip())
        if d.get("user") or d.get("access_token"):
            self.logged_in.emit()
        else:
            QMessageBox.warning(self,"Login", d.get("detail","Login failed"))

    def _trial(self):
        import secrets
        email=self.tEmail.text().strip().lower()
        if not email or "@" not in email:
            QMessageBox.warning(self,"Trial","Please enter a valid email."); return
        # unique, secure 6-digit PIN per user
        pin=str(secrets.randbelow(900000)+100000)
        try: self.api._init_local()
        except Exception: pass
        c=self.api.db.cursor()
        # prevent duplicate email
        existing=c.execute("SELECT id FROM users WHERE email=?",(email,)).fetchone()
        if existing:
            QMessageBox.warning(self,"Trial",
                "This email already has an account. Please use the Login tab, "
                "or use a different email for a new trial."); return
        try:
            uid=secrets.token_hex(8)
            c.execute("INSERT INTO users VALUES(?,?,?,?,?,?)",
                (uid, self.tName.text().strip() or "Parent", email,
                 self.api._h(pin), "trial", ""))
            cid=secrets.token_hex(8)
            c.execute("INSERT INTO children(id,parent,name,age) VALUES(?,?,?,?)",
                (cid, uid, self.tChild.text().strip() or "Child", self.tAge.value()))
            self.api.db.commit()
        except Exception as e:
            QMessageBox.warning(self,"Trial", f"Could not create trial: {e}"); return
        self.lEmail.setText(email); self.lPin.setText(pin)
        QMessageBox.information(self,"Trial Ready",
            f"Welcome! Your trial is ready.\n\n"
            f"Email: {email}\nYour PIN: {pin}\n\n"
            f"IMPORTANT: Write down your PIN — it is unique to you.\n"
            f"I've filled the Login tab — just press Login.")

    def _subscribe(self):
        plans=["individual_monthly","individual_yearly","institution_monthly","institution_yearly"]
        plan=plans[self.sPlan.currentIndex()]
        url=self.api.checkout_url(plan, self.sEmail.text().strip())
        if url: webbrowser.open(url)
        else: QMessageBox.information(self,"Subscribe",
            "Connect to the server to enable Stripe checkout.\n"
            "(Backend must be running with your Stripe keys.)")

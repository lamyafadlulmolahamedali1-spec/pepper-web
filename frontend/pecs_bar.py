"""Bottom PECS bar (50 daily symbols) + voice synth that changes Girl/Boy/Kids/Grandma.
© 2026 Lamya F. H. Ali"""
import threading
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QScrollArea
from PyQt6.QtCore import Qt, pyqtSignal
import theme as T

# ---- Voice synth that actually changes by selection ----
_HAS_TTS=False
try:
    import pyttsx3
    _HAS_TTS=True
except Exception:
    _HAS_TTS=False

_lock=threading.Lock()
_VOICE="Girl"
# pitch/rate presets per persona
_VOICE_PRESETS={
    "Girl":   {"rate":170,"pitch_pref":"female"},
    "Boy":    {"rate":160,"pitch_pref":"male"},
    "Kids":   {"rate":190,"pitch_pref":"female"},
    "Grandma":{"rate":130,"pitch_pref":"female"},
}

def set_voice(name): 
    global _VOICE
    _VOICE=name if name in _VOICE_PRESETS else "Girl"

def probe_tts():
    """Disable TTS safely if espeak is broken (prevents segfault)."""
    global _HAS_TTS
    if not _HAS_TTS: return
    try:
        import multiprocessing as mp
        def _t():
            import pyttsx3 as t; e=t.init(); e.say(" "); e.runAndWait(); e.stop()
        p=mp.Process(target=_t); p.start(); p.join(timeout=4)
        if p.exitcode!=0:
            _HAS_TTS=False
            if p.is_alive(): p.terminate()
    except Exception:
        _HAS_TTS=False

def speak(text):
    if not _HAS_TTS: return
    persona=_VOICE_PRESETS.get(_VOICE,_VOICE_PRESETS["Girl"])
    def _run():
        if not _lock.acquire(blocking=False): return
        try:
            import pyttsx3 as t
            e=t.init(); e.setProperty("rate",persona["rate"])
            # pick a matching system voice (male/female) if available
            try:
                for v in e.getProperty("voices"):
                    nm=(v.name or "").lower()
                    if persona["pitch_pref"]=="female" and ("female" in nm or "f5" in nm or "woman" in nm):
                        e.setProperty("voice",v.id); break
                    if persona["pitch_pref"]=="male" and ("male" in nm or "m1" in nm or "man" in nm):
                        e.setProperty("voice",v.id); break
            except Exception: pass
            e.say(text); e.runAndWait()
            try: e.stop()
            except Exception: pass
        except Exception: pass
        finally: _lock.release()
    threading.Thread(target=_run,daemon=True).start()


class PecsBar(QWidget):
    pecs_clicked=pyqtSignal(str, str)  # label, "label: phrase"

    def __init__(self):
        super().__init__()
        lay=QHBoxLayout(self); lay.setContentsMargins(4,4,4,4); lay.setSpacing(0)
        scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setFixedHeight(64)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        inner=QWidget(); row=QHBoxLayout(inner); row.setContentsMargins(2,2,2,2); row.setSpacing(4)
        for label,em in T.PECS:
            b=QPushButton(f"{em}\n{label}")
            b.setFixedSize(58,54)
            b.setStyleSheet(f"background:{T.DARK_PANEL2};color:{T.DARK_TEXT};"
                f"border:1px solid {T.DARK_BORDER};border-radius:8px;font-size:9px;")
            lab_l=label.lower()
            _AM_WORDS=("hungry","thirsty","tired","happy","sad","sick","hot","cold","scared","bored")
            _WANT_WORDS=("water","food","toilet","break","toy","music","hug","help","more","play","book","ball")
            if label in ("Yes","No","Please","Thanks","Hello","Bye"):
                phrase=label
            elif lab_l in _AM_WORDS:
                phrase=f"I am {lab_l}"
            elif lab_l=="toilet":
                phrase="I want the toilet"
            elif lab_l in _WANT_WORDS:
                phrase=f"I want {lab_l}"
            else:
                phrase=f"I want {lab_l}"
            b.clicked.connect(lambda _,l=label,p=phrase: (self.pecs_clicked.emit(l,f"{l}: {p}"), speak(p)))
            row.addWidget(b)
        scroll.setWidget(inner)
        lay.addWidget(scroll)

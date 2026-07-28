"""Calm background music + success chime (generated in code, no external files).
© 2026 Lamya Fadlulmola Hamed Ali"""
import math, struct, wave, os, tempfile, threading

_TMP = tempfile.gettempdir()

def _write_wav(path, samples, sr=22050):
    with wave.open(path, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(b"".join(struct.pack("<h", max(-32768, min(32767, int(s)))) for s in samples))

def _gen_chime():
    """short happy 3-note success chime."""
    sr=22050; out=[]
    for freq in (660, 880, 1320):  # E5, A5, E6
        for i in range(int(sr*0.14)):
            t=i/sr; out.append(math.sin(2*math.pi*freq*t)*math.exp(-6*t)*26000)
    return out, sr

def _gen_calm(seconds=30):
    """soft looping calm pad — gentle sine chords, low volume."""
    sr=22050; out=[]; n=int(sr*seconds)
    chords=[(261.63,329.63,392.0),(293.66,349.23,440.0),(220.0,277.18,329.63),(246.94,311.13,392.0)]
    seg=n//len(chords)
    for ci,ch in enumerate(chords):
        for i in range(seg):
            t=i/sr; env=0.5*(1-math.cos(2*math.pi*i/seg))  # smooth fade in/out
            s=sum(math.sin(2*math.pi*f*t) for f in ch)/len(ch)
            out.append(s*env*9000)
    return out, sr

_CHIME=os.path.join(_TMP,"pepper_chime.wav")
_CALM=os.path.join(_TMP,"pepper_calm.wav")
try:
    if not os.path.exists(_CHIME): s,sr=_gen_chime(); _write_wav(_CHIME,s,sr)
    if not os.path.exists(_CALM):  s,sr=_gen_calm();  _write_wav(_CALM,s,sr)
except Exception:
    _CHIME=_CALM=None

# ---- chime ----
def play_chime():
    if not _CHIME: return
    try:
        from PyQt6.QtMultimedia import QSoundEffect
        from PyQt6.QtCore import QUrl
        global _ce; _ce=QSoundEffect(); _ce.setSource(QUrl.fromLocalFile(_CHIME))
        _ce.setVolume(0.7); _ce.play()
    except Exception:
        try:
            import subprocess; subprocess.Popen(["aplay",_CHIME],
                stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        except Exception: pass

# ---- calm music (loop on/off) ----
class CalmMusic:
    def __init__(self):
        self._player=None; self._on=False
    def toggle(self):
        self._on = not self._on
        self.play() if self._on else self.stop()
        return self._on
    def play(self):
        if not _CALM: return
        try:
            from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
            from PyQt6.QtCore import QUrl
            self._out=QAudioOutput(); self._out.setVolume(0.35)
            self._player=QMediaPlayer(); self._player.setAudioOutput(self._out)
            self._player.setSource(QUrl.fromLocalFile(_CALM))
            try: self._player.setLoops(QMediaPlayer.Loops.Infinite)
            except Exception: pass
            self._player.play(); self._on=True
        except Exception:
            self._on=False
    def stop(self):
        try:
            if self._player: self._player.stop()
        except Exception: pass
        self._on=False
    @property
    def on(self): return self._on

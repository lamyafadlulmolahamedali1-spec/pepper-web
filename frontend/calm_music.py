"""Calm music library for ASD children — multiple tracks generated in code.
© 2026 Lamya Fadlulmola Hamed Ali"""
import math, struct, wave, os, tempfile
_TMP=tempfile.gettempdir()
def _write_wav(path,samples,sr=22050):
    with wave.open(path,"w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(b"".join(struct.pack("<h",max(-32768,min(32767,int(s)))) for s in samples))
def _adsr(i,n):
    a=int(n*0.15); r=int(n*0.2)
    if i<a: return i/a
    if i>n-r: return max(0.0,(n-i)/r)
    return 1.0
def _tone_track(seconds,chords,sr=22050,vol=9000):
    out=[]; n=int(sr*seconds); seg=n//len(chords)
    for ch in chords:
        for i in range(seg):
            t=i/sr; s=sum(math.sin(2*math.pi*f*t) for f in ch)/len(ch)
            out.append(s*_adsr(i,seg)*vol)
    return out,sr
TRACKS={
 "Gentle Waves":[(261.63,329.63,392.0),(293.66,349.23,440.0),(220.0,277.18,329.63),(246.94,311.13,392.0)],
 "Sleepy Stars":[(196.0,246.94,293.66),(174.61,220.0,261.63),(164.81,207.65,246.94),(146.83,185.0,220.0)],
 "Soft Rain":[(329.63,392.0,493.88),(293.66,349.23,440.0),(261.63,311.13,392.0),(246.94,293.66,349.23)],
 "Quiet Garden":[(220.0,261.63,329.63),(246.94,293.66,349.23),(261.63,329.63,392.0),(196.0,246.94,293.66)],
}
_files={}
def _ensure(track):
    if track in _files and os.path.exists(_files[track]): return _files[track]
    path=os.path.join(_TMP,f"pepper_calm_{abs(hash(track))%99999}.wav")
    try:
        s,sr=_tone_track(28,TRACKS[track]); _write_wav(path,s,sr); _files[track]=path; return path
    except Exception: return None
_CHIME=os.path.join(_TMP,"pepper_chime.wav")
try:
    if not os.path.exists(_CHIME):
        ch=[]
        for fr in (660,880,1320):
            for i in range(int(22050*0.14)):
                t=i/22050; ch.append(math.sin(2*math.pi*fr*t)*math.exp(-6*t)*26000)
        _write_wav(_CHIME,ch)
except Exception: _CHIME=None
_CUE=os.path.join(_TMP,"pepper_cue.wav")
try:
    if not os.path.exists(_CUE):
        cu=[]
        for i in range(int(22050*0.25)):
            t=i/22050; cu.append(math.sin(2*math.pi*523.25*t)*math.exp(-4*t)*20000)
        _write_wav(_CUE,cu)
except Exception: _CUE=None
def _play_once(path,vol=0.7):
    if not path: return
    try:
        from PyQt6.QtMultimedia import QSoundEffect
        from PyQt6.QtCore import QUrl
        global _eff; _eff=QSoundEffect(); _eff.setSource(QUrl.fromLocalFile(path))
        _eff.setVolume(vol); _eff.play()
    except Exception:
        try:
            import subprocess; subprocess.Popen(["aplay",path],
                stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        except Exception: pass
def play_chime(): _play_once(_CHIME,0.7)
def play_cue(): _play_once(_CUE,0.5)
class CalmMusic:
    def __init__(self): self._player=None; self._out=None; self._on=False; self.current=None
    def tracks(self): return list(TRACKS.keys())
    def play(self,track):
        path=_ensure(track)
        if not path: return False
        try:
            from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
            from PyQt6.QtCore import QUrl
            self.stop()
            self._out=QAudioOutput(); self._out.setVolume(0.35)
            self._player=QMediaPlayer(); self._player.setAudioOutput(self._out)
            self._player.setSource(QUrl.fromLocalFile(path))
            try: self._player.setLoops(QMediaPlayer.Loops.Infinite)
            except Exception: pass
            self._player.play(); self._on=True; self.current=track; return True
        except Exception:
            self._on=False; return False
    def stop(self):
        try:
            if self._player: self._player.stop()
        except Exception: pass
        self._on=False; self.current=None
    @property
    def on(self): return self._on

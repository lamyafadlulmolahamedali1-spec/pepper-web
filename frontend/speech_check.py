"""Speech checker — uses `arecord` (native Linux tool) instead of PyAudio.
Far more stable: no ALSA/PyAudio/Qt-thread conflicts.
© 2026 Lamya Fadlulmola Hamed Ali"""
import subprocess, threading, json, os, time, tempfile, signal

class SpeechChecker:
    def __init__(self):
        self._model=None
        self._proc=None
        self._wav_path=None
        self._recording=False
        self._rate=16000
        self._ensure_model()

    def _ensure_model(self):
        if self._model is not None: return self._model
        try:
            from vosk import Model
            for d in [os.path.expanduser("~/.cache/vosk-model-small-en-us-0.15"),
                      os.path.expanduser("~/vosk-model-small-en-us-0.15")]:
                if os.path.exists(d):
                    self._model=Model(d); break
        except Exception as e:
            print("[speech] model load failed:", e)
            self._model=None
        return self._model

    def start_recording(self):
        try:
            self._wav_path=os.path.join(tempfile.gettempdir(), f"pepper_speak_{int(time.time()*1000)}.wav")
            # arecord: native ALSA recorder, very stable, runs as a separate OS process
            self._proc=subprocess.Popen(
                ["arecord", "-q", "-f", "S16_LE", "-r", str(self._rate), "-c", "1", "-D", "default", self._wav_path],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._recording=True
        except Exception as e:
            print("[speech] arecord start failed:", e)
            self._recording=False

    def stop_and_process(self, target_word, callback):
        def _finish():
            print("[speech] _finish START")
            text=""
            try:
                if self._proc is not None:
                    # graceful stop so the WAV header is finalized correctly
                    self._proc.send_signal(signal.SIGTERM)
                    try:
                        self._proc.wait(timeout=2.0)
                    except Exception:
                        self._proc.kill()
                self._recording=False
                time.sleep(0.15)  # let the filesystem flush the wav file
                print("[speech] arecord stopped, transcribing...")
                text=self._transcribe()
                print("[speech] transcribe done ->", repr(text))
            except Exception as e:
                print("[speech] processing error (caught):", e)
                text=""
            try:
                matched=self._matches(text, target_word)
            except Exception:
                matched=False
            print("[speech] calling callback with:", repr(text), matched)
            try:
                callback(text, matched)
            except Exception as e:
                print("[speech] callback error (caught):", e)
            finally:
                try:
                    if self._wav_path and os.path.exists(self._wav_path):
                        os.remove(self._wav_path)
                except Exception:
                    pass
        threading.Thread(target=_finish, daemon=True).start()

    def _transcribe(self):
        if not self._wav_path or not os.path.exists(self._wav_path):
            return ""
        if os.path.getsize(self._wav_path) < 100:
            return ""
        if self._model:
            try:
                import wave
                from vosk import KaldiRecognizer
                wf=wave.open(self._wav_path,"rb")
                rec=KaldiRecognizer(self._model, wf.getframerate())
                while True:
                    data=wf.readframes(4000)
                    if len(data)==0: break
                    rec.AcceptWaveform(data)
                res=json.loads(rec.FinalResult())
                return res.get("text","").strip()
            except Exception as e:
                print("[speech] vosk failed (caught):", e)
                return ""
        try:
            import speech_recognition as sr
            r=sr.Recognizer()
            with sr.AudioFile(self._wav_path) as source:
                audio=r.record(source)
            return r.recognize_google(audio)
        except Exception as e:
            print("[speech] transcribe fallback failed:", e)
            return ""

    def _matches(self, text, target_word):
        """Phonetic matching tuned for child speech — accepts близкое
        pronunciation but rejects clearly different words."""
        if not target_word: return False
        t=(text or "").lower().strip()
        w=target_word.lower().strip()
        if not t: return False

        for token in t.split():
            if token == w: return True
            # same start + similar length (child mispronunciation)
            if token[0]==w[0] and abs(len(token)-len(w))<=1:
                diff=sum(1 for a,b in zip(token,w) if a!=b)
                if diff<=1: return True
            # high letter overlap for short words
            if len(w)<=4 and len(token)<=5:
                common=len(set(token)&set(w))
                if common>=len(w)-0 and token[0]==w[0]: return True
            # edit distance <=1 for longer words
            if len(w)>4 and _edit(token,w)<=1: return True
        return False


    def cleanup(self):
        try:
            if self._proc: self._proc.kill()
        except Exception: pass

def _similar(a,b):
    if abs(len(a)-len(b))>2: return False
    diff=sum(1 for x,y in zip(a,b) if x!=y)+abs(len(a)-len(b))
    return diff<=2


def _edit(a,b):
    if abs(len(a)-len(b))>2: return 99
    prev=list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        cur=[i]
        for j,cb in enumerate(b,1):
            cur.append(min(prev[j]+1, cur[j-1]+1, prev[j-1]+(ca!=cb)))
        prev=cur
    return prev[-1]

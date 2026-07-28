"""Pepper voice — offline TTS so Pepper greets, narrates tasks, and encourages.
© 2026 Lamya Fadlulmola Hamed Ali"""
import threading, queue, random
_engine=None; _q=queue.Queue(); _worker=None; _VOICE_OK=False
def _ensure_engine():
    global _engine,_VOICE_OK
    if _engine is not None: return _engine
    try:
        import pyttsx3
        _engine=pyttsx3.init(); _engine.setProperty("rate",125); _engine.setProperty("volume",0.8)
        try:
            voices=_engine.getProperty("voices")
            chosen=None
            # prefer British English (softer than US robotic), then any English
            for v in voices:
                vid=(v.id or "").lower()
                if vid in ("gmw/en","english (great britain)") or vid.endswith("/en"):
                    chosen=v.id; break
            if not chosen:
                for v in voices:
                    if "/en" in (v.id or "").lower() or "english" in (v.name or "").lower():
                        chosen=v.id; break
            if chosen: _engine.setProperty("voice",chosen)
            # softer, gentler delivery for children
            _engine.setProperty("pitch",60)  # slightly higher = friendlier (espeak supports pitch)
        except Exception: pass
        _VOICE_OK=True
    except Exception: _engine=None; _VOICE_OK=False
    return _engine
def _run_worker():
    eng=_ensure_engine()
    if not eng: return
    while True:
        text=_q.get()
        if text is None: break
        try: eng.say(text); eng.runAndWait()
        except Exception: pass
def _start_worker():
    global _worker
    if _worker is None or not _worker.is_alive():
        _worker=threading.Thread(target=_run_worker,daemon=True); _worker.start()
def _gesture_while_talking(dur=2.0):
    try:
        import pepper_sim as PSIM, threading, time
        PSIM.set_speaking(True)
        def _off():
            time.sleep(dur); PSIM.set_speaking(False)
        threading.Thread(target=_off,daemon=True).start()
    except Exception: pass

def speak(text):
    _gesture_while_talking(max(1.5, len(str(text))*0.07))
    if not text: return
    _ensure_engine(); _start_worker()
    if _VOICE_OK:
        if _q.qsize()>3:
            try:
                while _q.qsize()>1: _q.get_nowait()
            except Exception: pass
        _q.put(str(text))
def greet():
    speak("Hello! I am Pepper, your friend and your therapist. Let's learn and play together today!")
def say_task(instruction): speak(instruction)
_PRAISE=["Great job! You did it!","Wonderful! I am so proud of you!","Yes! That is exactly right!",
"Amazing work, my friend!","You are doing so well!","Fantastic! Keep going!"]
_ENCOURAGE=["Let's try together. You can do it!","Almost there! Try one more time.",
"It's okay, take your time. I believe in you.","Good try! Let's do it again together."]
def praise(): speak(random.choice(_PRAISE))
def encourage(): speak(random.choice(_ENCOURAGE))
def is_available(): _ensure_engine(); return _VOICE_OK

# كود تلبية الاستدعاء المطلوب من المنظومة

class PepperVoiceWrapper:
    def greet(self):
        try:
            eng = _ensure_engine()
            eng.say("Hello, welcome back to Pepper Clinical system.")
            eng.runAndWait()
        except Exception as e:
            print(f"TTS Greet Error: {e}")

    def speak(self, text):
        try:
            eng = _ensure_engine()
            eng.say(text)
            eng.runAndWait()
        except Exception as e:
            print(f"TTS Speak Error: {e}")

VOICE = PepperVoiceWrapper()

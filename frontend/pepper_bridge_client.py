import threading
import urllib.request
import json

PEPPER_API = "http://127.0.0.1:5055"

def _post(path, payload):
    def _run():
        try:
            req = urllib.request.Request(
                f"{PEPPER_API}{path}",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            urllib.request.urlopen(req, timeout=1.5)
        except Exception:
            pass
    threading.Thread(target=_run, daemon=True).start()

def pepp_speak(on: bool):
    _post("/pepper/speak", {"on": bool(on)})

def pepp_wave(duration=2.2):
    _post("/pepper/wave", {"duration": duration})

def pepp_clap(duration=2.0):
    _post("/pepper/clap", {"duration": duration})

def pepp_look(yaw=0.0, pitch=0.0, hold=2.5):
    _post("/pepper/look", {"yaw": yaw, "pitch": pitch, "hold": hold})

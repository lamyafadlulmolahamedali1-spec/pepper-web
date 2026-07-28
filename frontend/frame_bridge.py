"""Live frame bridge — child session writes latest camera frame; parent dashboard reads it.
© 2026 Lamya Fadlulmola Hamed Ali"""
import threading
class FrameBridge:
    def __init__(self):
        self._lock=threading.Lock(); self._jpeg=None; self._ts=0
    def put(self, jpeg_bytes):
        import time
        with self._lock:
            self._jpeg=jpeg_bytes; self._ts=time.time()
    def get(self):
        with self._lock:
            return self._jpeg, self._ts
    def is_fresh(self, max_age=2.0):
        import time
        with self._lock:
            return self._jpeg is not None and (time.time()-self._ts)<max_age
FRAMES=FrameBridge()

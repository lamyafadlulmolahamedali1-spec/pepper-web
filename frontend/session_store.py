"""SessionStore — shared live record of the current session (child writes, parent reads).
© 2026 Lamya Fadlulmola Hamed Ali"""
import time, threading
class SessionStore:
    def __init__(self): self._lock=threading.RLock(); self.reset()
    def reset(self, child=None):
        with self._lock:
            self.child=child or {}; self.active=False; self.started_at=time.time()
            self.score=0; self.correct=0; self.fail=0; self.skipped=0; self.total=0
            self.mastered=0; self.streak=0; self.conv_level=1
            self.chat=[]; self.log=[]; self.pecs=[]; self.tasks_done=[]
            self.emotions={}; self.attn_sum=0.0; self.attn_n=0; self.live={}
            self.skills={"Motor":50,"Cognitive":50,"Verbal":50,"Math":50,"Social":50}
    def start(self, child):
        self.reset(child)
        with self._lock: self.active=True; self.started_at=time.time()
    def add_chat(self, who, text):
        with self._lock:
            self.chat.append((time.strftime("%H:%M:%S"),who,text)); self.chat=self.chat[-200:]
    def add_log(self, text):
        with self._lock:
            self.log.append((time.strftime("%H:%M:%S"),text)); self.log=self.log[-200:]
    def add_pecs(self, label, phrase):
        with self._lock:
            self.pecs.append((time.strftime("%H:%M:%S"),label,phrase)); self.pecs=self.pecs[-100:]
    def record_task(self, task, ok, skipped=False):
        with self._lock:
            self.total+=1
            if skipped: self.skipped+=1; self.streak=0
            elif ok:
                self.correct+=1; self.score+=task.get("tokens",10); self.streak+=1
                if self.correct%10==0: self.mastered+=1
            else: self.fail+=1; self.streak=0
            self.tasks_done.append({"name":task.get("name",""),"domain":task.get("domain",""),
                "ok":bool(ok and not skipped),"skipped":skipped})
            dom=(task.get("domain","") or "").lower()
            key=("Motor" if "motor" in dom else "Cognitive" if "cogn" in dom
                 else "Verbal" if "verbal" in dom else "Math" if "math" in dom
                 else "Social" if "social" in dom else None)
            if key:
                self.skills[key]=max(0,min(100,self.skills[key]+(2 if (ok and not skipped) else -1)))
    def update_live(self, res):
        with self._lock:
            self.live=dict(res); a=res.get("attention",0)
            if a: self.attn_sum+=a; self.attn_n+=1
            emo=res.get("emotion","neutral"); self.emotions[emo]=self.emotions.get(emo,0)+1
    def end(self):
        with self._lock: self.active=False
    def snapshot(self):
        with self._lock:
            avg=round(self.attn_sum/self.attn_n,1) if self.attn_n else 0
            dom=max(self.emotions,key=self.emotions.get) if self.emotions else "neutral"
            rate=int(self.correct/self.total*100) if self.total else 0
            return {"child":dict(self.child),"active":self.active,
                "duration_sec":int(time.time()-self.started_at) if self.active else 0,
                "score":self.score,"correct":self.correct,"fail":self.fail,"skipped":self.skipped,
                "total":self.total,"mastered":self.mastered,"streak":self.streak,
                "conv_level":self.conv_level,"success_rate":rate,"avg_attention":avg,
                "dominant_emotion":dom,"emotions":dict(self.emotions),"chat":list(self.chat),
                "log":list(self.log),"pecs":list(self.pecs),"tasks_done":list(self.tasks_done),
                "skills":dict(self.skills),"live":dict(self.live)}
STORE=SessionStore()

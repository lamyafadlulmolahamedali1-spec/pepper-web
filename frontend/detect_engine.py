"""Unified detection engine — Python port of HTML logic, made STRONGER.
© 2026 Lamya Fadlulmola Hamed Ali"""
import math
def _h(a,b): return math.hypot(a.x-b.x, a.y-b.y)

class VotingBuffer:
    """Majority-vote over last N frames — removes jitter and false positives."""
    def __init__(self, size=5, threshold=0.6):
        from collections import deque
        self.buf=deque(maxlen=size); self.threshold=threshold
    def push(self, value):
        self.buf.append(bool(value))
        if len(self.buf)<self.buf.maxlen: return False
        return sum(self.buf)/len(self.buf) >= self.threshold
    def reset(self): self.buf.clear()
class DetectState:
    def __init__(self):
        self.wave_frames=0; self.head_buf=0; self.clapping=False
        self.motion_buf=[]; self.motion_sum=0.0
        self.prev={"lwx":0.5,"lwy":0.5,"rwx":0.5,"rwy":0.5}
        self.emo_smooth={"happy":0,"joyful":0,"surprised":0,"angry":0,"sad":0,"fear":0,"neutral":1.0}
        self.vote_wave=VotingBuffer(6,0.55)
        self.vote_handsup=VotingBuffer(4,0.6)
        self.vote_clap=VotingBuffer(3,0.6)
        self.vote_touchhead=VotingBuffer(4,0.5)
        self.vote_armsout=VotingBuffer(4,0.6)
        self.vote_point=VotingBuffer(3,0.6)
    def update_pose(self, lm):
        out={"hand_raised":False,"hands_up":False,"arms_out":False,"clap":False,
             "wave":False,"point":False,"touch_head":False,"motion":False}
        if not lm: return out
        def L(i): return lm[i]
        def ok(i):
            v=lm[i]; return v and (getattr(v,"visibility",0.9) or 0.9)>0.35
        lw,rw=L(15),L(16); ls,rs=L(11),L(12); nose=L(0); lEar,rEar=L(7),L(8)
        lwOk,rwOk,lsOk,rsOk=ok(15),ok(16),ok(11),ok(12)
        leftUp=lwOk and lsOk and (lw.y<ls.y-0.05)
        rightUp=rwOk and rsOk and (rw.y<rs.y-0.05)
        out["hand_raised"]=leftUp or rightUp; out["hands_up"]=leftUp and rightUp
        if lwOk and rwOk and lsOk and rsOk:
            wSpan=abs(lw.x-rw.x); shSpan=abs(ls.x-rs.x) or 0.15
            lAsh=abs(lw.y-ls.y)<0.25; rAsh=abs(rw.y-rs.y)<0.25
            out["arms_out"]=wSpan>shSpan*1.5 and lAsh and rAsh
        if lwOk and rwOk:
            wDist=_h(lw,rw); midY=(lw.y+rw.y)/2
            chY=(ls.y+rs.y)/2 if (lsOk and rsOk) else 0.55
            nearChest=abs(midY-chY)<0.32
            if not self.clapping and wDist<0.14 and nearChest: self.clapping=True
            if self.clapping and wDist>0.24: self.clapping=False
            out["clap"]=self.clapping
        wristX=lw.x if leftUp else (rw.x if rightUp else None)
        prevX=self.prev["lwx"] if leftUp else (self.prev["rwx"] if rightUp else None)
        if wristX is not None and prevX is not None and abs(wristX-prevX)>0.032:
            self.wave_frames=min(10,self.wave_frames+2)
        else: self.wave_frames=max(0,self.wave_frames-1)
        out["wave"]=self.wave_frames>=3
        out["point"]=(lwOk and _h(lw,nose)<0.15) or (rwOk and _h(rw,nose)<0.15)
        lwNose=lwOk and _h(lw,nose)<0.22 and lw.y<=nose.y+0.05
        rwNose=rwOk and _h(rw,nose)<0.22 and rw.y<=nose.y+0.05
        lwEar=lwOk and ok(7) and _h(lw,lEar)<0.18
        rwEar=rwOk and ok(8) and _h(rw,rEar)<0.18
        lwTop=lwOk and lw.y<nose.y-0.03 and abs(lw.x-nose.x)<0.30
        rwTop=rwOk and rw.y<nose.y-0.03 and abs(rw.x-nose.x)<0.30
        rawHead=lwNose or rwNose or lwEar or rwEar or lwTop or rwTop
        if rawHead: self.head_buf=min(5,self.head_buf+2)
        else: self.head_buf=max(0,self.head_buf-1)
        out["touch_head"]=self.head_buf>=2
        mv=(_h(lw,type("p",(),{"x":self.prev["lwx"],"y":self.prev["lwy"]})()) if lwOk else 0)+\
           (_h(rw,type("p",(),{"x":self.prev["rwx"],"y":self.prev["rwy"]})()) if rwOk else 0)
        self.motion_buf.append(mv); self.motion_sum+=mv
        if len(self.motion_buf)>8: self.motion_sum-=self.motion_buf.pop(0)
        out["motion"]=(self.motion_sum/max(1,len(self.motion_buf)))>0.010
        self.prev={"lwx":lw.x,"lwy":lw.y,"rwx":rw.x,"rwy":rw.y}
        # apply temporal voting for high-confidence, jitter-free detection
        out["wave"]        = self.vote_wave.push(out["wave"])
        out["hands_up"]    = self.vote_handsup.push(out["hands_up"])
        out["clap"]        = self.vote_clap.push(out["clap"])
        out["touch_head"]  = self.vote_touchhead.push(out["touch_head"])
        out["arms_out"]    = self.vote_armsout.push(out["arms_out"])
        out["point"]       = self.vote_point.push(out["point"])
        return out
    def count_fingers(self, mhl, handedness=None):
        if not mhl: return 0
        total=0
        for hi,lm in enumerate(mhl):
            raw="Right"
            if handedness and hi<len(handedness):
                try: raw=handedness[hi].classification[0].label
                except Exception: raw="Right"
            hl="Right" if raw=="Left" else "Left"
            n=0
            if hl=="Left":
                if lm.landmark[4].x<lm.landmark[3].x: n+=1
            else:
                if lm.landmark[4].x>lm.landmark[3].x: n+=1
            for t,pp in [(8,6),(12,10),(16,14),(20,18)]:
                if lm.landmark[t].y<lm.landmark[pp].y: n+=1
            total+=n
        return min(10,total)
    def update_emotion(self, fl, W=1.0, H=1.0):
        if not fl: return "neutral",0.0,{}
        lm=fl.landmark
        def p(i): return lm[i]
        def dd(a,b): return _h(p(a),p(b))
        mw=dd(78,308) or 1; mar=dd(13,14)/mw
        brow=((lm[107].y-lm[159].y)+(lm[336].y-lm[386].y))/2
        fW=dd(234,454) or 1; smileW=dd(61,291)/fW
        smileScore=max(0,(mar-0.18)*4.0+(smileW-0.40)*4.5)
        s={"happy":min(1,smileScore*0.7),"joyful":min(1,max(0,(mar-0.25)*3.5)*0.8),
           "surprised":min(1,max(0,(mar-0.22)*3.0)*0.5),
           "angry":min(1,max(0,brow*28)*max(0,(0.24-mar)*5)),
           "sad":min(1,max(0,brow*20)*max(0,(0.28-mar)*4)),
           "fear":min(1,max(0,(mar-0.15)*4)*0.5),"neutral":0}
        tot=sum(s.values()) or 1e-6
        for k in s: s[k]/=tot
        s["neutral"]=max(0,1-sum(v for k,v in s.items() if k!="neutral"))
        tot2=sum(s.values()) or 1e-6
        for k in s: s[k]/=tot2
        a=0.78
        for k in self.emo_smooth:
            self.emo_smooth[k]=a*self.emo_smooth.get(k,0)+(1-a)*s.get(k,0)
        dom=max(self.emo_smooth,key=self.emo_smooth.get); conf=self.emo_smooth[dom]
        pct={k:round(v*100) for k,v in self.emo_smooth.items()}
        return dom,round(conf,2),pct
    def is_smiling(self):
        return self.emo_smooth.get("happy",0)>0.35 or self.emo_smooth.get("joyful",0)>0.30
def verify_task(task, det_out, finger_count, emo_label, smiling):
    vk=task.get("verify_kind")
    if vk=="fingers": return finger_count==task.get("target")
    if vk=="gesture":
        tgt=task.get("target")
        if tgt=="wave": return det_out.get("wave")
        if tgt=="hands_up": return det_out.get("hands_up")
        if tgt=="clap": return det_out.get("clap")
        return False
    if vk=="touch": return det_out.get("touch_head") or det_out.get("point")
    if vk=="smile": return smiling or emo_label in ("happy","joyful")
    return False

"""High-performance vision: skeleton, pose, joints, emotion, fingers.
MediaPipe solutions API with OpenCV fallback. © 2026 Lamya F. H. Ali"""
import math
try:
    import cv2
    _HAS_CV=True
except Exception:
    _HAS_CV=False

_HAS_MP=False
try:
    import mediapipe as mp
    from expression_detect import detect_expression
    _=mp.solutions.pose
    _HAS_MP=True
except Exception:
    _HAS_MP=False


def _ang(a,b,c):
    ba=(a[0]-b[0],a[1]-b[1]); bc=(c[0]-b[0],c[1]-b[1])
    d=ba[0]*bc[0]+ba[1]*bc[1]; na=math.hypot(*ba); nc=math.hypot(*bc)
    if na*nc==0: return 0.0
    return math.degrees(math.acos(max(-1,min(1,d/(na*nc)))))

def _dist(a,b): return math.hypot(a[0]-b[0],a[1]-b[1])


class VisionEngine:
    def __init__(self, det=0.6, trk=0.5):
        self.ok=_HAS_CV; self.use_mp=_HAS_MP; self._init=False; self._fcount=0
        self._det=det; self._trk=trk
        self.pose=self.hands=self.face=None
        self._fc=None
        self.last={"fingers":0,"fingers_left":0,"fingers_right":0,"gesture":"none",
            "emotion":"neutral","emotion_conf":0.0,"attention":0.0,"pose_detected":False,
            "hands_detected":False,"face_detected":False,"joints":{},"posture":"unknown",
            "hand_raised":False,"head_touch":False,"clap":False,
            "emotions":{e:0.0 for e in ["angry","disgust","fear","happy","sad","surprise","neutral"]}}
        import time; self._clap_t=0; self._time=time

    def _ensure(self):
        if self._init or not self.ok: return
        if self.use_mp:
            self._P=mp.solutions.pose; self._H=mp.solutions.hands; self._F=mp.solutions.face_mesh
            self._draw=mp.solutions.drawing_utils
            self.pose=self._P.Pose(model_complexity=0,smooth_landmarks=True,
                min_detection_confidence=self._det,min_tracking_confidence=self._trk)
            self.hands=self._H.Hands(max_num_hands=2,model_complexity=0,
                min_detection_confidence=self._det,min_tracking_confidence=self._trk)
            self.face=self._F.FaceMesh(max_num_faces=1,refine_landmarks=True,
                min_detection_confidence=self._det,min_tracking_confidence=self._trk)
        else:
            self._fc=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
        self._init=True

    def _count(self,hl,label):
        lm=hl.landmark; tips=[4,8,12,16,20]; pips=[3,6,10,14,18]; c=0
        if label=="Right":
            if lm[4].x<lm[3].x: c+=1
        else:
            if lm[4].x>lm[3].x: c+=1
        for i in range(1,5):
            if lm[tips[i]].y<lm[pips[i]].y: c+=1
        return c

    def _gesture(self,total,hands):
        if total==0: return "fist"
        for hl,label in hands:
            lm=hl.landmark
            idx=lm[8].y<lm[6].y; mid=lm[12].y<lm[10].y
            ring=lm[16].y<lm[14].y; pink=lm[20].y<lm[18].y
            thumb=(lm[4].x<lm[3].x) if label=="Right" else (lm[4].x>lm[3].x)
            if idx and mid and not ring and not pink: return "peace"
            if thumb and not idx and not mid and not ring and not pink: return "thumbs_up"
            if idx and not mid and not ring and not pink: return "point"
        if total>=5: return "open_palm"
        return "open"

    def _pose_an(self,pl,w,h):
        lm=pl.landmark; P=self._P.PoseLandmark
        def pt(i): return (lm[i].x*w, lm[i].y*h)
        j={}
        try:
            j["L_elbow"]=round(_ang(pt(P.LEFT_SHOULDER),pt(P.LEFT_ELBOW),pt(P.LEFT_WRIST)))
            j["R_elbow"]=round(_ang(pt(P.RIGHT_SHOULDER),pt(P.RIGHT_ELBOW),pt(P.RIGHT_WRIST)))
            j["L_shoulder"]=round(_ang(pt(P.LEFT_ELBOW),pt(P.LEFT_SHOULDER),pt(P.LEFT_HIP)))
            j["R_shoulder"]=round(_ang(pt(P.RIGHT_ELBOW),pt(P.RIGHT_SHOULDER),pt(P.RIGHT_HIP)))
        except: pass
        posture="unknown"; raised=False; head=False
        try:
            ls,rs=pt(P.LEFT_SHOULDER),pt(P.RIGHT_SHOULDER)
            posture="upright" if abs(ls[1]-rs[1])<h*0.06 else "leaning"
            if lm[P.LEFT_WRIST].y<lm[P.LEFT_SHOULDER].y or lm[P.RIGHT_WRIST].y<lm[P.RIGHT_SHOULDER].y:
                raised=True
            nose=pt(P.NOSE)
            if _dist(pt(P.LEFT_WRIST),nose)<w*0.12 or _dist(pt(P.RIGHT_WRIST),nose)<w*0.12:
                head=True
        except: pass
        return j,posture,raised,head

    def _emotion(self,fl,w,h):
        # accurate geometric detector first (reliably catches smiles)
        try:
            from expression_detect import detect_expression
            lbl,conf=detect_expression(fl)
            scores={e:0.0 for e in ["angry","disgust","fear","happy","sad","surprise","neutral"]}
            key="surprise" if lbl=="surprised" else lbl
            if key in scores: scores[key]=conf
            # attention from face presence
            att=min(100.0, 60.0+conf*40.0)
            return (key, conf, att, scores)
        except Exception:
            pass
        lm=fl.landmark
        def pt(i): return (lm[i].x*w, lm[i].y*h)
        try:
            mw=_dist(pt(61),pt(291)); mh=_dist(pt(13),pt(14))
            brow=_dist(pt(70),pt(159))+_dist(pt(300),pt(386))
            fh=_dist(pt(10),pt(152))+1e-6
            smile=mw/fh; openr=mh/fh; browr=brow/fh
            scores={e:0.0 for e in ["angry","disgust","fear","happy","sad","surprise","neutral"]}
            if openr>0.18 and browr>0.22: emo,conf="surprise",min(1,openr*3)
            elif smile>0.46: emo,conf="happy",min(1,smile)
            elif smile<0.38 and openr<0.05: emo,conf="sad",0.6
            elif browr<0.16: emo,conf="angry",0.55
            else: emo,conf="neutral",0.78
            scores[emo]=round(conf,2); scores["neutral"]=max(scores["neutral"],round(1-conf,2))
            cx=pt(1)[0]/w; att=max(0,1-abs(cx-0.5)*2)*100
            return emo,round(conf,2),round(att,1),scores
        except:
            return "neutral",0.0,0.0,{e:0.0 for e in ["angry","disgust","fear","happy","sad","surprise","neutral"]}

    def process(self, frame, draw=True):
        if not self.ok: return frame, self.last
        self._ensure()
        h,w=frame.shape[:2]
        if not self.use_mp:
            gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            faces=self._fc.detectMultiScale(gray,1.2,5,minSize=(80,80))
            res=dict(self.last); res["clap"]=False
            if len(faces):
                x,y,fw,fh=sorted(faces,key=lambda b:-b[2]*b[3])[0]
                res["face_detected"]=True
                res["attention"]=round(max(0,1-abs((x+fw/2)/w-0.5)*2)*100,1)
                if draw:
                    cv2.rectangle(frame,(x,y),(x+fw,y+fh),(124,58,237),2)
            else: res["face_detected"]=False; res["attention"]=0.0
            self.last=res; return frame,res
        _small=cv2.resize(frame,(320,240))
        rgb=cv2.cvtColor(_small,cv2.COLOR_BGR2RGB); rgb.flags.writeable=False
        self._fcount += 1
        # Pose every frame (motion critical). Hands every 2nd, Face every 3rd —
        # big speed win with negligible accuracy loss (face/hands move slowly).
        pr=self.pose.process(rgb)
        if self._fcount % 2 == 0 or not hasattr(self,"_cache_hr"):
            hr=self.hands.process(rgb); self._cache_hr=hr
        else:
            hr=self._cache_hr
        if self._fcount % 3 == 0 or not hasattr(self,"_cache_fr"):
            fr=self.face.process(rgb); self._cache_fr=fr
        else:
            fr=self._cache_fr
        self._last_pose=pr.pose_landmarks if pr.pose_landmarks else None
        self._last_hands=hr.multi_hand_landmarks if hr.multi_hand_landmarks else None
        self._last_handedness=hr.multi_handedness if hr.multi_handedness else None
        self._last_face=fr.multi_face_landmarks[0] if fr.multi_face_landmarks else None
        rgb.flags.writeable=True; res=dict(self.last); res["clap"]=False
        if pr.pose_landmarks:
            res["pose_detected"]=True
            j,po,ra,hd=self._pose_an(pr.pose_landmarks,w,h)
            res["joints"]=j; res["posture"]=po; res["hand_raised"]=ra; res["head_touch"]=hd
            if draw:
                self._draw.draw_landmarks(frame,pr.pose_landmarks,self._P.POSE_CONNECTIONS,
                    self._draw.DrawingSpec(color=(80,220,120),thickness=2,circle_radius=3),
                    self._draw.DrawingSpec(color=(80,220,120),thickness=2))
        else: res["pose_detected"]=False
        total=0; lc=rc=0; hands=[]
        if hr.multi_hand_landmarks:
            res["hands_detected"]=True
            labels=[h.classification[0].label for h in hr.multi_handedness] if hr.multi_handedness else []
            for i,hl in enumerate(hr.multi_hand_landmarks):
                lbl=labels[i] if i<len(labels) else "Right"
                c=self._count(hl,lbl); total+=c
                if lbl=="Left": lc=c
                else: rc=c
                hands.append((hl,lbl))
                if draw:
                    self._draw.draw_landmarks(frame,hl,self._H.HAND_CONNECTIONS,
                        self._draw.DrawingSpec(color=(240,200,60),thickness=2,circle_radius=2),
                        self._draw.DrawingSpec(color=(240,160,60),thickness=2))
            res["gesture"]=self._gesture(total,hands)
            if len(hands)==2:
                w1=hands[0][0].landmark[0]; w2=hands[1][0].landmark[0]
                if abs(w1.x-w2.x)+abs(w1.y-w2.y)<0.12 and (self._time.time()-self._clap_t)>0.6:
                    res["clap"]=True; self._clap_t=self._time.time()
        else: res["hands_detected"]=False; res["gesture"]="none"
        res["fingers"]=total; res["fingers_left"]=lc; res["fingers_right"]=rc
        if fr.multi_face_landmarks:
            res["face_detected"]=True
            emo,conf,att,scores=self._emotion(fr.multi_face_landmarks[0],w,h)
            res["emotion"]=emo; res["emotion_conf"]=conf; res["attention"]=att; res["emotions"]=scores
            if draw:
                self._draw.draw_landmarks(frame,fr.multi_face_landmarks[0],
                    self._F.FACEMESH_TESSELATION,None,
                    self._draw.DrawingSpec(color=(80,220,120),thickness=1,circle_radius=1))
        else: res["face_detected"]=False; res["attention"]=0.0
        self.last=res; return frame,res

    def close(self):
        for s in (self.pose,self.hands,self.face):
            try:
                if s: s.close()
            except: pass

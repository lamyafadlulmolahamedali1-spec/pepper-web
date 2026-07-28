"""Detect 'touch your X' tasks using pose landmarks distance.
Works for: tummy/belly, nose, head, mouth, ears, shoulders, knees, eyes.
© 2026 Lamya Fadlulmola Hamed Ali"""
import math

# MediaPipe Pose landmark indices
NOSE=0; L_EYE=2; R_EYE=5; L_EAR=7; R_EAR=8; MOUTH_L=9; MOUTH_R=10
L_SH=11; R_SH=12; L_WR=15; R_WR=16; L_HIP=23; R_HIP=24; L_KNEE=25; R_KNEE=26

def _xy(lm, i, w, h):
    return (lm[i].x*w, lm[i].y*h)

def _dist(a,b):
    return math.hypot(a[0]-b[0], a[1]-b[1])

def detect_touch(pose_landmarks, target, w, h):
    """Return True if a hand is near the named body part."""
    if not pose_landmarks: return False
    lm = pose_landmarks.landmark
    lw = _xy(lm, L_WR, w, h); rw = _xy(lm, R_WR, w, h)
    # body scale = shoulder width (for distance threshold)
    scale = _dist(_xy(lm,L_SH,w,h), _xy(lm,R_SH,w,h)) or 80
    thr = scale * 0.6  # "near" threshold relative to body size

    t = target.lower()
    targets = []
    if "tummy" in t or "belly" in t or "stomach" in t:
        mid_hip = ((_xy(lm,L_HIP,w,h)[0]+_xy(lm,R_HIP,w,h)[0])/2,
                   (_xy(lm,L_HIP,w,h)[1]+_xy(lm,R_HIP,w,h)[1])/2)
        mid_sh = ((_xy(lm,L_SH,w,h)[0]+_xy(lm,R_SH,w,h)[0])/2,
                  (_xy(lm,L_SH,w,h)[1]+_xy(lm,R_SH,w,h)[1])/2)
        belly = ((mid_hip[0]+mid_sh[0])/2, (mid_hip[1]*0.6+mid_sh[1]*0.4))
        targets=[belly]
    elif "nose" in t: targets=[_xy(lm,NOSE,w,h)]
    elif "head" in t or "hair" in t: targets=[(_xy(lm,NOSE,w,h)[0], _xy(lm,NOSE,w,h)[1]-scale*0.5)]
    elif "mouth" in t: targets=[((_xy(lm,MOUTH_L,w,h)[0]+_xy(lm,MOUTH_R,w,h)[0])/2,
                                 (_xy(lm,MOUTH_L,w,h)[1]+_xy(lm,MOUTH_R,w,h)[1])/2)]
    elif "ear" in t: targets=[_xy(lm,L_EAR,w,h), _xy(lm,R_EAR,w,h)]
    elif "eye" in t: targets=[_xy(lm,L_EYE,w,h), _xy(lm,R_EYE,w,h)]
    elif "shoulder" in t: targets=[_xy(lm,L_SH,w,h), _xy(lm,R_SH,w,h)]
    elif "knee" in t: targets=[_xy(lm,L_KNEE,w,h), _xy(lm,R_KNEE,w,h)]; thr=scale*0.9
    elif "cheek" in t: targets=[_xy(lm,L_EAR,w,h), _xy(lm,R_EAR,w,h)]
    else: return False

    for tp in targets:
        if _dist(lw,tp)<thr or _dist(rw,tp)<thr:
            return True
    return False

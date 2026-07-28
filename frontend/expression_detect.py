"""Accurate expression detector from MediaPipe FaceMesh landmarks.
Assistive engagement signal (not clinical diagnosis). © 2026 Lamya F. H. Ali"""
import math
MOUTH_L=61; MOUTH_R=291; LIP_TOP=13; LIP_BOT=14
EYE_L_TOP=159; EYE_L_BOT=145; EYE_R_TOP=386; EYE_R_BOT=374
BROW_L=105; BROW_R=334; NOSE_TIP=1; CHIN=152; FOREHEAD=10
def _d(a,b): return math.hypot(a.x-b.x, a.y-b.y)
def detect_expression(face_landmarks):
    if not face_landmarks: return "neutral", 0.0
    lm=face_landmarks.landmark
    face_h=_d(lm[FOREHEAD],lm[CHIN]) or 0.2
    mouth_w=_d(lm[MOUTH_L],lm[MOUTH_R]); mouth_open=_d(lm[LIP_TOP],lm[LIP_BOT])
    mouth_w_ratio=mouth_w/face_h; mouth_open_ratio=mouth_open/face_h
    corner_y=(lm[MOUTH_L].y+lm[MOUTH_R].y)/2; center_y=(lm[LIP_TOP].y+lm[LIP_BOT].y)/2
    corner_lift=(center_y-corner_y)/face_h
    eye_l=_d(lm[EYE_L_TOP],lm[EYE_L_BOT]); eye_r=_d(lm[EYE_R_TOP],lm[EYE_R_BOT])
    eye_open=(eye_l+eye_r)/2/face_h
    brow_eye_l=abs(lm[BROW_L].y-lm[EYE_L_TOP].y)/face_h
    brow_eye_r=abs(lm[BROW_R].y-lm[EYE_R_TOP].y)/face_h
    brow_raise=(brow_eye_l+brow_eye_r)/2
    smile_score=0.0
    if mouth_w_ratio>0.42: smile_score+=(mouth_w_ratio-0.42)*4
    if corner_lift>0.005: smile_score+=corner_lift*18
    smile_score=min(1.0,smile_score)
    surprise_score=0.0
    if mouth_open_ratio>0.12: surprise_score+=(mouth_open_ratio-0.12)*5
    if brow_raise>0.16: surprise_score+=(brow_raise-0.16)*4
    surprise_score=min(1.0,surprise_score)
    sad_score=0.0
    if corner_lift<-0.004: sad_score+=(-corner_lift)*16
    sad_score=min(1.0,sad_score)
    scores={"happy":smile_score,"surprised":surprise_score,"sad":sad_score}
    label=max(scores,key=scores.get); conf=scores[label]
    if smile_score>=0.45 and smile_score>=surprise_score-0.1:
        return "happy", round(min(1.0,smile_score),2)
    if conf<0.32: return "neutral", round(1.0-conf,2)
    return label, round(conf,2)
def is_smiling(face_landmarks):
    label,conf=detect_expression(face_landmarks)
    return label=="happy" and conf>=0.45

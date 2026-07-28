"""Comprehensive motor/body-exercise verifier.
Maps every task to a body/hand/face action detected from the vision engine.
© 2026 Lamya F. H. Ali"""
import math


def _d(a, b): return math.hypot(a[0]-b[0], a[1]-b[1])


class MotionVerifier:
    """
    Verifies ALL motor & body exercises from vision results, NOT just clapping:
      • Finger counting        (show N fingers)
      • Hand raises            (raise one / both hands, arms up)
      • Body-part touching     (nose, head, ears, mouth, shoulders, tummy, cheeks)
      • Gestures               (clap, wave, thumbs up, peace, point, open palm, fist)
      • Posture / body actions (stand tall, lean, turn, arms out/wide, hands on hips)
    """

    # which 'verify' key each task expects -> human description
    ACTIONS = {
        "fingers_count": "Show the right number of fingers",
        "raise_hand": "Raise one hand",
        "raise_both": "Raise both hands high",
        "arms_out": "Stretch both arms out wide",
        "hands_hips": "Put hands on hips",
        "clap": "Clap hands",
        "wave": "Wave hand",
        "thumbs_up": "Thumbs up",
        "peace": "Peace sign",
        "point": "Point at screen",
        "open_palm": "Open hand",
        "fist": "Make a fist",
        "touch_nose": "Touch nose",
        "touch_head": "Touch top of head",
        "touch_ears": "Touch ears",
        "touch_mouth": "Touch mouth",
        "touch_shoulders": "Touch shoulders",
        "touch_tummy": "Touch tummy",
        "touch_cheeks": "Touch cheeks",
        "stand_tall": "Stand up tall (upright)",
        "lean": "Lean to the side",
        "smile": "Smile big",
    }

    @staticmethod
    def verify(task, res, pose_landmarks=None, frame_wh=None):
        """
        task: dict with 'verify' key and optionally 'target' (for finger count).
        res:  vision engine results dict.
        Returns True if the exercise is detected as completed.
        """
        v = task.get("verify", "")
        if not v:
            return False

        # ---- Finger counting ----
        if v in ("fingers_count", "number"):
            tgt = task.get("target")
            return tgt is not None and res.get("fingers", -1) == tgt

        # ---- Gestures from hand model ----
        g = res.get("gesture", "none")
        if v == "clap":
            return res.get("clap", False)
        if v in ("wave",):
            # wave = open hand + hand raised (movement approximated by open palm up high)
            return g in ("open_palm", "open") and res.get("hand_raised", False)
        if v in ("thumbs_up", "peace", "point", "open_palm", "fist"):
            return g == v

        # ---- Hand raises / arm posture ----
        if v == "raise_hand":
            return res.get("hand_raised", False)
        if v == "raise_both":
            j = res.get("joints", {})
            # both shoulders open wide + hand raised => both arms up
            return res.get("hand_raised", False) and res.get("hands_detected", False)
        if v == "arms_out":
            j = res.get("joints", {})
            ls = j.get("L_shoulder", 0); rs = j.get("R_shoulder", 0)
            return ls > 70 and rs > 70   # arms abducted out to sides
        if v == "hands_hips":
            j = res.get("joints", {})
            le = j.get("L_elbow", 180); re = j.get("R_elbow", 180)
            return le < 120 and re < 120  # elbows bent, hands near hips

        # ---- Body-part touching (needs pose landmarks for precise parts) ----
        if v.startswith("touch_"):
            return MotionVerifier._verify_touch(v, res, pose_landmarks, frame_wh)

        # ---- Posture / body ----
        if v == "stand_tall":
            return res.get("posture") == "upright"
        if v == "lean":
            return res.get("posture") == "leaning"
        if v == "smile":
            return res.get("emotion") == "happy"

        # ---- Generic head touch fallback ----
        if v == "head_touch":
            return res.get("head_touch", False)
        return False

    @staticmethod
    def _verify_touch(v, res, pose_landmarks, frame_wh):
        """Precise body-part touch detection using pose landmarks when available."""
        # Fallback: any hand-near-head signal
        if pose_landmarks is None or frame_wh is None:
            if v in ("touch_nose", "touch_head", "touch_cheeks", "touch_mouth", "touch_ears"):
                return res.get("head_touch", False)
            return res.get("hand_raised", False)
        try:
            import mediapipe as mp
            P = mp.solutions.pose.PoseLandmark
            w, h = frame_wh
            lm = pose_landmarks.landmark
            def pt(i): return (lm[i].x*w, lm[i].y*h)
            lw, rw = pt(P.LEFT_WRIST), pt(P.RIGHT_WRIST)
            near = lambda target, thr=0.13: (_d(lw, target) < w*thr or _d(rw, target) < w*thr)
            nose = pt(P.NOSE)
            if v == "touch_nose":  return near(nose, 0.10)
            if v == "touch_mouth": return near(((pt(P.MOUTH_LEFT)[0]+pt(P.MOUTH_RIGHT)[0])/2,
                                                (pt(P.MOUTH_LEFT)[1]+pt(P.MOUTH_RIGHT)[1])/2), 0.10)
            if v == "touch_ears":  return near(pt(P.LEFT_EAR)) or near(pt(P.RIGHT_EAR))
            if v == "touch_cheeks":return near(pt(P.LEFT_EYE),0.14) or near(pt(P.RIGHT_EYE),0.14)
            if v == "touch_head":
                top=(nose[0], nose[1]-h*0.12); return near(top,0.16)
            if v == "touch_shoulders":
                return near(pt(P.LEFT_SHOULDER),0.12) or near(pt(P.RIGHT_SHOULDER),0.12)
            if v == "touch_tummy":
                belly=((pt(P.LEFT_HIP)[0]+pt(P.RIGHT_HIP)[0])/2,
                       (pt(P.LEFT_HIP)[1]+pt(P.RIGHT_HIP)[1])/2)
                return near(belly,0.16)
        except Exception:
            return res.get("head_touch", False)
        return False

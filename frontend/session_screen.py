"""Live Therapy session screen — 3 columns, matches screenshot 6.
© 2026 Lamya F. H. Ali"""
import time, random
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

import theme as T
from session_store import STORE
from touch_detect import detect_touch
from touch_detect import detect_touch
from adaptive_engine import AdaptiveEngine, expanded_tasks
from aac_tools import AACSentenceBuilder, FirstThenBoard
from session_left import SessionLeft
from session_mid import SessionMid
from session_right import SessionRight
from pecs_bar import PecsBar, set_voice
import pepper_voice as PV
import pepper_sim as PSIM
from speech_check import SpeechChecker
from pepper_voice import speak as _raw_speak
from pepper_bridge_client import pepp_speak, pepp_wave, pepp_clap

def speak(text):
    pepp_speak(True)
    try:
        _raw_speak(text)
    finally:
        pepp_speak(False)

from touch_detect import detect_touch
from celebration import Celebration, play_clap
from music_button import MusicButton
from calm_music import play_chime, play_cue
from drawing_board import DrawingBoard
from life_skill_video import LifeSkillVideoDialog
from audio_fx import play_chime, CalmMusic
from motion_verifier import MotionVerifier
from detect_engine import DetectState, verify_task
from motor_tasks import motor_task, finger_task
from frame_bridge import FRAMES
from html_tasks import genTask, reset_tasks, next_full_cycle

try:
    from camera_thread import CameraThread
    _HAS_CAM=True
except Exception:
    _HAS_CAM=False


class SessionScreen(QWidget):
    speech_result=pyqtSignal(str, bool, str)  # text, matched, target_word
    finished=pyqtSignal()

    def __init__(self, app, api=None):
        super().__init__()
        self.app=app; self.api=api
        self.child=None; self.session_id=None
        self.tasks=[]; self.cur=None
        self.score=0; self.correct=0; self.fail=0; self.total=0; self.mastered=0
        self.start_t=0; self.cam=None
        self.attn_sum=0; self.attn_n=0; self.emotions={}
        self._last_pose=None; self._last_wh=None; self._locked=False
        self.calm=CalmMusic()
        self._build()

    def _build(self):
        self.setStyleSheet(f"background:{T.DARK_BG};")
        root=QVBoxLayout(self); root.setContentsMargins(6,6,6,6); root.setSpacing(4)

        # top bar
        top=QHBoxLayout()
        self.titleLbl=QLabel("🤖 Pepper V6 — Session")
        self.titleLbl.setStyleSheet(f"color:{T.DARK_TEXT};font-size:14px;font-weight:bold;")
        top.addWidget(self.titleLbl)
        top.addStretch()
        self.scoreLbl=QLabel("⭐ 0   🏆 0   🎯 0%")
        self.scoreLbl.setStyleSheet(f"color:{T.GOLD};font-size:13px;font-weight:bold;")
        top.addWidget(self.scoreLbl)
        self.btnBack=QLabel("  ⬅ Parent  ")
        self.btnBack.setStyleSheet(f"color:{T.PURPLE3};font-weight:bold;")
        self.btnBack.mousePressEvent=lambda e: self.finished.emit()
        top.addWidget(self.btnBack)
        self.btnBack=QLabel("  ⬅ Parent  ")
        self.btnBack.setStyleSheet(f"color:{T.PURPLE3};font-weight:bold;")
        self.btnBack.mousePressEvent=lambda e: self.finished.emit()
        top.addWidget(self.btnBack)
        self.btnExit=QLabel("  ⏹ End  ")
        self.btnExit.setStyleSheet(f"color:{T.RED};font-weight:bold;")
        self.btnExit.mousePressEvent=lambda e: self.end()
        top.addWidget(self.btnExit)
        root.addLayout(top)

        # 3 columns
        self.firstThen=FirstThenBoard()
        ftRow=QHBoxLayout(); ftRow.addStretch(); ftRow.addWidget(self.firstThen); ftRow.addStretch()
        root.addLayout(ftRow)
        cols=QHBoxLayout(); cols.setSpacing(6)
        self.left=SessionLeft(on_theme=self._set_theme)
        self.mid=SessionMid()
        self.right=SessionRight()
        cols.addWidget(self.left,32); cols.addWidget(self.mid,42); cols.addWidget(self.right,26)
        # AAC sentence builder button (added to right column)
        from PyQt6.QtWidgets import QPushButton as _QPB
        self.btnAAC=_QPB("🗣️ Talk (AAC)")
        self.btnAAC.setStyleSheet(f"background:{T.TEAL};color:white;border:none;border-radius:8px;padding:8px;font-weight:bold;")
        self.btnAAC.clicked.connect(self._open_aac)
        self.right.layout().addWidget(self.btnAAC)
        root.addLayout(cols,1)

        # PECS bar
        botbar=QHBoxLayout()
        self.musicBtn=MusicButton()
        botbar.addWidget(self.musicBtn)
        from PyQt6.QtWidgets import QSlider
        self.musicVol=QSlider(Qt.Orientation.Horizontal); self.musicVol.setRange(0,100)
        self.musicVol.setValue(35); self.musicVol.setFixedWidth(90)
        self.musicVol.valueChanged.connect(self._music_vol)
        botbar.addWidget(QLabel("🔉")); botbar.addWidget(self.musicVol)
        self.pecs=PecsBar()
        botbar.addWidget(self.pecs,1)
        root.addLayout(botbar)

        # copyright
        cr=QLabel(T.COPYRIGHT); cr.setStyleSheet(f"color:{T.DARK_MUTE};font-size:8px;")
        cr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(cr)

        # overlay celebration
        self.celebration=Celebration(self)

        # wire signals
        self.left.btnCam.clicked.connect(self._toggle_cam)
        self.mid.answer.connect(self._answer)
        self.mid.speak_toggle.connect(self._speak_toggle)
        self.speech_result.connect(self._on_speech_result)
        self.mid.voice.connect(lambda n: set_voice(n))
        self.right.next_task.connect(self._next)
        self.right.pause.connect(lambda: self._slog("System","⏸ Paused"))
        self.right.cheer.connect(lambda m: (self._slog("Pepper",m), speak(m)))
        self.right.save_pdf.connect(self._pdf)
        self.pecs.pecs_clicked.connect(lambda l,t: self._slog("Child",f"PECS — {t}"))

        self.calm=self.musicBtn.music
        self.adaptive=AdaptiveEngine()
        self.det=DetectState()
        self.speech=SpeechChecker()
        self._finger_count=0; self._emo='neutral'; self._det_out={}
        # timer
        self.timer=QTimer(self); self.timer.timeout.connect(self._tick)
        self._recording=False

    # ---------- lifecycle ----------
    def _slog(self, who, text):
        try: STORE.add_chat(who, text)
        except Exception: pass
        self.right.log(who, text)

    def start(self, child):
        self.child=child
        STORE.start(child)
        self._active=True
        try:
            if not getattr(self,'_sim_started',False):
                PSIM.launch_pepper_thread(); self._sim_started=True
        except Exception as e: print('[pepper] launch failed:', e)
        PV.greet()
        try: PSIM.wave()
        except Exception: pass
        PV.greet()
        try: PSIM.wave()
        except Exception: pass
        PV.greet()
        try: PSIM.wave()
        except Exception: pass
        self.titleLbl.setText(f"🤖 Pepper V6 — {child.get('name','Child')}")
        self.score=self.correct=self.fail=self.total=self.mastered=0
        self.attn_sum=self.attn_n=0; self.emotions={}
        self._build_pool()
        self.start_t=time.time(); self.timer.start(1000)
        try:
            if self.api: self.session_id=self.api.start_session(child["id"]).get("id")
        except Exception: self.session_id=None
        self._slog("Pepper", f"{child.get('name','')}, ready when you are! 🎯")
        self._next()

    def _build_pool(self):
        # mix: motor/body exercises + finger counts + cognitive grids (from API if available)
        # CLEAN detectable tasks only, in structured loop (ABA->ESDM->TEACCH->PRT)
        # Real HTML task generator: 12 varied types, no-repeat-last-8 variety
        # Real HTML task generator: 12 varied types, no-repeat-last-8 variety
        pool=[next_full_cycle() for _ in range(40)]
        self.tasks=pool

    def _tick(self):
        el=int(time.time()-self.start_t)
        self._update_score()

    def _update_score(self):
        rate=int(self.correct/self.total*100) if self.total else 0
        self.scoreLbl.setText(f"⭐ {self.score}   🏆 {self.mastered}   🎯 {rate}%")

    def _next(self):
        self._locked=False
        if len(self.tasks)<5:
            self.tasks += [next_full_cycle() for _ in range(40)]
        self.cur=self.tasks.pop(0); self.total+=1
        play_cue()  # soft "new task" cue
        # every 7 tasks: show a daily life-skill step-by-step video
        if self.total>1 and self.total % 7 == 1:
            try:
                if self.calm.on: self.calm.stop()
            except Exception: pass
            try: LifeSkillVideoDialog(self).exec()
            except Exception: pass
        # drawing tasks -> show the tracing board
        if self.cur.get("type")=="drawing":
            self._show_drawing(self.cur); return
        self.mid.show_task(self.cur)
        try:
            nxt=self.tasks[0] if self.tasks else None
            self.firstThen.set_schedule(self.cur, nxt)
        except Exception: pass
        self._slog("Pepper", self.cur.get("instruction",""))
        speak(self.cur.get("instruction",""))
        speak(self.cur.get("instruction",""))
        self._update_score()

    # ---------- answers ----------
    def _answer(self, correct):
        self._record(correct)
        if correct:
            pepp_clap()

    def _record(self, ok):
        if self._locked: return
        self._locked=True
        t=self.cur
        try: STORE.record_task(t, ok)
        except Exception: pass
        # adaptive: adjust difficulty, detect break, time reinforcement
        try:
            att=float(self.app.live.get("attention",100)) if getattr(self.app,"live",None) else 100
            decision=self.adaptive.record(ok, att)
            if decision.get("message"):
                self._slog("System", "🧠 " + decision["message"])
            if decision.get("break"):
                self._suggest_break()
        except Exception: pass
        if ok:
            self.score+=t.get("tokens",10); self.correct+=1
            if self.correct % 10 == 0: self.mastered+=1
            msg=t.get("success","Great!")
            self._slog("Pepper", f"✅ {msg}"); PV.praise()
            play_chime()
            try: PSIM.clap()
            except Exception: pass
            self.celebration.resize(self.size()); self.celebration.mini()
        else:
            self.fail+=1
            msg=t.get("fail","Try again!")
            self._slog("Pepper", f"↻ {msg}"); PV.encourage()
        self._update_score()
        try:
            if self.api and self.session_id:
                self.api.log_task(self.session_id, self.child["id"],
                    t.get("domain",""), t.get("type",""), ok,
                    self.app.live.get("attention",0), self.app.live.get("emotion",""))
        except Exception: pass
        # celebration + clap every 10 tasks
        if self.total % 10 == 0:
            self.celebration.resize(self.size()); self.celebration.celebrate()
            self._slog("System","🎉 10 TASKS! Celebration! 👏")
            try: PSIM.celebrate()
            except Exception: pass
            QTimer.singleShot(2700, self._next)
        else:
            QTimer.singleShot(700, self._next)

    # ---------- camera ----------
    def _toggle_cam(self):
        if self.cam and self.cam.isRunning():
            self.cam.stop(); self.cam=None
            self.left.btnCam.setText("📷 Start Camera")
            self.left.view.setText("Camera off"); return
        if not _HAS_CAM:
            QMessageBox.information(self,"Camera","Install opencv-python + mediapipe."); return
        self.cam=CameraThread()
        self.cam.frame_ready.connect(self.left.show_frame)
        self.cam.results_ready.connect(self._on_results)
        self.cam.error.connect(lambda m: self.left.view.setText(m))
        self.cam.start()
        self.left.btnCam.setText("⏹ Stop Camera")

    def _on_results(self, res):
        self.app.live=res
        try: STORE.update_live(res)
        except Exception: pass
        self._check_touch()
        self.left.update_metrics(res, self.score)
        if res.get("attention"): self.attn_sum+=res["attention"]; self.attn_n+=1
        emo=res.get("emotion","neutral"); self.emotions[emo]=self.emotions.get(emo,0)+1
        # store pose for precise body-touch checks
        self._last_pose=getattr(self.cam.engine,"_last_pose",None) if self.cam else None
        # STRONG detection engine (ported from HTML, enhanced)
        try:
            eng=self.cam.engine if self.cam else None
            if eng is not None:
                pl=getattr(eng,"_last_pose",None)
                if pl is not None:
                    self._det_out=self.det.update_pose(pl.landmark)
                mhl=getattr(eng,"_last_hands",None)
                hcl=getattr(eng,"_last_handedness",None)
                if mhl is not None:
                    self._finger_count=self.det.count_fingers(mhl,hcl)
                fl=getattr(eng,"_last_face",None)
                if fl is not None:
                    self._emo,_c,_p=self.det.update_emotion(fl)
                # verify the current clean task
                if self.cur and self.cur.get("verify_kind") and not self._locked:
                    if verify_task(self.cur, self._det_out, self._finger_count,
                                   self._emo, self.det.is_smiling()):
                        self._slog("System", f"✅ Detected: {self.cur.get('verify_kind')}")
                        self._record(True)
        except Exception as _e:
            pass
        # legacy auto-verify (fallback)
        if self.cur and self.cur.get("verify") and not self._locked:
            wh=None
            try:
                wh=(640,480)
            except Exception: wh=None
            if MotionVerifier.verify(self.cur, res, self._last_pose, wh):
                self._slog("System","✅ Motor verified — instant!")
                self._record(True)

    # ---------- speak / pdf ----------
    def _on_speech_result(self, said_text, matched, target_word):
        self._slog("System", f"🗣 Heard: \"{said_text}\"" if said_text else "🗣 (no speech detected)")
        if self.cur and self.cur.get("type")=="word" and not self._locked:
            if matched:
                self._record(True)
            else:
                self._slog("System", f"Expected: \"{target_word}\" — try again!")

    def _pepp_start_wave(self):
        pepp_wave()

    def _speak_toggle(self, on):
        from PyQt6.QtCore import QTimer
        if on:
            self._slog("System", "🎙 Listening...")
            try:
                self.speech.start_recording()
            except Exception as e:
                self._slog("System", f"Mic error: {e}")
        else:
            self._slog("System", "🎙 Processing...")
            target_word = self.cur.get("word") if self.cur else None

            def _done(said_text, matched):
                # Qt signals are thread-safe across threads — emit only.
                try:
                    self.speech_result.emit(said_text or "", bool(matched), target_word or "")
                except Exception as e:
                    print("[speech] emit failed:", e)
            try:
                self.speech.stop_and_process(target_word, _done)
            except Exception as e:
                self._slog("System", f"Speech error: {e}")
            except Exception as e:
                self._slog("System", f"Speech processing error: {e}")


    def _pdf(self):
        try:
            from report_pdf import build_report
            path=build_report(self.child, self._summary())
            QMessageBox.information(self,"PDF", f"Report saved:\n{path}")
        except Exception as e:
            QMessageBox.information(self,"PDF", f"PDF needs reportlab: pip install reportlab\n{e}")

    def _summary(self):
        avg=round(self.attn_sum/self.attn_n,1) if self.attn_n else 0
        dom=max(self.emotions,key=self.emotions.get) if self.emotions else "neutral"
        return {"score":self.score,"mastered":self.mastered,"ok":self.correct,
            "fail":self.fail,"total":self.total,"avg_attention":avg,"dominant_emotion":dom,
            "duration_sec":int(time.time()-self.start_t)}

    def _show_drawing(self, task):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout
        self._slog("Pepper", task.get("instruction","Trace it!")); speak(task.get("instruction",""))
        dlg=QDialog(self); dlg.setWindowTitle("Drawing Board"); dlg.resize(460,560)
        dlg.setStyleSheet("background:#0a0e1a;")
        lay=QVBoxLayout(dlg)
        board=DrawingBoard()
        kind=task.get("draw_kind","letter"); target=task.get("draw_target","A")
        board.set_task(target, kind, "#7c3aed")
        done={"ok":False}
        def _fin(ok):
            if done["ok"]: return
            done["ok"]=True; dlg.accept()
            self._record(bool(ok))
        board.done.connect(_fin)
        lay.addWidget(board)
        dlg.exec()

    def _music_vol(self, v):
        try:
            if self.musicBtn.music._out: self.musicBtn.music._out.setVolume(v/100.0)
        except Exception: pass

    def _open_aac(self):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout
        dlg=QDialog(self); dlg.setWindowTitle("AAC — Talk"); dlg.resize(560,560)
        dlg.setStyleSheet("background:#0a0e1a;")
        lay=QVBoxLayout(dlg)
        aac=AACSentenceBuilder()
        def _say(sentence):
            self._slog("Child", f"🗣️ {sentence}")
            try: STORE.add_pecs("AAC", sentence)
            except Exception: pass
            speak(sentence)
        aac.speak_sentence.connect(_say)
        lay.addWidget(aac); dlg.exec()

    def _check_touch(self):
        """For 'touch your X' tasks, verify using pose landmarks."""
        try:
            t=self.cur
            if not t or t.get("verify_kind")!="touch" or self._locked: return
            pose=self._last_pose
            wh=self._last_wh or (640,480)
            if pose is not None:
                if detect_touch(pose, t.get("touch_target",""), wh[0], wh[1]):
                    self._record(True)
        except Exception: pass

    def _suggest_break(self):
        from PyQt6.QtWidgets import QMessageBox
        try:
            # play calm music automatically during the break
            if not self.calm.on:
                self.calm.play(self.calm.tracks()[0]); self.musicBtn.setText("🎵 "+self.calm.current)
        except Exception: pass
        self._slog("Pepper", "Let's take a calm break 🌿 Breathe with me… in… and out…")
        QMessageBox.information(self, "Calm Break 🌿",
            "Great work! Let's rest for a moment.\n\n"
            "🌬️ Breathe in slowly… hold… breathe out.\n"
            "When you're ready, press OK to continue.")

    def _set_theme(self, name):
        th=T.THEMES.get(name)
        if th: self.setStyleSheet(f"background:{th['bg']};")
        self._slog("System", f"Theme: {name}")

    def end(self):
        self._active=False
        self.timer.stop()
        try: STORE.end()
        except Exception: pass
        if self.cam and self.cam.isRunning(): self.cam.stop(); self.cam=None
        s=self._summary()
        try:
            if self.api and self.session_id:
                self.api.end_session(self.session_id, s)
        except Exception: pass
        QMessageBox.information(self,"Session Complete",
            f"Score: {s['score']}\nMastered: {s['mastered']}\n"
            f"OK: {s['ok']}  Fail: {s['fail']}\nAvg attention: {s['avg_attention']}%")
        self.finished.emit()

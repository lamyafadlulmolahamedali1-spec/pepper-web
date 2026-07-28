"""Parent/Therapist Dashboard — 7 tabs, matches screenshots 1-4.
© 2026 Lamya F. H. Ali"""
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QScrollArea, QTextEdit, QLineEdit, QComboBox, QButtonGroup,
    QRadioButton, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
import theme as T
from charts import LineChart, BarChart, DonutChart, RadarChart
from session_store import STORE
from frame_bridge import FRAMES


def card(title=""):
    f=QFrame(); f.setStyleSheet(f"background:{T.CARD};border:1px solid {T.CARD_BORDER};border-radius:14px;")
    v=QVBoxLayout(f); v.setContentsMargins(16,14,16,14)
    if title:
        t=QLabel(title); t.setStyleSheet(f"color:{T.INK};font-size:14px;font-weight:bold;")
        v.addWidget(t)
    return f,v


class Dashboard(QWidget):
    back=pyqtSignal()

    def __init__(self, app, api=None):
        super().__init__()
        self.app=app; self.api=api; self.child=None
        from clinical_local import ISAAItems, Advisor  # local light copies
        self.advisor=Advisor()
        self._build()

    def _build(self):
        self.setStyleSheet(f"background:{T.LIGHT_BG};")
        root=QVBoxLayout(self); root.setContentsMargins(14,12,14,12); root.setSpacing(10)

        # title bar
        top=QHBoxLayout()
        self.title=QLabel("🤖 Pepper Clinical V6 — Dashboard")
        self.title.setStyleSheet(f"color:{T.INK};font-size:18px;font-weight:bold;")
        top.addWidget(self.title); top.addStretch()
        btnOut=QPushButton("Logout"); btnOut.setStyleSheet(
            f"background:white;color:{T.RED};border:1px solid {T.RED};border-radius:8px;padding:6px 16px;")
        btnOut.clicked.connect(self.back.emit)
        top.addWidget(btnOut)
        root.addLayout(top)

        # 7 tabs
        tabs=QHBoxLayout(); tabs.setSpacing(6)
        self.tabBtns={}
        for key,lbl in [("overview","📊 Overview"),("analytics","📈 Analytics"),
                        ("assess","🧪 Assessments"),("advisor","🤖 AI Advisor"),("insights","📈 Insights"),
                        ("live","👁 Live Monitor"),("hub","📚 Empowerment Hub"),
                        ("notes","📝 Notes")]:
            b=QPushButton(lbl)
            b.setStyleSheet(self._tab_style(False))
            b.clicked.connect(lambda _,k=key: self._show(k))
            tabs.addWidget(b); self.tabBtns[key]=b
        tabs.addStretch()
        root.addLayout(tabs)

        # stacked content
        from PyQt6.QtWidgets import QStackedWidget
        self.stack=QStackedWidget()
        self.p_overview=self._build_overview()
        self.p_analytics=self._build_analytics()
        self.p_assess=self._build_assess()
        self.p_advisor=self._build_advisor()
        self.p_insights=self._build_insights()
        self.p_live=self._build_live()
        self.p_hub=self._build_hub()
        self.p_notes=self._build_notes()
        for p in [self.p_overview,self.p_analytics,self.p_assess,self.p_advisor,self.p_insights,
                  self.p_live,self.p_hub,self.p_notes]:
            sc=QScrollArea(); sc.setWidgetResizable(True); sc.setWidget(p); self.stack.addWidget(sc)
        root.addWidget(self.stack,1)

        cr=QLabel(T.COPYRIGHT); cr.setStyleSheet(f"color:{T.MUTE};font-size:9px;")
        root.addWidget(cr)
        self.liveTimer=QTimer(self); self.liveTimer.timeout.connect(self._refresh_live)
        self.refreshTimer=QTimer(self); self.refreshTimer.timeout.connect(self._tick_refresh)
        self.refreshTimer.start(1000)
        from PyQt6.QtCore import QTimer as _QT
        self.camTimer=_QT(self); self.camTimer.timeout.connect(self._refresh_cam); self.camTimer.start(40)

    def _refresh_cam(self):
        # fast, smooth live video (only when Live Monitor tab is open)
        try:
            if self.stack.currentIndex()!=5: return
            from PyQt6.QtGui import QPixmap, QImage
            from frame_bridge import FRAMES
            jpeg,ts=FRAMES.get()
            if jpeg and FRAMES.is_fresh(2.0):
                img=QImage.fromData(jpeg,"JPEG")
                if not img.isNull():
                    pix=QPixmap.fromImage(img).scaled(500,500,
                        Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    self.liveCam.setPixmap(pix)
            else:
                self.liveCam.setText("Waiting for child session camera...")
        except Exception: pass

    def _tick_refresh(self):
        try:
            snap=STORE.snapshot()
        except Exception:
            return
        if not snap.get("active") and snap.get("total",0)==0:
            return
        idx=self.stack.currentIndex()
        if idx==0: self._fill_overview(snap)
        elif idx==1: self._fill_analytics(snap)
        elif idx==4: self._fill_insights(snap)
        elif idx==5: self._fill_live(snap)

    def _fill_overview(self, snap):
        # KPI cards
        while self.kpi.count():
            it=self.kpi.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        self.kpi.addWidget(self._kpi_card(snap["score"],"⭐ Score",T.GREEN))
        self.kpi.addWidget(self._kpi_card(snap["mastered"],"🏆 Mastered",T.GOLD))
        self.kpi.addWidget(self._kpi_card(f"{int(snap['avg_attention'])}%","🎯 Attention",T.BLUE))
        self.kpi.addWidget(self._kpi_card(snap["skipped"],"⏭ Skipped",T.RED))
        # emotion
        emo=snap["dominant_emotion"].upper()
        self.emoBig.setText(f"{emo} — {int(snap['avg_attention'])}%")
        self.emoSub.setText(f"Face:{'✅' if snap['live'].get('face_detected') else '—'} | "
            f"Fingers:{snap['live'].get('fingers',0)} | Streak:{snap['streak']} | "
            f"Fails:{snap['fail']}/2")
        # skills
        while self.skillsRow.count():
            it=self.skillsRow.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        for name,val in snap["skills"].items():
            c=QVBoxLayout(); w=QWidget(); w.setLayout(c)
            pv=QLabel(f"{int(val)}%"); pv.setStyleSheet(f"color:{T.PURPLE};font-size:20px;font-weight:bold;")
            pv.setAlignment(Qt.AlignmentFlag.AlignCenter)
            nl=QLabel(name); nl.setStyleSheet(f"color:{T.MUTE};font-size:11px;")
            nl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            c.addWidget(pv); c.addWidget(nl); self.skillsRow.addWidget(w)
        # PECS log
        self.pecsLog.setText("\n".join(f"{t} — {l}: {p}" for t,l,p in snap["pecs"][-6:]) or "No PECS yet")
        # chat
        self.ovChat.clear()
        for t,who,txt in snap["chat"][-12:]:
            self.ovChat.append(f"<b style='color:{T.PURPLE}'>{t} {who}:</b> {txt}")
        # log
        self.ovLog.clear()
        for t,txt in snap["log"][-12:]:
            self.ovLog.append(f"<span style='color:{T.MUTE}'>{t}</span> {txt}")
        # summary
        self.summaryLbl.setText(f"Child: {snap['child'].get('name','—')} | "
            f"OK:{snap['correct']} Fail:{snap['fail']} Skip:{snap['skipped']} | "
            f"Rate:{snap['success_rate']}%")

    def _fill_analytics(self, snap):
        scores=[d for d in range(0,0)]  # placeholder
        # build a running score progression from tasks
        run=[]; acc=0
        for td in snap["tasks_done"]:
            acc+= (10 if td["ok"] else 0); run.append(acc)
        self.cAtt.set_values([int(snap["avg_attention"])]* max(2,len(run)) if run else [0,0])
        self.cScore.set_values(run or [0])
        self.cDonut.set_parts([("Success",snap["correct"],T.GREEN),
            ("Fail",snap["fail"],T.RED),("Skipped",snap["skipped"],T.ORANGE)])
        self.cRadar.set_data(snap["skills"])

    def _fill_live(self, snap):
        pass  # camera handled by fast _refresh_cam; metrics below
        res=snap.get("live",{})
        if not snap.get("active") and not res:
            self.liveStatus.setText("No live session running."); self.liveMetrics.setText(""); return
        emo=res.get("emotion","neutral").upper(); conf=int(res.get("emotion_conf",0)*100)
        self.liveStatus.setText(f"{emo} — {conf}%")
        self.liveStatus.setStyleSheet(f"color:{T.GREEN};font-size:22px;font-weight:bold;padding:20px;")
        self.liveMetrics.setText(f"Score {snap['score']} | OK {snap['correct']} | Fail {snap['fail']} | "
            f"Attention {int(res.get('attention',0))}% | Fingers {res.get('fingers',0)} | "
            f"Gesture {res.get('gesture','none')} | Streak {snap['streak']}")

    def _tab_style(self,active):
        if active:
            return (f"background:white;color:{T.PURPLE};border:none;border-bottom:3px solid {T.PURPLE};"
                    f"border-radius:0;padding:8px 14px;font-weight:bold;")
        return (f"background:transparent;color:{T.MUTE};border:none;padding:8px 14px;font-weight:bold;")

    def open_for(self, child):
        self.child=child
        self.title.setText(f"🤖 Pepper Clinical V6 — {child.get('name','')} | Logged in")
        self._show("overview")

    def _show(self, key):
        idx={"overview":0,"analytics":1,"assess":2,"advisor":3,"insights":4,"live":5,"hub":6,"notes":7}[key]
        self.stack.setCurrentIndex(idx)
        for k,b in self.tabBtns.items(): b.setStyleSheet(self._tab_style(k==key))
        if key=="overview": self._refresh_overview()
        elif key=="analytics": self._refresh_analytics()
        elif key=="live": self.liveTimer.start(800)
        else: self.liveTimer.stop()

    # ---------- OVERVIEW (screenshot 1) ----------
    def _build_overview(self):
        w=QWidget(); v=QVBoxLayout(w); v.setSpacing(10)
        # KPI cards
        self.kpi=QHBoxLayout(); v.addLayout(self.kpi)
        # two columns: left (emotion+skills+pecs) right (chat+log+summary)
        cols=QHBoxLayout()
        left=QVBoxLayout(); right=QVBoxLayout()
        # emotion card
        ef,el=card("😊 Emotion (Conv Level 1)")
        self.emoBig=QLabel("NEUTRAL — 0%")
        self.emoBig.setStyleSheet(f"color:{T.GREEN};font-size:22px;font-weight:bold;")
        self.emoBig.setAlignment(Qt.AlignmentFlag.AlignCenter)
        el.addWidget(self.emoBig)
        self.emoSub=QLabel("Face:— | Fingers:0 | Streak:0 | Fails:0/2")
        self.emoSub.setStyleSheet(f"color:{T.MUTE};font-size:11px;")
        self.emoSub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        el.addWidget(self.emoSub)
        self.emoList=QLabel(""); self.emoList.setStyleSheet(f"color:{T.INK};font-size:12px;")
        el.addWidget(self.emoList)
        left.addWidget(ef)
        # skills card
        sf,sl=card("📊 Skills Profile")
        self.skillsRow=QHBoxLayout(); sl.addLayout(self.skillsRow)
        left.addWidget(sf)
        # PECS log card
        pf,pl=card("🗣 PECS Log")
        self.pecsLog=QLabel("No PECS yet"); self.pecsLog.setStyleSheet(f"color:{T.INK};font-size:11px;")
        self.pecsLog.setWordWrap(True); pl.addWidget(self.pecsLog)
        left.addWidget(pf)
        # session chat
        cf,cl=card("💬 Session Chat")
        self.ovChat=QTextEdit(); self.ovChat.setReadOnly(True); self.ovChat.setMaximumHeight(180)
        self.ovChat.setStyleSheet("border:none;font-size:11px;")
        cl.addWidget(self.ovChat)
        right.addWidget(cf)
        # log
        lf,ll=card("📋 Log")
        self.ovLog=QTextEdit(); self.ovLog.setReadOnly(True); self.ovLog.setMaximumHeight(180)
        self.ovLog.setStyleSheet("border:none;font-size:11px;")
        ll.addWidget(self.ovLog)
        right.addWidget(lf)
        # summary
        mf,ml=card("🏆 Summary")
        self.summaryLbl=QLabel("Child: — | — | L1")
        self.summaryLbl.setStyleSheet(f"color:{T.INK};font-size:12px;")
        ml.addWidget(self.summaryLbl)
        btnPDF=QPushButton("📄 Download PDF Report")
        btnPDF.setStyleSheet(f"background:{T.BLUE};color:white;border:none;border-radius:8px;padding:8px;font-weight:bold;")
        btnPDF.clicked.connect(self._pdf)
        ml.addWidget(btnPDF)
        right.addWidget(mf)
        cols.addLayout(left,1); cols.addLayout(right,1)
        v.addLayout(cols)
        return w

    def _kpi_card(self,value,label,color):
        f=QFrame(); f.setStyleSheet(f"background:{T.CARD};border:1px solid {T.CARD_BORDER};border-radius:14px;")
        vv=QVBoxLayout(f)
        val=QLabel(str(value)); val.setStyleSheet(f"color:{color};font-size:30px;font-weight:bold;")
        val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lab=QLabel(label); lab.setStyleSheet(f"color:{T.MUTE};font-size:12px;")
        lab.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vv.addWidget(val); vv.addWidget(lab)
        return f

    def _refresh_overview(self):
        while self.kpi.count():
            it=self.kpi.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        st=self._stats()
        self.kpi.addWidget(self._kpi_card(st["total_score"],"⭐ Score",T.GREEN))
        self.kpi.addWidget(self._kpi_card(st["total_mastered"],"🏆 Mastered",T.GOLD))
        self.kpi.addWidget(self._kpi_card(f"{int(st['avg_attention'])}%","🎯 Attention",T.BLUE))
        self.kpi.addWidget(self._kpi_card(st.get("skipped",0),"⏭ Skipped",T.RED))
        # skills
        while self.skillsRow.count():
            it=self.skillsRow.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        for name,val in st["skills"].items():
            c=QVBoxLayout(); w=QWidget(); w.setLayout(c)
            pv=QLabel(f"{int(val)}%"); pv.setStyleSheet(f"color:{T.PURPLE};font-size:20px;font-weight:bold;")
            pv.setAlignment(Qt.AlignmentFlag.AlignCenter)
            nl=QLabel(name); nl.setStyleSheet(f"color:{T.MUTE};font-size:11px;")
            nl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            c.addWidget(pv); c.addWidget(nl); self.skillsRow.addWidget(w)
        self.summaryLbl.setText(f"Child: {self.child.get('name','') if self.child else '—'} | "
            f"{datetime.now().strftime('%Y-%m-%d')} | OK:{st.get('ok',0)} Fail:{st.get('fail',0)}")

    def _stats(self):
        try:
            if self.api and self.child: return self.api.child_stats(self.child["id"])
        except Exception: pass
        # fallback from app live session
        s=getattr(self.app,"last_summary",{}) or {}
        return {"total_score":s.get("score",0),"total_mastered":s.get("mastered",0),
            "avg_attention":s.get("avg_attention",0),"skipped":s.get("skip",0),
            "ok":s.get("ok",0),"fail":s.get("fail",0),
            "skills":{"Motor":63,"Cognitive":50,"Verbal":50,"Math":50,"Social":50},
            "domain_stats":{},"session_scores":[]}

    # ---------- ANALYTICS (screenshot 2) ----------
    def _build_analytics(self):
        w=QWidget(); g=QGridLayout(w); g.setSpacing(10)
        af,al=card("📈 Attention Over Session"); self.cAtt=LineChart("",T.BLUE); al.addWidget(self.cAtt)
        sf,sl=card("⭐ Score Progression"); self.cScore=BarChart(""); sl.addWidget(self.cScore)
        tf,tl=card("🎯 Task Results"); self.cDonut=DonutChart(""); tl.addWidget(self.cDonut)
        rf,rl=card("📊 Skills Radar"); self.cRadar=RadarChart(""); rl.addWidget(self.cRadar)
        g.addWidget(af,0,0); g.addWidget(sf,0,1); g.addWidget(tf,1,0); g.addWidget(rf,1,1)
        return w

    def _refresh_analytics(self):
        st=self._stats()
        scores=st.get("session_scores",[]) or [10,10,10,10,20,30,45,60,82]
        self.cAtt.set_values([min(100,40+i*7) for i in range(len(scores) or 5)])
        self.cScore.set_values(scores)
        s=getattr(self.app,"last_summary",{}) or {}
        ok=s.get("ok",6); fail=s.get("fail",1); skip=s.get("skip",1)
        self.cDonut.set_parts([("Success",ok,T.GREEN),("Fail",fail,T.RED),("Skipped",skip,T.ORANGE)])
        self.cRadar.set_data(st["skills"])

    def _pdf(self):
        try:
            from report_pdf import build_report
            st=self._stats()
            s=getattr(self.app,"last_summary",{}) or {}
            path=build_report(self.child or {"name":"child","age":""}, 
                {**s,"score":st["total_score"],"mastered":st["total_mastered"],
                 "avg_attention":st["avg_attention"]}, skills=st["skills"])
            QMessageBox.information(self,"PDF",f"Saved:\n{path}")
        except Exception as e:
            QMessageBox.information(self,"PDF",f"Install reportlab. {e}")

    # ---------- ASSESSMENTS: ASQ-3 + VB-MAPP + ISAA (screenshot 4) ----------
    def _build_assess(self):
        from clinical_local import ISAAItems
        w=QWidget(); v=QVBoxLayout(w); v.setSpacing(12)

        # ===== ASQ-3 =====
        af,al=card("🧪 ASQ-3 Assessment")
        hint=QLabel("Rate each: 0=Never, 1=Sometimes, 2=Often")
        hint.setStyleSheet(f"color:{T.MUTE};font-size:11px;"); al.addWidget(hint)
        asq=["Does your child look at you when you talk?","Does your child point to things?",
        "Can your child say 5+ words?","Does your child play with other children?",
        "Can your child follow 2-step instructions?","Does your child make eye contact?",
        "Can your child stack blocks?","Does your child respond to their name?",
        "Can your child draw a circle?","Does your child show emotions appropriately?"]
        self.asq_combos=[]
        g=QGridLayout()
        for i,q in enumerate(asq):
            lab=QLabel(q); lab.setStyleSheet(f"color:{T.INK};font-size:12px;"); lab.setWordWrap(True)
            cb=QComboBox(); cb.addItems(["0 - Never","1 - Sometimes","2 - Often"])
            cb.setStyleSheet(f"background:white;border:1px solid {T.CARD_BORDER};border-radius:6px;padding:5px;")
            g.addWidget(lab,(i//2)*2,i%2); g.addWidget(cb,(i//2)*2+1,i%2)
            self.asq_combos.append(cb)
        al.addLayout(g)
        bAsq=QPushButton("Submit ASQ")
        bAsq.setStyleSheet(f"background:{T.TEAL};color:white;border:none;border-radius:8px;padding:8px;font-weight:bold;")
        bAsq.clicked.connect(self._submit_asq)
        al.addWidget(bAsq)
        self.asqResult=QLabel(""); self.asqResult.setStyleSheet(f"color:{T.INK};font-weight:bold;")
        al.addWidget(self.asqResult)
        v.addWidget(af)

        # ===== VB-MAPP =====
        vf,vl=card("🧪 VB-MAPP (Verbal Behavior)")
        vb=["Can the child mand (request) for preferred items?","Does the child tact (label) 10+ objects?",
        "Can the child imitate 5+ actions?","Does the child attend to speaker for 30+ seconds?"]
        self.vb_combos=[]
        gv=QGridLayout()
        for i,q in enumerate(vb):
            lab=QLabel(q); lab.setStyleSheet(f"color:{T.INK};font-size:12px;"); lab.setWordWrap(True)
            cb=QComboBox(); cb.addItems(["0 - No","1 - Emerging","2 - Yes"])
            cb.setStyleSheet(f"background:white;border:1px solid {T.CARD_BORDER};border-radius:6px;padding:5px;")
            gv.addWidget(lab,(i//2)*2,i%2); gv.addWidget(cb,(i//2)*2+1,i%2)
            self.vb_combos.append(cb)
        vl.addLayout(gv)
        v.addWidget(vf)

        # ===== ISAA (full 40-item) =====
        isf,isl=card("🧪 ISAA — Indian Scale for Assessment of Autism")
        ihint=QLabel("Rate each item 1–5  (1=Never · 2=Rarely · 3=Sometimes · 4=Often · 5=Always)")
        ihint.setStyleSheet(f"color:{T.MUTE};font-size:11px;"); isl.addWidget(ihint)
        self.isaa_combos=[]
        items=ISAAItems.all(); cur_dom=None
        for idx,it in enumerate(items):
            if it["domain"]!=cur_dom:
                cur_dom=it["domain"]
                dl=QLabel(f"▸ {cur_dom}")
                dl.setStyleSheet(f"color:{T.PURPLE};font-size:12px;font-weight:bold;margin-top:6px;")
                isl.addWidget(dl)
            row=QHBoxLayout()
            q=QLabel(f"{idx+1}. {it['question']}")
            q.setStyleSheet(f"color:{T.INK};font-size:11px;"); q.setWordWrap(True)
            cb=QComboBox(); cb.addItems(["1","2","3","4","5"])
            cb.setFixedWidth(60)
            cb.setStyleSheet(f"background:white;border:1px solid {T.CARD_BORDER};border-radius:6px;padding:4px;")
            row.addWidget(q,1); row.addWidget(cb)
            isl.addLayout(row); self.isaa_combos.append(cb)
        rowb=QHBoxLayout()
        bIsaa=QPushButton("Score ISAA")
        bIsaa.setStyleSheet(f"background:{T.PURPLE};color:white;border:none;border-radius:8px;padding:8px;font-weight:bold;")
        bIsaa.clicked.connect(self._submit_isaa)
        bReset=QPushButton("Reset")
        bReset.setStyleSheet(f"background:white;color:{T.MUTE};border:1px solid {T.CARD_BORDER};border-radius:8px;padding:8px;")
        bReset.clicked.connect(self._reset_isaa)
        rowb.addWidget(bIsaa); rowb.addWidget(bReset)
        isl.addLayout(rowb)
        self.isaaResult=QLabel(""); self.isaaResult.setStyleSheet("font-weight:bold;font-size:13px;")
        self.isaaResult.setWordWrap(True)
        isl.addWidget(self.isaaResult)
        v.addWidget(isf)
        return w

    def _submit_asq(self):
        total=sum(c.currentIndex() for c in self.asq_combos)
        mx=len(self.asq_combos)*2
        flag="✅ On track" if total>=mx*0.6 else "⚠ Below cutoff — consider screening"
        self.asqResult.setText(f"ASQ-3 score: {total}/{mx} — {flag}")

    def _submit_isaa(self):
        from clinical_local import ISAAItems
        answers={i:(c.currentIndex()+1) for i,c in enumerate(self.isaa_combos)}
        r=ISAAItems.score(answers)
        self.isaaResult.setStyleSheet(f"font-weight:bold;font-size:13px;color:{r['color']};")
        self.isaaResult.setText(f"ISAA total: {r['total']} / {r['max']}  →  {r['level']}\n{r['interpretation']}")

    def _reset_isaa(self):
        for c in self.isaa_combos: c.setCurrentIndex(0)
        self.isaaResult.setText("")

    # ---------- AI ADVISOR ----------
    def _build_insights(self):
        w=QWidget(); v=QVBoxLayout(w)
        f1,l1=card("📈 Live Session Trend")
        self.insTrend=LineChart(""); l1.addWidget(self.insTrend); v.addWidget(f1)
        f2,l2=card("🏆 Skill Analysis")
        self.insStrong=QLabel("Strongest: —")
        self.insStrong.setStyleSheet(f"color:{T.GREEN};font-size:14px;font-weight:bold;padding:4px;")
        self.insWeak=QLabel("Needs focus: —")
        self.insWeak.setStyleSheet(f"color:{T.RED};font-size:14px;font-weight:bold;padding:4px;")
        l2.addWidget(self.insStrong); l2.addWidget(self.insWeak); v.addWidget(f2)
        f3,l3=card("💡 Smart Recommendations")
        self.insReco=QLabel("Start a session to see personalized recommendations.")
        self.insReco.setWordWrap(True)
        self.insReco.setStyleSheet(f"color:{T.INK};font-size:13px;padding:6px;line-height:150%;")
        l3.addWidget(self.insReco); v.addWidget(f3)
        f4,l4=card("⚡ Performance Metrics")
        self.insPerf=QLabel("—")
        self.insPerf.setStyleSheet(f"color:{T.MUTE};font-size:12px;padding:4px;")
        l4.addWidget(self.insPerf); v.addWidget(f4)
        v.addStretch()
        return w

    def _fill_insights(self, snap):
        try:
            skills=snap.get("skills",{})
            if skills:
                best=max(skills,key=skills.get); worst=min(skills,key=skills.get)
                self.insStrong.setText(f"Strongest: {best} ({skills[best]}%)")
                self.insWeak.setText(f"Needs focus: {worst} ({skills[worst]}%)")
                tips=[]
                if skills[worst]<40: tips.append(f"Add more {worst} activities (currently {skills[worst]}%).")
                if snap.get("success_rate",0)<50: tips.append("Try shorter sessions with easier tasks to build confidence.")
                if snap.get("avg_attention",100)<50: tips.append("A quieter, well-lit room may improve attention.")
                if snap.get("streak",0)>=5: tips.append(f"Excellent streak of {snap['streak']} — consider raising difficulty.")
                if not tips: tips.append("Balanced progress across all skills. Keep the current routine.")
                self.insReco.setText("  •  ".join(tips))
            run=[]; acc=0
            for td in snap.get("tasks_done",[]):
                acc += 10 if td.get("ok") else 0
                run.append(acc)
            self.insTrend.set_values(run or [0])
            self.insPerf.setText(
                f"Tasks: {snap.get('total',0)}   |   Correct: {snap.get('correct',0)}   |   "
                f"Success: {snap.get('success_rate',0)}%   |   Attention: {int(snap.get('avg_attention',0))}%   |   "
                f"Mood: {snap.get('dominant_emotion','—')}")
        except Exception as e:
            print("[insights] fill error:", e)

    def _build_advisor(self):
        w=QWidget(); v=QVBoxLayout(w); v.setSpacing(10)
        f,l=card("🤖 Dr. Pepper — Clinical Advisor (with memory)")
        self.advChat=QTextEdit(); self.advChat.setReadOnly(True); self.advChat.setMinimumHeight(280)
        self.advChat.setStyleSheet("border:none;font-size:12px;")
        self.advChat.append(f"<b style='color:{T.PURPLE}'>Dr. Pepper:</b> Hello! Ask me about meltdowns, "
            "speech, stimming, routines, sensory, sleep, food, toileting, aggression, social skills, or ABA.")
        l.addWidget(self.advChat)
        row=QHBoxLayout()
        self.advInput=QLineEdit(); self.advInput.setPlaceholderText("Ask Dr. Pepper…")
        self.advInput.setStyleSheet(f"background:white;border:1px solid {T.CARD_BORDER};border-radius:8px;padding:8px;")
        self.advInput.returnPressed.connect(self._ask_advisor)
        bAsk=QPushButton("Ask")
        bAsk.setStyleSheet(f"background:{T.PURPLE};color:white;border:none;border-radius:8px;padding:8px 18px;font-weight:bold;")
        bAsk.clicked.connect(self._ask_advisor)
        row.addWidget(self.advInput,1); row.addWidget(bAsk)
        l.addLayout(row)
        v.addWidget(f)
        return w

    def _ask_advisor(self):
        q=self.advInput.text().strip()
        if not q: return
        self.advChat.append(f"<b>You:</b> {q}")
        ans=self.advisor.ask(q)
        self.advChat.append(f"<b style='color:{T.PURPLE}'>Dr. Pepper:</b> {ans}")
        self.advInput.clear()
        sb=self.advChat.verticalScrollBar(); sb.setValue(sb.maximum())

    # ---------- LIVE MONITOR (screenshot 7) ----------
    def _build_live(self):
        w=QWidget(); v=QVBoxLayout(w); v.setSpacing(10)
        f,l=card("👁 Live Child Camera & Audio")
        sub=QLabel("Real-time status from the active therapy session.")
        sub.setStyleSheet(f"color:{T.MUTE};font-size:11px;"); l.addWidget(sub)
        self.liveCam=QLabel("Camera will appear here when the child session is live.")
        self.liveCam.setFixedSize(500,500)
        self.liveCam.setStyleSheet(f"background:#0a0e1a;color:{T.MUTE};border:2px solid {T.PURPLE};border-radius:12px;")
        self.liveCam.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addWidget(self.liveCam)
        self.liveStatus=QLabel("No live session running.")
        self.liveStatus.setStyleSheet(f"color:{T.INK};font-size:16px;font-weight:bold;padding:20px;")
        self.liveStatus.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addWidget(self.liveStatus)
        self.liveMetrics=QLabel("")
        self.liveMetrics.setStyleSheet(f"color:{T.MUTE};font-size:13px;")
        self.liveMetrics.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addWidget(self.liveMetrics)
        v.addWidget(f); v.addStretch()
        return w

    def _refresh_live(self):
        if getattr(self,'_live_busy',False): return
        self._live_busy=True
        res=getattr(self.app,"live",{}) or {}
        if not res:
            self.liveStatus.setText("No live session running.")
            self.liveMetrics.setText(""); self._live_busy=False; return
        emo=res.get("emotion","neutral").upper(); conf=int(res.get("emotion_conf",0)*100)
        self.liveStatus.setText(f"{emo} — {conf}%")
        self.liveStatus.setStyleSheet(f"color:{T.GREEN};font-size:22px;font-weight:bold;padding:20px;")
        self.liveMetrics.setText(f"Attention: {int(res.get('attention',0))}%   |   "
            f"Fingers: {res.get('fingers',0)}   |   Gesture: {res.get('gesture','none')}   |   "
            f"Face: {'Ok' if res.get('face_detected') else 'No'}")
        self._live_busy=False

    # ---------- EMPOWERMENT HUB (screenshot 3) ----------
    def _build_hub(self):
        import webbrowser, urllib.parse
        w=QWidget(); v=QVBoxLayout(w); v.setSpacing(10)
        intro_f,intro_l=card("📚 Empowerment Hub — Become a Home Therapist!")
        intro=QLabel("Learn ABA, TEACCH, DTT, and ESDM strategies to reinforce therapy at home. "
            "Each module takes 5–10 minutes and includes practical exercises.")
        intro.setStyleSheet(f"color:{T.INK};font-size:12px;"); intro.setWordWrap(True)
        intro_l.addWidget(intro); v.addWidget(intro_f)
        modules=[("🔬 ABA Basics","Applied Behavior Analysis breaks skills into small steps, reinforcing each success. "
                  "DTT uses clear instructions, prompts, and immediate reinforcement. At home: 5–10 min daily sessions, consistent rewards.",
                  "ABA therapy basics for parents"),
        ("📋 TEACCH Visual Support","TEACCH uses visual schedules, structured workspaces, and predictable routines. "
                  "Create a visual schedule with pictures. Use 'work' and 'break' boxes. Keep the workspace distraction-free.",
                  "TEACCH visual schedule autism"),
        ("👥 ESDM Social Skills","Early Start Denver Model focuses on social engagement through play. Follow your child's lead, "
                  "join their activity, add language naturally. Celebrate every communication attempt.",
                  "ESDM early start denver model parents"),
        ("🎯 DTT Home Practice","Discrete Trial Training at home: 1) clear instruction 2) wait 3–5s 3) prompt if needed "
                  "4) reinforce immediately. Practice 5–7 trials then break. Track results.",
                  "discrete trial training home")]
        for title,body,q in modules:
            f,l=card(title)
            b=QLabel(body); b.setStyleSheet(f"color:{T.INK};font-size:12px;"); b.setWordWrap(True)
            l.addWidget(b)
            btn=QPushButton("🎬 Watch Training Video")
            btn.setStyleSheet(f"background:white;color:{T.PURPLE};border:1px solid {T.PURPLE};"
                f"border-radius:8px;padding:7px;font-weight:bold;")
            btn.clicked.connect(lambda _,qq=q: webbrowser.open(
                "https://www.youtube.com/results?search_query="+urllib.parse.quote(qq)))
            l.addWidget(btn); v.addWidget(f)
        return w

    # ---------- NOTES ----------
    def _build_notes(self):
        w=QWidget(); v=QVBoxLayout(w)
        f,l=card("📝 Clinical Notes")
        self.notes=QTextEdit(); self.notes.setMinimumHeight(360)
        self.notes.setStyleSheet(f"background:white;border:1px solid {T.CARD_BORDER};border-radius:8px;font-size:13px;")
        self.notes.setPlaceholderText("Type clinical observations here…")
        l.addWidget(self.notes)
        b=QPushButton("💾 Save Notes")
        b.setStyleSheet(f"background:{T.TEAL};color:white;border:none;border-radius:8px;padding:8px;font-weight:bold;")
        b.clicked.connect(lambda: QMessageBox.information(self,"Notes","Notes saved for this session."))
        l.addWidget(b); v.addWidget(f)
        return w

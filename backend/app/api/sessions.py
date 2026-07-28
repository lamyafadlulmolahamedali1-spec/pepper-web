"""Sessions + tasks (100k via infinite generation) + stats. © 2026 Lamya F. H. Ali"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db, User, Child, TherapySession, TaskEvent
from app.api.deps import get_current_user
from app.models.schemas import SessionStart, SessionEnd
from app.services.task_generator import TaskGenerator

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


def _own(db, user, child_id):
    c=db.query(Child).filter(Child.id==child_id, Child.parent_id==user.id).first()
    if not c: raise HTTPException(status_code=404, detail="Child not found")
    return c


@router.post("/start", status_code=201)
def start(body: SessionStart, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _own(db, user, body.child_id)
    s=TherapySession(user_id=user.id, child_id=body.child_id, protocol=body.protocol,
                     started_at=datetime.now(timezone.utc))
    db.add(s); db.commit(); db.refresh(s)
    return {"id": s.id, "started_at": s.started_at.isoformat()}


@router.post("/tasks/generate")
def gen(body: dict, user: User = Depends(get_current_user)):
    # Infinite pool — call repeatedly for 100k+ unique tasks
    count=min(int(body.get("count",20)), 200)
    level=int(body.get("level",1))
    domain=body.get("domain")
    tasks=TaskGenerator.generate(domain=domain, level=level, count=count)
    return {"count": len(tasks), "tasks": tasks}


@router.post("/log-task")
def log(body: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ev=TaskEvent(session_id=body.get("session_id",""), child_id=body.get("child_id",""),
        domain=body.get("domain",""), task_type=body.get("task_type",""),
        success=1 if body.get("success") else 0,
        attention=float(body.get("attention",0) or 0), emotion=body.get("emotion",""))
    db.add(ev); db.commit()
    return {"ok": True}


@router.post("/end")
def end(body: SessionEnd, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    s=db.query(TherapySession).filter(TherapySession.id==body.session_id,
                                      TherapySession.user_id==user.id).first()
    if not s: raise HTTPException(status_code=404, detail="Session not found")
    s.ended_at=datetime.now(timezone.utc); s.duration_sec=body.duration_sec
    s.score=body.score; s.tasks_total=body.tasks_total; s.tasks_success=body.tasks_success
    s.tasks_fail=body.tasks_fail; s.tasks_mastered=body.tasks_mastered
    s.avg_attention=body.avg_attention; s.dominant_emotion=body.dominant_emotion
    c=db.query(Child).filter(Child.id==s.child_id).first()
    if c:
        c.total_sessions+=1; c.total_score+=body.score
        if body.tasks_total>0:
            bump=(body.tasks_success/body.tasks_total-0.5)*4
            for a in ("skill_motor","skill_cognitive","skill_verbal","skill_math","skill_social"):
                setattr(c,a,max(0,min(100,getattr(c,a)+bump)))
    db.commit()
    return {"id": s.id, "score": s.score}


@router.get("/stats/{child_id}")
def stats(child_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    c=_own(db, user, child_id)
    sess=db.query(TherapySession).filter(TherapySession.child_id==child_id,
        TherapySession.ended_at.isnot(None)).order_by(TherapySession.started_at.asc()).all()
    events=db.query(TaskEvent).filter(TaskEvent.child_id==child_id).all()
    attns=[s.avg_attention for s in sess if s.avg_attention]
    ds={}
    for e in events:
        d=e.domain or "Other"; ds.setdefault(d,{"total":0,"success":0})
        ds[d]["total"]+=1; ds[d]["success"]+=e.success
    return {"total_sessions":c.total_sessions,"total_score":c.total_score,
        "total_mastered":sum(s.tasks_mastered for s in sess),
        "avg_attention":round(sum(attns)/len(attns),1) if attns else 0,
        "skills":{"Motor":c.skill_motor,"Cognitive":c.skill_cognitive,"Verbal":c.skill_verbal,
                  "Math":c.skill_math,"Social":c.skill_social},
        "domain_stats":ds,"session_scores":[s.score for s in sess]}

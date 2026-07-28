"""Clinical (ISAA + advisor) + life-skill videos. © 2026 Lamya F. H. Ali"""
from typing import Dict
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.clinical import ISAAAssessment, ClinicalAdvisor
from app.services.videos import all_videos, for_task

router = APIRouter(prefix="/api/clinical", tags=["Clinical"])
_advisors: Dict[str, ClinicalAdvisor] = {}

def _adv(uid="public"):
    if uid not in _advisors: _advisors[uid]=ClinicalAdvisor()
    return _advisors[uid]

@router.get("/isaa/items")
def isaa_items():
    return {"total": ISAAAssessment.total_items(), "items": ISAAAssessment.all_items()}

class ISAAReq(BaseModel):
    answers: Dict[str, int]

@router.post("/isaa/score")
def isaa_score(b: ISAAReq):
    return ISAAAssessment.score({int(k):v for k,v in b.answers.items()})

class AskReq(BaseModel):
    question: str

@router.post("/advisor/ask")
def advisor_ask(b: AskReq):
    a=_adv(); ans=a.ask(b.question)
    return {"answer":ans,"memory_size":len(a.history()),"topics":a.topics_discussed()}

@router.get("/advisor/history")
def advisor_history():
    a=_adv(); return {"history":a.history(),"topics":a.topics_discussed()}

@router.get("/videos")
def videos():
    return {"videos": all_videos()}

@router.get("/videos/for")
def video_for(task_type: str, name: str = ""):
    return for_task(task_type, name)

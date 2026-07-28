"""ISAA + AI Advisor with memory. © 2026 Lamya F. H. Ali"""
import time
from collections import Counter

ISAA_DOMAINS = {
 "Social Relationship & Reciprocity":["Has poor eye contact","Lacks social smile",
  "Remains aloof / prefers to be alone","Does not reach out to others",
  "Unable to relate to people","Unable to respond to social cues",
  "Engages in solitary repetitive play","Unable to take turns","Does not maintain peer relations"],
 "Emotional Responsiveness":["Inappropriate emotional response","Exaggerated emotions",
  "Self-stimulating emotions","Lacks fear of danger","Excited/agitated for no reason"],
 "Speech, Language & Communication":["Acquired speech then lost it","Difficulty using gestures",
  "Stereotyped repetitive language","Echolalic speech","Infantile squeals/noises",
  "Cannot initiate/sustain conversation","Uses jargon","Pronoun reversal","Cannot grasp pragmatics"],
 "Behaviour Patterns":["Stereotyped motor mannerisms","Attachment to objects","Hyperactivity",
  "Aggressive behaviour","Temper tantrums","Self-injurious behaviour","Insists on sameness"],
 "Sensory Aspects":["Unusually sensitive to stimuli","Stares into space","Difficulty tracking objects",
  "Unusual vision","Insensitive to pain","Responds by smelling/touching/tasting"],
 "Cognitive Component":["Inconsistent attention","Delay in responding","Unusual memory","Savant ability"],
}

class ISAAAssessment:
    @staticmethod
    def all_items():
        out=[]
        for d,qs in ISAA_DOMAINS.items():
            for q in qs: out.append({"domain":d,"question":q})
        return out
    @staticmethod
    def total_items(): return sum(len(v) for v in ISAA_DOMAINS.values())
    @staticmethod
    def score(answers):
        vals=[v for v in answers.values() if isinstance(v,(int,float))]
        total=sum(vals)
        if total<70: lvl,col="No Autism","#059669"
        elif total<=106: lvl,col="Mild Autism","#0d9488"
        elif total<=153: lvl,col="Moderate Autism","#d97706"
        else: lvl,col="Severe Autism","#dc2626"
        items=ISAAAssessment.all_items(); ds={}
        for i,v in answers.items():
            try: d=items[int(i)]["domain"]; ds[d]=ds.get(d,0)+v
            except: pass
        return {"total":total,"answered":len(vals),"max_possible":ISAAAssessment.total_items()*5,
        "level":lvl,"color":col,"domain_scores":ds,
        "interpretation":f"Total ISAA score: {total}. Classification: {lvl}. Screening aid only — a clinician must confirm."}

class ClinicalAdvisor:
    KB={"meltdown":"Meltdowns are involuntary responses to overload, not misbehaviour. Stay calm, reduce sensory input, give space, use few words, offer a calming item. Track triggers.",
    "eye contact":"Don't force eye contact. Hold a preferred toy near your face, reward any glance, build joint attention.",
    "speech":"Model single words, use visuals/PECS, narrate routines, pause to invite responses, honor every attempt. See an SLP.",
    "stimming":"Stimming is self-regulation. Allow safe stims; only redirect if harmful, replacing with a safe alternative.",
    "routine":"Predictable routines reduce anxiety. Use a visual schedule, preview changes, use timers (TEACCH).",
    "sensory":"Identify over/under-sensitivity. Offer a sensory diet: movement breaks, deep pressure, fidgets. See an OT.",
    "sleep":"Fixed bedtime routine, reduce screens, blackout curtains, weighted blanket; melatonin only with medical advice.",
    "food":"Avoid pressure. Introduce new foods beside preferred ones, repeated neutral exposure, involve the child.",
    "potty":"Ensure readiness, visual sequence, scheduled sits, reward success, stay consistent.",
    "aggression":"Identify the function (escape/attention/sensory). Teach a replacement skill, keep safe, stay neutral.",
    "social":"Structured play, turn-taking games, social stories, peer modeling. Reinforce every interaction attempt.",
    "aba":"ABA breaks skills into small steps with reinforcement and data. Modern ABA is play-based and child-led."}
    GREETING="Hello, I'm Dr. Pepper. Ask about meltdowns, speech, stimming, routines, sensory, sleep, food, toileting, aggression, social skills, or therapy methods. I remember our conversation."
    def __init__(self): self.memory=[]
    def _match(self,q):
        ql=q.lower()
        for k,a in self.KB.items():
            if k in ql: return k,a
        syn={"tantrum":"meltdown","scream":"meltdown","talk":"speech","language":"speech",
        "word":"speech","flap":"stimming","rock":"stimming","schedule":"routine","transition":"routine",
        "noise":"sensory","light":"sensory","bed":"sleep","night":"sleep","eat":"food","picky":"food",
        "toilet":"potty","hit":"aggression","bite":"aggression","friend":"social","play":"social",
        "therapy":"aba","look":"eye contact","gaze":"eye contact"}
        for s,k in syn.items():
            if s in ql: return k,self.KB[k]
        return None,None
    def ask(self,q):
        q=(q or "").strip()
        if not q: return self.GREETING
        topic,ans=self._match(q)
        if ans:
            recur=sum(1 for m in self.memory if m["topic"]==topic)
            reply=(f"(Building on what we discussed about {topic}:) " if recur else "")+ans
        else:
            topic="general"; reply="I can advise on meltdowns, eye contact, speech, stimming, routines, sensory, sleep, food, toileting, aggression, social skills, and therapy methods. Which is closest?"
        self.memory.append({"q":q,"a":reply,"topic":topic,"ts":time.time()})
        return reply
    def history(self): return self.memory
    def topics_discussed(self): return dict(Counter(m["topic"] for m in self.memory))

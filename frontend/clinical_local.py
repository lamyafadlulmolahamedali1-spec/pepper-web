"""Local light copies of ISAA + Advisor for offline dashboard. © 2026 Lamya F. H. Ali"""

ISAA_DOMAINS = {
 "Social Relationship & Reciprocity":["Has poor eye contact","Lacks social smile",
  "Prefers to be alone","Does not reach out to others","Unable to relate to people",
  "Unable to respond to social cues","Solitary repetitive play","Unable to take turns",
  "Does not maintain peer relations"],
 "Emotional Responsiveness":["Inappropriate emotional response","Exaggerated emotions",
  "Self-stimulating emotions","Lacks fear of danger","Excited for no reason"],
 "Speech, Language & Communication":["Acquired speech then lost it","Difficulty using gestures",
  "Stereotyped repetitive language","Echolalic speech","Infantile noises",
  "Cannot sustain conversation","Uses jargon","Pronoun reversal","Cannot grasp pragmatics"],
 "Behaviour Patterns":["Stereotyped mannerisms","Attachment to objects","Hyperactivity",
  "Aggressive behaviour","Temper tantrums","Self-injurious behaviour","Insists on sameness"],
 "Sensory Aspects":["Sensitive to stimuli","Stares into space","Difficulty tracking objects",
  "Unusual vision","Insensitive to pain","Smells/touches/tastes objects"],
 "Cognitive Component":["Inconsistent attention","Delay in responding","Unusual memory","Savant ability"],
}

class ISAAItems:
    @staticmethod
    def all():
        out=[]
        for d,qs in ISAA_DOMAINS.items():
            for q in qs: out.append({"domain":d,"question":q})
        return out
    @staticmethod
    def total(): return sum(len(v) for v in ISAA_DOMAINS.values())
    @staticmethod
    def score(answers):
        total=sum(v for v in answers.values() if isinstance(v,(int,float)))
        if total<70: lvl,col="No Autism","#059669"
        elif total<=106: lvl,col="Mild Autism","#0d9488"
        elif total<=153: lvl,col="Moderate Autism","#d97706"
        else: lvl,col="Severe Autism","#dc2626"
        return {"total":total,"level":lvl,"color":col,
            "max":ISAAItems.total()*5,
            "interpretation":f"ISAA total {total} — {lvl}. Screening aid only; a clinician must confirm."}

class Advisor:
    KB={"meltdown":"Stay calm, reduce sensory input, give space, few words, offer a calming item. Track triggers.",
    "eye contact":"Don't force it. Hold a preferred toy near your face, reward any glance.",
    "speech":"Model single words, use visuals/PECS, narrate routines, honor every attempt. See an SLP.",
    "stimming":"Stimming is self-regulation. Allow safe stims; redirect only if harmful.",
    "routine":"Use a visual schedule, preview changes, use timers (TEACCH).",
    "sensory":"Offer a sensory diet: movement breaks, deep pressure, fidgets. See an OT.",
    "sleep":"Fixed bedtime routine, reduce screens, blackout curtains; melatonin only with medical advice.",
    "food":"Avoid pressure. Introduce new foods beside preferred ones, repeated exposure.",
    "potty":"Visual sequence, scheduled sits, reward success, stay consistent.",
    "aggression":"Find the function, teach a replacement skill, keep safe, stay neutral.",
    "social":"Structured play, turn-taking, social stories, peer modeling.",
    "aba":"ABA breaks skills into small steps with reinforcement and data; modern ABA is play-based."}
    def __init__(self): self.memory=[]
    def ask(self,q):
        ql=(q or "").lower().strip()
        if not ql: return "Hello, I'm Dr. Pepper. Ask about meltdowns, speech, stimming, sleep, sensory, food, social skills, ABA…"
        syn={"tantrum":"meltdown","talk":"speech","language":"speech","flap":"stimming",
        "schedule":"routine","noise":"sensory","bed":"sleep","eat":"food","picky":"food",
        "toilet":"potty","hit":"aggression","friend":"social","therapy":"aba","look":"eye contact"}
        topic=None
        for k in self.KB:
            if k in ql: topic=k; break
        if not topic:
            for s,k in syn.items():
                if s in ql: topic=k; break
        if topic:
            recur=any(m["topic"]==topic for m in self.memory)
            ans=("(Building on what we discussed:) " if recur else "")+self.KB[topic]
        else:
            topic="general"; ans="I can advise on meltdowns, speech, stimming, routines, sensory, sleep, food, toileting, aggression, social skills, and ABA. Which is closest?"
        self.memory.append({"q":q,"a":ans,"topic":topic})
        return ans

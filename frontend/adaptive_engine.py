"""Adaptive engine for ASD therapy — difficulty adjustment, break detection,
token economy, prompt fading. © 2026 Lamya Fadlulmola Hamed Ali"""
class AdaptiveEngine:
    def __init__(self, start_level=1, max_level=5):
        self.level=start_level; self.max_level=max_level
        self.correct_streak=0; self.fail_streak=0; self.low_attention_streak=0
        self.tokens=0; self.tokens_to_reward=5; self.history=[]; self.prompts_given=0
    def record(self, success, attention=100.0):
        self.history.append(bool(success)); self.history=self.history[-20:]
        if success: self.correct_streak+=1; self.fail_streak=0; self.tokens+=1
        else: self.fail_streak+=1; self.correct_streak=0
        if attention<45: self.low_attention_streak+=1
        else: self.low_attention_streak=0
        return self._decide()
    def _decide(self):
        a={"level_change":0,"break":False,"reward":False,"prompt":"none","message":""}
        if self.tokens>=self.tokens_to_reward: a["reward"]=True; self.tokens=0
        if self.correct_streak>=3 and self.level<self.max_level:
            self.level+=1; self.correct_streak=0; a["level_change"]=1
            a["message"]=f"Level up! Now level {self.level} 🌟"
        if self.fail_streak>=3:
            if self.level>1: self.level-=1; a["level_change"]=-1
            a["prompt"]="full"; a["message"]="Let's make it easier — you've got this! 💪"; self.fail_streak=0
        if self.low_attention_streak>=4 or self.fail_streak>=5:
            a["break"]=True; a["message"]="Time for a calm break 🌿 — breathe and relax."; self.low_attention_streak=0
        return a
    def success_rate(self):
        return int(sum(self.history)/len(self.history)*100) if self.history else 0
    def prompt_level(self):
        if self.correct_streak>=4: return "independent"
        if self.correct_streak>=2: return "partial"
        return "full"
NEW_SKILLS={
 "Emotional Regulation":[("Take 3 deep breaths with me 🌬️","breathe"),("Show me your calm face 😌","calm_face"),
   ("Squeeze and release your hands 🤲","squeeze"),("Point to how you feel 😊😢😠","feelings")],
 "Joint Attention":[("Look where I'm pointing! 👉","follow_point"),("Look at the screen, then at me 👀","gaze_shift"),
   ("Find what I'm looking at 🔍","joint_look")],
 "Imitation":[("Do what I do — clap! 👏","imitate_clap"),("Copy me — arms up! 🙌","imitate_arms"),
   ("Copy my happy face 😄","imitate_smile")],
 "Requesting (Manding)":[("Ask for 'more' with your words or card ➕","mand_more"),("Ask for a break ⏸️","mand_break"),
   ("Tell me what you want 🗣️","mand_want")],
 "Turn Taking":[("My turn… now YOUR turn! 🔄","turn"),("Wait for the green light, then go 🟢","wait_go")],
 "Daily Routine":[("Show how you wash hands 🧼","wash_hands"),("Show how you brush teeth 🦷","brush_teeth"),
   ("Pretend to put on your shoes 👟","shoes"),("Show how you wave goodbye 👋","goodbye")],
 "Sensory Calming":[("Slow breathing — in… out… 🌬️","breathe"),("Gentle hand squeeze 🤲","squeeze"),
   ("Look at the calm colors 🌈","calm_look")],
}
def expanded_tasks(level=1, count=12):
    import random; out=[]; domains=list(NEW_SKILLS.keys())
    for _ in range(count):
        d=random.choice(domains); instr,verify=random.choice(NEW_SKILLS[d])
        out.append({"type":"skill","name":instr.split("—")[0].strip()[:24],
            "em":instr.split()[-1] if instr.split() else "🎯","instruction":instr,"verify":verify,
            "domain":d,"protocol":random.choice(["ABA-DTT","ESDM","TEACCH","PRT"]),"tokens":10,
            "success":"Wonderful! You did it! 🌟","fail":"Let's try together 💛"})
    return out

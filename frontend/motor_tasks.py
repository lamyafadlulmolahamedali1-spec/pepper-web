"""Body/motor exercise tasks — NO feet, NO jumping. © 2026 Lamya F. H. Ali"""
import random

BODY_EXERCISES = [
 ("Raise ONE hand!","🙋","raise_hand","Hand up! Great!"),
 ("Raise BOTH hands HIGH!","🙌","raise_both","Both hands! Amazing!"),
 ("Stretch your arms OUT wide!","🤸","arms_out","Arms wide! Perfect!"),
 ("Put your HANDS on your HIPS!","🧍","hands_hips","Hands on hips! Yes!"),
 ("CLAP your hands!","👏","clap","Clap clap! Wonderful!"),
 ("WAVE hello!","👋","wave","Lovely wave!"),
 ("Show THUMBS UP!","👍","thumbs_up","Thumbs up! Brilliant!"),
 ("Show a PEACE sign!","✌️","peace","Peace! Great!"),
 ("POINT at the screen!","☝️","point","Nice pointing!"),
 ("Show an OPEN hand!","🖐️","open_palm","Open hand! Yes!"),
 ("Make a FIST!","✊","fist","Strong fist!"),
 ("TOUCH your NOSE!","👃","touch_nose","Found your nose!"),
 ("TOUCH the TOP of your HEAD!","🙆","touch_head","Head! Great!"),
 ("TOUCH your EARS!","👂","touch_ears","Ears! Yes!"),
 ("TOUCH your MOUTH!","👄","touch_mouth","Mouth! Perfect!"),
 ("TOUCH your SHOULDERS!","💪","touch_shoulders","Shoulders! Amazing!"),
 ("TOUCH your TUMMY!","🤰","touch_tummy","Tummy! Yes!"),
 ("TOUCH your CHEEKS!","😊","touch_cheeks","Cheeks! Great!"),
 ("STAND up TALL!","🧍","stand_tall","Standing tall!"),
 ("Show a BIG SMILE!","😄","smile","Beautiful smile!"),
]

def motor_task():
    e=random.choice(BODY_EXERCISES)
    return {"type":"motor","name":e[0],"em":e[1],"instruction":e[0],"verify":e[2],
        "domain":"Motor","protocol":random.choice(["ABA-DTT","ESDM","PRT"]),
        "tokens":10,"success":e[3],"fail":f"Try again! {e[1]}"}

def finger_task():
    n=random.randint(1,5)
    return {"type":"number","name":f"Show {n}","em":"🖐️",
        "instruction":f"Show me {n} finger{'s' if n>1 else ''}!","verify":"fingers_count",
        "target":n,"domain":"Math","protocol":"ABA-DTT","tokens":10,
        "success":f"Yes! {n} fingers!","fail":f"Show {n} fingers!"}

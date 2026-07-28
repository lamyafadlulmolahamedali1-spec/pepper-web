"""Clean task generator — ONLY camera-detectable tasks. © 2026 Lamya F. H. Ali"""
import random
FINGER_TASKS=[
 {"name":"Show 1 finger","em":"☝️","instruction":"Show me ONE finger!","verify_kind":"fingers","target":1,"success":"One! Great counting!"},
 {"name":"Show 2 fingers","em":"✌️","instruction":"Show me TWO fingers!","verify_kind":"fingers","target":2,"success":"Two! Wonderful!"},
 {"name":"Show 3 fingers","em":"🤟","instruction":"Show me THREE fingers!","verify_kind":"fingers","target":3,"success":"Three! Amazing!"},
 {"name":"Show 4 fingers","em":"🖖","instruction":"Show me FOUR fingers!","verify_kind":"fingers","target":4,"success":"Four! Excellent!"},
 {"name":"Show 5 fingers","em":"🖐️","instruction":"Show me FIVE fingers! Open hand!","verify_kind":"fingers","target":5,"success":"Five! Perfect high five!"},
]
GESTURE_TASKS=[
 {"name":"Wave hello","em":"👋","instruction":"Wave your hand and say HELLO!","verify_kind":"gesture","target":"wave","success":"Hello! Lovely wave!"},
 {"name":"Both hands up","em":"🙌","instruction":"Put BOTH hands UP high!","verify_kind":"gesture","target":"hands_up","success":"Hands up! Fantastic!"},
 {"name":"Clap your hands","em":"👏","instruction":"CLAP your hands together!","verify_kind":"gesture","target":"clap","success":"Clap! Well done!"},
]
TOUCH_TASKS=[
 {"name":"Touch your head","em":"🙆","instruction":"Touch the TOP of your HEAD!","verify_kind":"touch","touch_target":"head","success":"Head! Great!"},
 {"name":"Touch your nose","em":"👃","instruction":"Touch your NOSE!","verify_kind":"touch","touch_target":"nose","success":"Nose! Found it!"},
 {"name":"Touch your mouth","em":"👄","instruction":"Touch your MOUTH!","verify_kind":"touch","touch_target":"mouth","success":"Mouth! Perfect!"},
 {"name":"Touch your ears","em":"👂","instruction":"Touch your EARS!","verify_kind":"touch","touch_target":"ears","success":"Ears! Yes!"},
 {"name":"Touch your shoulders","em":"💪","instruction":"Touch your SHOULDERS!","verify_kind":"touch","touch_target":"shoulders","success":"Shoulders! Amazing!"},
 {"name":"Touch your tummy","em":"🤍","instruction":"Touch your TUMMY!","verify_kind":"touch","touch_target":"tummy","success":"Tummy! Yes!"},
]
SMILE_TASKS=[
 {"name":"Big smile","em":"😄","instruction":"Show me your BIGGEST SMILE!","verify_kind":"smile","target":"happy","success":"What a beautiful smile!"},
]
METHODS=["ABA-DTT","ESDM","TEACCH","PRT"]
def _tag(task,method,tokens=10):
    t=dict(task); t.setdefault("type","motor"); t["protocol"]=method; t["tokens"]=tokens
    t.setdefault("fail","Let's try together!")
    t["domain"]=("Motor-Imitation" if t["verify_kind"] in ("gesture","touch")
        else "Cognitive-Counting" if t["verify_kind"]=="fingers" else "Social-Emotional")
    return t
def generate_tasks(count=20, structured=True):
    pool=[]; blocks=[(FINGER_TASKS,"ABA-DTT"),(GESTURE_TASKS,"ESDM"),(TOUCH_TASKS,"TEACCH"),(SMILE_TASKS,"PRT")]
    if structured:
        i=0
        while len(pool)<count:
            group,method=blocks[i%len(blocks)]; task=group[(i//len(blocks))%len(group)]
            pool.append(_tag(task,method)); i+=1
    else:
        allt=[]
        for group,method in blocks:
            for t in group: allt.append(_tag(t,method))
        random.shuffle(allt)
        while len(pool)<count: pool.extend(allt)
        pool=pool[:count]
    return pool
def all_task_types():
    out=[]
    for group,method in [(FINGER_TASKS,"ABA-DTT"),(GESTURE_TASKS,"ESDM"),(TOUCH_TASKS,"TEACCH"),(SMILE_TASKS,"PRT")]:
        for t in group: out.append(_tag(t,method))
    return out


# ---- Infinite ordered loop (ABA -> ESDM -> TEACCH -> PRT -> repeat) ----
_LOOP_BLOCKS=[("ABA-DTT",FINGER_TASKS),("ESDM",GESTURE_TASKS),("TEACCH",TOUCH_TASKS),("PRT",SMILE_TASKS)]
_loop_i=0
_loop_counters={m:0 for m,_ in _LOOP_BLOCKS}
def next_in_loop():
    global _loop_i
    method,group=_LOOP_BLOCKS[_loop_i % len(_LOOP_BLOCKS)]
    idx=_loop_counters[method] % len(group)
    t=_tag(group[idx], method)
    t["n"]=_loop_i+1
    _loop_counters[method]+=1
    _loop_i+=1
    return t
def reset_loop():
    global _loop_i, _loop_counters
    _loop_i=0
    _loop_counters={m:0 for m,_ in _LOOP_BLOCKS}
def total_capacity():
    return 100000


# ---- VISUAL CHOICE TASKS (tap the correct answer on screen — touch-screen friendly) ----
# These need NO camera; the child taps the right option. Great for colors/fruits/shapes.
_COLORS=[("RED","🔴"),("BLUE","🔵"),("GREEN","🟢"),("YELLOW","🟡"),("ORANGE","🟠"),("PURPLE","🟣")]
_FRUITS=[("apple","🍎"),("banana","🍌"),("orange","🍊"),("grapes","🍇"),("strawberry","🍓"),("watermelon","🍉")]
_VEGGIES=[("cucumber","🥒"),("carrot","🥕"),("tomato","🍅"),("corn","🌽"),("pepper","🫑"),("broccoli","🥦")]
_SHAPES=[("circle","⭕"),("square","🟥"),("triangle","🔺"),("star","⭐"),("heart","❤️"),("diamond","🔷")]
_ANIMALS=[("cat","🐱"),("dog","🐶"),("lion","🦁"),("fish","🐟"),("bird","🐦"),("rabbit","🐰")]

def _choice(group, method, prompt_word, domain):
    import random
    correct=random.choice(group)
    others=random.sample([g for g in group if g!=correct], 3)
    options=others+[correct]; random.shuffle(options)
    return {"type":"choice","verify_kind":"choice",
            "name":f"{prompt_word} {correct[0]}",
            "instruction":f"{prompt_word} the {correct[0]}!",
            "em":correct[1],"answer":correct[0],
            "options":[{"label":o[0],"em":o[1]} for o in options],
            "protocol":method,"domain":domain,"tokens":10,
            "success":f"Yes! That is {correct[0]}!","fail":"Try again!"}

def color_task(): return _choice(_COLORS,"TEACCH","Point to",  "Cognitive-Colors")
def fruit_task(): return _choice(_FRUITS,"TEACCH","Show me",   "Cognitive-Food")
def veggie_task():return _choice(_VEGGIES,"TEACCH","Show me",   "Cognitive-Food")
def shape_task(): return _choice(_SHAPES,"ABA-DTT","Find",      "Cognitive-Shapes")
def animal_task():return _choice(_ANIMALS,"ESDM","Show me",     "Cognitive-Animals")

# ---- FULL ORDERED CYCLE: one task from EVERY type, one after another ----
import random as _r
_CYCLE_BUILDERS=[
    lambda: _tag(_r.choice(SMILE_TASKS),"PRT"),        # 1 smile
    lambda: _tag(_r.choice(FINGER_TASKS),"ABA-DTT"),   # 2 fingers
    color_task,                                        # 3 color (choice)
    lambda: _tag(_r.choice(GESTURE_TASKS),"ESDM"),     # 4 gesture
    lambda: _tag(_r.choice(TOUCH_TASKS),"TEACCH"),     # 5 touch
    fruit_task,                                        # 6 fruit (choice)
    shape_task,                                        # 7 shape (choice)
    veggie_task,                                       # 8 veggie (choice)
    animal_task,                                       # 9 animal (choice)
]
_cycle_i=0
def next_ordered():
    """One task from EVERY type, in order, then repeat the cycle."""
    global _cycle_i
    builder=_CYCLE_BUILDERS[_cycle_i % len(_CYCLE_BUILDERS)]
    _cycle_i+=1
    t=builder(); t["n"]=_cycle_i
    return t
def reset_ordered():
    global _cycle_i; _cycle_i=0

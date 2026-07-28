"""Task generator — EXACT port of HTML TASK_GEN + genTask + mkGrid, plus DRAWING.
© 2026 Lamya Fadlulmola Hamed Ali"""
import random, time
def rnd(a): return random.choice(a)
def shuffle(a,n): b=a[:]; random.shuffle(b); return b[:n]

COLORS=[{"id":"red","color":"#ef4444","em":"🔴","label":"RED"},{"id":"blue","color":"#3b82f6","em":"🔵","label":"BLUE"},
{"id":"green","color":"#22c55e","em":"🟢","label":"GREEN"},{"id":"yellow","color":"#eab308","em":"🟡","label":"YELLOW"},
{"id":"purple","color":"#a855f7","em":"🟣","label":"PURPLE"},{"id":"orange","color":"#f97316","em":"🟠","label":"ORANGE"},
{"id":"pink","color":"#ec4899","em":"🩷","label":"PINK"},{"id":"brown","color":"#92400e","em":"🟫","label":"BROWN"}]
ANIMALS=[{"id":"dog","em":"🐶","label":"Dog"},{"id":"cat","em":"🐱","label":"Cat"},{"id":"lion","em":"🦁","label":"Lion"},
{"id":"elephant","em":"🐘","label":"Elephant"},{"id":"rabbit","em":"🐰","label":"Rabbit"},{"id":"bear","em":"🐻","label":"Bear"},
{"id":"monkey","em":"🐵","label":"Monkey"},{"id":"tiger","em":"🐯","label":"Tiger"},{"id":"duck","em":"🦆","label":"Duck"},
{"id":"fish","em":"🐟","label":"Fish"},{"id":"butterfly","em":"🦋","label":"Butterfly"}]
FRUITS=[{"id":"apple","em":"🍎","label":"Apple"},{"id":"banana","em":"🍌","label":"Banana"},{"id":"orange","em":"🍊","label":"Orange"},
{"id":"grapes","em":"🍇","label":"Grapes"},{"id":"strawberry","em":"🍓","label":"Strawberry"},{"id":"mango","em":"🥭","label":"Mango"},
{"id":"watermelon","em":"🍉","label":"Watermelon"},{"id":"cherry","em":"🍒","label":"Cherry"}]
SHAPES=[{"id":"circle","em":"⭕","label":"Circle"},{"id":"square","em":"⬛","label":"Square"},{"id":"triangle","em":"🔺","label":"Triangle"},
{"id":"star","em":"⭐","label":"Star"},{"id":"heart","em":"❤️","label":"Heart"},{"id":"diamond","em":"💎","label":"Diamond"}]
EMO_ITEMS=[{"id":"happy","em":"😊","label":"Happy"},{"id":"sad","em":"😢","label":"Sad"},{"id":"angry","em":"😠","label":"Angry"},
{"id":"scared","em":"😨","label":"Scared"},{"id":"surprised","em":"😲","label":"Surprised"},{"id":"tired","em":"😴","label":"Tired"},
{"id":"excited","em":"🤩","label":"Excited"},{"id":"bored","em":"😑","label":"Bored"}]
BODY=[{"id":"hand","em":"✋","label":"Hand"},{"id":"foot","em":"🦶","label":"Foot"},{"id":"eye","em":"👁️","label":"Eye"},
{"id":"nose","em":"👃","label":"Nose"},{"id":"ear","em":"👂","label":"Ear"},{"id":"mouth","em":"👄","label":"Mouth"},{"id":"arm","em":"💪","label":"Arm"}]
VEGS=[{"id":"carrot","em":"🥕","label":"Carrot"},{"id":"corn","em":"🌽","label":"Corn"},{"id":"tomato","em":"🍅","label":"Tomato"},{"id":"cucumber","em":"🥒","label":"Cucumber"}]
VEHICLES=[{"id":"car","em":"🚗","label":"Car"},{"id":"bus","em":"🚌","label":"Bus"},{"id":"plane","em":"✈️","label":"Plane"},{"id":"train","em":"🚂","label":"Train"}]
NUMBERS=[1,2,3,4,5,6,7,8,9,10]
LETTERS=list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
WORDS=["mama","papa","ball","water","more","yes","no","hello","cat","dog","up","go"]
MOTORS=[
 {"id":"wave","em":"👋","ins":"WAVE hello!","v":"wave","t":2,"ok":"Wonderful wave!"},
 {"id":"hands_up","em":"🙌","ins":"Put BOTH hands UP!","v":"hands_up","t":2,"ok":"Hands up! Great!"},
 {"id":"clap","em":"👏","ins":"CLAP your hands!","v":"clap","t":2,"ok":"Great clapping!"},
 {"id":"touch_nose","em":"👆","ins":"TOUCH your NOSE!","v":"touch_head","t":2,"ok":"Brilliant!"},
 {"id":"touch_head","em":"🤚","ins":"TOUCH the TOP of your HEAD!","v":"touch_head","t":2,"ok":"Well done!"},
 {"id":"raise_hand","em":"✋","ins":"RAISE one hand UP!","v":"hand_raised","t":2,"ok":"Nice raise!"},
]
DRAW_LETTERS=list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
DRAW_SHAPES=["circle","square","triangle","star"]

def mkGrid(pool,domain,protocol,tokens,mode):
    tgt=rnd(pool); dis=shuffle([x for x in pool if x["id"]!=tgt["id"]],3)
    opts=[tgt]+dis; random.shuffle(opts)
    cor=next(i for i,o in enumerate(opts) if o["id"]==tgt["id"])
    return {"type":"color_grid" if mode=="color" else "obj_grid",
            "id":f"{tgt['id']}_{int(time.time()*1000)%9999}","name":tgt["label"],
            "instruction":f"Find the {tgt['em']} {tgt['label']}!","options":opts,"correct":cor,
            "domain":domain,"protocol":protocol,"tokens":tokens,"level":2,
            "success":f"Correct! {tgt['label']}!","fail":f"Find {tgt['label']}!"}

def _motor():
    m=rnd(MOTORS)
    return {"type":"motor","id":f"m_{m['id']}_{int(time.time()*1000)%9999}","name":f"Motor: {m['em']}",
            "instruction":m["ins"],"em":m["em"],"verify":m["v"],"verify_kind":"motor","domain":"Motor",
            "protocol":rnd(["ABA-DTT","TEACCH"]),"tokens":m["t"],"level":1,"success":m["ok"],"fail":"Try again!"}

def _number():
    n=rnd(NUMBERS)
    return {"type":"number","id":f"n_{n}_{int(time.time()*1000)%9999}","name":f"Show {n} fingers",
            "instruction":f"Show me {n} finger{'s' if n>1 else ''}! 🖐️","target":n,"verify_kind":"fingers",
            "domain":"Math","protocol":"ABA-DTT","tokens":5,"level":2,"success":f"YES! {n} fingers!","fail":f"Show {n} fingers!"}

def _letter():
    L=rnd(LETTERS); dis=shuffle([x for x in LETTERS if x!=L],11); opts=[L]+dis; random.shuffle(opts)
    return {"type":"letter","id":f"l_{L}_{int(time.time()*1000)%9999}","name":f"Letter {L}",
            "instruction":f"Find the letter {L}!","options":opts,"correct":opts.index(L),
            "domain":"Cognitive","protocol":"TEACCH","tokens":3,"level":2,"success":f"YES! Letter {L}!","fail":f"Find letter {L}!"}

def _word():
    w=rnd(WORDS)
    return {"type":"word","id":f"w_{w}_{int(time.time()*1000)%9999}","name":f"Say: {w}",
            "instruction":f"Say the word: {w.upper()}! 🗣️","word":w,"domain":"Verbal","protocol":"ESDM",
            "tokens":4,"level":3,"success":f"I heard {w.upper()}!","fail":f"Say: {w}!"}

def _drawing():
    kind=rnd(["letter","shape"])
    if kind=="letter":
        target=rnd(DRAW_LETTERS); ins=f"Draw the letter {target}! Trace the gray line."
    else:
        target=rnd(DRAW_SHAPES); ins=f"Draw a {target}! Trace the gray line."
    return {"type":"drawing","id":f"d_{target}_{int(time.time()*1000)%9999}",
            "name":f"Draw {target}","instruction":ins,"draw_kind":kind,"draw_target":target,
            "verify_kind":"drawing","domain":"Motor-Fine","protocol":rnd(["TEACCH","ESDM"]),
            "tokens":6,"level":2,"success":f"Beautiful {target}!","fail":"Keep tracing!"}

TASK_GEN=[
    _motor,
    lambda: mkGrid(COLORS,"Cognitive","TEACCH",3,"color"),
    lambda: mkGrid(ANIMALS,"Cognitive","TEACCH",4,"obj"),
    lambda: mkGrid(FRUITS,"Cognitive","ABA-DTT",3,"obj"),
    lambda: mkGrid(VEGS,"Cognitive","ESDM",3,"obj"),
    lambda: mkGrid(SHAPES,"Math","ABA-DTT",3,"obj"),
    lambda: mkGrid(EMO_ITEMS,"Social","ESDM",5,"obj"),
    lambda: mkGrid(BODY,"Cognitive","ESDM",4,"obj"),
    lambda: mkGrid(VEHICLES,"Cognitive","TEACCH",3,"obj"),
    _number, _letter, _word, _drawing,
]

_tHist=[]
def genTask(conversation_level=3):
    cl=conversation_level
    if cl==1: al=[0,1,2,9]
    elif cl==2: al=[0,1,2,3,4,5,7,8,9,10]
    else: al=list(range(len(TASK_GEN)))
    shuffled=al[:]; random.shuffle(shuffled)
    idx=shuffled[0]; histLen=min(len(al)-1,8)
    for cand in shuffled:
        if cand not in _tHist[-histLen:]: idx=cand; break
    _tHist.append(idx)
    if len(_tHist)>30: _tHist.pop(0)
    return TASK_GEN[idx]()

def reset_tasks():
    global _tHist; _tHist=[]


# ---- FULL CYCLE: every task type appears exactly once, then a new cycle begins ----
_cycle_order=[]
_cycle_pos=0
def next_full_cycle():
    """Each of the 13 task types appears exactly once per cycle, shuffled order,
    then the cycle restarts with a fresh shuffle (never same order twice)."""
    global _cycle_order, _cycle_pos
    if not _cycle_order or _cycle_pos >= len(_cycle_order):
        _cycle_order = list(range(len(TASK_GEN)))
        random.shuffle(_cycle_order)
        _cycle_pos = 0
    idx = _cycle_order[_cycle_pos]
    _cycle_pos += 1
    return TASK_GEN[idx]()

def reset_cycle():
    global _cycle_order, _cycle_pos
    _cycle_order = []; _cycle_pos = 0

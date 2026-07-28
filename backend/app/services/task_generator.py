"""Task generator — NO feet/jumping, includes drawing. © 2026 Lamya F. H. Ali"""
import random

COLORS=[("red","🔴","#ef4444"),("blue","🔵","#3b82f6"),("green","🟢","#22c55e"),
("yellow","🟡","#eab308"),("orange","🟠","#f97316"),("purple","🟣","#a855f7"),
("pink","🩷","#ec4899"),("black","⬛","#1e293b"),("white","⬜","#e5e7eb")]
ANIMALS=[("dog","🐶"),("cat","🐱"),("lion","🦁"),("tiger","🐯"),("rabbit","🐰"),
("bear","🐻"),("elephant","🐘"),("monkey","🐒"),("butterfly","🦋"),("fish","🐟"),
("bird","🐦"),("frog","🐸"),("horse","🐴"),("owl","🦉"),("penguin","🐧")]
FRUITS=[("apple","🍎"),("banana","🍌"),("orange","🍊"),("grapes","🍇"),
("strawberry","🍓"),("watermelon","🍉"),("mango","🥭"),("lemon","🍋")]
SHAPES=[("circle","⭕"),("square","⬛"),("triangle","🔺"),("star","⭐"),("heart","❤️")]
LETTERS=list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
WORDS=["cat","dog","sun","ball","fish","tree","star","book","milk","mom","dad","yes"]
MOTORS=[("clap","👏","CLAP your hands 3 times!","clap","Amazing clap!"),
("wave","👋","WAVE hello!","wave","Great wave!"),
("thumbs","👍","Show THUMBS UP!","thumbs_up","Thumbs up!"),
("nose","👃","TOUCH your NOSE with one finger!","head_touch","Found your nose!"),
("head","🙆","Touch the TOP of your HEAD!","head_touch","Head touch!"),
("arms","🙌","Raise BOTH ARMS up HIGH!","hand_raised","Arms up!"),
("point","☝️","POINT at the camera!","point","Great pointing!"),
("peace","✌️","Show a PEACE sign!","peace","Peace!"),
("open","🖐️","Show an OPEN hand!","open_palm","Open hand!")]
SOCIAL=[("please","🙏","Say PLEASE!"),("thank you","💙","Say THANK YOU!"),
("hello","👋","Say HELLO and wave!"),("help","🆘","Ask for HELP!"),
("my turn","🔄","Say MY TURN politely!")]
DAILY=[("wash hands","🧼","Show how you WASH hands!","washing hands kids"),
("brush teeth","🦷","Show BRUSH teeth!","brushing teeth song kids"),
("drink","🥤","Pretend to DRINK!","drinking cup toddler"),
("clean up","🧹","Show CLEAN UP toys!","clean up song kids")]

def _grid(pool,label,em,n,domain,protocol):
    tgt=(label,em); others=random.sample([x for x in pool if x[0]!=label],min(n-1,len(pool)-1))
    opts=others+[tgt]; random.shuffle(opts)
    return {"type":"grid","name":f"Find {label}","em":em,
        "instruction":f"Find the {em} {label}!",
        "options":[{"label":o[0],"em":o[1],
            "color":next((c[2] for c in COLORS if c[0]==o[0]),"#ede9fe")} for o in opts],
        "correct":opts.index(tgt),"domain":domain,"protocol":protocol,"tokens":10,
        "success":f"PERFECT! {label}! You are a superstar!","fail":f"Find the {label}!"}

class TaskGenerator:
    DOMAINS=["motor","cognitive","verbal","math","social","daily","drawing"]
    @staticmethod
    def generate(domain=None,level=1,count=20):
        return [TaskGenerator._b(domain or random.choice(TaskGenerator.DOMAINS),level)
                for _ in range(count)]
    @staticmethod
    def _b(d,lv=1):
        return {"motor":TaskGenerator._m,"cognitive":TaskGenerator._c,
        "verbal":TaskGenerator._v,"math":TaskGenerator._n,"social":TaskGenerator._s,
        "daily":TaskGenerator._d,"drawing":TaskGenerator._dr}.get(d,TaskGenerator._m)(lv)
    @staticmethod
    def _m(lv=1):
        m=random.choice(MOTORS)
        return {"type":"motor","name":m[0].title(),"em":m[1],"instruction":m[2],
        "verify":m[3],"domain":"Motor","protocol":random.choice(["ABA-DTT","ESDM","PRT"]),
        "tokens":10,"success":m[4],"fail":f"Try again! {m[1]}"}
    @staticmethod
    def _c(lv=1):
        pick=random.choice(["color","animal","fruit","shape"])
        pool={"color":COLORS,"animal":ANIMALS,"fruit":FRUITS,"shape":SHAPES}[pick]
        t=random.choice(pool); return _grid(pool,t[0],t[1],min(3+lv,len(pool)),"Cognitive","TEACCH")
    @staticmethod
    def _v(lv=1):
        w=random.choice(WORDS)
        return {"type":"word","name":f"Say {w}","em":"🗣️","instruction":f"Say the word: {w.upper()}!",
        "word":w,"domain":"Verbal","protocol":"Verbal-Behavior","tokens":10,
        "success":f"I heard {w.upper()}!","fail":f"Say: {w}!"}
    @staticmethod
    def _n(lv=1):
        n=random.randint(1,5)
        return {"type":"number","name":f"Show {n}","em":"🖐️","instruction":f"Show me {n} finger{'s' if n>1 else ''}!",
        "target":n,"domain":"Math","protocol":"ABA-DTT","tokens":10,
        "success":f"Yes! {n}!","fail":f"Show {n} fingers!"}
    @staticmethod
    def _s(lv=1):
        t=random.choice(SOCIAL)
        return {"type":"social","name":t[0].title(),"em":t[1],"instruction":t[2],
        "phrase":t[0],"domain":"Social","protocol":"ESDM","tokens":10,
        "success":f"Excellent! {t[1]}","fail":f"Try: {t[0]}!"}
    @staticmethod
    def _d(lv=1):
        t=random.choice(DAILY)
        return {"type":"daily","name":t[0].title(),"em":t[1],"instruction":t[2],
        "youtube_query":t[3],"domain":"Daily Living","protocol":"TEACCH","tokens":10,
        "success":"Amazing life skill!","fail":"Try again!"}
    @staticmethod
    def _dr(lv=1):
        k=random.choice(["letter","shape"])
        if k=="letter":
            ch=random.choice(LETTERS)
            return {"type":"drawing","name":f"Draw {ch}","em":"✏️","instruction":f"Trace the letter {ch}!",
            "draw_target":ch,"draw_kind":"letter","domain":"Fine Motor","protocol":"TEACCH","tokens":10,
            "success":f"Beautiful {ch}!","fail":"Trace over the light lines!"}
        sh=random.choice(SHAPES)
        return {"type":"drawing","name":f"Draw {sh[0]}","em":"✏️","instruction":f"Trace the {sh[0]}! {sh[1]}",
        "draw_target":sh[0],"draw_kind":"shape","domain":"Fine Motor","protocol":"TEACCH","tokens":10,
        "success":f"Great {sh[0]}!","fail":"Trace the lines!"}

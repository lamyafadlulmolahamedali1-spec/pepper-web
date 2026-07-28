"""Pepper robot simulation — runs alongside the clinical app.
© 2026 Lamya Fadlulmola Hamed Ali"""
import time, threading, math, random, os as _os
from flask import Flask, request, jsonify
from flask_cors import CORS

_pepper=None
_sm=None
_balloons=[]
_speaking=False
_action={"name":None,"until":0.0}
_session_active={"on":False}
_sm_state={"yaw":0.0,"pitch":0.0,"rs":1.0,"ls":1.0,"re":0.4,"le":-0.4}
_sm=_sm  # keep SimulationManager slot
_gaze={"yaw":0.0,"pitch":0.0,"next_t":0.0,"hold":1.5}

def _lerp(a,b,f): return a+(b-a)*f

def _clock():
    return time.time()

def set_speaking(flag):
    global _speaking
    _speaking=bool(flag)

# ---------------- ROOM ----------------
def _build_room(p):
    """Modern luxury therapy room."""
    def box(pos,size,col,mass=0):
        vs=p.createVisualShape(p.GEOM_BOX,halfExtents=size,rgbaColor=col)
        cs=p.createCollisionShape(p.GEOM_BOX,halfExtents=size)
        return p.createMultiBody(mass,cs,vs,pos)
    def cyl(pos,r,h,col):
        vs=p.createVisualShape(p.GEOM_CYLINDER,radius=r,length=h,rgbaColor=col)
        return p.createMultiBody(0,-1,vs,pos)

    CREAM=[0.96,0.94,0.90,1]; CHARCOAL=[0.22,0.24,0.28,1]
    GOLD=[0.83,0.69,0.35,1]; WOOD=[0.42,0.28,0.18,1]; RUG=[0.85,0.80,0.88,1]

    box([0,3.2,1.4],[3.2,0.12,1.4],CREAM)
    box([-3.2,0,1.4],[0.12,3.2,1.4],CREAM)
    box([3.2,0,1.4],[0.12,3.2,1.4],CREAM)
    box([0,-3.2,1.4],[3.2,0.12,1.4],CREAM)
    box([0,3.08,0.12],[3.2,0.03,0.12],GOLD)
    box([0,0.6,0.008],[2.2,1.6,0.008],RUG)

    box([0,3.10,1.55],[1.35,0.04,0.82],[0.04,0.05,0.09,1])
    box([0,3.05,1.55],[1.29,0.02,0.76],[0.05,0.07,0.13,1])
    box([0,3.03,2.20],[1.20,0.01,0.09],[0.48,0.23,0.85,1])
    globals()["_ui"]={}
    box([-0.80,3.02,1.60],[0.42,0.01,0.42],[0.10,0.14,0.22,1])
    vs=p.createVisualShape(p.GEOM_SPHERE,radius=0.10,rgbaColor=[0.85,0.70,0.60,1])
    _ui=globals()["_ui"]
    _ui["face"]=p.createMultiBody(0,-1,vs,[-0.80,3.00,1.68])
    for i,(cx,cz) in enumerate([(-0.13,1.80),(0.30,1.80),(-0.13,1.40),(0.30,1.40)]):
        c=[[0.95,0.35,0.35,1],[0.35,0.75,0.95,1],[0.45,0.90,0.55,1],[0.98,0.85,0.35,1]][i]
        _ui[f"tile{i}"]=box([cx,3.02,cz],[0.19,0.01,0.17],c)
    for k,(cz,c) in enumerate([(1.90,[0.30,0.85,0.55,1]),(1.62,[0.98,0.80,0.30,1]),
                                (1.34,[0.55,0.60,0.95,1])]):
        box([0.92,3.02,cz],[0.28,0.01,0.10],c)
    box([0,3.02,1.00],[1.15,0.01,0.055],[0.15,0.18,0.26,1])
    _ui["prog"]=box([-0.60,3.01,1.00],[0.45,0.01,0.045],[0.30,0.90,0.55,1])

    box([0,3.09,2.55],[1.55,0.02,0.16],[0.48,0.23,0.85,1])
    box([0,3.06,2.55],[1.50,0.01,0.13],[1,1,1,1])
    try:
        p.addUserDebugText("PEPPER CLINICAL INFINITY  V6",[0,3.05,2.57],
                           textColorRGB=[0.30,0.10,0.60],textSize=1.6)
        p.addUserDebugText("Every child learns in their own beautiful way",
                           [0,3.05,2.40],textColorRGB=[0.20,0.35,0.55],textSize=1.0)
        p.addUserDebugText("Autism Therapy Room  -  You are safe here",
                           [0,3.05,0.55],textColorRGB=[0.30,0.45,0.35],textSize=1.0)
    except Exception: pass

    for dx,dz,c,r in [(-1.15,2.05,[0.98,0.80,0.25,1],0.10),(1.15,2.05,[0.35,0.75,0.95,1],0.09),
                      (-0.75,0.95,[0.45,0.90,0.55,1],0.07),(0.75,0.95,[0.95,0.45,0.55,1],0.07)]:
        vs=p.createVisualShape(p.GEOM_SPHERE,radius=r,rgbaColor=c)
        p.createMultiBody(0,-1,vs,[dx,3.13,dz])
    for dx,dz in [(-1.55,1.35),(1.55,1.35)]:
        box([dx,3.13,dz],[0.05,0.01,0.05],[0.85,0.55,0.90,1])

    def sofa(sx,sy,col,rot=0):
        w=0.95 if rot==0 else 0.42
        d=0.42 if rot==0 else 0.95
        box([sx,sy,0.30],[w,d,0.14],col)
        if rot==0: box([sx,sy+0.36,0.55],[w,0.09,0.28],col)
        else:      box([sx+0.36,sy,0.55],[0.09,d,0.28],col)
        for lx,ly in [(-w*0.85,-d*0.75),(w*0.85,-d*0.75),(-w*0.85,d*0.75),(w*0.85,d*0.75)]:
            cyl([sx+lx,sy+ly,0.08],0.032,0.16,GOLD)
        for cx in ([-0.5,0,0.5] if rot==0 else [0]):
            if rot==0: box([sx+cx,sy+0.05,0.47],[0.22,0.30,0.05],[col[0]*1.3,col[1]*1.3,col[2]*1.3,1])

    CH=[0.22,0.24,0.28,1]; NAVY=[0.18,0.24,0.38,1]; TAUPE=[0.42,0.38,0.36,1]
    sofa(-1.6,2.5,CH)
    sofa( 1.6,2.5,NAVY)
    sofa(-2.6,0.6,TAUPE,rot=1)
    sofa( 2.6,0.6,CH,rot=1)
    sofa( 0.0,-1.4,NAVY)

    tx,ty=0,0.9
    box([tx,ty,0.40],[0.60,0.35,0.025],WOOD)
    for lx,ly in [(-0.52,-0.27),(0.52,-0.27),(-0.52,0.27),(0.52,0.27)]:
        cyl([tx+lx,ty+ly,0.20],0.028,0.40,GOLD)
    cyl([tx-0.25,ty,0.46],0.06,0.10,[0.75,0.85,0.95,0.85])
    box([tx+0.20,ty,0.435],[0.13,0.09,0.012],[0.55,0.20,0.22,1])

    _here=_os.path.dirname(_os.path.abspath(__file__))
    def wall_img(fn,pos,hw,hh,axis="y"):
        path=_os.path.join(_here,fn)
        if axis=="y":
            fr=[hw+0.05,0.02,hh+0.05]; ip=[pos[0],pos[1]+0.03,pos[2]]
            vh=[hw,0.012,hh]
        else:
            fr=[0.02,hw+0.05,hh+0.05]; ip=[pos[0]+0.03,pos[1],pos[2]]
            vh=[0.012,hw,hh]
        box([pos[0],pos[1]+ (0.03 if axis=="y" else 0),pos[2]] if axis=="y" else
            [pos[0]+0.03,pos[1],pos[2]], fr, GOLD)
        if _os.path.exists(path):
            try:
                tex=p.loadTexture(path)
                vs=p.createVisualShape(p.GEOM_BOX,halfExtents=vh,rgbaColor=[1,1,1,1])
                bid=p.createMultiBody(0,-1,vs,ip)
                p.changeVisualShape(bid,-1,textureUniqueId=tex)
                print("[room] IMAGE OK:",fn); return
            except Exception as e: print("[room] tex fail",fn,e)
        else: print("[room] NOT FOUND:",path)
        box(ip,vh,[1,1,1,1])

    wall_img("autism.jpeg",  [-2.30,3.05,1.60], 0.62,0.62)
    wall_img("images.jpeg",  [ 2.30,3.05,1.60], 0.62,0.62)
    wall_img("images1.jpeg", [-3.10,1.20,1.55], 0.70,0.45, axis="x")

    box([0,3.06,2.45],[2.20,0.02,0.26],[0.48,0.23,0.85,1])
    box([0,3.03,2.45],[2.14,0.01,0.21],[1,1,1,1])
    try:
        p.addUserDebugText("PEPPER  CLINICAL  INFINITY  V6",[0,2.98,2.45],
                           textColorRGB=[0.35,0.08,0.68],textSize=2.6)
        p.addUserDebugText("AI-Assisted Autism Therapy Room",[0,2.98,2.20],
                           textColorRGB=[0.22,0.42,0.62],textSize=1.3)
        p.addUserDebugText("You are amazing exactly as you are",[-2.30,2.98,0.85],
                           textColorRGB=[0.55,0.30,0.15],textSize=1.1)
    except Exception: pass

# ---------------- FLASK BRIDGE (single instance) ----------------
_bridge_app=Flask("pepper_bridge")
CORS(_bridge_app)
_bridge_started={"on":False}

@_bridge_app.route("/pepper/status", methods=["GET"])
def _b_status():
    return jsonify({"ok":True,"speaking":_speaking,"action":_action["name"],
                     "session_active":_session_active["on"]})

@_bridge_app.route("/pepper/session", methods=["POST"])
def _b_session():
    d=request.get_json(force=True,silent=True) or {}
    _session_active["on"]=bool(d.get("active",False))
    return jsonify({"ok":True,"active":_session_active["on"]})

@_bridge_app.route("/pepper/speak", methods=["POST"])
def _b_speak():
    d=request.get_json(force=True,silent=True) or {}
    globals()["_speaking"]=bool(d.get("on",False))
    return jsonify({"ok":True,"speaking":globals()["_speaking"]})

@_bridge_app.route("/pepper/wave", methods=["POST"])
def _b_wave():
    d=request.get_json(force=True,silent=True) or {}
    _action["name"]="wave"; _action["until"]=_clock()+float(d.get("duration",2.2))
    return jsonify({"ok":True})

@_bridge_app.route("/pepper/clap", methods=["POST"])
def _b_clap():
    d=request.get_json(force=True,silent=True) or {}
    _action["name"]="clap"; _action["until"]=_clock()+float(d.get("duration",2.0))
    return jsonify({"ok":True})

@_bridge_app.route("/pepper/look", methods=["POST"])
def _b_look():
    d=request.get_json(force=True,silent=True) or {}
    _gaze["yaw"]=max(-1.5,min(1.5,float(d.get("yaw",0.0))))
    _gaze["pitch"]=max(-0.45,min(0.35,float(d.get("pitch",0.0))))
    _gaze["hold"]=float(d.get("hold",2.5))
    _gaze["next_t"]=_clock()+_gaze["hold"]
    return jsonify({"ok":True})

def _start_bridge_server(port=5055):
    if _bridge_started["on"]: return
    _bridge_started["on"]=True
    def _run():
        _bridge_app.run(host="0.0.0.0",port=port,debug=False,use_reloader=False)
    threading.Thread(target=_run,daemon=True).start()
    print(f"[pepper_bridge] API listening on http://0.0.0.0:{port}")

# ---------------- IDLE ANIMATION (NO LOCOMOTION — EVER) ----------------
def _pick_gaze_target(t):
    _gaze["yaw"]=random.uniform(-1.1,1.1)
    _gaze["pitch"]=random.uniform(-0.35,0.25)
    _gaze["hold"]=random.uniform(1.2,3.2)
    _gaze["next_t"]=t+_gaze["hold"]

def _idle_update(t):
    """Pepper NEVER moves from its spawn point. Only head look-around + arm wave/clap/gesture."""
    if _pepper is None: return
    if not _session_active.get("on",False): return
    try:
        if _action["name"] and t < _action["until"]:
            ph2=t*7.0
            if _action["name"]=="wave":
                _sm_state["yaw"]=_lerp(_sm_state["yaw"],0.35,0.6)
                _sm_state["pitch"]=_lerp(_sm_state["pitch"],-0.05,0.6)
                _sm_state["rs"]=_lerp(_sm_state["rs"],-0.9+0.5*math.sin(ph2),0.75)
                _sm_state["ls"]=_lerp(_sm_state["ls"],1.0,0.6)
                _sm_state["re"]=_lerp(_sm_state["re"],1.3+0.5*math.sin(ph2*1.3),0.75)
                _sm_state["le"]=_lerp(_sm_state["le"],-0.4,0.6)
            elif _action["name"]=="clap":
                cl=0.15*abs(math.sin(ph2*1.6))
                _sm_state["yaw"]=_lerp(_sm_state["yaw"],0.0,0.6)
                _sm_state["pitch"]=_lerp(_sm_state["pitch"],0.05,0.6)
                _sm_state["rs"]=_lerp(_sm_state["rs"],0.55+cl,0.8)
                _sm_state["ls"]=_lerp(_sm_state["ls"],0.55+cl,0.8)
                _sm_state["re"]=_lerp(_sm_state["re"],1.55,0.8)
                _sm_state["le"]=_lerp(_sm_state["le"],-1.55,0.8)
            _pepper.setAngles(["HeadYaw","HeadPitch"],[_sm_state["yaw"],_sm_state["pitch"]],1.0)
            _pepper.setAngles(["RShoulderPitch","LShoulderPitch","RElbowRoll","LElbowRoll"],
                              [_sm_state["rs"],_sm_state["ls"],_sm_state["re"],_sm_state["le"]],0.95)
            return
        elif _action["name"] and t>=_action["until"]:
            _action["name"]=None

        if _speaking:
            tgt_yaw=0.30*math.sin(t*0.7); tgt_pitch=0.08*math.sin(t*0.5)
        else:
            if t>=_gaze["next_t"]: _pick_gaze_target(t)
            tgt_yaw=_gaze["yaw"]; tgt_pitch=_gaze["pitch"]

        amp=1.05 if _speaking else 0.55
        blend=0.75 if _speaking else 0.45
        yaw_blend=0.70 if _speaking else 0.12
        ph=t*(11.0 if _speaking else 5.5)

        _sm_state["yaw"]=_lerp(_sm_state["yaw"],tgt_yaw,yaw_blend)
        _sm_state["pitch"]=_lerp(_sm_state["pitch"],tgt_pitch,yaw_blend)
        idle_breathe=0.0 if _speaking else 0.06*math.sin(t*0.9)
        _sm_state["rs"]=_lerp(_sm_state["rs"],1.00-amp*abs(math.sin(ph))+idle_breathe,blend)
        _sm_state["ls"]=_lerp(_sm_state["ls"],1.00-amp*abs(math.cos(ph*0.9))+idle_breathe,blend)
        _sm_state["re"]=_lerp(_sm_state["re"],0.40+amp*0.75*math.sin(ph*1.4),blend)
        _sm_state["le"]=_lerp(_sm_state["le"],-0.40-amp*0.75*math.cos(ph*1.4),blend)

        _pepper.setAngles(["HeadYaw","HeadPitch"],[_sm_state["yaw"],_sm_state["pitch"]],1.0)
        _pepper.setAngles(["RShoulderPitch","LShoulderPitch","RElbowRoll","LElbowRoll"],
                          [_sm_state["rs"],_sm_state["ls"],_sm_state["re"],_sm_state["le"]],0.95)
    except Exception: pass

def hello_wave():
    if _pepper is None: return
    try:
        _pepper.setAngles(["RShoulderPitch","RElbowRoll"],[-0.9,1.3],0.3)
        time.sleep(0.4)
        _pepper.setAngles(["RShoulderPitch","RElbowRoll"],[-1.2,1.6],0.3)
        time.sleep(0.4)
        _pepper.setAngles(["RShoulderPitch","LShoulderPitch"],[1.4,1.4],0.2)
    except Exception: pass

# ---------------- MAIN LOOP (SINGLE DEFINITION, SINGLE LAUNCH) ----------------
_already_running={"on":False}

def run_pepper_sim():
    global _pepper,_sm
    if _already_running["on"]:
        print("[pepper] sim already running — refusing duplicate launch")
        return
    _already_running["on"]=True
    try:
        from qibullet import SimulationManager
        _sm=SimulationManager()
        client=_sm.launchSimulation(gui=True)
        _pepper=_sm.spawnPepper(client, spawn_ground_plane=True)
        try:
            import pybullet as _p
            _build_room(_p)
        except Exception as e:
            print("[pepper] room error:", e)
        try: _pepper.goToPosture("Stand", 0.6)
        except Exception: pass

        _start_bridge_server(5055)

        # floating name label fixed above Pepper's actual head — never overlaps face
        try:
            hx,hy,hz=0.0,0.0,1.20
            try:
                base_pos,_ori=_p.getBasePositionAndOrientation(_pepper.getRobotModel())
                hx,hy,hz=base_pos
            except Exception: pass
            _p.addUserDebugText("Pepper Clinical Infinity",[hx-0.30,hy-0.35,hz+0.62],
                                 textColorRGB=[0.48,0.23,0.85],textSize=1.6)
        except Exception as e:
            print("[pepper] head label error:", e)

        print("[pepper] simulation ready")
        hello_wave()

        t=0.0
        while True:
            _idle_update(t)
            time.sleep(1/30.0)
            t+=1/30.0
    except Exception as e:
        print("[pepper] fatal error:", e)
        _already_running["on"]=False

def launch_pepper_thread():
    th=threading.Thread(target=run_pepper_sim, daemon=True)
    th.start()
    return th

if __name__=="__main__":
    run_pepper_sim()

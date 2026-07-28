"""API client — talks to backend, falls back to local SQLite. © 2026 Lamya F. H. Ali"""
import os, json, sqlite3, secrets, hashlib
from datetime import datetime, timezone

try:
    import requests
    _HAS_REQ=True
except Exception:
    _HAS_REQ=False

SERVER_URL=os.environ.get("PEPPER_SERVER","http://127.0.0.1:8000")
LOCAL_DB=os.path.join(os.path.expanduser("~"),".pepper_v6_local.db")


class ApiClient:
    """Online (backend) when reachable; otherwise offline local DB."""
    def __init__(self):
        self.token=None; self.user=None; self.online=False  # forced  # forced
        self.online=False  # FORCED OFFLINE — local SQLite only
        print(f"[Pepper] online={self.online}  (False = offline local mode)")
        print(f"[Pepper] online={self.online}")
        if not self.online: self._init_local()

    # ---------- local fallback ----------
    def _init_local(self):
        self.db=sqlite3.connect(LOCAL_DB, check_same_thread=False)
        c=self.db.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY, name TEXT,
            email TEXT UNIQUE, pin_hash TEXT, plan TEXT, expiry TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS children(id TEXT PRIMARY KEY, parent TEXT,
            name TEXT, age INT, sessions INT DEFAULT 0, score INT DEFAULT 0,
            m REAL DEFAULT 50, c REAL DEFAULT 50, v REAL DEFAULT 50, ma REAL DEFAULT 50, s REAL DEFAULT 50)""")
        self.db.commit()

    def _h(self,p): return hashlib.sha256(p.encode()).hexdigest()

    # ---------- auth ----------
    def register(self, name, email, pin, child_name, child_age):
        if self.online:
            r=requests.post(SERVER_URL+"/api/auth/trial", json={"full_name":name,
                "email":email,"child_name":child_name,"child_age":child_age},timeout=8)
            return r.json()
        c=self.db.cursor()
        email=(email or "").strip().lower()
        uid=secrets.token_hex(8)
        try:
            c.execute("INSERT INTO users VALUES(?,?,?,?,?,?)",
                (uid,name,email,self._h(pin),"trial",
                 datetime.now(timezone.utc).isoformat()))
            cid=secrets.token_hex(8)
            c.execute("INSERT INTO children(id,parent,name,age) VALUES(?,?,?,?)",
                (cid,uid,child_name,child_age))
            self.db.commit()
            return {"user_id":uid,"pin":pin,"message":"Local trial created"}
        except sqlite3.IntegrityError:
            return {"detail":"Email already registered"}

    def login(self, email, pin):
        if self.online:
            r=requests.post(SERVER_URL+"/api/auth/login", json={"email":email,"pin":pin},timeout=8)
            if r.status_code==200:
                d=r.json(); self.token=d["access_token"]; self.user=d["user"]; return d
            return {"detail":"Invalid email or PIN"}
        c=self.db.cursor()
        email=(email or "").strip().lower()
        row=c.execute("SELECT id,name,email,pin_hash,plan FROM users WHERE email=?",(email,)).fetchone()
        print(f"[Pepper] login attempt email={email!r} found={bool(row)}")
        if not row:
            print(f"[Pepper] no user with email={email!r}")
            return {"detail":"Invalid email or PIN"}
        if row[3]!=self._h(pin):
            print(f"[Pepper] PIN mismatch for {email!r}")
            return {"detail":"Invalid email or PIN"}
        self.user={"id":row[0],"full_name":row[1],"email":row[2],"plan":row[4]}
        self.token="local"
        return {"access_token":"local","user":self.user}

    def _auth(self): return {"Authorization":f"Bearer {self.token}"} if self.token else {}

    # ---------- children ----------
    def list_children(self):
        if self.online:
            try:
                r=requests.get(SERVER_URL+"/api/children", headers=self._auth(),timeout=6)
                return r.json()
            except Exception: return []
        c=self.db.cursor()
        rows=c.execute("SELECT id,name,age,sessions,score FROM children WHERE parent=?",
            (self.user["id"],)).fetchall()
        return [{"id":r[0],"name":r[1],"age":r[2],"total_sessions":r[3],"total_score":r[4]} for r in rows]

    def add_child(self, name, age, diagnosis=""):
        if self.online:
            r=requests.post(SERVER_URL+"/api/children", headers=self._auth(),
                json={"name":name,"age":age,"diagnosis":diagnosis},timeout=6)
            return r.json()
        cid=secrets.token_hex(8); c=self.db.cursor()
        c.execute("INSERT INTO children(id,parent,name,age) VALUES(?,?,?,?)",
            (cid,self.user["id"],name,age)); self.db.commit()
        return {"id":cid,"name":name,"age":age}

    # ---------- sessions ----------
    def start_session(self, child_id):
        if self.online:
            r=requests.post(SERVER_URL+"/api/sessions/start", headers=self._auth(),
                json={"child_id":child_id},timeout=6); return r.json()
        return {"id":secrets.token_hex(8)}

    def log_task(self, sid, cid, domain, ttype, ok, attn, emo):
        if self.online:
            try: requests.post(SERVER_URL+"/api/sessions/log-task", headers=self._auth(),
                json={"session_id":sid,"child_id":cid,"domain":domain,"task_type":ttype,
                "success":ok,"attention":attn,"emotion":emo},timeout=4)
            except Exception: pass

    def end_session(self, sid, summary):
        if self.online:
            try: requests.post(SERVER_URL+"/api/sessions/end", headers=self._auth(),
                json={"session_id":sid,**summary},timeout=6)
            except Exception: pass

    def child_stats(self, child_id):
        if self.online:
            try: return requests.get(SERVER_URL+f"/api/sessions/stats/{child_id}",
                headers=self._auth(),timeout=6).json()
            except Exception: pass
        c=self.db.cursor()
        row=c.execute("SELECT sessions,score,m,c,v,ma,s FROM children WHERE id=?",(child_id,)).fetchone()
        if not row: row=(0,0,50,50,50,50,50)
        return {"total_sessions":row[0],"total_score":row[1],"total_mastered":0,
            "avg_attention":0,"skills":{"Motor":row[2],"Cognitive":row[3],"Verbal":row[4],
            "Math":row[5],"Social":row[6]},"domain_stats":{},"session_scores":[]}

    # ---------- billing ----------
    def checkout_url(self, plan, email):
        if self.online:
            try: return requests.post(SERVER_URL+"/api/billing/checkout",
                json={"plan":plan,"email":email},timeout=8).json().get("checkout_url")
            except Exception: return None
        return None

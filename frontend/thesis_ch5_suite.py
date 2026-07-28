"""PEPPER CLINICAL INFINITY V6 — COMPLETE CHAPTER 5 BENCHMARK SUITE
One script, all engineering metrics. © 2026 Lamya Fadlulmola Hamed Ali
Usage: python3 thesis_ch5_suite.py [frames] [fingers]"""
import time, statistics, csv, sys, os, platform
REPORT=[]
def out(line=""):
    print(line); REPORT.append(line)
def pctl(arr,p):
    if not arr: return 0
    return sorted(arr)[min(len(arr)-1,int(len(arr)*p))]
def section(t): out("\n"+"="*72); out("  "+t); out("="*72)
def main():
    N=300; do_fingers=False
    for a in sys.argv[1:]:
        if a.isdigit(): N=int(a)
        if a=="fingers": do_fingers=True
    section("PEPPER CLINICAL INFINITY V6 — CHAPTER 5 PERFORMANCE SUITE")
    out("  System Performance Evaluation — engineering benchmark (CPU-only)")
    out("  Date: "+time.strftime("%Y-%m-%d %H:%M:%S"))
    section("[T0] TEST ENVIRONMENT")
    env={}
    try:
        import cv2, numpy as np, mediapipe as mp
        env["OpenCV"]=cv2.__version__; env["NumPy"]=np.__version__; env["MediaPipe"]=mp.__version__
    except Exception as e: out("Missing core library: "+str(e)); return
    try:
        import psutil; HAS_PS=True
        env["CPU_cores"]=psutil.cpu_count(logical=True); env["RAM_total_GB"]=round(psutil.virtual_memory().total/1e9,1)
    except Exception: HAS_PS=False
    env["Python"]=platform.python_version(); env["OS"]=platform.platform(); env["Processor"]=platform.processor() or "n/a"
    for k,v in env.items(): out(f"   {k:16}: {v}")
    rows=[]
    def addrow(table,metric,**kw):
        r={"table":table,"metric":metric}; r.update(kw); rows.append(r); return r
    section("[T1] MODEL INITIALIZATION / COLD-START (ms)")
    init={}
    t0=time.perf_counter(); pose=mp.solutions.pose.Pose(model_complexity=0,min_detection_confidence=0.5,min_tracking_confidence=0.5); init["Pose"]=(time.perf_counter()-t0)*1000
    t0=time.perf_counter(); face=mp.solutions.face_mesh.FaceMesh(max_num_faces=1,refine_landmarks=False,min_detection_confidence=0.5); init["FaceMesh"]=(time.perf_counter()-t0)*1000
    t0=time.perf_counter(); hands=mp.solutions.hands.Hands(max_num_hands=2,model_complexity=0,min_detection_confidence=0.5); init["Hands"]=(time.perf_counter()-t0)*1000
    out(f"   {'Model':14}{'Init (ms)':>12}{'Target':>12}{'Verdict':>10}")
    ti={"Pose":500,"FaceMesh":600,"Hands":500}
    for k,v in init.items():
        verdict="PASS" if v<ti[k] else "REVIEW"
        out(f"   {k:14}{v:12.1f}{('<'+str(ti[k])+'ms'):>12}{verdict:>10}")
        addrow("T1_coldstart",k+"_init_ms",value=round(v,1),target=ti[k],verdict=verdict)
    cap=None
    for idx in [1,0,2]:
        c=cv2.VideoCapture(idx,cv2.CAP_V4L2)
        try:
            c.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            c.set(cv2.CAP_PROP_FPS, 30)
            c.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception: pass
        if c.isOpened():
            ok,_=c.read()
            if ok: cap=c; out(f"\n   [camera] using index {idx} @ 640x480"); break
            c.release()
    if cap is None: out("\n   [camera] none found — synthetic frames")
    pose_t=[];face_t=[];hands_t=[];total_t=[];pose_hit=face_hit=hands_hit=frames=0;cpu=[];ram=[]
    proc=psutil.Process(os.getpid()) if HAS_PS else None
    if proc: proc.cpu_percent(None)
    out(f"\n   [measuring {N} frames — Ctrl+C to stop early]\n"); t_start=time.time()
    try:
        while frames<N:
            if cap is not None:
                ok,frame=cap.read()
                if not ok: continue
            else: frame=(np.random.rand(480,640,3)*255).astype('uint8')
            small=cv2.resize(frame,(320,240))
            rgb=cv2.cvtColor(small,cv2.COLOR_BGR2RGB); rgb.flags.writeable=False
            f0=time.perf_counter()
            t0=time.perf_counter(); pr=pose.process(rgb); pose_t.append((time.perf_counter()-t0)*1000)
            if frames%2==0 or 'fr' not in dir():
                t0=time.perf_counter(); fr=face.process(rgb); face_t.append((time.perf_counter()-t0)*1000)
            if frames%2==0 or 'hr' not in dir():
                t0=time.perf_counter(); hr=hands.process(rgb); hands_t.append((time.perf_counter()-t0)*1000)
            total_t.append((time.perf_counter()-f0)*1000)
            if pr.pose_landmarks: pose_hit+=1
            if fr.multi_face_landmarks: face_hit+=1
            if hr.multi_hand_landmarks: hands_hit+=1
            frames+=1
            if proc and frames%10==0: cpu.append(proc.cpu_percent(None)); ram.append(proc.memory_info().rss/1e6)
            if frames%30==0: out(f"      {frames}/{N} | end-to-end {total_t[-1]:.1f} ms")
    except KeyboardInterrupt: out("\n   [stopped early]")
    if cap is not None: cap.release()
    elapsed=time.time()-t_start; fps=frames/elapsed if elapsed else 0
    section("[T2] COMPONENT LATENCY (ms) — full distribution")
    out(f"   {'Component':16}{'avg':>8}{'p50':>8}{'p95':>8}{'p99':>8}{'min':>8}{'max':>8}{'jitter':>8}{'target':>9}{'verdict':>9}")
    def lat(name,arr,target):
        if not arr: return
        avg=statistics.mean(arr); sd=statistics.pstdev(arr)
        r=dict(avg=round(avg,2),p50=round(pctl(arr,.5),2),p95=round(pctl(arr,.95),2),p99=round(pctl(arr,.99),2),mn=round(min(arr),2),mx=round(max(arr),2),sd=round(sd,2))
        v="PASS" if avg<target else "REVIEW"
        out(f"   {name:16}{r['avg']:8.2f}{r['p50']:8.2f}{r['p95']:8.2f}{r['p99']:8.2f}{r['mn']:8.2f}{r['mx']:8.2f}{r['sd']:8.2f}{('<'+str(target)):>9}{v:>9}")
        addrow("T2_latency",name,avg_ms=r['avg'],p50_ms=r['p50'],p95_ms=r['p95'],p99_ms=r['p99'],min_ms=r['mn'],max_ms=r['mx'],jitter_ms=r['sd'],target_ms=target,verdict=v)
    lat("Pose",pose_t,20); lat("FaceMesh",face_t,25); lat("Hands",hands_t,20); lat("End-to-end",total_t,33.3)
    if total_t:
        margin=(33.3-statistics.mean(total_t))/33.3*100
        out(f"\n   Real-time headroom vs 30 FPS budget (33.3 ms): {margin:.0f}%")
        addrow("T2_latency","realtime_headroom_%",value=round(margin,0))
    section("[T3] THROUGHPUT (frames per second)")
    peak=1000/min(total_t) if total_t else 0
    out(f"   Sustained FPS : {fps:6.1f}   (target >15)   {'PASS' if fps>15 else 'REVIEW'}")
    out(f"   Peak FPS      : {peak:6.1f}")
    out(f"   Frames measured: {frames}   Duration: {elapsed:.1f}s")
    addrow("T3_throughput","sustained_fps",value=round(fps,1),target=15,verdict="PASS" if fps>15 else "REVIEW")
    addrow("T3_throughput","peak_fps",value=round(peak,1))
    section("[T4] DETECTION RELIABILITY (% frames with valid landmarks)")
    for nm,hit in [("Pose",pose_hit),("Face",face_hit),("Hands",hands_hit)]:
        rate=hit/frames*100 if frames else 0
        out(f"   {nm:10}{rate:6.1f}%   ({hit}/{frames} frames)")
        addrow("T4_reliability",nm+"_detect_%",value=round(rate,1))
    if proc and cpu:
        section("[T5] RESOURCE USAGE (CPU-only operation)")
        out(f"   CPU  avg {statistics.mean(cpu):5.1f}%   peak {max(cpu):5.1f}%")
        out(f"   RAM  avg {statistics.mean(ram):5.0f} MB   peak {max(ram):5.0f} MB")
        addrow("T5_resource","cpu_avg_%",value=round(statistics.mean(cpu),1))
        addrow("T5_resource","cpu_peak_%",value=round(max(cpu),1))
        addrow("T5_resource","ram_avg_mb",value=round(statistics.mean(ram),0))
        addrow("T5_resource","ram_peak_mb",value=round(max(ram),0))
    section("[T6] TASK GENERATION (variety & capacity)")
    try:
        import html_tasks as HT
        t0=time.perf_counter(); sample=[HT.genTask(3) for _ in range(5000)]; gen_ms=(time.perf_counter()-t0)*1000
        types=set(t["type"] for t in sample); protos=set(t["protocol"] for t in sample)
        b2b=sum(1 for i in range(1,len(sample)) if sample[i]["type"]==sample[i-1]["type"])
        out(f"   Generated 5,000 tasks in {gen_ms:.1f} ms ({gen_ms/5000:.3f} ms/task)")
        out(f"   Distinct task types  : {len(types)}  {sorted(types)}")
        out(f"   Teaching methods     : {sorted(protos)}")
        out(f"   Back-to-back repeats : {b2b}/4999 ({b2b/4999*100:.1f}%)  (lower = better variety)")
        out(f"   Advertised capacity  : 100,000+ tasks")
        addrow("T6_tasks","gen_time_per_task_ms",value=round(gen_ms/5000,3))
        addrow("T6_tasks","distinct_types",value=len(types))
        addrow("T6_tasks","methods",value=len(protos))
        addrow("T6_tasks","b2b_repeat_%",value=round(b2b/4999*100,1))
    except Exception as e: out("   (html_tasks not importable: "+str(e)+")")
    if do_fingers:
        section("[T7] FINGER-COUNT ACCURACY (manual protocol)")
        out("   Show 0..5 fingers; record trials/correct manually (chirality-corrected).")
        addrow("T7_fingers","note",value="manual trial")
    keys=["table","metric","value","avg_ms","p50_ms","p95_ms","p99_ms","min_ms","max_ms","jitter_ms","target","target_ms","verdict"]
    with open("thesis_ch5_results.csv","w",newline="") as fp:
        w=csv.DictWriter(fp,fieldnames=keys); w.writeheader()
        for r in rows: w.writerow({k:r.get(k,"") for k in keys})
    with open("thesis_ch5_report.txt","w") as fp: fp.write("\n".join(REPORT))
    section("SUMMARY (for Abstract / Conclusion)")
    if total_t: out(f"   - End-to-end vision latency : {statistics.mean(total_t):.1f} ms (CPU-only)")
    out(f"   - Sustained throughput      : {fps:.1f} FPS")
    out(f"   - Detection reliability     : Pose {pose_hit/max(1,frames)*100:.0f}% / Face {face_hit/max(1,frames)*100:.0f}% / Hands {hands_hit/max(1,frames)*100:.0f}%")
    if proc and ram: out(f"   - Memory footprint          : {statistics.mean(ram):.0f} MB avg")
    out("   - Saved: thesis_ch5_results.csv + thesis_ch5_report.txt")
    out("="*72)
if __name__=="__main__": main()

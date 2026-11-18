import cv2,numpy as np,json,subprocess,sys,math
P=json.load(open("plan/edit_plan.json"));FPS=30
W,H=1080,1920;AX,AY=540,700
cuts=[0]+P["cuts"]
def ease(x):x=min(1,max(0,x));return x*x*(3-2*x)
def zoom(t):
    seg=max(i for i,c in enumerate(cuts) if t>=c-1e-6)
    s=cuts[seg];e=(cuts+[P["duration"]])[seg+1]
    lo,hi=[(1.0,1.06),(1.13,1.18),(1.0,1.04),(1.12,1.15),(1.0,1.05),(1.12,1.16),(1.0,1.09)][seg]
    z=lo+(hi-lo)*ease((t-s)/(e-s))
    for p in P["punch_zooms"]:
        d=t-p["t"]
        if d>=0: z+=p["amp"]*(ease(d/0.2) if d<0.2 else 1-ease((d-0.2)/0.6))*(d<0.8)
    return z
def dim(t):
    v=0
    for e in P["events"]:
        if e["type"]=="back_text":
            v=max(v,ease((t-e["start"])/0.2)*(1-ease((t-(e["end"]-0.2))/0.2)))
    return v
cap=cv2.VideoCapture("raw/cut.mp4")
N=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fcuts=[round(c*FPS) for c in cuts]
masks=[]
for i in range(N):
    m=cv2.imread(f"matte/raw/{i+1:04d}.png",0);masks.append(m)
def mk(cmd):return subprocess.Popen(cmd,stdin=subprocess.PIPE)
bg=mk(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r","30","-i","-","-c:v","libx264","-crf","12","-preset","fast","-pix_fmt","yuv420p","layers/bg.mp4"])
pe=mk(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","bgra","-s",f"{W}x{H}","-r","30","-i","-","-c:v","prores_ks","-profile:v","4444","-pix_fmt","yuva444p10le","layers/person.mov"])
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
vig=1-0.22*np.clip((((xx-W/2)/(W*0.62))**2+((yy-H/2)/(H*0.62))**2),0,1.2)**1.3
vig=vig[...,None].astype(np.float32)
dbg=len(sys.argv)>1
def seg_of(i):return max(k for k,c in enumerate(fcuts) if i>=c)
for i in range(N):
    ok,fr=cap.read()
    if not ok:break
    # temporal median within same scene
    s=seg_of(i);idx=[j for j in (i-1,i,i+1) if 0<=j<N and seg_of(j)==s]
    ms=np.stack([masks[j] for j in idx]);m=np.median(ms,0).astype(np.uint8) if len(idx)>=3 else masks[i]
    m=cv2.resize(m,(W,H),interpolation=cv2.INTER_CUBIC)
    m=cv2.ximgproc.guidedFilter(fr,m,16,1e-3*255*255) if hasattr(cv2,'ximgproc') else m
    mf=m.astype(np.float32)/255
    mf=np.clip((mf-0.12)/(0.78-0.12),0,1)         # soft threshold
    mf=cv2.erode(mf,np.ones((3,3),np.uint8))       # ~1px
    mf=cv2.GaussianBlur(mf,(0,0),1.1)               # feather
    t=i/FPS;z=zoom(t)
    dx=W*0.004*math.sin(t*1.7)+W*0.002*math.sin(t*3.1);dy=H*0.004*math.cos(t*1.3)
    M=np.float32([[z,0,AX-z*AX+dx],[0,z,AY-z*AY+dy]])
    frz=cv2.warpAffine(fr,M,(W,H),flags=cv2.INTER_LANCZOS4,borderMode=cv2.BORDER_REFLECT)
    mz=cv2.warpAffine(mf,M,(W,H),flags=cv2.INTER_LINEAR)
    # grade
    f=frz.astype(np.float32)/255
    f=np.clip((f-0.5)*1.09+0.5+0.01,0,1)
    g=f.mean(2,keepdims=True);f=np.clip(g+(f-g)*1.12,0,1)
    f=f*vig
    person=f.copy()
    d=dim(t)
    if d>0.001:
        b=cv2.GaussianBlur(f,(0,0),3)
        f=(f*(1-d)+b*d)*(1-0.15*d)
    bg.stdin.write((np.clip(f,0,1)*255).astype(np.uint8).tobytes())
    rgba=np.dstack([np.clip(person,0,1)*255,mz*255]).astype(np.uint8)
    pe.stdin.write(rgba.tobytes())
    if dbg and i in (10,60,100,150,200,260,300,380):
        comp=person*mz[...,None]+np.array([0.2,0.9,0.2],np.float32)*(1-mz[...,None])
        cv2.imwrite(f"plan/mchk_{i}.jpg",(comp*255).astype(np.uint8))
bg.stdin.close();pe.stdin.close();bg.wait();pe.wait();print("done",N)

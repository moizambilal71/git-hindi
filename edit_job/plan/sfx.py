import numpy as np,json,soundfile as sf,subprocess
from scipy import signal
SR=44100; P=json.load(open("plan/edit_plan.json")); DUR=16.7
rng=np.random.default_rng(3)
def env(n,a=0.005,d=0.2,p=2.5):
    t=np.arange(n)/SR; e=np.minimum(t/a,1)*np.exp(-t/d*p/2.5); return e
def whoosh(dur=0.5,up=True,v=1):
    n=int(SR*dur); x=rng.normal(0,1,n); t=np.linspace(0,1,n)
    fc=(300+3500*t**2) if up else (3800-3400*t); out=np.zeros(n); 
    # time-varying bandpass via blocks
    B=256
    for i in range(0,n,B):
        f=float(np.mean(fc[i:i+B])); b,a=signal.butter(2,[max(80,f*0.6)/(SR/2),min(f*1.5,20000)/(SR/2)],'band'); out[i:i+B]=signal.lfilter(b,a,x[i:i+B])
    e=np.sin(np.pi*t)**1.5; return out*e*0.9*v
def pop(f=520,v=1):
    n=int(SR*0.18); t=np.arange(n)/SR; fr=f*(0.55+0.45*np.exp(-t*35)); ph=2*np.pi*np.cumsum(fr)/SR
    return np.sin(ph)*env(n,0.002,0.07)*v
def ping(f=1760,v=1):
    n=int(SR*0.6); t=np.arange(n)/SR
    return (np.sin(2*np.pi*f*t)+0.4*np.sin(2*np.pi*f*2.01*t)+0.2*np.sin(2*np.pi*f*3.02*t))*env(n,0.002,0.25)*0.45*v
def tick(v=1):
    n=int(SR*0.04); x=rng.normal(0,1,n); b,a=signal.butter(2,2500/(SR/2),'high'); return signal.lfilter(b,a,x)*env(n,0.0005,0.012)*0.5*v
def shimmer(dur=0.6,v=1):
    n=int(SR*dur); t=np.arange(n)/SR; out=np.zeros(n)
    for k,f in enumerate([523,659,784,1046,1319]): out+=np.sin(2*np.pi*f*(1+0.25*t/dur)*t)*np.clip((t-k*dur*0.12)/0.05,0,1)
    return out/5*np.sin(np.pi*np.clip(t/dur,0,1))**0.7*v
def bass(v=1):
    n=int(SR*0.45); t=np.arange(n)/SR; fr=45+90*np.exp(-t*18); ph=2*np.pi*np.cumsum(fr)/SR
    return np.sin(ph)*env(n,0.002,0.22)*0.9*v
def riser(dur=0.55,v=1):
    n=int(SR*dur); t=np.arange(n)/SR; x=rng.normal(0,1,n); b,a=signal.butter(2,[800/(SR/2),9000/(SR/2)],'band'); x=signal.lfilter(b,a,x)
    return (x*(t/dur)**2*0.5+np.sin(2*np.pi*(300+1500*(t/dur)**2)*t)*0.2*(t/dur))*v
def glitch(v=1):
    n=int(SR*0.25); x=rng.normal(0,1,n); x=np.round(x*3)/3
    g=(rng.random(n//500+1)>0.4).repeat(500)[:n]; return x*g*env(n,0.001,0.12)*0.5*v
EV=[]  # (time, kind, gain)
def add(t,k,v=1.0,**kw): EV.append((t,k,v,kw))
tk={"glitch":0,"whip":1,"glass":2,"halftone":3,"pixel":4,"zoomthrough":5}
for tr in P["transitions"]:
    k=tr["k"]
    if k=="glitch": add(tr["t"]-0.02,"glitch",0.9)
    elif k=="halftone": add(tr["t"]-0.05,"whoosh",0.7,up=False,dur=0.4)
    elif k=="pixel": add(tr["t"]-0.03,"tick",1.2); add(tr["t"]+0.06,"tick",1.0)
    else: add(tr["t"]-0.12,"whoosh",0.9,up=(k!="whip"),dur=0.45)
for b in P["back"]: add(b["s"]+0.02,"pop",0.85,f=420+60*(hash(b["id"])%5))
for f in P["front"]:
    if f["type"] in("tile","route","ring"): add(f["s"]+0.05,"ping",0.7,f=1568+(hash(f["id"])%4)*110)
    if f["type"]=="plus": add(f["s"],"pop",0.9,f=800)
    if f["type"]=="cta": add(f["s"],"ping",0.9,f=2093); add(f["s"],"pop",0.8,f=600)
    if f["type"]=="tile" and f.get("check"): add(f["check"],"tick",1.4)
    if f["type"]=="tile" and f.get("strike"): add(f["strike"],"tick",1.6)
    if f["type"]=="ring": add(f["fillStart"],"shimmer",0.55,dur=f["fillEnd"]-f["fillStart"]+0.2); add(f["fillEnd"],"ping",0.8,f=2349)
    if f["type"]=="route": add(f["s"]+0.12,"shimmer",0.35,dur=0.5)
for z in P["zoom"]: add(z["t"],"bass",0.9)
add(13.55,"riser",0.8,dur=0.58)
# caption ticks (quiet), skipped if crowded
cap=[(c["s"],"tick",0.35,{}) for c in P["captions"]]
def crowded(t,ev): return sum(1 for e in ev if abs(e[0]-t)<0.12)>=2
for c in cap:
    if not crowded(c[0],EV): EV.append(c)
EV.sort(key=lambda e:e[0])
# enforce max 2 simultaneous (0.15s window)
keep=[]
for e in EV:
    if sum(1 for k in keep if abs(k[0]-e[0])<0.15)<2: keep.append(e)
print(len(EV),"->",len(keep),"sfx")
n=int(SR*DUR); bus=np.zeros(n)
fn={"whoosh":whoosh,"pop":pop,"ping":ping,"tick":tick,"shimmer":shimmer,"bass":bass,"riser":riser,"glitch":glitch}
for t,k,v,kw in keep:
    jitter=1+rng.uniform(-0.05,0.05)
    kw=dict(kw)
    if k in("pop","ping") and "f" in kw: kw["f"]*=jitter
    x=fn[k](v=v,**kw); i=max(0,int(t*SR)); x=x[:n-i]; bus[i:i+len(x)]+=x
sf.write("sfx/sfx_bus.wav",bus.astype(np.float32),SR)
json.dump([{"t":round(t,2),"sfx":k} for t,k,v,kw in keep],open("plan/sfx_events.json","w"))
# music bed: soft lo-fi pad Am F C G, 4s per chord at ~ 90bpm feel
t=np.arange(n)/SR; chords=[[220,261.6,329.6],[174.6,220,261.6],[261.6,329.6,392],[196,246.9,293.7]]
m=np.zeros(n)
for i in range(0,n,int(SR*3)):
    ch=chords[(i//int(SR*3))%4]; seg=np.arange(min(int(SR*3),n-i))/SR
    e=np.minimum(seg/0.8,1)*np.minimum((3-seg)/0.8,1)
    for f in ch: m[i:i+len(seg)]+=(np.sin(2*np.pi*f*seg)+0.3*signal.sawtooth(2*np.pi*f*seg*1.003))*e*0.2
    m[i:i+len(seg)]+=np.sin(2*np.pi*ch[0]/2*seg)*e*0.35
b,a=signal.butter(2,1400/(SR/2)); m=signal.lfilter(b,a,m)
# soft kick-ish pulse for rhythm
for k in range(int(DUR*1.5)):
    i=int(k/1.5*SR); x=bass(0.5)[:n-i]; m[i:i+len(x)]+=x*0.5
sf.write("sfx/music.wav",(m/np.abs(m).max()*0.8).astype(np.float32),SR)

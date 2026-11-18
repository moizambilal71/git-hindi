import numpy as np,soundfile as sf,json,subprocess
from scipy import signal
SR=48000;rng=np.random.default_rng(7)
def env(n,a=0.005,d=None):
    t=np.arange(n)/SR;d=d or n/SR/3;return np.minimum(t/a,1)*np.exp(-t/d)
def whoosh(dur=0.5,up=True,v=0):
    n=int(SR*dur);x=rng.standard_normal(n);t=np.linspace(0,1,n)
    fc=(400+3500*t**1.5) if up else (3900-3500*t)
    out=np.zeros(n);y=np.zeros(n);
    b=signal.butter(2,[300/(SR/2),4000/(SR/2)],'band');x=signal.lfilter(*b,x)
    mod=np.sin(np.pi*t)**1.5
    return x*mod*0.6*(1+0.1*v)
def pop(v=0):
    n=int(SR*0.18);t=np.arange(n)/SR;f=520*(1+0.12*v)*np.exp(-t*22)+180
    return np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,0.002,0.05)
def glass(v=0):
    n=int(SR*0.7);t=np.arange(n)/SR;f0=1800+200*v
    return (np.sin(2*np.pi*f0*t)+0.5*np.sin(2*np.pi*f0*2.76*t)+0.3*np.sin(2*np.pi*f0*5.4*t))*env(n,0.001,0.16)*0.5
def tick(v=0):
    n=int(SR*0.04);x=rng.standard_normal(n);b=signal.butter(2,[2500/(SR/2),7000/(SR/2)],'band')
    return signal.lfilter(*b,x)*env(n,0.0005,0.008)*1.4
def bass():
    n=int(SR*0.6);t=np.arange(n)/SR;f=45+90*np.exp(-t*18)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,0.002,0.2)*1.3
def riser(dur=0.35):
    n=int(SR*dur);t=np.linspace(0,1,n);x=rng.standard_normal(n)
    b=signal.butter(2,[800/(SR/2),6000/(SR/2)],'band');x=signal.lfilter(*b,x)
    return x*t**2*0.6+np.sin(2*np.pi*np.cumsum(300+1500*t**2)/SR)*t**2*0.3
def shimmer(dur=0.9):
    n=int(SR*dur);t=np.arange(n)/SR;o=np.zeros(n)
    for i,f in enumerate([880,1320,1760,2640]):
        o+=np.sin(2*np.pi*f*t)*np.exp(-(t-i*0.08).clip(0)*5)*(t>i*0.08)*0.3
    return o
def glitch():
    n=int(SR*0.2);x=rng.standard_normal(n);x=np.sign(x)*(rng.random(n)>0.4)
    m=(np.floor(np.arange(n)/SR*60)%2);return x*m*env(n,0.001,0.08)*0.5
P=json.load(open("plan/edit_plan.json"))
def at(name,t,v=0):
    return {"whoosh":lambda:whoosh(0.45,v%2==0,v),"pop":lambda:pop(v),"glass":lambda:glass(v),"tick":lambda:tick(v),"bass":bass,"riser":riser,"shimmer":shimmer,"glitch":glitch}[name](),t
hits=[]
def H(n,t,v=0):hits.append((n,t,v))
# timed to events (cut-timeline seconds)
H("whoosh",0.05);H("pop",0.07);H("pop",1.16,1)
for i in range(17):H("tick",2.58+i*0.067,i%3)
H("pop",2.45);H("pop",3.45,1);H("whoosh",3.55,1)
H("bass",4.06);H("whoosh",4.0,1);H("glass",4.58)
H("riser",5.25);H("whoosh",5.45,1)
H("pop",5.55);H("pop",6.40,1);H("glass",6.42)
H("glitch",7.95)
H("whoosh",7.7);H("pop",8.32);H("pop",9.14,1);H("pop",10.32,2);H("pop",11.48,3)
H("whoosh",10.22,1);H("glitch",11.38);H("tick",11.5)
H("bass",11.5);H("shimmer",12.2);H("pop",12.3,2);H("whoosh",3.58)
json.dump(hits,open("sfx/hits.json","w"))
dur=13.04;N=int((dur+1)*SR);sfx=np.zeros(N)
for n,t,v in hits:
    s,_=at(n,t,v);i=int(t*SR);sfx[i:i+len(s)]+=s[:N-i]
sfx/=max(1e-9,np.abs(sfx).max())
# voice: clean
subprocess.run(["ffmpeg","-y","-v","error","-i","raw/cut.mp4","-vn","-ac","2","-ar","48000","-af","highpass=f=90,afftdn=nr=12:nf=-40,equalizer=f=3000:t=q:w=1.2:g=2,acompressor=threshold=-20dB:ratio=3:attack=10:release=120:makeup=1,alimiter=limit=0.85","sfx/voice.wav"],check=True)
v,_=sf.read("sfx/voice.wav");v=v[:N] if len(v)>=N else np.pad(v,((0,N-len(v)),(0,0)))
vp=np.abs(v).max()
# SFX peak ~ -10.5 dB under voice peak
sfx2=(sfx*vp*10**(-10.5/20))[:,None]*np.ones((1,2))
# sidechain-style: duck sfx lightly when voice loud? keep sfx as is. Soft music bed: low pad, ducked
t=np.arange(N)/SR
pad=sum(np.sin(2*np.pi*f*t+ph)*a for f,ph,a in [(110,0,.5),(164.8,1,.35),(220,2,.3),(277.2,3,.2)])*(0.6+0.4*np.sin(2*np.pi*t/6.5))
pad=pad+0.12*np.sign(np.sin(2*np.pi*2*t))*np.exp(-((t*2)%1)*9)*np.sin(2*np.pi*55*t)  # soft pulse
env_v=np.abs(v).mean(1);k=int(SR*0.12);env_v=np.convolve(env_v,np.ones(k)/k,'same');duck=1-0.65*np.clip(env_v/(env_v.max()*0.4),0,1)
pad=pad*duck;pad=pad/np.abs(pad).max()*vp*10**(-19.5/20)
mix=v+sfx2+pad[:,None]
sf.write("sfx/mix_raw.wav",mix[:int(dur*SR)]*0.6,SR,subtype="FLOAT")
print("peak voice",vp)

import numpy as np, wave, sys
SR=48000; D=241.0; n=int(SR*D); t=np.arange(n)/SR
rng=np.random.default_rng(7)
def lp(x,fc):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); X*=1/(1+(f/fc)**4); return np.fft.irfft(X,len(x))
def bp(x,a,b):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); X*=((f>a)&(f<b)); return np.fft.irfft(X,len(x))
def env(a,b,fi=1.0,fo=1.0):
    return np.clip((t-a)/fi,0,1)*np.clip((b-t)/fo,0,1)
def smooth(a,b,v0,v1): 
    u=np.clip((t-a)/(b-a),0,1); return v0+(v1-v0)*u*u*(3-2*u)
L=np.zeros(n); R=np.zeros(n)
# wind
w=bp(rng.normal(0,1,n),150,900); w/=np.abs(w).max()
mod=0.55+0.45*np.sin(2*np.pi*t/9.0+1)*np.sin(2*np.pi*t/23.0)
wind=w*mod*0.35
wl=lp(rng.normal(0,1,n),300); wl/=np.abs(wl).max()
L+=wind+wl*0.18; R+=np.roll(wind,2400)+np.roll(wl,1200)*0.18
# drone: dark section 0-160 and 205-224, pad warm after
drone=(np.sin(2*np.pi*55*t)+0.6*np.sin(2*np.pi*82.41*t)+0.35*np.sin(2*np.pi*110.3*t))*0.22
dark=env(0,224,3,3)*(1-smooth(160,170,0,1))+0
dr=drone*(0.25+0.1*np.sin(2*np.pi*t/14))*dark
peaks=[(86.0,89.5),(116.4,119.6),(219.2,224.4),(51.0,56.0)]
for a,b in peaks:
    dr+=drone*1.4*np.clip((t-a)/(b-a),0,1)**2*(t<b)*np.clip((b+2.5-t)/2.5,0,1)*(t>=a)
L+=dr; R+=dr
# warm pad (hadith, repentance, dua)
freqs=[220.0,277.18,329.63,440.0,554.37]
pad=sum(np.sin(2*np.pi*f*t+i)*(0.5/(i+1)) for i,f in enumerate(freqs))
pad*=0.10*(0.8+0.2*np.sin(2*np.pi*t/7))
pe=smooth(160,172,0,1)*(1-smooth(184,184.01,0,0))  # hadith
pe=np.where(t<184,smooth(160,172,0,1),np.where(t<205.4,smooth(184,200,0.7,1.0),np.where(t<224.2,0.0,smooth(224.2,232,0,1))))
pad*=pe*env(0,D,0.1,3.0)
L+=pad; R+=pad
# water drops 29.9-32.6
for k in range(9):
    tt=29.9+k*0.33
    i0=int(tt*SR); m=int(0.35*SR)
    if i0+m<n:
        e=np.exp(-np.arange(m)/SR*14); f=900+k*40
        d=np.sin(2*np.pi*f*np.arange(m)/SR)*e*0.12
        L[i0:i0+m]+=d; R[i0:i0+m]+=d
# soil thuds (handfuls) 51.4-62.5 : noise burst + low thump
def thump(tt,amp=0.6,pan=0.5,f0=70,dur=0.5):
    i0=int(tt*SR); m=int(dur*SR)
    if i0+m>=n: return
    x=np.arange(m)/SR
    nz=lp(rng.normal(0,1,m),500)*np.exp(-x*9)
    th=np.sin(2*np.pi*(f0+40*np.exp(-x*20))*x)*np.exp(-x*8)
    s=(nz*0.7+th*0.9)*amp
    L[i0:i0+m]+=s*(1-pan); R[i0:i0+m]+=s*pan
tt=51.6
while tt<62.5:
    for j in range(5):
        thump(tt+j*0.07+rng.uniform(0,0.04),amp=rng.uniform(0.15,0.3),pan=rng.uniform(.3,.7),f0=90,dur=0.35)
    thump(tt+0.35,0.55,0.5,55,0.6)
    tt+=1.15
# footsteps walking away 58-69 (fading, panning outward)
s=58.0; k=0
while s<69.2:
    a=0.35*(1-(s-58)/12)
    thump(s,a,0.5+0.45*((s-58)/11)*(1 if k%2 else -1)*0.5,110,0.25)
    s+=0.62; k+=1
# funeral procession footsteps 35.7-44
s=35.7
while s<40.4:
    thump(s,0.14,0.5+0.2*np.sin(s),120,0.22); s+=0.55
# farewell footsteps 213.9-220
s=213.9; k=0
while s<219.6:
    a=0.3*(1-(s-213.9)/7)
    thump(s,a,0.5+0.3*(s-213.9)/6,115,0.25); s+=0.6; k+=1
# heartbeat in questioning / final peak
for a,b in ((79.4,89.0),(219.4,224.0)):
    s=a
    while s<b:
        for off,am in ((0,.30),(0.28,.20)):
            i0=int((s+off)*SR); m=int(0.3*SR)
            x=np.arange(m)/SR; h=np.sin(2*np.pi*48*x)*np.exp(-x*14)*am
            L[i0:i0+m]+=h; R[i0:i0+m]+=h
        s+=0.95-0.25*(s-a)/(b-a)
# carefully timed silence: duck everything to near zero 119.4-128.6 except faint wind
duck=1-0.88*(env(119.2,128.8,0.4,0.9)>0.001)*np.clip(np.minimum((t-119.2)/0.4,(129.0-t)/0.9),0,1)
L*=duck; R*=duck
# global
fade=np.clip(t/1.5,0,1)*np.clip((D-t)/2.5,0,1)
L*=fade; R*=fade
m=max(np.abs(L).max(),np.abs(R).max()); L/=m; R/=m
out=np.stack([L,R],1)*0.9
pcm=(out*32767).astype('<i2')
with wave.open(sys.argv[1],'wb') as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(pcm.tobytes())

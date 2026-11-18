import numpy as np,soundfile as sf,sys
sys.argv=['x']
exec(open("sfx/synth.py").read().split("P=json.load")[0])   # reuse synth functions
x,sr=sf.read("sfx/mix_raw.wav");x=x if x.ndim==2 else x[:,None]*np.ones((1,2))
T0=12.64;total=16.54;N=int(total*SR)
out=np.zeros((N,2));out[:len(x)]=x[:N]
# fade out old pad tail so it doesn't clash with the card
a=int(12.9*SR);b=int(13.3*SR);out[a:b]*= np.linspace(1,0.35,b-a)[:,None];
amp=0.097
def put(s,t,g=1.0):
    i=int(t*SR);s=s*amp*g;out[i:i+len(s),0]+=s[:N-i];out[i:i+len(s),1]+=s[:N-i]
put(whoosh(0.5,True,1),T0-0.05);put(glitch(),T0+0.02,0.6)
put(pop(0),T0+0.33,1.3);put(shimmer(),T0+0.4,0.8)
for i in range(11):put(tick(i%3),T0+1.13+i*0.05,0.7)   # letters
for i in range(3):put(tick(i),T0+2.07+i*0.17,1.2)       # dots
put(pop(2),T0+2.33,1.2);put(glass(1),T0+2.35,1.0)       # date pill + chime
put(glass(3),T0+2.6,0.5)
# soft pad tail under the card
t=np.arange(N-int(13.0*SR))/SR;pad=sum(np.sin(2*np.pi*f*t)*a_ for f,a_ in [(220,.5),(277.2,.35),(329.6,.3)])
env=np.minimum(t/0.8,1)*np.minimum((t[-1]-t)/1.2,1);pad=pad*env*0.034
out[int(13.0*SR):,0]+=pad;out[int(13.0*SR):,1]+=pad
sf.write("sfx/mix_end.wav",out,SR,subtype="FLOAT")

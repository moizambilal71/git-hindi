import numpy as np,cv2,json,subprocess,sys,glob,os
P=json.load(open("plan/edit_plan.json")); N=501; fps=30
W,H=1080,1920
rng=np.random.default_rng(7)
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
vig=1-0.28*(((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2*0.8); vig=np.clip(vig,0.55,1)[...,None]
def grade(im):
    f=im.astype(np.float32)/255
    f=np.clip((f-0.5)*1.07+0.5,0,1)
    g=f.mean(2,keepdims=True); f=np.clip(g+(f-g)*1.10,0,1)
    return f
def dark_amt(t):
    a=0
    for b in P["back"]:
        s,e=max(b["s"],0.3),b["e"]
        a=max(a,np.clip((t-s)/0.2,0,1)*np.clip((e-t)/0.2,0,1)*0.30)
    return a
def zoom_amt(t):
    z=0
    for q in P["zoom"]:
        d=t-q["t"]
        z+=q["a"]*(np.exp(-(d/0.06)**2) if d<0 else np.exp(-d/0.45))
    return z
def scale_about(img,z,cx=W/2,cy=H*0.42):
    if abs(z-1)<1e-4: return img
    M=np.float32([[z,0,cx*(1-z)],[0,z,cy*(1-z)]])
    return cv2.warpAffine(img,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
def trans_fx(img,fi):
    for tr in P["transitions"]:
        f=fi-int(round(tr["t"]*fps)); 
        if tr["k"]=="zoomthrough": f+=3
        if f<0 or f>8: continue
        p=f/8; k=np.sin(np.pi*p)
        if tr["k"]=="glitch":
            o=img.copy(); d=int(18*k)
            o[...,0]=np.roll(img[...,0],d,1); o[...,2]=np.roll(img[...,2],-d,1)
            for _ in range(5):
                y0=int(rng.integers(0,H-120)); hh=int(rng.integers(30,120)); o[y0:y0+hh]=np.roll(o[y0:y0+hh],int(rng.integers(-60,60)),1)
            img=o
        elif tr["k"]=="whip":
            kk=int(1+90*k)|1; img=cv2.blur(img,(kk,1)); img=np.roll(img,int(-150*np.sin(np.pi*p)*(1 if p<.5 else -1)),1)
        elif tr["k"]=="zoomthrough":
            zmax=1+0.35*k; acc=np.zeros_like(img)
            for z in np.linspace(1,zmax,7): acc+=scale_about(img,z,W/2,H*0.45)
            img=acc/7
    return img
def flash(fi):
    a=0
    for tr in P["transitions"]:
        f=fi-int(round(tr["t"]*fps))
        if 0<=f<3: a=max(a,0.28*(1-f/3))
    return a
def rd(path,flag=cv2.IMREAD_UNCHANGED): return cv2.imread(path,flag)
def frames(scale=1.0):
    for i in range(N):
        t=i/fps
        base=grade(rd(f"raw/fr/{i+1:04d}.jpg"))
        m=rd(f"matte/m/{i+1:04d}.png",0).astype(np.float32)[...,None]/255
        d=dark_amt(t)
        bg=base*(1-d)*vig; bg=bg*(1-d*0.3)+ (bg.mean(2,keepdims=True))*d*0.3
        L1=rd(f"layers/back/element-{i:03d}.png").astype(np.float32)/255
        a=L1[...,3:4]; out=bg*(1-a)+L1[...,[0,1,2]]*a
        pers=base*(0.97+0.03*vig)
        out=out*(1-m)+pers*m
        out=(np.clip(out,0,1)*255).astype(np.uint8)
        out=scale_about(out,1+zoom_amt(t))
        out=trans_fx(out,i)
        out=out.astype(np.float32)/255
        L3=rd(f"layers/front/element-{i:03d}.png").astype(np.float32)/255
        a=L3[...,3:4]; out=out*(1-a)+L3[...,[0,1,2]]*a
        fl=flash(i); out=out+fl*(1-out)
        out=out+rng.normal(0,0.012,(H,W,1)).astype(np.float32)
        out=(np.clip(out,0,1)*255).astype(np.uint8)
        yield out
if __name__=="__main__":
    if sys.argv[1]=="stills":
        os.makedirs("out/stills",exist_ok=True)
        want=[int(x) for x in sys.argv[2].split(",")]
        for i,fr in enumerate(frames()):
            if i in want: cv2.imwrite(f"out/stills/{i:04d}.jpg",fr)
            if i>max(want): break
    else:
        pr=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r","30","-i","-","-c:v","libx264","-crf","17","-preset","medium","-pix_fmt","yuv420p","out/video_noaudio.mp4"],stdin=subprocess.PIPE)
        for fr in frames(): pr.stdin.write(fr.tobytes())
        pr.stdin.close(); pr.wait()

import numpy as np,cv2,glob,time
from PIL import Image
from rembg import new_session, remove
s=new_session("u2net_human_seg",providers=["CPUExecutionProvider"])
fs=sorted(glob.glob("raw/fr/*.jpg")); raw=[]
t=time.time()
for i,f in enumerate(fs):
    im=Image.open(f).resize((540,960))
    m=np.array(remove(im,session=s,only_mask=True)).astype(np.float32)/255
    raw.append(m)
    if i%50==0: print(i,time.time()-t,flush=True)
raw=np.stack(raw)
out=[];prev=None
for i,m in enumerate(raw):
    # soft threshold curve
    m=np.clip((m-0.25)/0.55,0,1); m=m*m*(3-2*m)
    # keep components connected to main body
    b=(m>0.5).astype(np.uint8); n,lab,st,_=cv2.connectedComponentsWithStats(b)
    if n>1:
        keep=np.zeros_like(b); big=1+np.argmax(st[1:,4])
        for k in range(1,n):
            if k==big or st[k,4]>0.04*b.size: keep[lab==k]=1
        keep=cv2.dilate(keep,np.ones((9,9),np.uint8)); m=m*keep
    out.append(m)
out=np.stack(out)
# temporal smoothing 3 frame weighted
sm=out.copy()
for i in range(len(out)):
    a=out[max(i-1,0)];c=out[min(i+1,len(out)-1)]
    sm[i]=0.25*a+0.5*out[i]+0.25*c
for i,m in enumerate(sm):
    m=cv2.erode(m,np.ones((3,3),np.uint8))
    m=cv2.resize(m,(1080,1920),interpolation=cv2.INTER_CUBIC)
    m=cv2.GaussianBlur(m,(0,0),1.6)
    cv2.imwrite(f"matte/m/{i+1:04d}.png",(np.clip(m,0,1)*255).astype(np.uint8))
print("done")

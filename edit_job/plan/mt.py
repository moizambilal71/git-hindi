import sys,time,numpy as np
from PIL import Image
from rembg import new_session, remove
for name in ["u2net_human_seg","isnet-general-use"]:
    try:
        t=time.time(); s=new_session(name,providers=["CPUExecutionProvider"])
        im=Image.open("raw/fr/0200.jpg").resize((540,960))
        r=remove(im,session=s,only_mask=True); r.save(f"matte/test_{name}.png"); print(name,"ok",time.time()-t)
    except Exception as e: print(name,"FAIL",repr(e)[:200])

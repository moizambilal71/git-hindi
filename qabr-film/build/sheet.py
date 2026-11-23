import sys,render
from PIL import Image
ts=[float(x) for x in sys.argv[2:]]
ims=[render.frame_at(t).resize((360,640)) for t in ts]
cols=6; rows=(len(ims)+cols-1)//cols
c=Image.new('RGB',(360*cols,640*rows))
for i,im in enumerate(ims): c.paste(im,((i%cols)*360,(i//cols)*640))
c.save(sys.argv[1])

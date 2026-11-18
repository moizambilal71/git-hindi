import subprocess,re,json
PAD=0.08
segs=[]
for n in "ab":
    o=subprocess.run(["ffmpeg","-i",f"raw/{n}.wav","-af","silencedetect=n=-34dB:d=0.30","-f","null","-"],capture_output=True,text=True).stderr
    st=[float(x) for x in re.findall(r"silence_start: ([\d.]+)",o)]
    en=[float(x) for x in re.findall(r"silence_end: ([\d.]+)",o)]
    dur=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"raw/{n}.mp4"]))
    # speech = complement
    sil=list(zip(st,en+[dur]*(len(st)-len(en))))
    cur=0;sp=[]
    for s,e in sil:
        if s>cur+0.05: sp.append((cur,s))
        cur=e
    if cur<dur-0.05: sp.append((cur,dur))
    for s,e in sp: segs.append((n,max(0,s-PAD),min(dur,e+PAD)))
EXT=1.75;TAIL=(12.5151,13.65);SPD=(TAIL[1]-TAIL[0])/EXT
print(segs)
json.dump(segs,open("plan/segs.json","w"))
fc="";cat=""
for i,(n,s,e) in enumerate(segs):
    idx="ab".index(n)
    fc+=f"[{idx}:v]trim={s:.3f}:{e:.3f},setpts=PTS-STARTPTS[v{i}];[{idx}:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS[a{i}];"
    cat+=f"[v{i}][a{i}]"
n=len(segs)
fc+=f"[1:v]trim={TAIL[0]}:{TAIL[1]},setpts=(PTS-STARTPTS)/{SPD:.5f}[v{n}];[1:a]atrim={TAIL[0]}:{TAIL[1]},asetpts=PTS-STARTPTS,atempo={SPD:.5f}[a{n}];"
fc+=f"{cat}[v{n}][a{n}]concat=n={n+1}:v=1:a=1[v][a]"
subprocess.run(["ffmpeg","-y","-v","error","-i","raw/a.mp4","-i","raw/b.mp4","-filter_complex",fc,"-map","[v]","-map","[a]","-r","30","-c:v","libx264","-crf","12","-preset","fast","-pix_fmt","yuv420p","-c:a","aac","-b:a","256k","raw/cut.mp4"],check=True)
# cumulative timeline
t=0;tl=[]
for n,s,e in segs: tl.append({"clip":n,"src_s":s,"src_e":e,"out_s":round(t,3),"out_e":round(t+e-s,3)}); t+=e-s
json.dump(tl,open("plan/timeline.json","w"),indent=1); print(t+EXT)

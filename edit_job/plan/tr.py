import sys,json,soundfile as sf
from faster_whisper import WhisperModel
m=WhisperModel("medium",device="cpu",compute_type="int8")
out={}
for n in "ab":
    seg,info=m.transcribe(sf.read(f"raw/{n}.wav",dtype="float32")[0],word_timestamps=True,language="hi",condition_on_previous_text=False,beam_size=5,vad_filter=False)
    out[n]={"lang":info.language,"prob":info.language_probability,"words":[{"w":w.word,"s":w.start,"e":w.end} for s in seg for w in s.words]}
    print(n,info.language,info.language_probability," ".join(w["w"] for w in out[n]["words"]))
json.dump(out,open("plan/raw_tr.json","w"),ensure_ascii=False,indent=1)

import json,sys
from faster_whisper import WhisperModel
m=WhisperModel(sys.argv[1],device="cpu",compute_type="int8")
import soundfile as sf
audio,_=sf.read("raw/a16.wav",dtype="float32")
seg,info=m.transcribe(audio,word_timestamps=True,vad_filter=False,beam_size=5)
out=[];print(info.language,info.language_probability)
for s in seg:
  for w in s.words: out.append({"w":w.word.strip(),"s":round(w.start,2),"e":round(w.end,2)})
json.dump({"lang":info.language,"words":out},open("plan/transcript.json","w"),ensure_ascii=False,indent=1)
print(" ".join(f'{w["w"]}[{w["s"]}]' for w in out))

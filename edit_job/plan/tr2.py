import json,soundfile as sf
from faster_whisper import WhisperModel
m=WhisperModel("medium",device="cpu",compute_type="int8")
seg,i=m.transcribe(sf.read("raw/cut.wav",dtype="float32")[0],word_timestamps=True,language="hi",condition_on_previous_text=False,beam_size=5,initial_prompt="Dhaba Uncle home kitchen register download profile menu upload go live earning")
w=[{"w":x.word.strip(),"s":round(x.start,2),"e":round(x.end,2)} for s in seg for x in s.words]
json.dump({"language":"hi","words":w},open("plan/transcript.json","w"),ensure_ascii=False,indent=1);print(w)

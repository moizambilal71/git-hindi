#!/bin/bash
cd /home/user/git-hindi/edit_job
M=$(ffmpeg -y -i sfx/mix_raw.wav -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | python3 -c "
import sys,json,re;t=sys.stdin.read();d=json.loads(t[t.rindex('{'):t.rindex('}')+1]);print(f\"measured_I={d['input_i']}:measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}:measured_thresh={d['input_thresh']}:offset={d['target_offset']}\")")
ffmpeg -y -v error -i layers/bg.mp4 -i layers/Back.mov -i layers/person.mov -i layers/Front.mov -i layers/Caps.mov -i layers/Top.mov -i sfx/mix_raw.wav \
 -filter_complex "[0:v]format=yuv420p[a];[a][1:v]overlay=format=auto:shortest=1[b];[b][2:v]overlay=format=auto:shortest=1[c];[c][3:v]overlay=format=auto:shortest=1[d];[d][4:v]overlay=format=auto:shortest=1[e];[e][5:v]overlay=format=auto:shortest=1,format=yuv420p[v];[6:a]loudnorm=I=-14:TP=-1.5:LRA=11:$M:linear=true,aresample=48000[au]" \
 -map "[v]" -map "[au]" -t 13.04 -r 30 -c:v libx264 -crf 17 -preset medium -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart out/final_1080x1920.mp4
ffmpeg -y -v error -i out/final_1080x1920.mp4 -vf scale=540:960 -c:v libx264 -crf 22 -preset fast -c:a copy -movflags +faststart out/final_preview_540x960.mp4

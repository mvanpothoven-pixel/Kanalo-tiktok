#!/bin/bash
# Composite one fun video (runs in the Higgsfield sandbox; cloudfront is blocked from the Claude workspace).
# compose.sh ID CLIP_URL LANG -> out/ID.mp4   (6 s AI clip + hook/payoff cards + 3.6 s blurred end card + baked music, 9.6 s)
set -e
ID=$1; CLIP=$2; LG=$3; R=https://raw.githubusercontent.com/mvanpothoven-pixel/Kanalo-tiktok/main/pub/fun
mkdir -p in out
[ -f in/$(basename $CLIP) ] || curl -sSf -o in/$(basename $CLIP) "$CLIP"
for f in ${ID}_hook.png ${ID}_pay.png ${ID}.mp3 end_${LG}.png; do [ -f in/$f ] || curl -sSf -o in/$f "$R/$f"; done
ffmpeg -nostdin -v error -y -i in/$(basename $CLIP) -loop 1 -i in/${ID}_hook.png -loop 1 -i in/${ID}_pay.png -loop 1 -i in/end_${LG}.png -i in/${ID}.mp3 \
 -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,trim=0:6,setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=3.6,split[a][b];\
[b]boxblur=24:2,eq=brightness=-0.28:saturation=0.7[bb];[a][bb]overlay=enable='gte(t,6)'[c];\
[c][1:v]overlay=enable='lt(t,3.2)'[d];[d][2:v]overlay=enable='between(t,3.2,6)'[e];[e][3:v]overlay=enable='gte(t,6.1)',trim=0:9.6[v];\
[4:a]atrim=0:9.6,afade=in:d=0.15,afade=out:st=8.8:d=0.8[au]" \
 -map "[v]" -map "[au]" -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart -t 9.6 out/${ID}.mp4

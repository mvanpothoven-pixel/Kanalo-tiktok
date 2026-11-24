#!/bin/bash
# Runs in the Higgsfield sandbox (cloudfront is blocked from the Claude workspace).
# creator_compose.sh ID CLIP_URL LANG -> out/ID.mp4 : 8 s talking AI creator (+hook card) + 4 s real app demo + 2.5 s end card; voice + music bed
set -e
ID=$1; CLIP=$2; LG=$3; R=https://raw.githubusercontent.com/mvanpothoven-pixel/Kanalo-tiktok/main/pub
mkdir -p in out
C=in/$(basename $CLIP); [ -f $C ] || curl -sSf -o $C "$CLIP"
for f in creator/demo_$LG.mp4 creator/hook_$LG.png creator/music_$LG.mp3 fun/end_$LG.png; do b=in/$(basename $f); [ -f $b ] || curl -sSf -o $b "$R/$f"; done
ffmpeg -nostdin -v error -y -i $C -i in/demo_$LG.mp4 -loop 1 -i in/hook_$LG.png -loop 1 -i in/end_$LG.png -i in/music_$LG.mp3 -filter_complex "\
[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,trim=0:8,setpts=PTS-STARTPTS[c];[c][2:v]overlay=shortest=1[c2];\
[1:v]fps=30,setsar=1,tpad=stop_mode=clone:stop_duration=2.5,split[d][e];[e]boxblur=24:2,eq=brightness=-0.3:saturation=0.7[eb];\
[d][eb]overlay=enable='gte(t,4)'[d2];[d2][3:v]overlay=enable='gte(t,4.1)':shortest=1,trim=0:6.5,setpts=PTS-STARTPTS[d3];\
[c2][d3]concat=n=2:v=1:a=0[v];\
[0:a]atrim=0:8,asetpts=PTS-STARTPTS,apad=whole_dur=14.5[va];\
[4:a]atrim=0:14.5,asetpts=PTS-STARTPTS,volume='if(lt(t,7.8),0.13,0.9)':eval=frame[ma];\
[va][ma]amix=inputs=2:normalize=0:duration=first,afade=out:st=13.6:d=0.9[au]" \
 -map "[v]" -map "[au]" -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart -t 14.5 out/$ID.mp4

---
name: whisper-ffmpeg
description: Transcribe speech to subtitles with Whisper (faster-whisper, Python) and cut, convert or burn subtitles into video with FFmpeg. Use for any montage task on files in Монтаж/Исходники.
---

# Whisper + FFmpeg

Setup (once per session): `pip3 install -r requirements.txt`. FFmpeg and Python 3 are preinstalled.
Whisper models download from huggingface.co, so that host must be allowed by the network.

## Transcribe to SRT

```bash
python3 scripts/transcribe.py Монтаж/Исходники/video.mp4 --model small --lang kk
```

Writes `video.srt` next to the input. Language codes: `kk` Kazakh, `ru` Russian, omit for auto.

## Common FFmpeg recipes

- Extract audio: `ffmpeg -i in.mp4 -vn -ac 1 -ar 16000 audio.wav`
- Cut: `ffmpeg -ss 00:00:05 -to 00:00:20 -i in.mp4 -c copy out.mp4`
- Vertical 9:16: `ffmpeg -i in.mp4 -vf "crop=ih*9/16:ih,scale=1080:1920" out.mp4`
- Burn subtitles: `ffmpeg -i in.mp4 -vf subtitles=in.srt out.mp4`

Finished videos go to `Монтаж/Готовые`.

# erxan-3d

Video montage workspace.

- `Монтаж/Исходники` — source footage, `Монтаж/Референсы` — references, `Монтаж/Готовые` — finished videos.
- `3D/` — 3D program (separate session; video work stays in `Монтаж`).

## Tools and skills (`.claude/skills`)

| Tool | Skill |
|---|---|
| HyperFrames (HTML → MP4, `npx hyperframes`) | `hyperframes`, `hyperframes-cli`, `hyperframes-registry`, `media-use`, … |
| Remotion (React → MP4, `npx remotion`) | `remotion-best-practices` (router), `remotion-create`, `remotion-render`, … |
| Whisper (faster-whisper) | `whisper-ffmpeg`, `scripts/transcribe.py` |
| FFmpeg | `whisper-ffmpeg` |
| yt-dlp (video download from a link) | `yt-dlp "<link>" -o "Монтаж/Исходники/%(title)s.%(ext)s"` |
| Python 3 | `pip3 install -r requirements.txt` |

Remotion needs a paid company license for some businesses; see the `remotion-license` skill.

## Montage rules (from the user)

- Subtitles and cards always in the lower part of the frame; never over the face or the main subject.
- No black-and-white sections; no top progress bar; no "блог" header.
- Keep the ending of the speaker's last sentence and what it shows.
- Add background music (ducked under the voice) and card sound effects (`scripts/audio_fx.py`).
- Length: aim for 30–60 s (the user finds 15–25 s reels too short). If the footage is shorter, say so and ask for more clips rather than padding; keep natural pauses shorter than 0.3 s instead of cutting everything.
- Synthesised music is a fallback; always also offer a no-music version (user adds a trending Instagram track) with the original sound kept clear.
- Never keep off-topic talk or swearing from the background; mute it.
- Whenever the user states a new preference, add it to this list.

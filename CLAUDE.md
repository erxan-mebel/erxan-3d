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
| Python 3 | `pip3 install -r requirements.txt` |

Remotion needs a paid company license for some businesses; see the `remotion-license` skill.

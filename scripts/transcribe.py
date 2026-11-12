"""Transcribe an audio/video file to an .srt subtitle file with faster-whisper."""
import argparse
import subprocess
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel


def ts(t: float) -> str:
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def load_audio(path: str) -> np.ndarray:
    """Decode any audio/video file to 16 kHz mono float32 with FFmpeg."""
    raw = subprocess.run(
        ["ffmpeg", "-nostdin", "-loglevel", "error", "-i", path,
         "-vn", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
        check=True, capture_output=True,
    ).stdout
    return np.frombuffer(raw, dtype=np.float32)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("--model", default="small")
    p.add_argument("--lang", default=None)
    a = p.parse_args()

    model = WhisperModel(a.model, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(load_audio(a.input), language=a.lang, vad_filter=True)
    out = Path(a.input).with_suffix(".srt")
    with out.open("w", encoding="utf-8") as f:
        for i, s in enumerate(segments, 1):
            f.write(f"{i}\n{ts(s.start)} --> {ts(s.end)}\n{s.text.strip()}\n\n")
    print(out)


if __name__ == "__main__":
    main()

"""Kazakh voiceover for reel 07 with Piper (ISSAI voices). Numbers are spelled out for the TTS."""
import json, subprocess, sys, wave
from pathlib import Path
from piper import PiperVoice, SynthesisConfig

SPEAKER = int(sys.argv[1]) if len(sys.argv) > 1 else 1
LINES = [
 (0.3, 3.3, "Қымбат деп ойлаған жиһазыңыз шын мәнінде арзанға түседі."),
 (3.4, 6.0, "Ал арзан деп алғаныңыз — қымбатқа."),
 (6.1, 9.0, "Сенбейсіз бе? Соңына дейін көріңіз."),
 (9.2, 12.0, "Мына екі стол сырттай бірдей."),
 (12.1, 15.0, "Бірақ біреуі екі есе қымбат."),
 (15.1, 17.4, "Бұл ақша қайда кетеді?"),
 (17.6, 20.0, "Бірінші айырма — плитада."),
 (20.1, 23.0, "Тығыз плита ылғалдан ісінбейді."),
 (23.1, 27.4, "Оған бұралған бұрандалар жылдар өтсе де босамайды."),
 (27.6, 31.0, "Сосын кромка — жиһаздың шетіне жапсырылатын лента."),
 (31.1, 33.6, "Қалың кромка соққыға шыдайды."),
 (33.7, 36.8, "Жұқасы әдетте бірінші болып көшеді."),
 (37.0, 41.0, "Тартпалар мен есіктер мыңдаған рет ашылып-жабылады."),
 (41.1, 44.6, "Бұл жүкті сапалы рельстер мен петлялар көтереді."),
 (44.7, 47.6, "Арзандары тез бұзылады."),
 (47.8, 50.2, "Ең соңғысы — шебердің еңбегі."),
 (50.3, 53.6, "Әр деталь миллиметрге дейін дәл кесілсе,"),
 (53.7, 57.6, "есіктер тегіс жабылады, бұрыштар бірдей шығады."),
 (57.8, 60.2, "Енді екі жыл өтті делік."),
 (60.3, 62.8, "Арзан стол мына күйге келеді."),
 (62.9, 65.8, "Сапалысы — бірінші күндегідей."),
 (66.0, 68.4, "Енді есептейік."),
 (68.5, 71.6, "Арзан стол екі жылда істен шықты —"),
 (71.7, 74.6, "жылына қырық бес мың теңгеге түсті."),
 (74.7, 78.6, "Сапалы стол он жыл қызмет етеді — жылына он сегіз мың теңге."),
 (78.7, 81.8, "Он жылда арзан столды бес рет ауыстырасыз —"),
 (81.9, 84.4, "төрт жүз елу мың теңге жұмсайсыз."),
 (84.5, 87.6, "Сапалысы жүз сексен мың теңге — бір-ақ рет алынады."),
 (87.8, 90.8, "Қайсысы арзан екенін енді өзіңіз көрдіңіз."),
 (90.9, 94.8, "Директке өлшеміңізді жазыңыз — бағасын есептеп береміз."),
]
TOTAL = 96.0
out = Path("parts"); out.mkdir(exist_ok=True)
v = PiperVoice.load("kk_KZ-issai-high.onnx")
cfg = SynthesisConfig(speaker_id=SPEAKER, length_scale=0.95)
inputs, filt, report = [], [], []
for i, (s, e, t) in enumerate(LINES):
    p = out / f"l{i:02}.wav"
    with wave.open(str(p), "wb") as w:
        v.synthesize_wav(t, w, syn_config=cfg)
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]))
    slot = (LINES[i + 1][0] if i + 1 < len(LINES) else TOTAL) - s - 0.05
    tempo = max(1.0, d / slot)
    report.append((i, round(d, 2), round(slot, 2), round(tempo, 2)))
    inputs += ["-i", str(p)]
    chain = f"[{i}:a]aresample=48000,silenceremove=start_periods=1:start_threshold=-45dB"
    if tempo > 1.0:
        chain += f",atempo={min(tempo, 2.0):.3f}"
    chain += f",adelay={int(s * 1000)}|{int(s * 1000)}[a{i}]"
    filt.append(chain)
mix = ";".join(filt) + ";" + "".join(f"[a{i}]" for i in range(len(LINES))) + f"amix=inputs={len(LINES)}:normalize=0,apad=whole_dur={TOTAL},atrim=0:{TOTAL}," \
      "highpass=f=70,equalizer=f=3000:t=q:w=1.5:g=2,acompressor=threshold=-20dB:ratio=3:makeup=2,loudnorm=I=-15:TP=-1.5[out]"
subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", mix, "-map", "[out]", "-ac", "2", "voice.wav"], check=True)
for r in report:
    if r[3] > 1.0: print("sped up", r)
print("voice.wav ready")

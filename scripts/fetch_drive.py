"""Download a publicly shared Google Drive file into Монтаж/Исходники.

Usage: python3 scripts/fetch_drive.py "<drive share link>" [output name]
The file must be shared as "Anyone with the link".
"""
import re
import shutil
import sys
import urllib.request
from pathlib import Path


def file_id(link: str) -> str:
    m = re.search(r"/d/([\w-]{20,})", link) or re.search(r"[?&]id=([\w-]{20,})", link)
    if not m:
        sys.exit(f"Could not find a file id in: {link}")
    return m.group(1)


def main() -> None:
    fid = file_id(sys.argv[1])
    url = f"https://drive.usercontent.google.com/download?id={fid}&export=download&confirm=t"
    with urllib.request.urlopen(url) as r:
        if "text/html" in r.headers.get("Content-Type", ""):
            sys.exit("Drive returned a web page, not the file: set sharing to 'Anyone with the link'.")
        name = sys.argv[2] if len(sys.argv) > 2 else None
        if not name:
            m = re.search(r'filename="?([^";]+)', r.headers.get("Content-Disposition", ""))
            name = m.group(1) if m else f"{fid}.mp4"
        out = Path("Монтаж/Исходники") / Path(name).name
        with out.open("wb") as f:
            shutil.copyfileobj(r, f, 1 << 20)
    print(f"{out} {out.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()

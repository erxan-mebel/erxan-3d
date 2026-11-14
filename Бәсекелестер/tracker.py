"""Competitor reels tracker for Erxan Mebel.

Reads Instagram usernames from competitors.txt, pulls their recent posts through the official
Instagram Graph API (Business Discovery), flags posts that perform far above the account's usual
level, and writes a report (report.html + report.md) plus a history file.

Auth: the token is never stored here. In the cloud session the network proxy adds
"Authorization: Bearer <token>" to requests for graph.facebook.com; locally you can set IG_TOKEN.

Environment:
  IG_USER_ID      your own Instagram professional account id (required)
  IG_TOKEN        optional, only when the proxy does not inject the token
  GRAPH_VERSION   default v27.0

Usage:
  python3 Бәсекелестер/tracker.py           # real run
  python3 Бәсекелестер/tracker.py --demo    # sample data, to see the report format
"""
import html
import json
import os
import statistics
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE / "data"
VIRAL_X = 3.0          # post counts as "атып кетті" at 3x the account's median engagement
MIN_SCORE = 50         # ignore tiny accounts' noise
FIELDS = ("followers_count,media_count,"
          "media.limit(50){id,caption,like_count,comments_count,media_type,media_product_type,permalink,timestamp}")


def load_competitors():
    names = []
    for line in (HERE / "competitors.txt").read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip().lstrip("@")
        if line:
            names.append(line)
    return names


def fetch(username):
    ver = os.environ.get("GRAPH_VERSION", "v27.0")
    uid = os.environ.get("IG_USER_ID", "17841462847161597")  # @erxan_mebel
    q = urllib.parse.urlencode({"fields": f"business_discovery.username({username}){{{FIELDS}}}"})
    req = urllib.request.Request(f"https://graph.facebook.com/{ver}/{uid}?{q}")
    req.add_header("Authorization", f"Bearer {os.environ.get('IG_TOKEN', 'proxy-injects-token')}")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["business_discovery"]


def demo(username, k):
    import random
    rnd = random.Random(k)
    media = []
    for i in range(30):
        likes = int(rnd.lognormvariate(4.5, 0.6))
        if i in (3, 17):
            likes *= 8
        media.append({"id": f"{k}{i}", "caption": f"DEMO пост {i}", "like_count": likes,
                      "comments_count": likes // 15, "media_product_type": "REELS",
                      "permalink": "https://www.instagram.com/", "timestamp": f"2026-10-{1 + i % 28:02d}T10:00:00+0000"})
    return {"followers_count": 5000 + 1000 * k, "media_count": 300, "media": {"data": media}}


def score(m):
    return (m.get("like_count") or 0) + 3 * (m.get("comments_count") or 0)


def analyse(username, info):
    posts = info.get("media", {}).get("data", [])
    scores = [score(m) for m in posts] or [0]
    med = statistics.median(scores) or 1
    rows = []
    for m in posts:
        s = score(m)
        rows.append({"account": username, "followers": info.get("followers_count"), "score": s,
                     "x": round(s / med, 1), "likes": m.get("like_count"), "comments": m.get("comments_count"),
                     "type": m.get("media_product_type") or m.get("media_type"), "url": m.get("permalink"),
                     "date": (m.get("timestamp") or "")[:10], "caption": (m.get("caption") or "").strip()[:140],
                     "viral": s >= MIN_SCORE and s / med >= VIRAL_X})
    return rows, med


def write_report(rows, meds, errors, stamp, is_demo):
    viral = sorted((r for r in rows if r["viral"]), key=lambda r: -r["x"])
    top = sorted(rows, key=lambda r: -r["score"])[:20]
    title = "Бәсекелестер: атып кеткен видеолар" + (" (DEMO)" if is_demo else "")
    md = [f"# {title}", f"_Жаңартылды: {stamp}_", "",
          f"«Атып кетті» = аккаунттың әдеттегі деңгейінен {VIRAL_X:g} есе жоғары (лайк + 3×пікір).", "",
          "| Аккаунт | Күні | Түрі | Лайк | Пікір | Әдеттегіден | Сілтеме | Мәтіні |", "|---|---|---|---|---|---|---|---|"]
    for r in viral:
        md.append(f"| @{r['account']} | {r['date']} | {r['type']} | {r['likes']} | {r['comments']} | ×{r['x']} | "
                  f"[ашу]({r['url']}) | {r['caption'].replace('|', '/').replace(chr(10), ' ')} |")
    if errors:
        md += ["", "## Қате шыққан аккаунттар"] + [f"- @{u}: {e}" for u, e in errors]
    (HERE / "report.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    def tr(r):
        return (f"<tr><td>@{html.escape(r['account'])}</td><td>{r['date']}</td><td>{r['type']}</td>"
                f"<td>{r['likes']}</td><td>{r['comments']}</td><td><b>×{r['x']}</b></td>"
                f"<td><a href='{html.escape(r['url'] or '')}'>ашу</a></td><td>{html.escape(r['caption'])}</td></tr>")
    head = "<tr><th>Аккаунт</th><th>Күні</th><th>Түрі</th><th>Лайк</th><th>Пікір</th><th>Әдеттегіден</th><th></th><th>Мәтіні</th></tr>"
    page = f"""<!doctype html><html lang="kk"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>
body{{font-family:Inter,system-ui,sans-serif;margin:16px;background:#faf7f4;color:#1d1d1f}}h1{{color:#b8653d;font-size:22px}}
table{{border-collapse:collapse;width:100%;font-size:14px;background:#fff}}th,td{{padding:6px 8px;border-bottom:1px solid #eee;text-align:left;vertical-align:top}}
th{{background:#d9825b;color:#fff}}.wrap{{overflow-x:auto}}</style></head><body>
<h1>🔥 {title}</h1><p>Жаңартылды: {stamp}. «Атып кетті» = аккаунттың әдеттегі деңгейінен {VIRAL_X:g} есе жоғары.</p>
<div class="wrap"><table>{head}{''.join(tr(r) for r in viral) or '<tr><td colspan=8>Әзірге жоқ</td></tr>'}</table></div>
<h2>Ең көп жинаған 20 пост</h2><div class="wrap"><table>{head}{''.join(tr(r) for r in top)}</table></div>
{'<h2>Қате</h2><ul>' + ''.join(f'<li>@{html.escape(u)}: {html.escape(e)}</li>' for u, e in errors) + '</ul>' if errors else ''}
</body></html>"""
    (HERE / "report.html").write_text(page, encoding="utf-8")
    return viral


def main():
    is_demo = "--demo" in sys.argv
    DATA.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    rows, meds, errors = [], {}, []
    for k, user in enumerate(load_competitors()):
        try:
            info = demo(user, k) if is_demo else fetch(user)
            r, med = analyse(user, info)
            rows += r
            meds[user] = med
        except Exception as e:  # keep going for the other accounts
            errors.append((user, str(e)[:200]))
    if not is_demo:
        with (DATA / "history.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps({"at": stamp, "rows": rows}, ensure_ascii=False) + "\n")
    viral = write_report(rows, meds, errors, stamp, is_demo)
    print(f"{len(rows)} posts, {len(viral)} viral, {len(errors)} errors -> {HERE / 'report.html'}")


if __name__ == "__main__":
    main()

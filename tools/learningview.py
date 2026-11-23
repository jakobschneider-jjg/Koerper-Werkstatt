#!/usr/bin/env python3
"""Baut die LearningView-Fassung der Körper-Werkstatt mit eingebetteten Gebärdenvideos.

Aufruf: python3 tools/learningview.py <Ordner mit 1.mp4 … 9.mp4 (Reihenfolge wie Drehliste)> <Zieldatei.html>
Die Videos werden auf 640 × 360 ohne Ton verkleinert (ffmpeg) und als Daten in die Datei geschrieben.
Videos und die gebaute Datei gehören NICHT in dieses öffentliche Repository.
"""
import base64, glob, os, re, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src, out = sys.argv[1], sys.argv[2]
html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
data = []
with tempfile.TemporaryDirectory() as t:
    for i in range(1, 10):
        f = [p for p in glob.glob(os.path.join(src, "*")) if re.fullmatch(r"0?%d(\D.*)?\.(mp4|mov|m4v)" % i, os.path.basename(p), re.I)]
        if len(f) != 1: sys.exit("Video %d nicht eindeutig gefunden: %s" % (i, f))
        o = os.path.join(t, "%d.mp4" % i)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f[0], "-an", "-vf", "scale=640:360:flags=lanczos,fps=30",
                        "-c:v", "libx264", "-profile:v", "main", "-level", "3.1", "-pix_fmt", "yuv420p", "-preset", "slow",
                        "-crf", "26", "-movflags", "+faststart", o], check=True)
        data.append("data:video/mp4;base64," + base64.b64encode(open(o, "rb").read()).decode())
js = "<script>/* Gebärdenvideos V01–V09, eingebettet */\nconst VIDLOCAL=[\n" + ",\n".join('"%s"' % d for d in data) + "];\n</script>\n"
i = html.index("<script>")
html = html[:i] + js + html[i:]
open(out, "w", encoding="utf-8").write(html)
print("Gebaut:", out, "(%.1f MB)" % (len(html.encode()) / 1e6))

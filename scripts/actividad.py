"""Rellena el bloque de actividad del README (entre las marcas ACTIVIDAD) con datos públicos de GitHub."""
import json
import os
import re
import urllib.request
from datetime import datetime

USUARIO = "JOFLEY"
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def api(ruta):
    req = urllib.request.Request(f"https://api.github.com/{ruta}", headers={"Accept": "application/vnd.github+json"})
    token = os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def fecha(iso):
    d = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return f"{d.day} {MESES[d.month - 1]} {d.year}"


def lineas():
    out = []
    for rel in api("repos/JOFLEY/nido-releases/releases?per_page=3"):
        if rel.get("draft"):
            continue
        out.append(f"🪺 Nido **{rel['tag_name']}** publicado · [{fecha(rel['published_at'])}]({rel['html_url']})")

    vistos = set()
    for ev in api(f"users/{USUARIO}/events/public?per_page=30"):
        repo = ev["repo"]["name"]
        if repo == f"{USUARIO}/{USUARIO}" or ev["type"] not in ("PushEvent", "CreateEvent", "PublicEvent"):
            continue
        clave = (ev["type"], repo)
        if clave in vistos:
            continue
        vistos.add(clave)
        enlace = f"[{repo.split('/')[1]}](https://github.com/{repo})"
        if ev["type"] == "PushEvent":
            out.append(f"🔨 Cambios en {enlace} · {fecha(ev['created_at'])}")
        elif ev["type"] == "PublicEvent":
            out.append(f"🌱 Ahora es público: {enlace} · {fecha(ev['created_at'])}")
        elif ev["payload"].get("ref_type") == "repository":
            out.append(f"✨ Nuevo repositorio: {enlace} · {fecha(ev['created_at'])}")
        if len(out) >= 6:
            break
    return out[:6]


def main():
    readme = open("README.md", encoding="utf-8").read()
    cuerpo = "\n".join(f"- {l}" for l in lineas()) or "- Trabajando en algo nuevo… 🛠️"
    nuevo = re.sub(
        r"(<!--ACTIVIDAD:inicio-->\n).*?(\n<!--ACTIVIDAD:fin-->)",
        lambda m: m.group(1) + cuerpo + m.group(2),
        readme,
        flags=re.S,
    )
    open("README.md", "w", encoding="utf-8", newline="\n").write(nuevo)


if __name__ == "__main__":
    main()

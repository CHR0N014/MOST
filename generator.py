#!/usr/bin/env python3
"""Gera o site estatico a partir de data/topics.json.

Uso:
    python3 generator.py

Le data/topics.json, escreve as paginas em pages/ e o index.html, sitemap.xml
e robots.txt na raiz. O site resultante e 100% estatico, pronto para GitHub Pages.
"""
import json
import html
import pathlib
import datetime

ROOT = pathlib.Path(__file__).resolve().parent
DATA = ROOT / "data" / "topics.json"
OUT = ROOT / "pages"
ADS = ROOT / "data" / "ads.txt"

E = lambda s: html.escape(str(s), quote=True)

HEAD = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{base}/{slug}.html">
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<header class="site">
  <div class="wrap">
    <a class="brand" href="../index.html">{site}</a>
    <nav>
      <a href="../index.html">Inicio</a>
      <a href="../sobre.html">Sobre</a>
      <a href="../contato.html">Contato</a>
      <a href="../ferramentas.html">Ferramentas</a>
    </nav>
  </div>
</header>
<main class="wrap">
"""

FOOT = """</main>
<footer class="site">
  <div class="wrap">
    <p>&copy; {year} {site} &mdash; <a href="../sobre.html">Sobre</a> &middot; <a href="../contato.html">Contato</a> &middot; <a href="../privacidade.html">Privacidade</a> &middot; <a href="../termos.html">Termos</a></p>
  </div>
</footer>
</body>
</html>
"""

AD_BLOCK = """<div class="ad-slot">{ad}</div>"""


def read_ads():
    if ADS.exists():
        return ADS.read_text(encoding="utf-8").strip()
    return "Publicidade"


def render_topic(site, t, ad_html):
    base = site["base_url"].rstrip("/")
    slug = t["slug"]
    out = [HEAD.format(
        lang=site["lang"], site=E(site["name"]), title=E(t["title"] + " | " + site["name"]),
        desc=E(t["description"]), base=E(base), slug=E(slug),
    )]
    out.append('<article>')
    out.append(f'<div class="tag">{E(t["category"])}</div>')
    out.append(f'<h1>{E(t["title"])}</h1>')
    out.append(f'<p class="muted">Atualizado em <time datetime="{datetime.date.today().isoformat()}">{datetime.date.today().strftime("%d/%m/%Y")}</time></p>')
    out.append(f'<p>{E(t["intro"])}</p>')
    out.append(AD_BLOCK.format(ad=ad_html))
    for i, sec in enumerate(t["sections"]):
        out.append(f'<h2>{E(sec["h"])}</h2>')
        for p in sec["p"]:
            out.append(f'<p>{E(p)}</p>')
        if i == 1:
            out.append(AD_BLOCK.format(ad=ad_html))
    if t.get("faq"):
        out.append('<h2>Perguntas frequentes</h2>')
        for item in t["faq"]:
            out.append(f'<h3>{E(item["q"])}</h3>')
            out.append(f'<p>{E(item["a"])}</p>')
    out.append('</article>')
    out.append(FOOT.format(year=datetime.date.today().year, site=E(site["name"])))
    return "\n".join(out)


def render_index(site, topics):
    base = site["base_url"].rstrip("/")
    cards = []
    cards.append(
        '    <div class="card">\n'
        '      <div class="tag">Ferramenta</div>\n'
        '      <h3 class="post-title"><a href="calculadora-juros-compostos.html">Simulador de juros compostos</a></h3>\n'
        '      <p class="muted">Calcule quanto o seu dinheiro rende com aportes mensais. Resultado na hora.</p>\n'
        '    </div>'
    )
    for t in topics:
        cards.append(
            f'    <div class="card">\n'
            f'      <div class="tag">{E(t["category"])}</div>\n'
            f'      <h3 class="post-title"><a href="pages/{E(t["slug"])}.html">{E(t["title"])}</a></h3>\n'
            f'      <p class="muted">{E(t["description"])}</p>\n'
            f'    </div>'
        )
    body = f"""<!DOCTYPE html>
<html lang="{site["lang"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(site["name"])} &mdash; {E(site["tagline"])}</title>
<meta name="description" content="{E(site["tagline"])}. Guias praticos de financas pessoais.">
<link rel="canonical" href="{E(base)}/">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="site">
  <div class="wrap">
    <a class="brand" href="index.html">{E(site["name"])}</a>
    <nav>
      <a href="index.html">Inicio</a>
      <a href="sobre.html">Sobre</a>
      <a href="contato.html">Contato</a>
      <a href="ferramentas.html">Ferramentas</a>
    </nav>
  </div>
</header>
<main class="wrap">
  <h1>{E(site["tagline"])}</h1>
  <p class="muted">Guias diretos para organizar o dinheiro, sair de dividas e comecar a investir.</p>
  <div class="ad-slot">{E(read_ads())}</div>
  <h2>Guias</h2>
  <div class="grid">
{chr(10).join(cards)}
  </div>
</main>
<footer class="site">
  <div class="wrap">
    <p>&copy; {datetime.date.today().year} {E(site["name"])} &mdash; <a href="sobre.html">Sobre</a> &middot; <a href="contato.html">Contato</a> &middot; <a href="privacidade.html">Privacidade</a> &middot; <a href="termos.html">Termos</a></p>
  </div>
</footer>
</body>
</html>
"""
    return body


def render_sitemap(site, topics):
    base = site["base_url"].rstrip("/")
    urls = [f"{base}/", f"{base}/sobre.html", f"{base}/contato.html",
            f"{base}/privacidade.html", f"{base}/termos.html",
            f"{base}/ferramentas.html", f"{base}/calculadora-juros-compostos.html"]
    urls += [f"{base}/pages/{t['slug']}.html" for t in topics]
    items = "\n".join(f"  <url><loc>{E(u)}</loc></url>" for u in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{items}\n</urlset>\n'


def render_robots(site):
    base = site["base_url"].rstrip("/")
    return f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n"


def main():
    cfg = json.loads(DATA.read_text(encoding="utf-8"))
    site = cfg["site"]
    topics = cfg["topics"]
    OUT.mkdir(exist_ok=True)
    ad_html = read_ads()

    for t in topics:
        (OUT / f"{t['slug']}.html").write_text(render_topic(site, t, ad_html), encoding="utf-8")
    (ROOT / "index.html").write_text(render_index(site, topics), encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(render_sitemap(site, topics), encoding="utf-8")
    (ROOT / "robots.txt").write_text(render_robots(site), encoding="utf-8")
    print(f"Gerado: {len(topics)} paginas + index + sitemap + robots")


if __name__ == "__main__":
    main()

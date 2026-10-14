#!/usr/bin/env python3
"""Gera o site estatico a partir dos arquivos data/topics*.json.

Uso:
    python3 generator.py

Escreve as paginas em pages/ e o index.html, sitemap.xml e robots.txt na raiz.
Site 100% estatico, pronto para GitHub Pages.
"""
import json
import html
import glob
import pathlib
import datetime

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "pages"
ADS = ROOT / "data" / "ads.txt"
AFFILIATES = ROOT / "data" / "affiliates.json"

E = lambda s: html.escape(str(s), quote=True)

HEAD = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{base}/{slug}.html">
<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<link rel="stylesheet" href="../assets/style.css">
<link rel="alternate" type="application/rss+xml" title="Feed" href="../feed.xml">
<script type="application/ld+json">{schema}</script>
</head>
<body>
<header class="site">
  <div class="wrap">
    <a class="brand" href="../index.html">{site}</a>
    <nav>
      <a href="../index.html">Inicio</a>
      <a href="../ferramentas.html">Ferramentas</a>
      <a href="../sobre.html">Sobre</a>
      <a href="../contato.html">Contato</a>
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


def read_ads():
    if ADS.exists():
        return ADS.read_text(encoding="utf-8").strip()
    return "Publicidade"


def read_affiliates():
    if AFFILIATES.exists():
        return json.loads(AFFILIATES.read_text(encoding="utf-8"))
    return {}


def load_topics():
    topics = []
    for path in sorted(glob.glob(str(ROOT / "data" / "topics*.json"))):
        data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
        topics.extend(data["topics"])
    return topics


def schema_for(site, t):
    base = site["base_url"].rstrip("/")
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Article",
                "headline": t["title"],
                "description": t["description"],
                "inLanguage": site["lang"],
                "mainEntityOfPage": f"{base}/pages/{t['slug']}.html",
            }
        ],
    }
    if t.get("faq"):
        graph["@graph"].append({
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": f["q"],
                 "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
                for f in t["faq"]
            ],
        })
    return json.dumps(graph, ensure_ascii=False, separators=(",", ":"))


def related_for(topics, t):
    same = [x for x in topics if x["category"] == t["category"] and x["slug"] != t["slug"]]
    others = [x for x in topics if x["category"] != t["category"] and x["slug"] != t["slug"]]
    return (same + others)[:4]


def render_topic(site, topics, t, ad_html, affiliates):
    base = site["base_url"].rstrip("/")
    out = [HEAD.format(
        lang=site["lang"], site=E(site["name"]), title=E(t["title"] + " | " + site["name"]),
        desc=E(t["description"]), base=E(base), slug=E(t["slug"]),
        schema=schema_for(site, t),
    )]
    out.append('<article>')
    out.append(f'<div class="tag"><a href="../categoria/{slugify(t["category"])}.html">{E(t["category"])}</a></div>')
    out.append(f'<h1>{E(t["title"])}</h1>')
    out.append(f'<p class="muted">Atualizado em <time datetime="{datetime.date.today().isoformat()}">{datetime.date.today().strftime("%d/%m/%Y")}</time></p>')
    out.append(f'<p>{E(t["intro"])}</p>')
    out.append(f'<div class="ad-slot">{ad_html}</div>')
    for i, sec in enumerate(t["sections"]):
        out.append(f'<h2>{E(sec["h"])}</h2>')
        for p in sec["p"]:
            out.append(f'<p>{E(p)}</p>')
    if t.get("faq"):
        out.append('<h2>Perguntas frequentes</h2>')
        for item in t["faq"]:
            out.append(f'<h3>{E(item["q"])}</h3>')
            out.append(f'<p>{E(item["a"])}</p>')
    box = affiliates.get(t["category"])
    if box:
        out.append('<aside class="recs">')
        out.append(f'<h2>{E(box["title"])}</h2>')
        for r in box["items"]:
            out.append(f'<p><a href="{E(r["url"])}" rel="nofollow sponsored">{E(r["label"])}</a> &mdash; {E(r["note"])}</p>')
        out.append('<p class="muted small">Alguns links podem gerar comissao. Isso nao altera o preco para voce.</p>')
        out.append('</aside>')
    rel = related_for(topics, t)
    if rel:
        out.append('<h2>Leia tambem</h2>')
        out.append('<ul class="related">')
        for r in rel:
            out.append(f'<li><a href="{E(r["slug"])}.html">{E(r["title"])}</a></li>')
        out.append('</ul>')
    out.append('</article>')
    out.append(FOOT.format(year=datetime.date.today().year, site=E(site["name"])))
    return "\n".join(out)


def slugify(s):
    import unicodedata
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return s.lower().strip().replace(" ", "-")


def render_category(site, cat, topics):
    base = site["base_url"].rstrip("/")
    slug = slugify(cat)
    items = "\n".join(
        f'    <li><a href="../pages/{E(t["slug"])}.html">{E(t["title"])}</a> &mdash; {E(t["description"])}</li>'
        for t in topics
    )
    return f"""<!DOCTYPE html>
<html lang="{site["lang"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(cat)} &mdash; guias | {E(site["name"])}</title>
<meta name="description" content="Guias de {E(cat)} em financas pessoais. {len(topics)} artigos praticos.">
<link rel="canonical" href="{E(base)}/categoria/{E(slug)}.html">
<link rel="stylesheet" href="../assets/style.css">
<link rel="alternate" type="application/rss+xml" title="Feed" href="../feed.xml">
</head>
<body>
<header class="site">
  <div class="wrap">
    <a class="brand" href="../index.html">{E(site["name"])}</a>
    <nav>
      <a href="../index.html">Inicio</a>
      <a href="../ferramentas.html">Ferramentas</a>
      <a href="../sobre.html">Sobre</a>
      <a href="../contato.html">Contato</a>
    </nav>
  </div>
</header>
<main class="wrap">
  <div class="tag">Categoria</div>
  <h1>{E(cat)}</h1>
  <p class="muted">{len(topics)} guias sobre {E(cat)}.</p>
  <ul class="related">
{items}
  </ul>
</main>
<footer class="site">
  <div class="wrap">
    <p>&copy; {datetime.date.today().year} {E(site["name"])} &mdash; <a href="../sobre.html">Sobre</a> &middot; <a href="../contato.html">Contato</a> &middot; <a href="../privacidade.html">Privacidade</a> &middot; <a href="../termos.html">Termos</a></p>
  </div>
</footer>
</body>
</html>
"""




def render_index(site, topics, ad_html):
    base = site["base_url"].rstrip("/")
    cats = sorted({t["category"] for t in topics})
    cats_nav = " &middot; ".join(
        f'<a href="categoria/{slugify(c)}.html">{E(c)}</a>' for c in cats)
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
    return f"""<!DOCTYPE html>
<html lang="{site["lang"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(site["name"])} &mdash; {E(site["tagline"])}</title>
<meta name="description" content="{E(site["tagline"])}. Guias praticos de financas pessoais.">
<link rel="canonical" href="{E(base)}/">
<link rel="stylesheet" href="assets/style.css">
<link rel="alternate" type="application/rss+xml" title="Feed" href="feed.xml">
</head>
<body>
<header class="site">
  <div class="wrap">
    <a class="brand" href="index.html">{E(site["name"])}</a>
    <nav>
      <a href="index.html">Inicio</a>
      <a href="ferramentas.html">Ferramentas</a>
      <a href="sobre.html">Sobre</a>
      <a href="contato.html">Contato</a>
    </nav>
  </div>
</header>
<main class="wrap">
  <h1>{E(site["tagline"])}</h1>
  <p class="muted">Guias diretos para organizar o dinheiro, sair de dividas e comecar a investir.</p>
  <div class="ad-slot">{ad_html}</div>
  <h2>Categorias</h2>
  <p>{cats_nav}</p>
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


def render_sitemap(site, topics):
    base = site["base_url"].rstrip("/")
    urls = [f"{base}/", f"{base}/sobre.html", f"{base}/contato.html",
            f"{base}/privacidade.html", f"{base}/termos.html",
            f"{base}/ferramentas.html", f"{base}/calculadora-juros-compostos.html"]
    urls += [f"{base}/pages/{t['slug']}.html" for t in topics]
    cats = sorted({t["category"] for t in topics})
    urls += [f"{base}/categoria/{slugify(c)}.html" for c in cats]
    items = "\n".join(f"  <url><loc>{E(u)}</loc></url>" for u in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{items}\n</urlset>\n'


def render_feed(site, topics):
    base = site["base_url"].rstrip("/")
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    items = []
    for t in topics:
        items.append(
            f"  <item>\n"
            f"    <title>{E(t['title'])}</title>\n"
            f"    <link>{base}/pages/{E(t['slug'])}.html</link>\n"
            f"    <guid>{base}/pages/{E(t['slug'])}.html</guid>\n"
            f"    <description>{E(t['description'])}</description>\n"
            f"  </item>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0">\n<channel>\n'
        f"  <title>{E(site['name'])}</title>\n"
        f"  <link>{base}/</link>\n"
        f"  <description>{E(site['tagline'])}</description>\n"
        f"  <language>{site['lang']}</language>\n"
        f"  <lastBuildDate>{now}</lastBuildDate>\n"
        + "\n".join(items) + "\n</channel>\n</rss>\n"
    )


def render_robots(site):
    base = site["base_url"].rstrip("/")
    return f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n"


def main():
    site = json.loads((ROOT / "data" / "topics.json").read_text(encoding="utf-8"))["site"]
    topics = load_topics()
    OUT.mkdir(exist_ok=True)
    ad_html = read_ads()
    affiliates = read_affiliates()

    for t in topics:
        (OUT / f"{t['slug']}.html").write_text(
            render_topic(site, topics, t, ad_html, affiliates), encoding="utf-8")
    cats = {}
    for t in topics:
        cats.setdefault(t["category"], []).append(t)
    catdir = ROOT / "categoria"
    catdir.mkdir(exist_ok=True)
    for cat, group in cats.items():
        (catdir / f"{slugify(cat)}.html").write_text(
            render_category(site, cat, group), encoding="utf-8")
    (ROOT / "index.html").write_text(render_index(site, topics, ad_html), encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(render_sitemap(site, topics), encoding="utf-8")
    (ROOT / "robots.txt").write_text(render_robots(site), encoding="utf-8")
    (ROOT / "feed.xml").write_text(render_feed(site, topics), encoding="utf-8")
    print(f"Gerado: {len(topics)} paginas + index + sitemap + robots")


if __name__ == "__main__":
    main()

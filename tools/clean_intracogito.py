#!/usr/bin/env python3
"""Nettoie les éditions Intracogito exportées de Substack vers le gabarit du site.

Usage : python3 tools/clean_intracogito.py <dossier_export_substack> <num> [<num> ...]
  ex.   python3 tools/clean_intracogito.py ~/Downloads/4bVM0I6LSG_PUIGjJiDyog 57 58 59

Écrit, pour chaque édition :
  content/intracogito/<NNN>.html   corps de l'article au gabarit du site
et met à jour content/intracogito/editions.json (métadonnées : titre, date, slug,
image Substack d'origine + légende, nombre de mots...).

Gabarit cible (identique à #066) :
  <p><strong>Réflexion № 01 :</strong></p>
  <blockquote><p>citation</p><p><strong>Auteur</strong></p></blockquote>
  <p><em>~ Entre les lignes :</em></p>
  <blockquote><p>commentaire</p></blockquote>
  <hr/>  (entre deux réflexions)
"""
import csv, glob, json, os, re, sys
from bs4 import BeautifulSoup, NavigableString

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "content", "intracogito")

def clean_author(t):
    t = t.strip()
    t = re.sub(r"^[—–\-]+\s*", "", t)
    t = t.strip().rstrip(".").strip()
    return t

def norm_quote(bq, soup):
    """Retourne (citation, auteur) depuis un blockquote Substack de format variable."""
    for inner in bq.find_all("blockquote"):
        inner.unwrap()
    ps = [p for p in bq.find_all("p") if p.get_text(strip=True)]
    if not ps:
        return None
    last = ps[-1]
    txt_last = last.get_text(" ", strip=True)
    if len(ps) >= 2 and re.match(r"^[—–\-]", txt_last):
        author = clean_author(txt_last)
        quote = " ".join(p.decode_contents().strip() for p in ps[:-1])
        return quote, author
    # citation + <br/> — Auteur dans le même <p>
    html = last.decode_contents()
    m = re.split(r"<br\s*/?>\s*(?:<strong>)?\s*[—–]\s*", html)
    if len(m) == 2:
        quote_last = m[0].strip()
        author = clean_author(BeautifulSoup(m[1], "html.parser").get_text(" ", strip=True))
        quote = " ".join([p.decode_contents().strip() for p in ps[:-1]] + [quote_last])
        return quote, author
    return " ".join(p.decode_contents().strip() for p in ps), ""

def strip_tags_keep_inline(html):
    s = BeautifulSoup(html, "html.parser")
    for a in s.find_all("a"):
        a.unwrap()
    for sp in s.find_all("span"):
        sp.unwrap()
    out = str(s)
    out = re.sub(r"\s+", " ", out).strip()
    return out

def clean(path):
    soup = BeautifulSoup(open(path, encoding="utf-8"), "html.parser")
    cover_url, caption = "", ""
    for c in soup.select(".captioned-image-container"):
        img = c.find("img")
        if img and not cover_url:
            cover_url = img.get("src", "")
            cap = c.find("figcaption")
            caption = cap.get_text(" ", strip=True) if cap else ""
        c.decompose()
    for svg in soup.find_all("svg"):
        svg.decompose()
    parts = []
    stop = False
    elems = [e for e in soup.contents if not (isinstance(e, NavigableString) and not e.strip())]
    for el in elems:
        if stop:
            break
        name = getattr(el, "name", None)
        text = el.get_text(" ", strip=True) if name else str(el).strip()
        if name in ("h1", "h2", "h3", "h4") and ("Aller plus loin" in text or "Merci" in text):
            stop = True; continue
        if text.startswith("✽ Merci") or text.startswith("✹ Aller plus loin"):
            stop = True; continue
        if name == "div" and el.find("hr"):
            if parts and parts[-1] != "<hr/>":
                parts.append("<hr/>")
            continue
        if name == "hr":
            if parts and parts[-1] != "<hr/>":
                parts.append("<hr/>")
            continue
        if name == "p":
            if not text:
                continue
            m = re.match(r"^Réflexion\s*№\s*(\d+)\s*:?$", text)
            if m:
                parts.append(f"<p><strong>Réflexion № {int(m.group(1)):02d} :</strong></p>"); continue
            if re.match(r"^~\s*Entre les lignes\s*:?$", text):
                parts.append("<p><em>~ Entre les lignes :</em></p>"); continue
            parts.append("<p>" + strip_tags_keep_inline(el.decode_contents()) + "</p>"); continue
        if name == "blockquote":
            prev = parts[-1] if parts else ""
            if "Réflexion №" in prev:
                r = norm_quote(el, soup)
                if r:
                    q, a = r
                    q = strip_tags_keep_inline(q)
                    a_html = f"<p><strong>{a}</strong></p>" if a else ""
                    parts.append(f"<blockquote><p>{q}</p>{a_html}</blockquote>")
                continue
            for inner in el.find_all("blockquote"):
                inner.unwrap()
            ps = [strip_tags_keep_inline(p.decode_contents()) for p in el.find_all("p") if p.get_text(strip=True)]
            parts.append("<blockquote>" + "".join(f"<p>{p}</p>" for p in ps) + "</blockquote>"); continue
        if name in ("ul", "ol"):
            parts.append(strip_tags_keep_inline(str(el))); continue
        if name and text:
            parts.append("<p>" + strip_tags_keep_inline(el.decode_contents()) + "</p>")
    while parts and parts[-1] == "<hr/>":
        parts.pop()
    body = "".join(parts)
    body = body.replace("<em>d’Intracogito </em>", "<em>d’Intracogito</em> ")
    body = re.sub(r"\s+</p>", "</p>", body)
    words = len(BeautifulSoup(body, "html.parser").get_text(" ").split())
    n_ref = len(re.findall(r"Réflexion №", body))
    authors = re.findall(r"</p><p><strong>([^<]+)</strong></p></blockquote>", body)
    intro = BeautifulSoup(parts[0], "html.parser").get_text(" ", strip=True) if parts else ""
    return body, cover_url, caption, words, n_ref, authors, intro

def main():
    export = os.path.expanduser(sys.argv[1]); nums = [int(n) for n in sys.argv[2:]]
    rows = {r["post_id"]: r for r in csv.DictReader(open(os.path.join(export, "posts.csv"), encoding="utf-8"))}
    meta_path = os.path.join(OUT, "editions.json")
    meta = json.load(open(meta_path, encoding="utf-8")) if os.path.exists(meta_path) else {}
    os.makedirs(OUT, exist_ok=True)
    # Retrouve chaque édition par son TITRE (« Intracogito #N - ... ») : les noms de
    # fichiers Substack ne suivent pas toujours le numéro (introspectio-1, intracogito-12
    # pour la #13, intracogito-lamour pour la #23...).
    by_num = {}
    for pid, r in rows.items():
        m = re.match(r"^\s*Intracogito\s*#\s*(\d+)\s*-", r.get("title", ""))
        if m and r.get("is_published") == "true":
            by_num[int(m.group(1))] = pid
    for n in nums:
        post_id = by_num.get(n)
        f = os.path.join(export, "posts", f"{post_id}.html") if post_id else None
        if not f or not os.path.exists(f):
            print(f"#{n}: introuvable"); continue
        row = rows[post_id]
        slug = re.sub(r"^\d+\.(?:intracogito|introspectio)-(?:\d+-)?", "", post_id)
        # slug déjà pris par une autre édition -> suffixe avec le numéro
        if any(v.get("slug") == slug and v.get("num") != n for v in meta.values() if v):
            slug = f"{slug}-{n}"
        title = re.sub(r"^\s*Intracogito\s*#\s*\d+\s*-\s*", "", row.get("title", "")).strip()
        body, cover_url, caption, words, n_ref, authors, intro = clean(f)
        open(os.path.join(OUT, f"{n:03d}.html"), "w", encoding="utf-8").write(body)
        meta[f"{n:03d}"] = {
            "num": n, "title": title, "slug": slug, "date": row.get("post_date", "")[:10],
            "substack_cover_url": cover_url, "cover_caption": caption,
            "words": words, "reflexions": n_ref, "authors": authors, "intro": intro,
        }
        print(f"#{n:03d} {title!r} {meta[f'{n:03d}']['date']} slug={slug} réflexions={n_ref} mots={words} auteurs={authors} | image: {caption}")
    json.dump(dict(sorted(meta.items())), open(meta_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()

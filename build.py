#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Assemble toutes les pages du site Intracogito V1 (structure vide, DA aeon-style)
à partir de fragments partagés, avec balises SEO completes par page.
"""
import os
import json, re

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_URL = "https://intracogito.vercel.app"

IMG_DIMENSIONS = {
    "assets/img/cogito-001-cover.jpg": (1600, 817),
    "assets/img/intracogito-66-cover.jpg": (1200, 627),
    "assets/img/author-elouan.jpg": (300, 300),
    "assets/img/cogito-001-fig1-voyage-of-life.jpg": (900, 592),
    "assets/img/cogito-001-fig2-developpement-limite.jpg": (900, 625),
    "assets/img/cogito-001-fig3-ecole-athenes.jpg": (900, 496),
    "assets/img/vitruvian-man.jpg": (700, 700),
    "assets/img/cogito-002-cover.jpg": (794, 562),
    "assets/img/cogito-002-fig1-victor-frankl.jpg": (1100, 407),
    "assets/img/cogito-002-fig2-circuit-recompense.jpg": (1100, 733),
    "assets/img/cogito-002-fig3-sisyphe.jpg": (1100, 567),
    "assets/img/cogito-002-fig4-ulysse-sirenes.jpg": (1100, 733),
    "assets/img/cogito-003-cover.jpg": (1100, 732),
    "assets/img/cogito-003-fig1-axiome-mathematiques.jpg": (1100, 513),
    "assets/img/cogito-003-fig2-petit-prince.jpg": (960, 527),
    "assets/img/cogito-003-fig3-alchimiste-coelho.jpg": (880, 346),
    "assets/img/cogito-004-cover.jpg": (1100, 697),
    "assets/img/cogito-004-fig1-quatre-nobles-verites.jpg": (1100, 550),
    "assets/img/cogito-004-fig2-statue-bouddha.jpg": (1100, 586),
    "assets/img/cogito-004-fig3-siddhartha-hesse.jpg": (1100, 550),
    "assets/img/cogito-004-fig4-frederic-lenoir.jpg": (1100, 632),
    "assets/img/cogito-005-cover.jpg": (1100, 747),
    "assets/img/cogito-005-fig1-creation-michel-ange.jpg": (1024, 532),
    "assets/img/cogito-005-fig2-les-lutteurs.jpg": (1100, 550),
    "assets/img/cogito-005-fig3-schopenhauer.jpg": (1100, 619),
    "assets/img/cogito-005-fig4-serment-horaces.jpg": (1100, 640),
    "assets/img/cogito-006-cover.jpg": (1100, 575),
    "assets/img/cogito-006-fig1-moine-bouddhiste.jpg": (1100, 631),
    "assets/img/cogito-006-fig2-allegorie-caverne.jpg": (980, 546),
    "assets/img/cogito-007-cover.jpg": (1100, 578),
    "assets/img/cogito-007-fig1-cout-voie-par-defaut.jpg": (1100, 409),
    "assets/img/cogito-007-fig2-diner-philosophes.jpg": (1100, 505),
    "assets/img/cogito-007-fig3-proces-eichmann.jpg": (1100, 550),
    "assets/img/cogito-007-fig4-escp.jpg": (1100, 543),
    "assets/img/cogito-007-fig5-marionnettes.jpg": (1100, 550),
    "assets/img/cogito-008-cover.jpg": (1100, 603),
    "assets/img/cogito-008-fig1-francois-jullien.jpg": (1100, 495),
    "assets/img/cogito-008-fig2-citation-naval-ravikant.jpg": (1100, 482),
    "assets/img/cogito-008-fig3-nighthawks-hopper.jpg": (1100, 507),
    "assets/img/cogito-008-fig4-perfect-days.jpg": (1100, 455),
}

def img_wh(path):
    dims = IMG_DIMENSIONS.get(path)
    if not dims and not path.startswith("http") and os.path.exists(os.path.join(ROOT, path)):
        try:  # dimensions lues dans le fichier si absentes de IMG_DIMENSIONS
            from PIL import Image
            with Image.open(os.path.join(ROOT, path)) as _im:
                dims = IMG_DIMENSIONS[path] = _im.size
        except Exception:
            pass
    return f' width="{dims[0]}" height="{dims[1]}"' if dims else ""

def img_src(path, prefix=""):
    """Chemin d'image utilisable dans une page (URL externe laissée telle quelle)."""
    if not path:
        return None
    return path if path.startswith("http") else f"{prefix}{path}"

# ---------------------------------------------------------------------------
# ÉDITIONS INTRACOGITO, chargées depuis content/intracogito/
#   - editions.json : métadonnées (titre, date, slug, crédit image, 3 recos...)
#   - NNN.html      : corps de l'édition au gabarit du site
# Pour ajouter des éditions : python3 tools/clean_intracogito.py <export> <num...>
# puis compléter editions.json (crédit, recommandations) et rebuilder.
# Si l'image de couverture locale manque, on retombe sur l'image Substack
# d'origine (utile pour un aperçu) et le build affiche un avertissement.
# ---------------------------------------------------------------------------
INTRACOGITO_DIR = os.path.join(ROOT, "content", "intracogito")
INTRACOGITO_EDITIONS = []
for _key, _e in json.load(open(os.path.join(INTRACOGITO_DIR, "editions.json"), encoding="utf-8")).items():
    _e = dict(_e)
    _e["body"] = open(os.path.join(INTRACOGITO_DIR, f"{_key}.html"), encoding="utf-8").read()
    # pas de séparateur entre l'intro et la première réflexion (gabarit #066)
    _e["body"] = _e["body"].replace("</p><hr/><p><strong>Réflexion № 01 :", "</p><p><strong>Réflexion № 01 :")
    # un séparateur avant chaque réflexion à partir de la 2e, même s'il manquait dans Substack
    _e["body"] = re.sub(r"(?<!<hr/>)(<p><strong>Réflexion № (?!01)\d+ :)", r"<hr/>\1", _e["body"])
    _e["href"] = f"essais/{_e['slug']}.html"
    _e["badge"] = f"Intracogito #{_e['num']:03d}"
    if not os.path.exists(os.path.join(ROOT, _e["cover"])):
        if _e.get("substack_cover_url"):
            print(f"[!] image manquante pour {_e['badge']} : {_e['cover']} -> image Substack utilisée")
            _e["cover"] = _e["substack_cover_url"]
        else:
            # pas d'image du tout : emplacement vide sur les cartes, bandeau sombre sur la page
            print(f"[!] pas d'image pour {_e['badge']} (déposer {_e['cover']})")
            _e["cover"] = None
    INTRACOGITO_EDITIONS.append(_e)
INTRACOGITO_EDITIONS.sort(key=lambda e: e["date"], reverse=True)

MOIS_FR = ["", "janvier", "février", "mars", "avril", "mai", "juin",
           "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

def format_date_fr(iso_date):
    """'2026-03-18' -> '18 mars 2026' (affichage visible, pour matcher le JSON-LD)."""
    y, m, d = iso_date.split("-")
    return f"{int(d)} {MOIS_FR[int(m)]} {y}"

FONTS_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com" />\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
    '<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;'
    '0,9..144,500;0,9..144,600;0,9..144,700;1,9..144,400;1,9..144,500&family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;'
    '0,8..60,600;0,8..60,700;1,8..60,400;1,8..60,600&family=IBM+Plex+Mono:wght@400;500;700&'
    'family=Inter:wght@300;400;500&display=swap" rel="stylesheet" />'
)

SOCIAL_ICONS = """<a href="https://elouannoel.substack.com/" target="_blank" rel="noopener" aria-label="Substack">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M4 4h16v2.3H4V4zm0 5.1h16v2.3H4V9.1zM4 14.2h16V22l-8-4.3L4 22V14.2z"/></svg>
        </a>
        <a href="https://www.instagram.com/intracogito_fr/" target="_blank" rel="noopener" aria-label="Instagram">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/></svg>
        </a>
        <a href="https://www.tiktok.com/@intracogito_fr" target="_blank" rel="noopener" aria-label="TikTok">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-2.88 2.5 2.89 2.89 0 0 1-2.89-2.89 2.89 2.89 0 0 1 2.89-2.89c.28 0 .54.04.79.1V9.01a6.27 6.27 0 0 0-.79-.05 6.34 6.34 0 0 0-6.34 6.34 6.34 6.34 0 0 0 6.34 6.34 6.34 6.34 0 0 0 6.33-6.34V8.69a8.18 8.18 0 0 0 4.78 1.52V6.76a4.85 4.85 0 0 1-1-.07z"/></svg>
        </a>
        <a href="https://www.threads.com/@intracogito_fr" target="_blank" rel="noopener" aria-label="Threads">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M13 3c-4 0-6.5 2.8-6.5 7.3v3.4c0 4.5 2.5 7.3 6.2 7.3 3.1 0 5.1-1.6 5.1-4.1 0-2-1.3-3.2-3.5-3.5l-2-.3c-1.1-.15-1.7-.6-1.7-1.3 0-.8.8-1.3 2-1.3 1.3 0 2.1.6 2.3 1.6l2.3-.4C16.8 9.6 15.2 8 12.9 8c-2.4 0-4 1.4-4 3.4 0 1.7 1.1 2.8 3.3 3.1l2 .3c1.2.2 1.7.6 1.7 1.3 0 .9-.9 1.5-2.3 1.5-1.8 0-2.9-.9-3.1-2.3"/></svg>
        </a>"""

BOOKMARK_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M6 3h12v18l-6-4-6 4V3z"/></svg>'
FILE_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 19.5V6a2 2 0 0 1 2-2h11l3 3v12.5a1.5 1.5 0 0 1-1.5 1.5H5.5A1.5 1.5 0 0 1 4 19.5z"/></svg>'
MENU_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><line x1="3" y1="7" x2="21" y2="7"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="17" x2="21" y2="17"/></svg>'
SEARCH_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>'
CLOSE_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><line x1="4" y1="4" x2="20" y2="20"/><line x1="20" y1="4" x2="4" y2="20"/></svg>'

def topbar(prefix="", on_hero=False, active=""):
    cls = "topbar on-hero" if on_hero else "topbar"
    def nav_cls(name):
        return ' class="active"' if name == active else ""
    return f"""<header class="{cls}">
  <div class="wrap topbar-inner">
    <div class="topbar-left">
      <div class="topbar-actions">
        <button class="menu-trigger" onclick="toggleMenu()" aria-label="Ouvrir le menu">
          {MENU_SVG}
          <span class="lbl">Menu</span>
        </button>
        <span class="topbar-sep" aria-hidden="true">/</span>
        <button class="search-trigger" onclick="toggleSearch()" aria-label="Rechercher">
          {SEARCH_SVG}
        </button>
      </div>
      <div class="topbar-social">
        {SOCIAL_ICONS}
      </div>
    </div>
    <a href="{prefix}index.html" class="topbar-logo" aria-label="Intracogito, accueil">
      <img class="logo-dark" src="{prefix}assets/img/logo-intracogito.png" alt="Intracogito" width="1200" height="151" />
      <img class="logo-light" src="{prefix}assets/img/logo-intracogito-light.png" alt="" aria-hidden="true" width="1200" height="151" />
    </a>
    <div class="topbar-right">
      <div class="topbar-right-row topbar-right-main">
        <a href="https://elouannoel.substack.com/" target="_blank" rel="noopener">Newsletter</a>
      </div>
      <div class="topbar-right-row topbar-right-sub">
        <a href="{prefix}a-propos.html">À propos</a>
        <span class="topbar-sep" aria-hidden="true">/</span>
        <a href="https://buymeacoffee.com/elouannoel" target="_blank" rel="noopener">Soutenir</a>
      </div>
    </div>
  </div>
  {menu_overlay(prefix)}
  {search_overlay(prefix)}
</header>"""

def menu_overlay(prefix=""):
    return f"""<div class="menu-overlay" id="menu-overlay">
    <div class="wrap menu-top">
      <button class="menu-close" onclick="toggleMenu()">
        {CLOSE_SVG}
        Close
      </button>
      <div class="menu-top-social">
        {SOCIAL_ICONS}
      </div>
    </div>
    <nav class="wrap menu-body" aria-label="Menu principal">
      <div class="menu-topics">
        <a href="{prefix}intracogito.html" class="menu-topic t1">Intracogito</a>
        <a href="{prefix}cogito.html" class="menu-topic t2">Cogito</a>
        <a href="{prefix}philosophes.html" class="menu-topic t3">Philosophes</a>
        <a href="{prefix}concepts.html" class="menu-topic t4">Concepts</a>
        <a href="{prefix}comparatifs.html" class="menu-topic t5">Comparatifs</a>
      </div>
      <div class="menu-extra">
        <a href="https://elouannoel.substack.com/" target="_blank" rel="noopener">Newsletter</a>
        <a href="{prefix}a-propos.html">À propos</a>
        <a href="https://buymeacoffee.com/elouannoel" target="_blank" rel="noopener">Soutenir</a>
      </div>
    </nav>
  </div>"""

def search_overlay(prefix=""):
    return f"""<div class="search-overlay" id="search-overlay">
    <div class="wrap search-overlay-inner">
      <div class="search-top">
        <button class="menu-close" onclick="toggleSearch()">
          {CLOSE_SVG}
          Close
        </button>
      </div>
      <div class="search-box">
        {SEARCH_SVG}
        <input type="text" id="search-input" placeholder="Rechercher un mot, un thème, un titre…" autocomplete="off" oninput="performSearch(this.value)" />
      </div>
      <div class="search-results" id="search-results"></div>
    </div>
  </div>"""

def footer(prefix=""):
    # Bande unique et compacte : copyright · réseaux (icônes) + contact · mentions légales
    return f"""<footer id="a-propos">
  <div class="wrap footer-band">
    <span class="footer-copy">© 2026 Intracogito</span>
    <div class="footer-mid">
      <div class="footer-social">
        {SOCIAL_ICONS}
      </div>
      <a class="footer-mail" href="mailto:elouan.noel@gmail.com">elouan.noel@gmail.com</a>
    </div>
    <a class="footer-legal" href="{prefix}mentions-legales.html">Mentions légales</a>
  </div>
</footer>"""

TOGGLE_SCRIPT = """<script>
function toggleMenu(){
  var m = document.getElementById('menu-overlay');
  m.classList.toggle('open');
}
function switchRubriqueTab(el, which){
  var tabs = el.parentElement.querySelectorAll('a');
  for (var i = 0; i < tabs.length; i++) { tabs[i].classList.remove('active'); }
  el.classList.add('active');
  var gl = document.getElementById('grid-latest');
  var gp = document.getElementById('grid-popular');
  if (gl) gl.style.display = (which === 'latest') ? '' : 'none';
  if (gp) gp.style.display = (which === 'popular') ? '' : 'none';
  return false;
}
function toggleSearch(){
  var s = document.getElementById('search-overlay');
  if (!s) return;
  s.classList.toggle('open');
  if (s.classList.contains('open')) {
    var inp = document.getElementById('search-input');
    setTimeout(function(){ if (inp) inp.focus(); }, 60);
    _loadSearchIndex();
  }
}
function _loadSearchIndex(){
  if (!window.__searchIndexPromise) {
    window.__searchIndexPromise = fetch('/assets/search-index.json').then(function(r){ return r.json(); }).catch(function(){ return []; });
  }
  return window.__searchIndexPromise;
}
function _normalize(s){
  return (s || '').toString().toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
}
function _escHtml(s){
  return (s || '').toString().replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; });
}
function _highlight(text, words){
  text = text || '';
  var normText = _normalize(text);
  var ranges = [];
  for (var w = 0; w < words.length; w++) {
    var word = words[w];
    if (!word) continue;
    var idx = 0;
    while (true) {
      var pos = normText.indexOf(word, idx);
      if (pos === -1) break;
      ranges.push([pos, pos + word.length]);
      idx = pos + word.length;
    }
  }
  if (!ranges.length) return _escHtml(text);
  ranges.sort(function(a,b){ return a[0] - b[0]; });
  var merged = [ranges[0].slice()];
  for (var i = 1; i < ranges.length; i++) {
    var r = ranges[i];
    var last = merged[merged.length - 1];
    if (r[0] <= last[1]) { last[1] = Math.max(last[1], r[1]); }
    else { merged.push(r.slice()); }
  }
  var out = '';
  var cursor = 0;
  for (var i = 0; i < merged.length; i++) {
    var r = merged[i];
    out += _escHtml(text.substring(cursor, r[0]));
    out += '<mark>' + _escHtml(text.substring(r[0], r[1])) + '</mark>';
    cursor = r[1];
  }
  out += _escHtml(text.substring(cursor));
  return out;
}
function performSearch(query){
  var out = document.getElementById('search-results');
  if (!out) return;
  var q = _normalize(query).trim();
  if (!q) { out.innerHTML = ''; return; }
  var words = q.split(/\s+/).filter(Boolean);
  _loadSearchIndex().then(function(items){
    var results = [];
    for (var i = 0; i < items.length; i++) {
      var it = items[i];
      var hayTitle = _normalize(it.title);
      var hayBadge = _normalize(it.badge);
      var hayText = _normalize(it.text);
      var hay = hayTitle + ' ' + hayBadge + ' ' + hayText;
      var ok = true;
      var score = 0;
      for (var w = 0; w < words.length; w++) {
        var word = words[w];
        if (hay.indexOf(word) === -1) { ok = false; break; }
        if (hayTitle.indexOf(word) !== -1) score += 10;
      }
      if (ok) {
        var idx = hayText.indexOf(words[0]);
        var snippet;
        if (idx >= 0) {
          snippet = '… ' + it.text.substring(Math.max(0, idx - 60), idx + 140) + ' …';
        } else {
          snippet = it.text.substring(0, 160) + (it.text.length > 160 ? ' …' : '');
        }
        results.push({ it: it, score: score, snippet: snippet });
      }
    }
    results.sort(function(a,b){ return b.score - a.score; });
    results = results.slice(0, 20);
    if (!results.length) {
      out.innerHTML = '<p class="search-empty">Aucun résultat pour « ' + _escHtml(query) + ' ».</p>';
      return;
    }
    out.innerHTML = results.map(function(r){
      return '<a class="search-result" href="' + r.it.href + '">' +
        '<img src="' + r.it.img + '" alt="" loading="lazy" />' +
        '<div><span class="search-result-badge">' + _escHtml(r.it.badge) + '</span>' +
        '<h3>' + _highlight(r.it.title, words) + '</h3>' +
        '<p>' + _highlight(r.snippet, words) + '</p></div></a>';
    }).join('');
  });
}
</script>"""

# ---------------------------------------------------------------------------
# HERO ROTATIF — l'essai Cogito en plein écran change chaque semaine.
#
# Règle : tous les essais tagués "cogito" entrent automatiquement dans ce
# pool dès qu'ils sont ajoutés ci-dessous (aucune autre manip nécessaire).
# La rotation elle-même est calculée côté navigateur (site statique, pas de
# rebuild nécessaire chaque semaine) : index = numéro de semaine (continu,
# depuis l'epoch Unix) modulo le nombre d'essais du pool. Donc tous les
# visiteurs voient le même essai pendant 7 jours, puis ça change tout seul.
#
# Pour tester sans attendre une semaine : ouvrir la page avec ?semaine=0,
# ?semaine=1, ?semaine=2... pour forcer un index. Ajouter &debug=1 pour
# afficher un petit badge en bas de l'écran confirmant l'index actif.
# ---------------------------------------------------------------------------
COGITO_ESSAYS = [
    {
        "href": "essais/la-quete-de-notre-destinee.html",
        "badge": "Cogito #001",
        "date": "2026-03-18",
        "title": "La quête de notre destinée",
        "chapo": "Entre sens et identité",
        "cover": "assets/img/cogito-001-cover.jpg",
        "cover_alt": "Hermann David Salomon Corrodi, Evening on the banks of the Nile (1905)",
    },
    {
        "href": "essais/la-matiere-premiere-du-heros.html",
        "badge": "Cogito #002",
        "date": "2026-04-01",
        "title": "La matière première du héros",
        "chapo": "Choisir sa souffrance",
        "cover": "assets/img/cogito-002-cover.jpg",
        "cover_alt": "Edvard Munch, Le Cri (1893)",
    },
    {
        "href": "essais/la-force-de-lintuition.html",
        "badge": "Cogito #003",
        "date": "2026-04-22",
        "title": "La force de l'intuition",
        "chapo": "Entre le cœur et la raison",
        "cover": "assets/img/cogito-003-cover.jpg",
        "cover_alt": "Albert Bierstadt, Yosemite Valley (1868)",
    },
    {
        "href": "essais/la-verite-du-chemin.html",
        "badge": "Cogito #004",
        "date": "2026-05-13",
        "title": "La vérité du chemin",
        "chapo": "Ce que le bouddhisme enseigne du chemin",
        "cover": "assets/img/cogito-004-cover.jpg",
        "cover_alt": "Nicholas Roerich, Tibet. Himalayas (1933)",
    },
    {
        "href": "essais/lunite-du-corps-et-de-lesprit.html",
        "badge": "Cogito #005",
        "date": "2026-06-10",
        "title": "L'unité du corps et de l'esprit",
        "chapo": "Ce que le corps dit de la pensée",
        "cover": "assets/img/cogito-005-cover.jpg",
        "cover_alt": "Auguste Rodin, Le Penseur",
    },
    {
        "href": "essais/le-poids-de-lidentite.html",
        "badge": "Cogito #006",
        "date": "2026-07-15",
        "title": "Le poids de l'identité",
        "chapo": "À quoi choisit-on de s'identifier ?",
        "cover": "assets/img/cogito-006-cover.jpg",
        "cover_alt": "John Ross Key, Mt. Diablo, San Joaquin Valley",
    },
    {
        "href": "essais/la-voie-par-defaut.html",
        "badge": "Cogito #007",
        "date": "2026-09-09",
        "title": "La voie par défaut",
        "chapo": "Sur le courage de penser par soi-même",
        "cover": "assets/img/cogito-007-cover.jpg",
        "cover_alt": "Johann Ludwig Bleuler, Wimmis an der Kander bey Thun",
    },
    {
        "href": "essais/les-transformations-silencieuses.html",
        "badge": "Cogito #008",
        "date": "2026-10-07",
        "title": "Les transformations silencieuses",
        "chapo": "Ce qui change sans qu'on le voie",
        "cover": "assets/img/cogito-008-cover.jpg",
        "cover_alt": "Richard Wilson, Italian Landscape (1765)",
    },
]

# HERO DE LA HOMEPAGE : toujours le dernier essai Cogito publié.
# COGITO_ESSAYS est rangé dans l'ordre de publication (du plus ancien au plus
# récent) : il suffit d'ajouter le nouvel essai EN FIN de liste pour qu'il
# passe automatiquement en couverture au prochain build.
HERO_ESSAI = next(e for e in COGITO_ESSAYS if e["href"] == "essais/la-quete-de-notre-destinee.html")  # Cogito #001, fixé en une (demande Elouan 27/10)

# Tous les articles réels (Cogito + Intracogito), du plus récent au plus ancien :
# alimente la page Essais, les « Articles récents » de l'accueil et les recos.
ALL_ARTICLES = sorted(
    [{"href": c["href"], "meta": "Cogito", "title": c["title"], "chapo": c["badge"], "img": c["cover"], "date": c["date"]} for c in COGITO_ESSAYS]
    + [{"href": e["href"], "meta": "Intracogito", "title": e["title"], "chapo": e["badge"], "img": e["cover"], "date": e["date"]} for e in INTRACOGITO_EDITIONS],
    key=lambda a: a["date"], reverse=True,
)
ARTICLES_BY_HREF = {a["href"]: a for a in ALL_ARTICLES}

def article_card(a, prefix="", chapo=None, show_author=True):
    return card(f"{prefix}{a['href']}", meta=a["meta"], title=a["title"], chapo=chapo if chapo is not None else a["chapo"], author="Elouan Noël" if show_author else None, img=img_src(a["img"], prefix))

def hero_rotation_script(essays):
    data = json.dumps(essays, ensure_ascii=False)
    return f"""<script type="application/json" id="cogito-essais-data">{data}</script>
<script>
(function(){{
  var dataEl = document.getElementById('cogito-essais-data');
  if (!dataEl) return;
  var essais = JSON.parse(dataEl.textContent || '[]');
  if (!essais.length) return;
  var WEEK_MS = 7 * 24 * 60 * 60 * 1000;
  var params = new URLSearchParams(window.location.search);
  var forced = params.get('semaine');
  var weekIndex = forced !== null ? parseInt(forced, 10) : Math.floor(Date.now() / WEEK_MS);
  var idx = ((weekIndex % essais.length) + essais.length) % essais.length;
  var essai = essais[idx];
  var hero = document.getElementById('hero-rotatif');
  if (hero) hero.setAttribute('data-essai-index', idx);
  var badgeEl = document.getElementById('hero-badge');
  var titleEl = document.getElementById('hero-title');
  var chapoEl = document.getElementById('hero-chapo');
  var linkEl = document.getElementById('hero-link');
  var mediaEl = document.getElementById('hero-media');
  var bgImgEl = document.getElementById('hero-bg-img');
  if (badgeEl) badgeEl.textContent = essai.badge || 'Rubrique';
  if (titleEl) titleEl.textContent = essai.title || 'Titre';
  if (chapoEl) {{
    if (essai.chapo) {{ chapoEl.textContent = essai.chapo; chapoEl.style.display = ''; }}
    else {{ chapoEl.style.display = 'none'; }}
  }}
  if (linkEl) linkEl.setAttribute('href', essai.href || '#');
  if (essai.cover && bgImgEl && mediaEl) {{
    bgImgEl.src = essai.cover;
    bgImgEl.alt = essai.cover_alt || essai.title || '';
    bgImgEl.style.display = '';
    mediaEl.style.display = 'none';
  }}
  if (params.get('debug') === '1') {{
    var dbg = document.createElement('div');
    dbg.style.cssText = 'position:fixed;bottom:0;left:0;background:#111;color:#8f8;font:11px monospace;padding:4px 8px;z-index:9999;';
    dbg.textContent = 'debug hero rotatif, index actif: ' + idx + ' / ' + essais.length + ' (semaine#' + weekIndex + ')';
    document.body.appendChild(dbg);
  }}
}})();
</script>"""

def card(href, badge=True, meta="Rubrique", title="Titre", chapo="Sous-titre", author=None, img=None):
    badge_html = f'<span class="card-badge">{BOOKMARK_SVG}</span>' if badge else ""
    author_html = f'<span class="card-author">{author}</span>' if author else ""
    tag = "a" if href else "div"
    href_attr = f' href="{href}"' if href else ""
    img_html = f'<img src="{img}" alt="{title}" loading="lazy"{img_wh(img.replace("../", "", 1))} />' if img else '<div class="ph-box"><span>Image</span></div>'
    return f"""<{tag} class="card"{href_attr}>
      <div class="card-img">
        {img_html}
        {badge_html}
      </div>
      <span class="card-meta-line">{FILE_SVG if badge else ""}{meta}</span>
      <h3 class="card-title">{title}</h3>
      <p class="card-chapo">{chapo}</p>
      {author_html}
    </{tag}>"""

OG_DEFAULT_IMAGE = f"{BASE_URL}/assets/img/og-default.jpg"

PLAUSIBLE_SCRIPT = """<!-- Privacy-friendly analytics by Plausible -->
<script async src="https://plausible.io/js/pa--T_GhxjEw82keNVG-arb8.js"></script>
<script>
  window.plausible=window.plausible||function(){(plausible.q=plausible.q||[]).push(arguments)},plausible.init=plausible.init||function(i){plausible.o=i||{}};
  plausible.init()
</script>"""

UMAMI_SCRIPT = """<!-- Privacy-friendly analytics by Umami -->
<script defer src="https://cloud.umami.is/script.js" data-website-id="653389b3-c8eb-448c-ba35-0a2e5c9e57ab"></script>"""

def head_meta(title, description, path, og_type="website", robots=None, extra_jsonld="", image=None):
    canonical = f"{BASE_URL}/{path}" if path else f"{BASE_URL}/"
    robots_tag = f'\n<meta name="robots" content="{robots}" />' if robots else ""
    rel = '../' if '/' in path else ''
    og_image = image or OG_DEFAULT_IMAGE
    return f"""<meta charset="UTF-8" />
<script>if ('scrollRestoration' in history) {{ history.scrollRestoration = 'manual'; }} window.scrollTo(0, 0);</script>
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{title}</title>
<meta name="description" content="{description}" />
<link rel="canonical" href="{canonical}" />{robots_tag}
<link rel="icon" href="{rel}assets/img/favicon.png" type="image/png" />
<link rel="icon" href="{rel}assets/img/favicon-32.png" sizes="32x32" type="image/png" />
<link rel="apple-touch-icon" href="{rel}assets/img/apple-touch-icon.png" />
<meta property="og:type" content="{og_type}" />
<meta property="og:site_name" content="Intracogito" />
<meta property="og:title" content="{title}" />
<meta property="og:description" content="{description}" />
<meta property="og:url" content="{canonical}" />
<meta property="og:image" content="{og_image}" />
<meta property="og:locale" content="fr_FR" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{title}" />
<meta name="twitter:description" content="{description}" />
<meta name="twitter:image" content="{og_image}" />
{FONTS_LINK}
<link rel="stylesheet" href="{rel}assets/site.css" />
{PLAUSIBLE_SCRIPT}
{UMAMI_SCRIPT}
{extra_jsonld}"""

# ---------------------------------------------------------------------------
# PAGE: index.html (contenu seul, sans head — publié via Artifact file_path)
# ---------------------------------------------------------------------------
PERSON_JSONLD = """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "Intracogito",
  "url": "https://intracogito.vercel.app/",
  "inLanguage": "fr",
  "author": {
    "@type": "Person",
    "name": "Elouan Noël",
    "email": "mailto:elouan.noel@gmail.com",
    "sameAs": [
      "https://elouannoel.substack.com/",
      "https://www.instagram.com/intracogito_fr/",
      "https://www.tiktok.com/@intracogito_fr",
      "https://www.threads.com/@intracogito_fr"
    ]
  }
}
</script>"""

INDEX_CONTENT = f"""<!-- ══════════════ TOPBAR ══════════════ -->
{topbar(active="")}
<main>

<!-- ══════════════ CARTE NEWSLETTER, coin bas-droit, non bloquante ══════════════ -->
<div class="newsletter-popup" id="newsletter-popup">
  <button class="newsletter-popup-close" id="newsletter-popup-close" aria-label="Fermer">
    {CLOSE_SVG}
  </button>
  <div class="newsletter-popup-head">
    <img class="newsletter-popup-photo" src="assets/img/vitruvian-man.jpg" alt="Elouan Noël" loading="lazy" />
    <div>
      <h2>Rejoins Intracogito</h2>
      <p>Une édition chaque dimanche à 13h, directement dans ta boîte mail.</p>
    </div>
  </div>
  <a href="https://elouannoel.substack.com/" target="_blank" rel="noopener" class="hero-cta newsletter-popup-cta">S'abonner sur Substack →</a>
</div>
<script>
(function(){{
  var KEY = 'ic_newsletter_popup_seen';
  var THIRTY_DAYS = 30 * 24 * 60 * 60 * 1000;
  try {{
    var last = localStorage.getItem(KEY);
    if (last && (Date.now() - parseInt(last, 10)) < THIRTY_DAYS) return;
  }} catch (e) {{}}
  var popup = document.getElementById('newsletter-popup');
  if (!popup) return;
  function markSeen(){{
    try {{ localStorage.setItem(KEY, Date.now().toString()); }} catch (e) {{}}
  }}
  function closePopup(){{
    popup.classList.remove('open');
    markSeen();
  }}
  setTimeout(function(){{ popup.classList.add('open'); }}, 900);
  var closeBtn = document.getElementById('newsletter-popup-close');
  if (closeBtn) closeBtn.addEventListener('click', closePopup);
  document.addEventListener('keydown', function(ev){{ if (ev.key === 'Escape' && popup.classList.contains('open')) closePopup(); }});
}})();
</script>

<!-- ══════════════ HERO, le dernier essai Cogito publié ══════════════ -->
<section class="hero-full" id="hero-dernier-essai">
  <img class="bg-cover-img" src="{HERO_ESSAI['cover']}" alt="{HERO_ESSAI['cover_alt']}" loading="eager" fetchpriority="high" />
  <div class="wrap hero-full-content">
    <span class="hero-eyebrow">{HERO_ESSAI['badge']}</span>
    <h1>{HERO_ESSAI['title']}</h1>
    <p class="chapo">{HERO_ESSAI['chapo']}</p>
    <a href="{HERO_ESSAI['href']}" class="hero-cta">Lire l'essai →</a>
  </div>
</section>

<!-- ══════════════ ARTICLES RÉCENTS (Cogito + Intracogito) ══════════════ -->
<section class="sec">
  <div class="wrap">
    <div class="card-grid">
      {"".join(article_card(x, show_author=False) for x in ALL_ARTICLES[:18])}
    </div>
    <div class="sec-all">
      <a href="essais.html" class="hero-cta">Lire tous les articles →</a>
    </div>
  </div>
</section>


</main>
{footer()}
{TOGGLE_SCRIPT}
"""

# Variante "contenu seul" (sans doctype/head/body), utilisée uniquement pour
# publier la homepage comme file_path d'un Artifact Claude, qui ajoute lui-même
# son propre squelette de page à la publication.
index_artifact_body = f"""<link rel="stylesheet" href="assets/site.css" />
{FONTS_LINK}
{PERSON_JSONLD}

{INDEX_CONTENT}"""

# Page complète et valide, c'est CELLE-CI qui est écrite sur disque comme
# index.html et servie par le vrai site (Vercel) : il lui faut son propre
# doctype/head/body, sinon le head_meta (title, description, favicon,
# og:image, sitemap, etc.) n'existe nulle part sur la page d'accueil réelle.
index_html = f"""<!doctype html>
<html lang="fr">
<head>
{head_meta("Intracogito, philosophie appliquée chaque semaine", "Intracogito : une citation philosophique commentée chaque semaine, et des essais Cogito pour aller plus loin. Philosophie appliquée à la vie quotidienne.", "", og_type="website", extra_jsonld=PERSON_JSONLD)}
</head>
<body>
{INDEX_CONTENT}
</body>
</html>
"""

# ---------------------------------------------------------------------------
# PAGE: essais.html
# ---------------------------------------------------------------------------
essais_html = f"""<!doctype html>
<html lang="fr">
<head>
{head_meta(
    "Essais, Intracogito",
    "Tous les essais Intracogito : philosophes, concepts et comparatifs de philosophie pratique, expliqués simplement et appliqués au quotidien.",
    "essais.html"
)}
</head>
<body>

{topbar(active="essais")}
<main>

<div class="wrap listing-head">
  <h1>Essais</h1>
  <p>Les essais Cogito et les éditions Intracogito, dans l'ordre de publication.</p>
</div>

<section class="sec">
  <div class="wrap card-grid">
    {"".join(article_card(x) for x in ALL_ARTICLES)}
  </div>
</section>

</main>
{footer()}
{TOGGLE_SCRIPT}
</body>
</html>
"""

# ---------------------------------------------------------------------------
# PAGES DE RUBRIQUE : philosophes / concepts / comparatifs
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# POPULARITÉ (onglet "Popular" des rubriques Cogito / Intracogito) : likes et
# vues relevés sur le dashboard Substack (captures du 27/10/2026). Score =
# (likes / max_likes) + (vues / max_vues), calculé séparément pour chaque
# rubrique (échelles très différentes). Mettre à jour ces deux dicts et
# relancer le build quand de nouvelles stats sont dispo.
# ---------------------------------------------------------------------------
INTRACOGITO_STATS = {
    1:(20,561), 2:(15,167), 3:(11,77), 4:(9,132), 5:(11,143), 6:(8,120), 7:(8,123), 8:(9,109),
    9:(4,84), 10:(6,107), 11:(4,96), 12:(4,92), 13:(4,99), 14:(4,98), 15:(4,86), 16:(4,122),
    17:(3,81), 18:(2,79), 19:(3,86), 20:(1,68), 21:(3,93), 22:(3,98), 23:(8,122), 24:(3,96),
    26:(8,123), 27:(7,122), 28:(7,129), 29:(11,146), 30:(10,204), 31:(14,243), 32:(9,311),
    33:(10,306), 34:(10,401), 35:(11,407), 36:(8,371), 37:(14,438), 38:(10,394), 39:(9,430),
    40:(15,435), 41:(8,494), 42:(12,461), 43:(9,439), 44:(8,422), 45:(7,472), 46:(7,490),
    47:(8,596), 48:(12,609), 49:(12,559), 52:(6,499), 53:(6,529), 54:(5,508), 55:(8,500),
    56:(5,584), 57:(9,508), 58:(4,535), 59:(6,583), 60:(5,584), 61:(3,487), 62:(6,501),
    63:(3,590), 64:(6,604), 65:(6,523), 66:(3,481), 67:(3,341),
}
COGITO_STATS = {
    1:(4,363), 2:(9,430), 3:(8,419), 4:(7,444), 5:(10,625), 6:(2,571), 7:(4,644), 8:(12,704),
}

def _popularity_score(stats):
    max_l = max(v[0] for v in stats.values())
    max_v = max(v[1] for v in stats.values())
    return {num: (l / max_l + v / max_v) for num, (l, v) in stats.items()}

RUBRIQUES = {
    "philosophes": {
        "label": "Philosophes",
        "desc": "Les philosophes expliqués simplement : leurs idées clés et comment les appliquer au quotidien.",
        "subtopics": ["Stoïcisme", "Épicurisme", "Existentialisme", "Marc Aurèle", "Épictète",
                      "Sénèque", "Nietzsche", "Camus", "Socrate", "Spinoza"],
        "subtopic_links": {"Marc Aurèle": "philosophes/marc-aurele.html"},
        "real_cards": [
            {"href": "philosophes/marc-aurele.html", "meta": "Philosophes", "title": "Marc Aurèle",
             "chapo": "Garder son calme face à ce qu'on ne contrôle pas", "author": "Elouan Noël", "img": None},
        ],
    },
    "concepts": {
        "label": "Concepts",
        "desc": "Les grands concepts de la philosophie pratique, définis et reliés à des situations concrètes.",
        "subtopics": ["Ataraxie", "Dichotomie du contrôle", "Absurde", "Vertu", "Eudaimonia",
                      "Résilience", "Détachement", "Présent", "Sens de la vie", "Liberté"],
    },
    "comparatifs": {
        "label": "Comparatifs",
        "desc": "Deux écoles, deux penseurs, deux idées mises face à face pour mieux choisir ce qui te convient.",
        "subtopics": ["Stoïcisme vs épicurisme", "Nietzsche vs Schopenhauer", "Bonheur vs sens",
                      "Raison vs instinct", "Stoïcisme vs bouddhisme"],
        "real_card": None,
    },
    "cogito": {
        "label": "Cogito",
        "desc": "Les essais Cogito : la version longue et approfondie d'Intracogito, une réflexion personnelle structurée toutes les 3 semaines.",
        "subtopics": [],
        "real_cards": [
            {"href": "essais/les-transformations-silencieuses.html", "meta": "Cogito", "title": "Les transformations silencieuses", "chapo": "Cogito #008", "author": "Elouan Noël", "img": "assets/img/cogito-008-cover.jpg"},
            {"href": "essais/la-voie-par-defaut.html", "meta": "Cogito", "title": "La voie par défaut", "chapo": "Cogito #007", "author": "Elouan Noël", "img": "assets/img/cogito-007-cover.jpg"},
            {"href": "essais/le-poids-de-lidentite.html", "meta": "Cogito", "title": "Le poids de l'identité", "chapo": "Cogito #006", "author": "Elouan Noël", "img": "assets/img/cogito-006-cover.jpg"},
            {"href": "essais/lunite-du-corps-et-de-lesprit.html", "meta": "Cogito", "title": "L'unité du corps et de l'esprit", "chapo": "Cogito #005", "author": "Elouan Noël", "img": "assets/img/cogito-005-cover.jpg"},
            {"href": "essais/la-verite-du-chemin.html", "meta": "Cogito", "title": "La vérité du chemin", "chapo": "Cogito #004", "author": "Elouan Noël", "img": "assets/img/cogito-004-cover.jpg"},
            {"href": "essais/la-force-de-lintuition.html", "meta": "Cogito", "title": "La force de l'intuition", "chapo": "Cogito #003", "author": "Elouan Noël", "img": "assets/img/cogito-003-cover.jpg"},
            {"href": "essais/la-matiere-premiere-du-heros.html", "meta": "Cogito", "title": "La matière première du héros", "chapo": "Cogito #002", "author": "Elouan Noël", "img": "assets/img/cogito-002-cover.jpg"},
            {"href": "essais/la-quete-de-notre-destinee.html", "meta": "Cogito", "title": "La quête de notre destinée", "chapo": "Cogito #001", "author": "Elouan Noël", "img": "assets/img/cogito-001-cover.jpg"},
        ],
        "popular_cards": sorted(
            [
                {"href": "essais/les-transformations-silencieuses.html", "meta": "Cogito", "title": "Les transformations silencieuses", "chapo": "Cogito #008", "author": "Elouan Noël", "img": "assets/img/cogito-008-cover.jpg", "_num": 8},
                {"href": "essais/la-voie-par-defaut.html", "meta": "Cogito", "title": "La voie par défaut", "chapo": "Cogito #007", "author": "Elouan Noël", "img": "assets/img/cogito-007-cover.jpg", "_num": 7},
                {"href": "essais/le-poids-de-lidentite.html", "meta": "Cogito", "title": "Le poids de l'identité", "chapo": "Cogito #006", "author": "Elouan Noël", "img": "assets/img/cogito-006-cover.jpg", "_num": 6},
                {"href": "essais/lunite-du-corps-et-de-lesprit.html", "meta": "Cogito", "title": "L'unité du corps et de l'esprit", "chapo": "Cogito #005", "author": "Elouan Noël", "img": "assets/img/cogito-005-cover.jpg", "_num": 5},
                {"href": "essais/la-verite-du-chemin.html", "meta": "Cogito", "title": "La vérité du chemin", "chapo": "Cogito #004", "author": "Elouan Noël", "img": "assets/img/cogito-004-cover.jpg", "_num": 4},
                {"href": "essais/la-force-de-lintuition.html", "meta": "Cogito", "title": "La force de l'intuition", "chapo": "Cogito #003", "author": "Elouan Noël", "img": "assets/img/cogito-003-cover.jpg", "_num": 3},
                {"href": "essais/la-matiere-premiere-du-heros.html", "meta": "Cogito", "title": "La matière première du héros", "chapo": "Cogito #002", "author": "Elouan Noël", "img": "assets/img/cogito-002-cover.jpg", "_num": 2},
                {"href": "essais/la-quete-de-notre-destinee.html", "meta": "Cogito", "title": "La quête de notre destinée", "chapo": "Cogito #001", "author": "Elouan Noël", "img": "assets/img/cogito-001-cover.jpg", "_num": 1},
            ],
            key=lambda c: -_popularity_score(COGITO_STATS)[c["_num"]],
        ),
    },
    "intracogito": {
        "label": "Intracogito",
        "desc": "Les éditions Intracogito : citations philosophiques commentées, chaque semaine, pour penser mieux au quotidien.",
        "subtopics": [],
        "real_cards": [
            {"href": e["href"], "meta": "Intracogito", "title": e["title"], "chapo": e["badge"], "author": "Elouan Noël", "img": e["cover"]}
            for e in INTRACOGITO_EDITIONS
        ],
        "popular_cards": sorted(
            [
                {"href": e["href"], "meta": "Intracogito", "title": e["title"], "chapo": e["badge"], "author": "Elouan Noël", "img": e["cover"], "_num": e["num"]}
                for e in INTRACOGITO_EDITIONS
            ],
            key=lambda c: -_popularity_score(INTRACOGITO_STATS).get(c["_num"], 0),
        ),
    },
}


def rubrique_page(slug, data):
    tabs = """<div class="rubrique-tabs">
      <a href="#" class="active" data-tab="latest" onclick="return switchRubriqueTab(this,'latest')">Latest</a>
      <a href="#" data-tab="popular" onclick="return switchRubriqueTab(this,'popular')">Popular</a>
    </div>"""
    subtopics_block = ""
    real_cards = data.get("real_cards")
    if not real_cards:
        # Rubrique sans article publié : un simple message, aucune carte ni lien vide
        return f"""<!doctype html>
<html lang="fr">
<head>
{head_meta(f"{data['label']}, Intracogito", data["desc"], f"{slug}.html")}
</head>
<body>

{topbar(active=slug)}
<main>

<div class="rubrique-head {slug}">
  <h1>{data['label']}</h1>
  <p>{data['desc']}</p>
</div>

<section class="sec rubrique-empty">
  <div class="wrap">
    <p class="rubrique-empty-label">Articles à venir</p>
    <p>Cette rubrique est en préparation. En attendant, retrouve les éditions Intracogito et les essais Cogito.</p>
    <a href="essais.html" class="hero-cta">Lire tous les articles →</a>
  </div>
</section>

</main>
{footer()}
{TOGGLE_SCRIPT}
</body>
</html>
"""
    if data["subtopics"]:
        _subtopic_links = data.get("subtopic_links", {})
        subtopics_html = "\n      ".join(f'<a href="{_subtopic_links.get(s, "essais.html")}">{s}</a>' for s in data["subtopics"])
        subtopics_block = f"""<div class="subtopic-cloud">
  {subtopics_html}
</div>"""
    real_cards = data.get("real_cards")
    if real_cards:
        def _card(c):
            return card(**{k: v for k, v in c.items() if k != "_num"})
        cards = "\n    ".join(_card(c) for c in real_cards)
        popular_cards = data.get("popular_cards")
        cards_popular = "\n    ".join(_card(c) for c in popular_cards) if popular_cards else cards
    else:
        real = data.get("real_card")
        first_card = card(**real) if real else card(None, badge=False)
        cards = "\n    ".join([first_card, card(None, badge=False), card(None, badge=False), card(None, badge=False)])
        cards_popular = cards
    return f"""<!doctype html>
<html lang="fr">
<head>
{head_meta(
    f"{data['label']}, Intracogito",
    data["desc"],
    f"{slug}.html"
)}
</head>
<body>

{topbar(active=slug)}
<main>

<div class="rubrique-head {slug}">
  <h1>{data['label']}</h1>
  <p>{data['desc']}</p>
</div>
{subtopics_block}
{tabs}

<section class="sec" style="padding-top:0;">
  <div class="wrap card-grid" id="grid-latest">
    {cards}
  </div>
  <div class="wrap card-grid" id="grid-popular" style="display:none;">
    {cards_popular}
  </div>
</section>

</main>
{footer()}
{TOGGLE_SCRIPT}
</body>
</html>
"""

# ---------------------------------------------------------------------------
# PAGE : essais/exemple-stoicisme.html (gabarit d'article)
# ---------------------------------------------------------------------------
article_jsonld = """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Intracogito", "item": "https://intracogito.vercel.app/"},
    {"@type": "ListItem", "position": 2, "name": "Essais", "item": "https://intracogito.vercel.app/essais.html"},
    {"@type": "ListItem", "position": 3, "name": "Titre", "item": "https://intracogito.vercel.app/essais/exemple-stoicisme.html"}
  ]
}
</script>"""

article_html = f"""<!doctype html>
<html lang="fr">
<head>
{head_meta(
    "Gabarit d'essai, Intracogito",
    "Gabarit de page essai Intracogito : structure vide à remplir, pas un essai réel.",
    "essais/exemple-stoicisme.html",
    og_type="article",
    robots="noindex, follow",
    extra_jsonld=article_jsonld
)}
</head>
<body>

{topbar(prefix="../", on_hero=True)}
<main>

<section class="article-hero">
  <div class="article-hero-content">
    <h1>Titre</h1>
    <p class="chapo">Sous-titre</p>
  </div>
</section>
<p class="article-credit" style="color:var(--ink-muted); text-align:right; padding: .4rem var(--px);">Crédit image</p>

<div class="wrap article-meta-wrap">
  <div class="article-tags">
    <a class="article-tag" href="../essais.html">Rubrique</a>
    <a class="article-tag" href="../essais.html">Rubrique</a>
    <a class="article-tag" href="../essais.html">Rubrique</a>
  </div>
  <div class="article-author-row">
    <div class="article-author-avatar"><div class="ph-box"><span>Photo</span></div></div>
    <div>
      <div class="article-author-name">Auteur</div>
      <p class="article-author-bio">Bio courte de l'auteur, une phrase.</p>
    </div>
  </div>
  <div class="article-sub-meta">
    <span>Durée de lecture</span>
    <span>·</span>
    <span>Nombre de mots</span>
  </div>
</div>

<div class="wrap article-body">
  <p class="placeholder">[Gabarit d'exemple, ce texte est un emplacement de démonstration. Le contenu réel de chaque essai sera rédigé par Elouan, dans son univers et son style. Il montre juste la structure attendue : une image concrète pour ouvrir, un renversement, une chute courte et applicable, voir le guide de style « Entre les lignes ».]</p>
  <p>[Paragraphe 1, image ou exemple concret d'ouverture]</p>
  <p>[Paragraphe 2, le renversement : ce que la citation ou le concept ne dit pas au premier abord]</p>

  <div class="newsletter-insert">
    <h3>Rejoins la newsletter</h3>
    <p>Une édition par semaine, 4 à 5 citations commentées. Gratuit, désabonnement en un clic.</p>
    <a href="https://elouannoel.substack.com/" target="_blank" rel="noopener" class="hero-cta">S'abonner →</a>
  </div>

  <p>[Paragraphe 3, la chute : l'idée à retenir, formulée court]</p>
</div>

<div class="article-related">
  <div class="wrap">
    <h2 class="sec-title">À lire aussi</h2>
    <div class="card-grid">
      {card("../essais.html", badge=False)}
      {card("../essais.html", badge=False)}
      {card("../essais.html", badge=False)}
    </div>
  </div>
</div>

</main>
{footer(prefix="../")}
{TOGGLE_SCRIPT}
</body>
</html>
"""

# ---------------------------------------------------------------------------
# ESSAIS RÉELS — repris de l'export Substack (dossier "posts" fourni par Elouan),
# nettoyés (figures simplifiées, scripts/boutons substack retirés). Images
# hébergées directement sur le CDN Substack d'Elouan (ses propres fichiers).
# ---------------------------------------------------------------------------

COGITO_001_BODY = """<p>J’aime beaucoup l’idée de destinée. Pas au sens déterministe, pas une trajectoire figée qui dirait : “Tu finiras comme ça, quoi qu’il arrive.”</p><p>Mais plutôt au sens d’une direction. L’idée qu’il existerait, quelque part, une version plus accomplie de moi-même. Une ligne idéale vers laquelle je pourrais tendre. Non pas écrite d’avance, mais potentielle.</p><p>L’exercice n’est pas de démontrer que cette croyance est vraie mais simplement que cette perspective peut être utile. Et c’est peut-être suffisant.</p><p>Cet essai a pour but d’exposer une réflexion personnelle qui m’a permis de cadrer la notion d’identité et de la relier à celle de sens et de ce vers quoi l’on aspire.</p><p>J’en présenterai d’abord les présupposés et les fondements théoriques, avant d’en proposer une analogie mathématique pour clarifier mon idée. Je mettrai enfin ce raisonnement en perspective avec la pensée d’Aristote, dont le concept de puissance vient éclairer ce raisonnement.</p><hr/><h2><strong>Ce que cela suppose</strong></h2><p>Ce cadre repose sur un présupposé fort : l’existence humaine ne serait pas neutre. Elle serait orientée Il y aurait en chacun de nous des puissances, des dispositions, des inclinations profondes, et vivre consisterait à les actualiser.</p><p>On peut rejeter cette hypothèse et considérer que la vie n’a pas de direction intrinsèque, que le sens se construit arbitrairement, ou qu’il n’y en a pas.</p><p>Mais si l’on accepte, ne serait-ce qu’à titre heuristique, l’idée que nous portons en nous une forme plus accomplie de nous-mêmes, alors la manière de vivre change.</p><p>La question devient : comment s’en rapprocher ?</p><figure><img alt="Thomas Cole, The Voyage of Life: Manhood (1842)" loading="lazy" width="900" height="592" src="../assets/img/cogito-001-fig1-voyage-of-life.jpg"/><figcaption>Thomas Cole, The Voyage of Life: Manhood (1842)</figcaption></figure><hr/><h2><strong>L’itération comme chemin</strong></h2><p>Un vélo ne tient en équilibre que lorsqu’il est en mouvement ; à l’arrêt, il tombe.  C’est la “vélo”-cité qui crée la stabilité. Peut-être que la vie fonctionne de la même manière. </p><p>On cherche parfois à comprendre qui l’on est avant d’agir, à clarifier sa direction avant de commencer. Mais l’équilibre ne se trouve pas dans l’immobilité. C’est dans le mouvement que quelque chose se révèle. En expérimentant, en itérant, certaines choses ne prennent pas, d’autres accrochent, et quelques-unes finissent par s’imposer. </p><p>À force d’itérations, une cohérence apparaît. On ne découvre pas son identité d’un coup à mon sens ; on l’approche progressivement, en avançant. C’est dans l’exécution que le sens commence à se dessiner.</p><hr/><h2><strong>De l’élan à l’identité</strong></h2><p>Une fois que l’on admet que le mouvement et l’itération constituent un bon moyen de découvrir ce à quoi l’on aspire réellement, il devient possible de disséquer les phases de nos comportements. J’aime distinguer quatre étapes qui permettent de comprendre comment une activité passe, ou non, du statut d’essai à celui de dimension identitaire : </p><hr/><blockquote><p><strong>1 - Motivation    2- Discipline      3- Habitude     4- Identité</strong></p></blockquote><hr/><p><strong>Motivation: </strong></p><p>Prenons l’exemple de la course à pied. Au départ, il y a souvent un élan. Une vidéo inspirante, un ami, un objectif précis, un marathon à préparer. La motivation joue son rôle : elle déclenche le mouvement. </p><p><strong>Discipline:</strong></p><p>Puis vient la discipline. On suit un plan, on s’entraîne même quand l’envie est absente, parce qu’un objectif est en vue. Tant que cet objectif structure l’effort, la pratique tient.</p><p><strong>Habitude:</strong></p><p>Mais une fois la course terminée, l’objectif externe disparaît. C’est ici que quelque chose se joue. Soit la pratique s’arrête, parce qu’elle n’était qu’un moyen en vue d’une fin ponctuelle. Soit elle s’installe. Elle devient habitude : on court sans se demander si l’on doit courir. L’effort est intégré au rythme de vie.</p><p><strong>Identité</strong></p><p>Et parfois, pour certains, une étape supplémentaire est franchie. La course cesse d’être une activité parmi d’autres et devient une composante de l’identité. Cela devient évident et l’on se dit “je suis un coureur”. La pratique devient structurante ; elle organise le temps, les priorités, l’image de soi. </p><p>Toutes les itérations ne vont pas jusque-là, et ce n’est pas un échec. Mais lorsqu’une activité atteint ce niveau d’intégration, elle devient un terme stable dans l’équation personnelle. C’est à partir de là qu’une l’analogie mathématique peut nous aider à mettre ce cadre en image. </p><hr/><h2><strong>Le développement limité de notre vie</strong></h2><p>En mathématiques, un développement limité permet d’approximer une fonction complexe. </p><p>L’image importante à saisir c’est qu’une fonction a une courbe, comme la fonction exponentielle ci-dessous, et que plus un développement limité a d’ordres, plus la ligne bleue épouse la courbe de la fonction que l’on estime.</p><figure><img alt="Développement limité d'une fonction exponentielle par ordres successifs (illustration mathématique)" loading="lazy" width="900" height="625" src="../assets/img/cogito-001-fig2-developpement-limite.jpg"/></figure><p>Ainsi, chaque nouvel ordre améliore l’approximation.</p><p>Peut-être que vivre, c’est faire la même chose avec soi-même. La “courbe idéale” n’est pas donnée d’un coup mais chacune de nos itérations correspond à un essai pour l’approcher progressivement.</p><p>Les ordres mathématiques deviennent nos piliers identitaires. Une fois que l’on en a trouvé un, on itère pour en ajouter un nouveau. On approxime notre vie idéale en ajoutant des dimensions identitaires :</p><p>Je suis père. Et…<br/>Je suis chercheur. Et…<br/>Je suis croyant. Et…<br/>Je suis un coureur.</p><p>Chaque fois qu’une dimension devient intégrée, elle affine la trajectoire.</p><p>A l’inverse, chaque fois qu’une tentative échoue à dépasser la discipline, elle nous renseigne aussi : ce n’est peut-être pas constitutif de qui l’on est. Ainsi, l’identité devient une série d’approximations successives.</p><hr/><h2><strong>Aristote et le concept de puissance</strong></h2><p>L’idée selon laquelle l’existence humaine serait orientée n’est pas nouvelle. Chez Aristote, on trouve une distinction fondamentale entre puissance (<em>dunamis</em>) et acte (<em>energeia</em>). Une chose n’est pas seulement ce qu’elle est actuellement ; elle est aussi ce qu’elle peut devenir. Le gland porte en puissance le chêne. L’actualisation de cette puissance constitue son accomplissement.</p><p>Transposée à l’existence humaine, cette idée implique que nous portons en nous des dispositions, des formes possibles, qui ne demandent qu’à être réalisées. La vie ne serait pas une simple succession d’événements contingents, mais un processus d’actualisation progressive.</p><figure><img alt="L’École d’Athènes, Raphaël (1510): Platon et Aristote entourés de philosophes antiques" loading="lazy" width="900" height="496" src="../assets/img/cogito-001-fig3-ecole-athenes.jpg"/><figcaption>L’École d’Athènes, Raphaël (1510): Platon et Aristote entourés de philosophes antiques</figcaption></figure><p>Cette perspective repose sur une anthropologie exigeante : elle suppose que l’homme a une nature, et que cette nature contient une orientation. On peut contester ce présupposé. Mais il offre une cohérence conceptuelle à l’intuition développée ici : vivre, ce n’est pas inventer arbitrairement son identité, c’est découvrir par l’expérience ce que l’on porte en puissance.</p><hr/><h2><strong>Conclusion</strong></h2><p>Ce modèle n’a pas vocation à exclure les autres. Au contraire. Avoir plusieurs modèles de pensée permet de prendre de la hauteur sur sa propre existence.</p><p>Celui-ci est simplement une proposition : considérer que l’on porte en soi une ligne idéale, et que vivre consiste à s’en rapprocher par itérations successives. Si ce modèle t’aide à clarifier ne serait-ce qu’un peu qui tu es, ce vers quoi tu tends, alors il aura rempli sa fonction.</p><p>A bientôt pour de nouvelles réflexions, </p><p>Elouan</p>"""

INTRACOGITO_66_BODY = """<p>✹ L’édition d’aujourd’hui <em>d’Intracogito</em> propose des réflexions sur l’héritage entendu comme ce que l’on laisse au monde après notre passage.</p><p><strong>Réflexion № 01 :</strong></p><blockquote><p>Une civilisation se mesure à ce qu’elle pense devoir à ses morts.</p><p><strong>Hannah Arendt</strong></p></blockquote><p><em>~ Entre les lignes :</em></p><blockquote><p>Chaque mot qu’on prononce, chaque loi, chaque route a été façonné par des gens qui ne sont plus là. Une société qui se sent redevable envers ses morts (garde ses mémoires, entretient ses cimetières, refuse d’oublier) reconnaît qu’elle n’est pas née d’elle-même. Une société qui, elle, ne pense rien devoir à son passé n’a alors aucune raison de laisser quoi que ce soit aux suivants.</p></blockquote><hr/><p><strong>Réflexion № 02 :</strong></p><blockquote><p>Ne détruis jamais une clôture avant d’avoir compris pourquoi elle a été construite. Elle retient peut-être les loups dont tu ignores l’existence.</p><p><strong>G. K. Chesterton</strong></p></blockquote><p><em>~ Entre les lignes :</em></p><blockquote><p>Faire table rase est un réflexe de jeunesse : s’indigner contre des règles ou des institutions d’un autre temps nourrit l’élan d’innovation. Mais le temps est un bon filtre. À l’image des mythes qui survivent aux empires, ce qui dure a souvent survécu parce qu’il répondait à quelque chose. Durer ne légitime rien mais doit inciter à une forme d’humilité avant de démolir.</p></blockquote><hr/><p><strong>Réflexion № 03 :</strong></p><blockquote><p>Chaque génération doit, dans une relative opacité, découvrir sa mission, la remplir ou la trahir.</p><p>Frantz Fanon</p></blockquote><p><em>~ Entre les lignes :</em></p><blockquote><p>Personne ne remet de feuille de route à une génération. Les enfants de l’après-guerre avaient une mission lisible : reconstruire. Aujourd’hui, c’est beaucoup plus difficile, il n’y a que des tendances, des signaux faibles. Le devoir devient alors de déchiffrer ce flou. Ensuite, on se construit en alignement avec cet héritage, ou bien contre lui.</p></blockquote><hr/><p><strong>Réflexion № 04 :</strong></p><blockquote><p>Ce que tu laisses derrière toi n’est pas ce qui est gravé dans le marbre. C’est ce qui est tissé dans la vie des autres.</p><p><strong>Périclès</strong></p></blockquote><p><em>~ Entre les lignes :</em></p><blockquote><p>Une belle maison, une carrière réussie : tout ça se vend, se partage, s’abîme. Ce qui traverse vraiment le temps est immatériel : un souvenir, un échange, une façon d’aimer qu’on retrouve chez ses enfants. Ces traces se dégradent moins vite. Et elles pèsent lourd : elles transmettent de l’espoir et une énergie particulière.</p></blockquote>"""

COGITO_002_BODY = """<h2>Une question mal posée</h2>
<p>Il y a 5 ans, j’ai eu une discussion avec une amie qui venait de courir un marathon. À cette époque, ayant moi-même envie d’en courir un, je lui ai demandé, assez naïvement, comment elle avait vécu la course, si “elle n’avait pas trop souffert”.</p>
<p>Elle m’a répondu que cette question ne s’était pas posée. Elle courait à la mémoire d’un proche perdu récemment. Dans ce contexte, la souffrance n’était pas absente, mais elle était devenue secondaire.</p>
<p>Ce moment a été un premier déclic. Il m’a fait réaliser qu’il existe des situations difficiles dans lesquelles la souffrance n’est plus un problème en soi. À partir de ce constat, la perception qu’on en a change complètement.</p>
<p>L’objectif de cet essai est de revenir sur cette intuition : comprendre ce que l’on met derrière la souffrance, et proposer une manière de la sublimer.</p>
<h2>Ce que cela suppose</h2>
<p>Le terme de souffrance est souvent utilisé de manière large, sans distinction claire entre la douleur physique, l’inconfort mental, la frustration ou le sentiment d’absurdité. Pourtant, ces dimensions ne recouvrent pas exactement la même réalité.</p>
<p>L’hypothèse qui guide cet essai est la suivante : ce qui rend la souffrance difficile à supporter n’est pas uniquement son intensité, mais la place qu’elle occupe dans notre existence, et la manière dont nous l’interprétons. Une même expérience peut être vécue comme insupportable ou comme nécessaire selon le cadre dans lequel elle s’inscrit.</p>
<p>Ce raisonnement s’appuie sur trois piliers que j’essaie d’articuler ensemble : la pensée de certains philosophes qui ont fait de la souffrance un objet central, un mécanisme neurobiologique qui explique pourquoi le sens agit concrètement sur la douleur, et ma propre expérience.</p>
<hr/>
<h2>L’homme qui tenait debout dans les camps</h2>
<p>Viktor Frankl, psychiatre autrichien, a survécu à quatre camps de concentration nazis : Auschwitz, Dachau, Kaufering, Türkheim. Ce qu’il y a observé n’est pas de l’ordre de la théorie, c’est une constatation arrachée à l’expérience la plus extrême qui soit.</p>
<figure><img alt="Victor Frankl (1905-1997)" loading="lazy" width="1100" height="407" src="../assets/img/cogito-002-fig1-victor-frankl.jpg"/><figcaption>Victor Frankl (1905-1997)</figcaption></figure>
<p>Dans des conditions où tout est retiré, liberté, dignité, chaleur, nourriture, il observe que certains tiennent quand d’autres s’effondrent. Et ce qui les distingue n’est pas la force physique, ni même le hasard des conditions. C’est la capacité à maintenir une raison d’être.</p>
<p>Certains survivaient parce qu’ils pensaient à retrouver un proche. D’autres parce qu’ils portaient en eux une œuvre inachevée, un témoignage à rendre, une promesse à honorer. Frankl lui-même pensait à sa femme, dont il ne savait pas encore qu’elle était morte. Cette pensée l’a maintenu debout.</p>
<p>Son intuition centrale, qu’il développera ensuite dans Man’s Search for Meaning : on peut supporter presque n’importe quel comment si l’on a un pourquoi suffisamment fort. La souffrance ne disparaît pas, mais elle cesse d’être absurde dès lors qu’elle s’inscrit dans une direction. Elle n’est plus simplement subie : elle devient portée . Et ce déplacement change tout.</p>
<hr/>
<h2>Choisir sa souffrance</h2>
<p>Il y a une citation de Sahil Bloom que j’aime beaucoup et qui éclaire ce point de manière directe :</p>
<blockquote><p>Il est difficile de construire des relations profondes et sincères. Mais il est aussi difficile de rester en surface avec tout le monde. Il est difficile de bâtir le corps qu’on désire. Mais il est tout aussi difficile de le voir se détériorer faute d’usage. Il est difficile de créer une vie pleine de sens. Mais vivre sans but est une autre forme de souffrance. Choisis ta souffrance.</p></blockquote>
<p>Ce que cette citation met en lumière, c’est que la souffrance n’est pas une anomalie à corriger. Elle fait partie de la condition humaine. La question n’est donc pas comment l’éviter, mais laquelle choisir et pourquoi .</p>
<p>Une fois qu’on admet ça, la question n’est plus “comment souffrir le moins possible”, mais “est-ce que cette souffrance me sert à construire quelque chose ?” Est-ce qu’elle me rapproche d’une version de moi-même plus accomplie, d’une vie qui correspond davantage à qui je suis, à ce vers quoi je tends ?</p>
<p>Si l’on croit qu’il existe en chacun de nous une ligne idéale à approcher par itérations, alors la souffrance orientée vers cette ligne n’est pas un problème. C’est un passage obligé.</p>
<hr/>
<h2>Quand la douleur devient un carburant</h2>
<p>Ce cadre ne repose pas uniquement sur une intuition philosophique. Il trouve un ancrage neurobiologique dans le fonctionnement du circuit de la récompense.</p>
<p>La dopamine oriente nos comportements en fonction des bénéfices anticipés . Elle ne s’active pas seulement lorsque le plaisir est obtenu, mais surtout lorsqu’il est attendu. Un effort inscrit dans une trajectoire claire : s’entraîner, construire une relation, poursuivre un projet, est perçu par le cerveau comme un chemin vers une récompense. Ce mécanisme rend la douleur, physique ou psychologique, beaucoup plus tolérable. Elle est portée par quelque chose de plus grand qu’elle.</p>
<p>À l’inverse, lorsque la souffrance n’est reliée à aucune finalité, il se produit quelque chose de plus lourd : non seulement la douleur est là, mais la dopamine chute, et avec elle arrive la frustration, le sentiment de manque, l’impression que rien ne vaut la peine. C’est une double peine. On ne souffre plus pour quelque chose : on souffre, et en plus on ressent l’absence de sens comme une douleur supplémentaire.</p>
<p>Ce n’est donc pas la présence de la souffrance qui détermine notre expérience. C’est sa place dans le circuit : comme passage vers un bien, ou comme impasse.</p>
<figure><img alt="Illustration simplifiée du circuit de la récompense" loading="lazy" width="1100" height="733" src="../assets/img/cogito-002-fig2-circuit-recompense.jpg"/><figcaption>Illustration simplifiée du circuit de la récompense</figcaption></figure>
<hr/>
<h2>L’éternel insatisfait</h2>
<p>Il y a un danger dans ce raisonnement qu’il faut nommer clairement : celui de l’éternel insatisfait. Cette figure du développement personnel à outrance qui se dit chaque matin qu’il doit faire mieux, aller plus loin, retarder encore le plaisir au profit d’un futur hypothétique. Et qui finit par se demander, à cinquante ans : quand est-ce que je profite, au fond ?</p>
<p>Endurer pour quelque chose de futur est vertueux jusqu’à un certain point. Mais si ce point n’est jamais atteint, si la célébration est toujours remise à plus tard, alors on passe à côté de l’essentiel.</p>
<p>S’entraîner à fond, oui. Mais aussi apprendre à célébrer à fond : une course terminée, un projet livré, une promotion reçue. Passer du temps sans agenda avec les gens qu’on aime. Regarder derrière soi et laisser entrer la fierté. Ces phases ne sont pas des pauses dans la vie : elles en font partie. Elles justifient l’effort, elles lui donnent une saveur. Et cette logique de cycles est la seule qui soit vraiment viable sur le long terme.</p>
<hr/>
<h2>Ma relation personnelle à la souffrance</h2>
<p>Il y a quelques mois, j’ai couru un ultra-trail, une course de plus de 24 heures. Là où l’entraînement et la motivation ont leurs limites, et où quelque chose de plus fondamental prend le relais.</p>
<p>Dans ce type d’épreuve, une question revient inévitablement. Pourquoi je me fais autant de mal ? À quoi ça sert ? Je pourrais être chez moi. C’est une question honnête, et le corps la pose avec une insistance croissante.</p>
<p>Ce qui se passe à ce moment-là est intéressant : on ne peut plus simuler. Il n’y a plus de réponse de façade qui tienne. Les raisons superficielles s’évaporent face à la douleur réelle. Et il ne reste que le pourquoi profond, ce “mental” qu’on a ou qu’on n’a pas.</p>
<p>Dans mon cas, ce pourquoi avait plusieurs visages. Je courais avec mon meilleur ami et cette course était le point d’arrivée d’un an de préparation partagée, la preuve concrète d’une transformation qu’on avait faite ensemble. J’avais des proches sur le parcours qui m’assistaient et m’encourageaient et au fond de moi, je voulais les rendre fiers, inspirer à travers cet effort.</p>
<p>Ces raisons-là ont tenu. Pas parce qu’elles supprimaient la douleur, mais parce qu’elles lui donnaient un sens. Et c’est exactement ce que Frankl avait observé dans les camps, à une échelle infiniment plus grave : le pourquoi change l’expérience du comment . Si on est aligné avec ses raisons profondes, la souffrance devient au service de quelque chose. Et il y a dans cette dynamique quelque chose de presque noble.</p>
<hr/>
<h2>Sisyphe et la question du sens</h2>
<figure><img alt="Illustration de Sisyphe accomplissant son supplice" loading="lazy" width="1100" height="567" src="../assets/img/cogito-002-fig3-sisyphe.jpg"/><figcaption>Illustration de Sisyphe accomplissant son supplice</figcaption></figure>
<p>Albert Camus part d’un constat que je partage : ce qui rend la souffrance vraiment insupportable, ce n’est pas son intensité. C’est son absurdité. La question à quoi bon ?, sans réponse, est plus difficile à vivre que la douleur elle-même.</p>
<p>Mais à partir de là, Camus tire une conclusion différente. Pour lui, le monde est fondamentalement absurde, il n’existe pas de sens inscrit dans les choses, pas de direction naturelle de l’existence. Face à cette absurdité, il propose non pas de se leurrer, mais de se révolter. Accepter l’absurde lucidement, refuser le suicide philosophique qui consiste à inventer un sens artificiel, et vivre malgré, intensément, pleinement, sans illusion. Sisyphe pousse son rocher infiniment et Camus nous demande de l’imaginer heureux.</p>
<p>Là où Camus refuse de donner du sens parce que le monde n’en offre pas, je pense qu’on peut choisir d’en construire un volontairement, non pas parce que c’est vrai au sens objectif, mais parce que c’est utile, voire nécessaire. Ce n’est pas de la naïveté. C’est une croyance utile.</p>
<p>Et cet essai est précisément une tentative de justifier pourquoi : inscrire ses épreuves dans une quête, celle de qui l’on est, de ce vers quoi l’on tend, de cette ligne idéale dont je parlais dans <a href="../essais/la-quete-de-notre-destinee.html">le premier Cogito</a>, c’est ce qui transforme la souffrance en carburant plutôt qu’en impasse.</p>
<hr/>
<h2>Le retour du héros</h2>
<p>Toute l’histoire de l’humanité raconte la même chose sous des formes différentes. L’Odyssée, les grands récits mythologiques, les films qui nous marquent, suivent tous la même structure. Un héros part, traverse des épreuves, affronte des monstres, perd parfois, doute, tient quand même, et finit par rentrer transformé.</p>
<p>Ce qui rend la fin belle, ce n’est pas l’arrivée en elle-même. C’est le chemin qu’il a fallu emprunter pour y arriver. Sans le cyclope, sans Charybde et Scylla, sans les années de mer et de tempête, le retour d’Ulysse à Ithaque ne signifie rien.</p>
<figure><img alt="Ulysse attaché au mât pour résister aux sirènes." loading="lazy" width="1100" height="733" src="../assets/img/cogito-002-fig4-ulysse-sirenes.jpg"/><figcaption>Ulysse attaché au mât pour résister aux sirènes.</figcaption></figure>
<p>Je crois que chaque existence fonctionne de la même manière. On ne peut être fier de quelque chose qui ne nous a rien coûté. La victoire n’a de saveur que parce qu’il y a eu une difficulté à vaincre. La fierté n’existe que parce qu’il y a eu un moment où l’abandon était possible et qu’on a choisi de continuer.</p>
<p>La souffrance est inévitable. Ce n’est pas une opinion c’est un constat. A partir de là, on peut choisir par moment quelle souffrance endurer et pourquoi.</p>
<p>Lorsqu’elle s’inscrit dans une quête, celle de notre propre Ithaque, elle cesse d’être un obstacle. Elle devient la matière même de l’histoire qu’on est en train d’écrire. Mon amie qui courait ce marathon n’avait pas aboli la souffrance. Elle lui avait simplement donné un nom. Et ce nom avait tout changé.</p>
<p>À bientôt pour de nouvelles réflexions</p>
<p>Elouan</p>"""

COGITO_003_BODY = """<h2>Introduction</h2>
<p>Il y a des citations philosophiques si célèbres qu’elles finissent par se charger d’un sens bien plus étroit que celui qu’elles portaient. Celle-ci en est l’exemple parfait.</p>
<blockquote><p>« Le cœur a ses raisons que la raison ne connaît point. »</p><p><strong>Pascal</strong></p></blockquote>
<p>On y voit généralement un appel à l’amour, une permission de ne pas réfléchir. Mais Pascal, mathématicien, ne parlait pas d’amour mais de foi religieuse. Il a voulu mettre en avant quelque chose de plus fondamental : l’idée que certaines vérités se ressentent avant de se démontrer. Qu’elles sont premières .</p>
<p>C’est cette forme “d’intuition” que j’ai envie de réhabiliter aujourd’hui, non pas comme un don mystérieux réservé à quelques-uns, mais comme quelque chose que l’on peut apprendre à écouter. Et avec elle, une question pratique : comment créer les conditions pour que cette intuition apparaisse ?</p>
<h2>La proposition de Pascal</h2>
<p>Pour comprendre Pascal, il faut comprendre qui il était. C’était un mathématicien qui a posé les bases du calcul des probabilités au XVIIe siècle. Un homme qui pensait en termes de démonstration, de preuve, de structure.</p>
<p>Et c’est justement parce qu’il était mathématicien qu’il a compris une chose que beaucoup refusent d’admettre : tout raisonnement repose sur des fondations qui, elles, ne se démontrent pas.</p>
<p>En mathématiques, on accepte comme évident que deux droites parallèles ne se croiseront jamais. Ce n’est pas démontré, c’est posé. C’est ce que l’on nomme un “axiome”. Et c’est sur ces piliers non démontrables que repose toute la logique mathématique.</p>
<figure><img alt="Schéma illustrant un axiome en mathématiques" loading="lazy" width="1100" height="513" src="../assets/img/cogito-003-fig1-axiome-mathematiques.jpg"/></figure>
<p>Pascal dans sa citation dit la même chose de la foi religieuse : elle est cet axiome. On ne peut pas la démontrer et c’est précisément pour ça qu’elle précède la raison. La raison ne fait que confirmer, après coup, ce que le cœur sait déjà. Ainsi, il formule :</p>
<blockquote><p>« Les principes se sentent, les propositions se concluent. »</p></blockquote>
<p>Appliqué à l’amour, puisque c’est ainsi qu’on entend le plus souvent cette phrase, ce raisonnement met en avant que l’on tombe amoureux d’abord.</p>
<p>Ensuite, on cherche à se le rationaliser : ses yeux, son humour, sa façon d’être. Mais ce ne sont pas ces qualités qui causent l’amour. La preuve est simple : si on les énumère à quelqu’un d’autre, cette personne ne tombera pas amoureuse. On ne tombe pas amoureux de qualités. On tombe amoureux de quelque chose de premier et la raison arrive après, pour habiller ce que le cœur savait déjà.</p>
<hr/>
<h2>Le piège de l’intuition</h2>
<p>Mais voilà où ça devient délicat.</p>
<p>Si les vérités du cœur sont des intuitions premières, on pourrait en déduire qu’elles sont toujours immédiatement perceptibles. Que si ta vocation existe, elle s’impose. Que si ce n’est pas évident, c’est qu’elle existe pas.</p>
<p>On imagine tous cet enfant qui sait à huit ans qu’il sera pilote de chasse. Tout est tracé, clair, intuitif. Il ne reste plus qu’à travailler. Et il y a quelque chose d’attrayant dans cette image, un confort, une simplicité que beaucoup envient à l’aune d’une société vidée de sens et de direction.</p>
<figure><img alt="Le Petit Prince, Mark Osborne (2015), d'après Antoine de Saint-Exupéry" loading="lazy" width="960" height="527" src="../assets/img/cogito-003-fig2-petit-prince.jpg"/><figcaption>Le Petit Prince, Mark Osborne (2015), d'après Antoine de Saint-Exupéry</figcaption></figure>
<p>La plupart des gens ne sont pas cet enfant. Et pour eux, le raisonnement devient : si ce n’est pas évident, c’est peut-être que ça n’existe pas. Si je ne suis pas passionné d’un sujet ou éperdument amoureux au premier regard alors c’est que ce n’est pas la bonne passion ou la bonne personne.</p>
<p>C’est à mon sens un raisonnement faux et potentiellement dangereux.</p>
<hr/>
<h2>L’intuition en tant que perspective</h2>
<p>A titre personnel, l’exemple de ma pratique sportive illustre bien l’idée d’intuition en tant que perpective.</p>
<p>Voici les sports que j’ai pratiqués dans différents clubs au fil des années : le kayak, le roller, le surf, le VTT, l’athlétisme, la course à pied, le street workout. Ces activités me sont souvent apparues comme variées, sans logique commune apparente.</p>
<p>Avec le recul et une nouvelle perspective, j’ai réalisé récemment qu’un dénominateur commun existait. La nature. Chaque pratique est reliée à un lieu, un élément ou un espace extérieur.</p>
<p>Ce n’est pas que la vérité était absente. C’est qu’il fallait trouver le bon angle pour la voir. A mon sens, si l’intuition n’est pas toujours donnée d’emblée, notre chemin éclairera toujours nos décisions prisent avec le coeur.</p>
<hr/>
<h2>Santiago et le trésor</h2>
<p>Dans L’Alchimiste de Paulo Coelho, un jeune berger andalou nommé Santiago rêve d’un trésor caché au pied des Pyramides d’Égypte. Il quitte tout. Il traverse l’Espagne, puis l’Afrique du Nord, apprend à lire les signes du désert, rencontre des sages, surmonte des épreuves intérieures autant qu’extérieures.</p>
<p>Au bout du voyage, il découvre que le trésor se trouvait là où il avait dormi la première nuit : dans une vieille église en ruines, en Espagne, à des milliers de kilomètres de là.</p>
<figure><img alt="L'Alchimiste, de Paulo Coelho" loading="lazy" width="880" height="346" src="../assets/img/cogito-003-fig3-alchimiste-coelho.jpg"/><figcaption>L'Alchimiste, de Paulo Coelho</figcaption></figure>
<p>Ce n’est pas une histoire sur l’inutilité du voyage. C’est l’inverse. Sans la traversée du désert, sans chaque étape arrachée, Santiago n’aurait jamais eu la perspective nécessaire pour voir ce qui avait toujours été là. Le voyage n’était pas un détour. C’était la condition de la révélation.</p>
<p>Les intuitions profondes fonctionnent parfois de la même façon. Elles sont là. Mais elles attendent qu’on ait fait suffisamment de chemin pour les reconnaître.</p>
<p>Je n’entends pas le terme '“chemin” ici comme une période nécessairement longue. On l’associe souvent à l’âge ou l’expérience, mais on peut avoir 60 ans et moins d’intuition qu’un jeune de 30 ans qui a vécu et agit en conscience en décidant d’affronter ses grands questionnements.</p>
<blockquote><p>Tu ne pourras jamais fuir ton cœur. Alors autant écouter ce qu’il a à te dire</p><p><strong>Paulo Coelho, L’alchimiste (1988)</strong></p></blockquote>
<hr/>
<h2>Ce que l’intuition mérite</h2>
<p>Alors que faire quand rien n’est évident ?</p>
<p>D’abord, ne pas conclure trop vite que l’on a pas d’instinct. L’absence d’intuition ne veut pas dire absence de vérité, cela veut dire qu’on n’a peut-être pas encore la bonne perspective.</p>
<p>Pour y accéder, j’ai personnellement une philosophie d’itérations que j’ai développée dans mon premier essai : <a href="../essais/la-quete-de-notre-destinee.html">Cogito #001</a> . Je suis persuadé que l’action et l’inertie nous éclaire sur ce que l’on veut et qui on est.</p>
<p>Ainsi, certaines vérités dites '“du coeur” se sentent avant de se comprendre. Et les ignorer parce qu’elles ne s’expriment pas en langage rationnel, c’est passer à côté de quelque chose d’à mon sens essentiel.</p>
<p>Qui sur son lit de mort regrette d’avoir trop écouté son intuition ?</p>
<p>Alors peut-être qu’il est temps de lui redonner sa force. Travailler sur soi pour qu’elle nous soit audible plus souvent et avoir le courage de l’écouter quand on l’entend.</p>
<p>À bientôt pour de nouvelles réflexions</p>
<p>Elouan</p>"""

COGITO_004_BODY = """<h2>Introduction</h2>
<p>Il y a des idées qui ne s’imposent pas d’un coup. Elles reviennent, sous des formes différentes, à des moments différents.</p>
<p>La première fois que j’ai été confronté au bouddhisme, c’était à travers des échanges avec mon père, dans une période marquée par une épreuve personnelle. Ce qui m’a frappé, ce n’était pas la doctrine : c’était la manière dont cette philosophie semblait offrir une façon différente d’habiter la souffrance. Presque apaisée.</p>
<p>Quelques années plus tard, en Thaïlande, j’ai passé une soirée avec un moine bouddhiste à qui j’ai pu poser toutes mes questions. Ce n’était plus une idée abstraite, mais une manière de vivre incarnée, choisie, cohérente.</p>
<p>Enfin, au Népal, j’ai vécu un mois dans une famille bouddhiste. L’enseignement que j’ai tiré n’était pas dans un discours ou une théorie mais dans des moments de vie.</p>
<p>À chaque fois, le même constat : cette philosophie semblait fonctionner pour ceux qui la vivaient .</p>
<p>C’est cette observation qui est au cœur de cet essai. Le bouddhisme s’organise autour de quatre nobles vérités. Les trois premières sont un diagnostic : la souffrance existe, elle a une origine, elle peut cesser. La quatrième est différente. On l’appelle “la vérité du chemin”. Et c’est cette vérité qui, à titre personnel, m’a le plus marqué et que je souhaite mettre en avant aujourd’hui.</p>
<hr/>
<h2>Les quatre nobles vérités : un diagnostic</h2>
<p>Le bouddhisme pose d’abord un constat que peu de traditions osent formuler aussi directement.</p>
<p>La première noble vérité, dukkha, affirme que l’existence est structurellement marquée par une forme d’insatisfaction. Non pas une souffrance intense au sens dramatique, mais un inconfort diffus, inhérent au fait que rien ne dure.</p>
<p>La deuxième en identifie l’origine : le désir et l’attachement, tanhā . Nous cherchons à fixer ce qui est, par nature, instable : des situations, des relations, des identités.</p>
<p>La troisième affirme qu’une sortie est possible. L’insatisfaction n’est pas une fatalité.</p>
<p>Et la quatrième propose un chemin, le Noble Sentier Octuple qui est fait de huit dimensions : vision juste, intention juste, parole juste, action juste, moyen d’existence juste, effort juste, pleine conscience, concentration.</p>
<p>Cette quatrième vérité est d’une nature différente. Elle ne décrit pas le monde. Elle propose une manière de le traverser. Et elle exige quelque chose que les trois premières n’exigent pas : qu’on la parcoure soi-même.</p>
<figure><img alt="Schéma des quatre nobles vérités du bouddhisme" loading="lazy" width="1100" height="550" src="../assets/img/cogito-004-fig1-quatre-nobles-verites.jpg"/></figure>
<hr/>
<h2>Bouddha n’est pas un modèle : il est une preuve</h2>
<p>C’est en Thaïlande que j’ai compris quelque chose qui m’a profondément marqué.</p>
<p>En discutant avec un moine durant une soirée où l’on était coincé dans une auberge suite à un épisode de pluie importante, j’ai pu lui ai posé toutes les questions possibles.</p>
<p>J’avais en particulier envie de comprendre pourquoi on m’a toujours dit que le bouddhisme était une philosophie et pas une religion mais, qu’en deux jours ici, j’ai visité énormément de temples ou tout le monde “priait” Bouddha.</p>
<p>Sa réponse a été simple. Il m’a expliqué que ceux qui prient ne sont pas dans une posture de demande. Ils ne cherchent pas à fléchir une volonté divine ou à modifier le cours des événements. Ils demandent la force à un être éclairé qui a lui-même parcouru son chemin, d’avoir la lucidité de trouver le leur.</p>
<p>Cette distinction m’a beaucoup frappé. Et elle rejoint une conviction que j’ai développée dans mon essai <a href="../essais/la-quete-de-notre-destinee.html">Cogito #001 : La quête de notre destinée</a> . Notre chemin nous est propre. Il ne peut pas être délégué, ni imité, ni copié.</p>
<figure><img alt="Statue de Bouddha, Gandhâra" loading="lazy" width="1100" height="586" src="../assets/img/cogito-004-fig2-statue-bouddha.jpg"/><figcaption>Statue de Bouddha, Gandhâra</figcaption></figure>
<h2>Le danger de la voie par défaut</h2>
<p>Cet enseignement a particulièrement résonné avec moi. Dans le cadre de mes études, une voie “par défaut” est clairement tracée pour tous les élèves. Tout pousse vers elle : les classements, les recruteurs, les alumni, la culture ambiante. Si on ne se pose pas activement la question “ est-ce que ce chemin me correspond vraiment ? ”, tout est structuré pour qu’on ne se la pose jamais. Cette pression sociale et ce conformisme sont puissants précisément parce qu’ils ne sont pas explicites. C’est le propre de la manipulation qui repose sur une “illusion de liberté” : personne ne t’obligera jamais à faire tel ou tel choix de carrière.</p>
<p>La prière bouddhiste, dans ce sens, est une pratique de lucidité. Permets-moi de comprendre ce à quoi j’aspire vraiment. Et non : donne-moi ce que je veux. Plutôt : donne-moi la clarté de savoir ce que je dois chercher.</p>
<p>Le Bouddha n’est pas un modèle à imiter. Il est la preuve qu’un chemin est possible. Et que ce chemin, chacun doit l’emprunter lui-même.</p>
<hr/>
<h2>Siddhartha : la sagesse comme expérience</h2>
<p>C’est dans Siddhartha de Hermann Hesse que cette idée prend peut-être sa forme la plus belle.</p>
<p>Le personnage ne trouve justement pas la sagesse en suivant Bouddhac. Il l’entend, il reconnaît sa grandeur, et il part dans la direction opposée. Il traverse l’excès, le plaisir, la richesse, puis l’ascèse la plus radicale. Avant, finalement, de trouver.</p>
<p>Une citation résume ce parcours :</p>
<blockquote><p>Comme il est bon d’avoir appris à ses dépens ce que l’on doit savoir.</p><p><strong>Herman Hesse, Siddhartha</strong></p></blockquote>
<p>Ce n’est pas de la résignation. C’est une reconnaissance : certaines choses ne peuvent pas être enseignées. Elles doivent être vécues.</p>
<figure><img alt="Couverture du livre Siddhartha de Hermann Hesse" loading="lazy" width="1100" height="550" src="../assets/img/cogito-004-fig3-siddhartha-hesse.jpg"/><figcaption>Couverture du livre Siddhartha de Hermann Hesse</figcaption></figure>
<p>La tradition zen illustre cela différemment.</p>
<p>Un élève demande à un maître combien de temps il lui faudra pour atteindre la maîtrise. Le maître répond : “Dix ans.” L’élève insiste : “Et si je travaille deux fois plus ?” Le maître répond : “Alors vingt ans.”</p>
<p>La sagesse ne se force pas. Elle se construit. Dans le temps, dans l’expérience, dans ce qu’on accepte de traverser.</p>
<hr/>
<h2>Le mouvement comme nature profonde</h2>
<p>La vérité du chemin repose sur une transformation personnelle. Mais pour accepter de se transformer, il faut d’abord accepter deux choses que le bouddhisme pose comme fondamentales : anattā (non-soi) et anicca (impermanence).</p>
<p>Anattā affirme que ce que nous appelons “moi” n’est pas une entité stable. C’est un agrégat de sensations, de pensées, d’émotions en mouvement constant. Si on croit avoir une identité figée, marcher sur un chemin de transformation devient une menace. Anattā retourne cette logique : tu es déjà un processus en mouvement. Et anicca complète l’idée : rien ne dure. S’accrocher à ce qui change inévitablement, c’est précisément la source de la souffrance décrite par les trois premières vérités.</p>
<p>Cette idée a une résonance scientifique intéressante. Les neurosciences confirment qu’il n’existe pas de “soi central” dans le cerveau : le soi est une construction, un récit que le cerveau se raconte. Et les recherches sur la contagion émotionnelle montrent que nos états internes ne sont pas produits de manière isolée : ils sont en interaction constante avec ce qui nous entourent. Ce que le bouddhisme intuitionne depuis des siècles, la science commence à en décrire les mécanismes.</p>
<p>Concrètement, cela m’a conduit à accorder beaucoup plus d’importance à ce que je laisse entrer dans ma vie : les lieux où l’on passe du temps, les relations, les mots et l’énergie transmise dans nos discours. Si nous ne sommes pas imperméables, alors ce qui nous entoure participe de ce que nous devenons.</p>
<hr/>
<h2>Le piège du détachement</h2>
<p>Frédéric Lenoir, dans Petit traité de vie intérieure, met en avant une limite à cette philosophie que je trouve juste : le non-attachement, poussé jusqu’à son terme logique, peut conduire à une forme de retrait du monde. Bouddha recommande le non-attachement à tous les êtres vivants, y compris ceux qui nous sont les plus proches.</p>
<figure><img alt="Portrait de Frédéric Lenoir, auteur de Petit traité de vie intérieure" loading="lazy" width="1100" height="632" src="../assets/img/cogito-004-fig4-frederic-lenoir.jpg"/><figcaption>Portrait de Frédéric Lenoir, auteur de Petit traité de vie intérieure</figcaption></figure>
<p>Lenoir, ayant passé beaucoup de temps dans l’Himalaya, a observé des moines ayant médité parfois vingt ou trente ans, mais qui ont pleuré à la mort de leur maître spirituel. Ils s’étaient profondément attachés à lui. Et il en tire une observation que je partage : l’être humain, pour s’épanouir pleinement, tisse naturellement des liens affectifs forts. L’amour et l’amitié, donnés et reçus, ne sont pas une faiblesse. Ils sont une condition de la vie intérieure.</p>
<p>Je comprends la logique du détachement pour les biens matériels mais je ne souhaite pas l’appliquer de manière absolue. S’attacher, c’est prendre un risque. C’est aussi la condition pour vivre des relations intenses.</p>
<p>Et c’est peut-être là l’enseignement le plus précieux : cette philosophie ne propose pas un modèle unique. Elle propose un chemin. À chacun de décider jusqu’où il va.</p>
<hr/>
<h2>Conclusion</h2>
<p>Le bouddhisme ne m’a pas apporté des réponses définitives.</p>
<p>Il m’a offert quelque chose de plus utile : des cadres. Pour penser l’impermanence sans en être paralysé. Pour distinguer un désir qui construit d’un attachement qui fige. Pour comprendre que la sagesse n’est pas une destination, mais une manière de marcher.</p>
<p>À bientôt pour de nouvelles réflexions</p>
<p>Elouan</p>
<p>PS : En creusant le sujet, je suis tombé sur une vidéo assez intrigante sur les cas de réincarnation documentées. Je vous mets le lien si ça vous intéresse.</p>
<p><a href="https://www.youtube.com/watch?v=WCMZFgDiE0k&t=75s" target="_blank" rel="noopener">RÉINCARNATION : Ces Enfants se souviennent de leur Vie Précédente !</a></p>"""

COGITO_005_BODY = """<p>Il y a une chose qui m’a toujours frappé dans les longues courses d’endurance, c’est à quel point, à un moment donné, le corps ne suit plus seul.</p>
<p>Sur une de mes courses dont j’ai parlé dans <a href="../essais/la-matiere-premiere-du-heros.html">Cogito #002</a>, il y a eu des kilomètres où quelque chose d’autre que les jambes courait. La conviction que l’effort avait un sens, que des personnes m’attendaient plus loin sur le parcours, que cette course était l’aboutissement de quelque chose de plus grand qu’elle. Tout cela a rendu mon corps capable d’aller à des endroits qu’il n’aurait pas atteints seul. Des endroits que je ne pensais pas pouvoir atteindre.</p>
<p>Dernièrement, j’ai pris le départ d’un trail en montagne avec une blessure au genou droit encore récente. Beaucoup d’appréhension. Beaucoup de craintes. Mon discours intérieur était centré autour d’une seule peur : aggraver la blessure, surtout en descente. Il ne faut pas que je force. Abandonner reste une option. Fais attention au genou droit.</p>
<p>J’ai abandonné. Mais pas à cause du genou droit. À cause du genou gauche, celui qui n’avait rien.</p>
<p>Je ne dis pas que j’ai provoqué cette blessure par la pensée. Mais la coïncidence m’a fait réfléchir. Quel aurait été le scénario si j’avais abordé cette course différemment, sans cette peur comme boussole intérieure ?</p>
<p>C’est l’idée que j’ai envie d’explorer dans cet essai. À quel point notre vie intérieure : nos pensées, nos convictions, notre rapport à nous-mêmes façonne notre corps ? Et à l’inverse, dans quelle mesure notre état physiologique produit-il notre philosophie ? Que nous apprend la vie des philosophes sur leur philosophie ? Et quelle est, en définitive, la posture la plus utile pour mieux vivre ?</p>
<hr/>
<h2>Un postulat admis, rarement intériorisé</h2>
<p>L’idée que le corps et l’esprit sont liés n’est pas controversée. Elle est même, à bien y regarder, la position la plus ancienne. Le problème n’est donc pas cognitif. Presque tout le monde admet que l’état du corps influence la pensée, que le manque de sommeil altère le jugement, que l’alimentation agit sur l’humeur, que le sport libère.</p>
<figure><img alt="La création du monde, Michel Ange" loading="lazy" width="1024" height="532" src="../assets/img/cogito-005-fig1-creation-michel-ange.jpg"/><figcaption>La création du monde, Michel Ange</figcaption></figure>
<p>Et pourtant.</p>
<p>On estime que 30 à 40 % de la population des pays industrialisés souffre de manque de sommeil chronique. La part d’aliments ultra-transformés dans notre alimentation quotidienne n’a jamais été aussi haute. Ces réalités ne semblent pas vraiment nous inquiéter sur la qualité de la pensée que nous développons.</p>
<p>Nous savons que le corps et l’esprit sont liés. Nous n’en tirons que rarement les conséquences.</p>
<hr/>
<h2>Platon, l’homme aux larges épaules</h2>
<figure><img alt="Les lutteurs, sculpture romaine représentant 2 pancratiastes" loading="lazy" width="1100" height="550" src="../assets/img/cogito-005-fig2-les-lutteurs.jpg"/><figcaption>Les lutteurs, sculpture romaine représentant 2 pancratiastes</figcaption></figure>
<p>Le mot “Platon” vient du grec platos : le large, le costaud. Une des questions est de savoir si le surnom est une métaphore de la grandeur de l’esprit ou un constat physique. Les deux sont peut-être vrais. Platon pratiquait le pancrace, l’ancêtre du MMA, un sport de combat complet qui mêlait lutte et frappe.</p>
<p>Il y a dans cette image quelque chose qui dérange notre vision moderne du “philosophe”. Le philosophe athlète, qui plus est dans un sport plutôt violent, n’est pas ce à quoi on nous a habitués. Durant l’Antiquité, c’était la norme.</p>
<p>Les Grecs ne se posaient pas la question de l’articulation entre corps et esprit parce que cette question, pour eux, ne se posait tout simplement pas. Mathema signifiait la connaissance en général. Un philosophe était mathématicien, rhéteur, parfois homme politique, souvent sportif. La sectorisation avec le penseur pâle d’un côté, l’athlète de l’autre, est une dissociation moderne. Et comme chaque changement, il a des avantages, et un coût.</p>
<p>Ce coût, c’est la perte d’une certaine approche holistique. En apprenant à spécialiser et à compartimenter, nous avons parfois oublié que la discipline intellectuelle et la discipline physique ne sont pas deux pratiques parallèles : elles se nourrissent l’une l’autre.</p>
<hr/>
<h2>Schopenhauer, l’architecte de son malheur ?</h2>
<p>Une fois qu’on admet cette interdépendance, vient la question classique de l’œuf et de la poule. Qu’est-ce qui influence quoi en premier : la pensée ou le corps ? La vie de Schopenhauer offre une ébauche de réponse à cette question.</p>
<p>Arthur Schopenhauer est l’un des philosophes les plus pessimistes de l’histoire de la pensée occidentale. Sa formule est connue :</p>
<blockquote><p>La vie oscille entre souffrance et ennui, comme un pendule.</p><p><strong>Schopenhauer, Le monde comme volonté et comme représentation</strong></p></blockquote>
<figure><img alt="Schopenhauer, philosophe pessimiste" loading="lazy" width="1100" height="619" src="../assets/img/cogito-005-fig3-schopenhauer.jpg"/><figcaption>Schopenhauer, philosophe pessimiste</figcaption></figure>
<p>On peut le lire comme un génie qui a mis des mots sur quelque chose de vrai. On peut aussi regarder sa biographie.</p>
<p>Schopenhauer ne pratiquait pas d’activité physique : privé, donc, de dopamine.</p>
<p>Il n’aimait pas les gens, évitait le contact social : privé de sérotonine.</p>
<p>On ne lui connaît pas vraiment d’histoire intime : privé d’endorphines.</p>
<p>Ces trois hormones que le langage commun appelle communément “hormones du bonheur” étaient, dans sa vie, absentes.</p>
<p>Il ne s’agit pas de certifier que la cause de son pessimisme vient de cette “carence” hormonale. Ce serait réducteur pour sa pensée. Mais il y a dans ce constat quelque chose qui donne à réfléchir : un corps durablement privé de ce qui le rend heureux tend à produire une pensée qui considère le malheur comme l’état normal des choses. Peut-être que Schopenhauer n’a pas écrit sur le malheur malgré sa manière de vivre. Peut-être qu’il l’a écrit depuis elle.</p>
<hr/>
<h2>Nietzsche, quand la limite forge la pensée</h2>
<p>Nietzsche avait une santé extrêmement fragile. Des migraines chroniques, une constitution défaillante qui l’a contraint à quitter l’Allemagne pour chercher des cieux plus cléments. Et pourtant, c’est lui qui a théorisé la volonté de puissance, le dépassement de soi, la vitalité comme valeur suprême.</p>
<p>Dans le cadre précédent, Nietzsche est un contre-exemple. Un homme malade qui prône la vitalité, voilà de quoi remettre en cause l’idée selon laquelle “on a la philosophie de sa physiologie.”</p>
<p>Mais il y a une autre lecture possible. Précisément parce que son corps le limitait, Nietzsche a peut-être compris quelque chose que ceux en bonne santé ne voient pas toujours : la vitalité est une conquête quotidienne, pas une donnée. Le corps ne s’assume pas, il se travaille.</p>
<p>Et l’inverse est tout aussi juste. Une philosophie aussi sombre que celle de Schopenhauer aurait probablement été destructrice pour un corps déjà aussi fragile que celui de Nietzsche. Avec le pendule de la souffrance comme unique horizon, avec un système de pensée qui ne justifie pas la vie, on peut se demander s’il aurait eu la force de tenir et d’écrire ses plus beaux ouvrages durant ces années de maladie. La philosophie de la vitalité n’était peut-être pas seulement une idée. C’était peut-être aussi un remède.</p>
<figure><img alt="Le Serment des Horaces, Jacques-Louis David (1784)" loading="lazy" width="1100" height="640" src="../assets/img/cogito-005-fig4-serment-horaces.jpg"/><figcaption>Le Serment des Horaces, Jacques-Louis David (1784)</figcaption></figure>
<hr/>
<h2>La réalité que nos pensées construisent</h2>
<p>On estime qu’un être humain a entre 40 000 et 60 000 pensées par jour. La plupart sont automatiques, inconscientes, répétitives. Ce que l’on se raconte en boucle finit par façonner nos comportements à travers des milliers de micro-décisions invisibles.</p>
<p>Une personne qui commence chaque journée avec la conviction que “ça ne marchera pas” ne va pas changer de vie par la seule force de la pensée. Mais elle va, imperceptiblement, éviter les risques, souffler, abréger les conversations, lâcher les occasions avant qu’elles n’arrivent.</p>
<p>Elle entre dans un cercle : la critique, le retrait, l’interprétation négative de chaque événement. Ces comportements, répétés des milliers de fois, finissent par construire une réalité qui confirme son pessimisme de départ.</p>
<p>Certains poussent cette conclusion encore plus loin, autour de concepts comme la loi de l’attraction, ou encore les vibrations auxquelles on se met. L’idée n’est pas ici de plonger dans ces notions plus intuitives et spirituelles mais leur pertinence n’est pas pour autant à rejeter. Il est facile d’admettre qu’une personne qui rayonne par sa bonne humeur peut, d’une certaine manière, transposer sa joie de vivre dans le réel et dans ses relations. Elle attire différemment. Elle interprète différemment. Elle crée, autour d’elle, une réalité différente, conforme à son monde intérieur.</p>
<p>Et dans l’autre sens, broyer du noir a des conséquences documentées. En 2001, une étude menée sur des religieuses catholiques connue sous le nom de <a href="https://en.wikipedia.org/wiki/Nun_Study" target="_blank" rel="noopener">Nun Study</a> a montré que celles qui exprimaient le plus d’émotions positives dans leurs écrits autobiographiques à 22 ans vivaient en moyenne 10 ans de plus que celles dont les textes étaient les plus neutres ou négatifs. 10 ans.</p>
<p>Les pensées chroniquement négatives élèvent le cortisol sur la durée, perturbent le sommeil, et favorisent les inflammations chroniques. Ce n’est pas une métaphore. C’est de la biologie.</p>
<hr/>
<h2>Ce que l’expérience m’a confirmé</h2>
<p>Les deux courses évoquées en introduction m’ont rappelé, chacune à leur manière, à quel point le lien entre corps et esprit est concret. Pas théorique. Concret, dans les jambes et dans la tête, au moment où l’on cherche à tenir.</p>
<p>C’est pour ça que j’ai valorisé, notamment en classe préparatoire, mon sommeil et la pratique du sport aussi régulièrement que possible. Dans un environnement où la majorité des étudiants fonctionnaient en déficit de sommeil, renonçant aux séances de sport pour travailler par culpabilité autant que par manque de temps, j’avais la conviction que c’était précisément le contraire qui me permettrait de performer au niveau intellectuel demandé.</p>
<p>Cette conviction, je la dois en grande partie à une discussion que j’ai eue avec un proche avant que j’entre en prépa, il m’avait dit quelque chose de simple :</p>
<blockquote><p>“Les personnes qui réussissent leur prépa ne sont pas celles qui travaillent le plus. Ce sont celles qui prennent soin de leur corps, qui dorment, qui font du sport, et qui savent couper.”</p></blockquote>
<p>J’ai eu la chance que ce conseil arrive au bon moment. J’avais déjà, sans vraiment le formuler, fait ce chemin-là. Il a simplement mis des mots sur une intuition que je pressentais.</p>
<hr/>
<h2>Conclusion</h2>
<p>Je reste convaincu aujourd’hui que la manière dont on perçoit le monde, les intentions qu’on prête aux gens, l’énergie qu’on donne et la façon dont on interprète ce qui nous arrive, est l’essentiel. Nous créons notre réalité à partir de nos pensées.</p>
<p>Si ce cadre est orienté vers une philosophie tournée vers la vie, on peut sincèrement créer la réalité que l’on souhaite.</p>
<p>Se nourrir d’une énergie créative dans la manière de voir le monde est à mon sens essentiel. Malgré tous les arguments rationnels, malgré les constats qui peuvent pousser à l’inverse, il y a une formule d’Antonio Gramsci qui conclut bien cet essai.</p>
<blockquote><p>Le pessimisme de la connaissance n’empêche pas l’optimisme de la volonté.</p><p><strong>Antonio Gramsci</strong></p></blockquote>
<p>À bientôt pour de nouvelles réflexions</p>
<p>Elouan</p>"""

COGITO_006_BODY = """<h2>Introduction</h2>
<p>Il y a quelques semaines, un ami m’a dit : “Ah mais toi, tu es vraiment ultra sociable.”</p>
<p>J’ai souri. Parce que dans un autre cercle, celui de mes années de lycée, j’aurais été décrit exactement à l’inverse. Même personne, mais deux identités a priori contradictoires.</p>
<p>J’ai plusieurs cercles sociaux constitués à des époques différentes : le lycée, la prépa, les études supérieures, le cadre professionnel. Dans chacun, les gens m’ont connu à un âge différent et donc m’ont attribué une identité différente.</p>
<p>Cela pose une question : qu’est-ce que l’identité, au fond ? Qu’est-ce qui reste quand tout change ?</p>
<p>La réponse touche peut-être à quelque chose dont la philosophie ne peut pas résoudre seule. À une question de croyance, presque spirituelle. Croire ou non qu’il existe quelque chose de non matériel, une âme, un fil conducteur qui traverse les années malgré les mutations du corps et de l’esprit.</p>
<p>C’est peut-être une croyance utile. Je ne trancherai pas ici.</p>
<p>La question à laquelle je souhaite répondre aujourd’hui est plus pratique : à quoi est-ce que je m’identifie, consciemment ou non ? Et est-ce que ces choix me servent ?</p>
<h2>L’illusion de permanence</h2>
<p>Héraclite l’avait dit : on ne se baigne jamais deux fois dans le même fleuve. Montaigne, deux millénaires plus tard, a poussé l’image encore plus loin :</p>
<blockquote><p>Car tant plus il serrera et pressera ce qui de sa nature coule par tout, tant plus il perdra ce qu’il vouloit tenir et empoigner.</p><p><strong>Montaigne</strong></p></blockquote>
<p>Vouloir saisir ce que l’on est revient à empoigner de l’eau. Les cellules se régénèrent. La manière de penser évolue.</p>
<p>Le bouddhisme, que j’ai exploré dans <a href="../essais/la-verite-du-chemin.html">Cogito #004</a>, va jusqu’à nier l’existence d’un soi stable : anattā, le non-soi. Et les neurosciences confirment qu’il n’existe pas de “moi central” dans le cerveau. Le soi est une narration que l’esprit construit sur lui-même.</p>
<figure><img alt="Moine bouddhiste en marche." loading="lazy" width="1100" height="631" src="../assets/img/cogito-006-fig1-moine-bouddhiste.jpg"/><figcaption>Moine bouddhiste en marche.</figcaption></figure>
<p>Ce paradoxe est au cœur de la question identitaire : tout change, mais on se sent le même. Et si l’identité est une fiction utile, nécessaire peut-être, alors la vraie question n’est pas qu’est-ce que je suis, mais à quoi est-ce que je choisis de m’identifier .</p>
<hr/>
<h2>S’identifier à sa souffrance</h2>
<p>Le premier piège est le plus silencieux.</p>
<p>Chris Williamson le formule avec une précision que j’aime beaucoup :</p>
<blockquote><p>Être touché par ce qu’il t’arrive, ce n’est pas être une victime, c’est être humain. En faire une partie de ton identité, c’est là qu’intervient le terme ‘victimisation’.</p><p><strong>Chris Williamson</strong></p></blockquote>
<p>Vivre une dépression, traverser un échec, porter une blessure, c’est humain. Mais il y a un glissement insidieux entre traverser quelque chose et être quelque chose. “Je traverse une période difficile” et “je suis dépressif” ne mobilisent pas les mêmes ressources. La deuxième formulation inscrit l’état dans la personne. Et une identité ne se quitte pas comme on dépasse une période : elle demande une forme de deuil.</p>
<p>Parce qu’une identité est, par définition, supposée être stable. Cela demande un effort qui va bien au-delà du simple soin.</p>
<p>Ce phénomène se retrouve dans certaines dynamiques de groupe. Certains cercles d’amis ou familiaux, inconsciemment n’ont pas intérêt à ce que l’on change. Notre évolution les confronte à leur propre stagnation. Ils nous ramènent à ce qu’on était, comme des crabes qui tirent vers le bas celui qui tente de sortir du seau. Ce n’est pas toujours de la malveillance. C’est souvent la mécanique de l’identité collective qui cherche à se maintenir.</p>
<hr/>
<h2>S’identifier à ses idées</h2>
<p>Il y a une forme encore plus subtile d’identification dont on parle peu : celle aux idées.</p>
<p>Nietzsche l’a formulé dans Humain, trop humain :</p>
<blockquote><p>Les convictions sont des ennemis de la vérité plus dangereux que les mensonges.</p><p><strong>Nietzsche</strong></p></blockquote>
<figure><img alt="Illustration de l'allégorie de la Caverne, des ombres prises pour la réalité." loading="lazy" width="980" height="546" src="../assets/img/cogito-006-fig2-allegorie-caverne.jpg"/><figcaption>Illustration de l'allégorie de la Caverne, des ombres prises pour la réalité.</figcaption></figure>
<p>Un mensonge peut être révélé. Une conviction, non, parce qu’elle n’est pas tenue pour un mensonge. Elle est tenue pour ce que l’on est. La remettre en question, c’est se remettre en question soi-même. Et ça, à nouveau, c’est une opération identitaire, pas intellectuelle.</p>
<p>Simone Weil, philosophe du XXe siècle, l’a décrit dans sa Note sur la suppression générale des partis politiques : on n’adhère pas à un parti parce qu’on a pesé chaque idée de son programme. On adhère parce qu’on veut appartenir à un groupe qui nous ressemble. Ensuite, les idées deviennent secondaires, défendues non parce qu’elles sont justes, mais parce qu’elles sont les nôtres. La loyauté au parti, écrit-elle, entraîne nécessairement une déloyauté envers soi-même. Et à grande échelle : “l’opération de prendre parti a remplacé l’opération de penser.”</p>
<hr/>
<h2>Le langage comme architecture de soi</h2>
<p>Si l’identité est en partie ce qu’on se raconte sur soi-même, le vocabulaire disponible détermine la qualité de ce récit.</p>
<blockquote><p>Tu ne comprendras jamais une culture sans d’abord comprendre sa langue. Et tu ne te comprendras jamais toi-même sans comprendre les mots que tu utilises pour te décrire.</p><p><strong>Chris Williamson</strong></p></blockquote>
<p>Ce n’est pas une intuition vague, c’est documenté. La neuroscientifique Lisa Feldman Barrett a montré que les personnes disposant d’un vocabulaire émotionnel plus riche traversent leurs états intérieurs avec plus de précision et les régulent mieux. Avoir un seul mot pour “ça ne va pas” et en avoir dix : frustration, honte, épuisement, mélancolie, angoisse… Ce n’est pas la même expérience intérieure. Ce n’est pas le même accès à soi-même.</p>
<p>Ce que cela implique pour l’identité : plus on dispose de mots précis pour décrire ce qu’on valorise, ce qu’on refuse, ce qu’on devient, plus on peut choisir consciemment à quoi s’identifier. Et plus on peut repérer, en temps réel, quand on se laisse glisser dans une identification qui ne nous sert pas.</p>
<p>Le discours intérieur ne s’arrête jamais. La question, c’est avec quels mots il tourne et quel niveau de conscience.</p>
<hr/>
<h2>Conclusion</h2>
<p>Je ne prétends pas avoir une réponse définitive à la question de “ce qui reste”. Ce qui “reste” est peut-être indémontrable. C’est peut-être une croyance, un fil narratif que l’esprit tisse pour maintenir la continuité du soi.</p>
<p>Ce qui me paraît certain, en revanche, c’est que nous nous identifions à quelque chose, en permanence. Nous nous racontons une histoire sur nous-mêmes. Et que nous le fassions consciemment ou non, cette histoire a des effets réels.</p>
<p>Dans <a href="../essais/la-quete-de-notre-destinee.html">Cogito #001</a>, j’avais développé l’idée que l’identité se construit par itérations, qu’on l’approche progressivement en agissant, en tentant, en s’ajustant.</p>
<p>Ce processus demande une chose : savoir à quoi on s’identifie en cours de route.</p>
<p>Parce que s’identifier à sa souffrance la rend permanente. S’identifier à ses convictions rend l’honnêteté intellectuelle impossible. Et s’identifier à un groupe qui se définit contre un autre rend la paix impossible.</p>
<p>Ce à quoi tu t’identifies te tient. La question, c’est de savoir si cela te tient debout, ou si cela te tient en cage.</p>
<p>À bientôt pour de nouvelles réflexions</p>
<p>Elouan</p>"""

COGITO_007_BODY = """<h2>Introduction</h2>
<p>Il y a une étude qui m’a frappé quand je l’ai découverte.</p>
<p>Bronnie Ware, infirmière en soins palliatifs australienne, a passé des années au chevet de personnes en fin de vie. Elle leur posait une question simple : qu’est-ce que vous regrettez ? Les réponses, après des centaines de conversations, convergeaient toujours vers les mêmes thèmes. Le premier regret, de loin le plus fréquent : “J’aurais voulu avoir le courage de vivre une vie fidèle à moi-même, et non la vie que les autres attendaient de moi.”</p>
<p>C’est un constat massif, documenté, répété sur des cohortes entières de gens en train de faire le bilan de leur existence. Et pourtant. On connaît cette étude. Elle circule, on la partage, on opine. Et on continue. La plupart des gens avancent dans leurs idées, dans leurs choix moraux, dans leur vision de la réussite sur la voie que l’on a tracée pour eux.</p>
<p>L'objectif de cet essai est de comprendre pourquoi et les dangers qu'il y a à sous-traiter sa pensée, sa morale ou sa vision d’une “vie réussie”.</p>
<h2>Le poids qu'on refuse de porter</h2>
<p>Nous sommes des êtres sociaux. Pendant des millénaires, être rejeté par la tribu signifiait mourir. Ce câblage oriente silencieusement des milliers de nos décisions. Il nous pousse à un certain mimétisme, vers ce qui est accepté, vers ce qui est conforme.</p>
<p>De plus, choisir la voie par défaut c’est aussi moins cher. Suivre une trace déjà tracée par d’autres ne demande aucun effort direct : on avance sans avoir à choisir. Mais ce “sans effort” est trompeur : le poids de la décision ne disparaît pas, il se déplace dans le temps. Il pèse plus tard, en différé, au moment où l’effet boule de neige est trop important…</p>
<figure><img alt="Le coût de la voie par défaut : éviter l'effort ne fait que repousser le fardeau." loading="lazy" width="1100" height="409" src="../assets/img/cogito-007-fig1-cout-voie-par-defaut.jpg"/><figcaption>Le coût de la voie par défaut : éviter l'effort ne fait que repousser le fardeau.</figcaption></figure>
<h2>Le courage des idées</h2>
<p>Dans tout groupe social, certaines idées sont faciles à avoir. Elles ne froissent personne. Elles sont acceptées, attendues, elles font partie du cadre implicite. D’autres idées, en revanche, exposent. Tenir une position minoritaire dans un groupe d’amis, en famille, ou en public, c’est prendre un risque social réel.</p>
<p>Et face à ce risque, il est plus confortable d’adhérer. Pas par conviction mais par inertie, pour ne pas “faire de vagues”.</p>
<p>Platon a notamment mis en avant cette idée dans son concept de la doxa : l’opinion commune, le bruit du monde, par opposition à la connaissance réelle. La doxa ne se propage pas parce qu’elle est vraie. Elle se propage parce qu’elle est répétée. Et plus une idée est répétée, plus elle semble normale, légitime, évidente.</p>
<p>En 1784, Kant posait la question directement : “Qu’est-ce que les Lumières ?” Sa réponse: la sortie de l’homme de sa minorité intellectuelle. Et il nommait ce qui y fait obstacle non pas l’intelligence, mais le courage. “Sapere aude” : Aie le courage de te servir de ton propre entendement.</p>
<figure><img alt="Jean Huber, Le Dîner des philosophes (1772)" loading="lazy" width="1100" height="505" src="../assets/img/cogito-007-fig2-diner-philosophes.jpg"/><figcaption>Jean Huber, Le Dîner des philosophes (1772)</figcaption></figure>
<p>Ce courage est rare. Solomon Asch l’a mesuré en laboratoire dans les années 1950 : dans une expérience célèbre, des participants devaient comparer des lignes de longueurs évidentes. Quand des complices désignaient unanimement la mauvaise réponse, 75 % des participants finissaient par se ranger à l’avis du groupe contre l’évidence de leurs propres yeux.</p>
<p>Ce n’est pas de la stupidité. C’est de la biologie. Mais en avoir conscience change quelque chose. Cela invite à une forme d’humilité : sur ce que l’on pense savoir, sur les idées qu’on défend sans les avoir vraiment examinées, sur la différence entre une conviction réfléchie et une conviction héritée par osmose sociale.</p>
<h2>Le danger du conformisme moral</h2>
<p>La question morale, ce qui est bien, ce qui est mal, est peut-être le terrain le plus dangereux où s’exerce la voie par défaut.</p>
<p>En 1961, Hannah Arendt assiste au procès d’Adolf Eichmann à Jérusalem. Eichmann était l’un des principaux organisateurs de la déportation des Juifs d’Europe vers les camps d’extermination. Ce que découvre Arendt au tribunal la stupéfie. Elle s’attendait à un monstre. Elle trouve un homme banal : méthodique, obéissant, zélé et incapable de penser au-delà de sa fonction.</p>
<figure><img alt="Photo historique d'Eichmann dans sa cabine de verre, procès de Jérusalem, 1961" loading="lazy" width="1100" height="550" src="../assets/img/cogito-007-fig3-proces-eichmann.jpg"/><figcaption>Photo historique d'Eichmann dans sa cabine de verre, procès de Jérusalem, 1961</figcaption></figure>
<p>Il n’avait pas décidé que tuer des millions de personnes était une bonne chose. Il avait simplement exécuté des ordres. Il avait délégué la question morale à l’institution qui l’employait.</p>
<p>Arendt en tire une conclusion simple : “Le mal peut être banal.” Pas le produit d’une cruauté exceptionnelle, mais d’une absence ordinaire de pensée. Ce n’est pas le sadisme qui a rendu possible la Shoah : c’est le conformisme à grande échelle.</p>
<p>Ne pas choisir, c’est déjà choisir. Il n’existe pas de neutralité morale. Chaque inaction est un acte. Ceux qui ont “suivi les ordres” portent une responsabilité réelle précisément parce qu’ils ont renoncé à l’exercer.</p>
<p>Certaines choses sont universellement condamnables. Mais quand on sous-traite la question du bien et du mal à une institution, on perd sa souveraineté morale et l’histoire montre les conséquences terribles que peut avoir cette décision. A nouveau, c’est le manque de courage qui mène à ces situations.</p>
<h2>La réussite par défaut</h2>
<p>Il existe un modèle de réussite sociale. Il est visible, reconnaissable, mesurable. Une situation stable, un salaire respectable, une famille, une belle maison, des vacances... Ces éléments ne sont pas mauvais en soi.</p>
<p>Mais il y a une distinction que j’avais développée dans <a href="../essais/lambition.html">un Intracogito sur l’ambition</a> et que je trouve essentielle ici :</p>
<blockquote><p>Ce n’est pas parce qu’une chose est difficile à obtenir qu’elle a nécessairement de la valeur.</p></blockquote>
<p>On peut passer sa vie à courir après des choses difficiles sans jamais se demander si ce sont les bonnes pour nous. Vouloir ce poste parce qu’il est inaccessible, vouloir ce mode de vie parce qu’il impressionne. C’est parfois une forme de lâcheté déguisée. Elle évite la vraie question : qu’est-ce que je veux vraiment ?</p>
<h2>La voie des écoles de commerce</h2>
<p>En école de commerce, j’ai vite compris à quel point il était facile de suivre une trajectoire sans avoir réellement décidé de la prendre. L’école valorise naturellement les débouchés prestigieux et les salaires de sortie élevés pour leur renommée ; les grands groupes cherchent à attirer le plus grand nombre de candidats possible. Et nous, étudiants, devons faire très tôt des choix qui peuvent structurer toute une carrière, parfois avec le poids d’un crédit contracté pour financer nos études.</p>
<figure><img alt="L'école Supérieure de commerce de Paris, mon école de commerce" loading="lazy" width="1100" height="543" src="../assets/img/cogito-007-fig4-escp.jpg"/><figcaption>L'école Supérieure de commerce de Paris, mon école de commerce</figcaption></figure>
<p>Dans ce contexte, certaines voies comme le conseil ou la finance deviennent presque évidentes tant tout semble organisé pour nous y conduire. Pour ceux qui ont une réelle appétence pour ces métiers, c’est une formidable opportunité. Mais pour les autres, le danger est précisément de ne jamais s’être demandé ce qu’ils voulaient vraiment.</p>
<p>S’engager dans une vie professionnelle par défaut reste un choix, même lorsque l’on n’en mesure pas encore la portée. Et c’est parfois plusieurs années plus tard que cette décision se révèle pleinement, lorsque surgissent le mal-être au travail, l’épuisement ou la nécessité de remettre profondément en question une trajectoire.</p>
<h2>Le piège anticonformiste</h2>
<p>Il y a un danger à nommer qui guette précisément les gens qui ont compris tout ce qui précède.</p>
<p>Une fois conscients de la doxa, du conformisme moral, de la réussite programmée, il est tentant de tirer une conclusion symétrique : tout ce que pense la majorité est suspect, tout standard est un piège, toute institution est une manipulation. Et donc : faire l’inverse, systématiquement, c’est penser par soi-même.</p>
<p>Ce n’est pas penser par soi-même. C’est se construire contre quelque chose.</p>
<p>Quelqu’un qui s’appuie contre un mur. Si on enlève le mur, il tombe. Parce que sa posture dépend entièrement de ce contre quoi il se tient. L’anticonformisme systématique est cette posture, une identité construite par réaction, qui n’existe que si l’adversaire existe.</p>
<figure><img alt="Illustration de marionnettes, métaphore du conditionnement" loading="lazy" width="1100" height="550" src="../assets/img/cogito-007-fig5-marionnettes.jpg"/></figure>
<p>Le but n’est pas de rejeter les standards, mais de savoir pourquoi on les choisit ou pourquoi on les refuse. Une personne qui examine sa vie et conclut qu’elle veut la stabilité, la famille, la carrière classique et qui les choisit lucidement vit plus librement que celui qui les rejette “par principe”.</p>
<h2>Conclusion</h2>
<p>La voie par défaut mène à une vie par défaut. Et une vie par défaut, c’est une vie de cases cochées par des gens qui ne seront pas là, au moment où vous ferez, vous aussi, le bilan.</p>
<p>C’est tout le vertige de l’étude de Bronnie Ware. On n’a qu’une vie. Il n’existe pas de bouton “rejouer”. Certaines leçons ne peuvent tout simplement pas s’apprendre sur un lit de mort.</p>
<p>À bientôt pour de nouvelles réflexions</p>
<p>Elouan</p>"""

COGITO_008_BODY = """<p>On ne se voit pas vieillir. On ne devient pas proche de quelqu’un à un instant précis. On ne perd pas confiance en soi un mardi matin. Une relation ne se dégrade pas nécessairement le jour d’une dispute parce que la vaisselle n’a pas été lavée.</p>
<p>Et pourtant, toutes ces choses arrivent. Certaines de nos transformations sont aussi celles que l’on perçoit le moins.</p>
<p>Ce sont des “ transformations silencieuses”, elles ont lieu sous nos yeux, mais elles sont trop lentes, trop continues et pas assez quantifiable pour que l’on puisse isoler le moment où quelque chose change. On n’en constate souvent que le résultat.</p>
<p>C’est cette idée que j’ai envie d’explorer ici, avec une question assez simple : si une partie importante de ce qui façonne notre vie agit silencieusement, de quoi s’agit-il vraiment et avons-nous intérêt à apprendre à le percevoir ?</p>
<h2>L’événement et la transformation</h2>
<p>Nous sommes très bons pour voir les événements. Une rencontre. Une rupture. Une promotion. Une blessure. Une victoire.</p>
<p>L’événement possède quelque chose de confortable : il a une date, parfois une cause et un responsable. Il permet de raconter une histoire avec un avant et un après. La transformation fonctionne différemment.</p>
<p>Le philosophe François Jullien oppose dans son essai Les transformations silencieuses, à ce titre l’action et la transformation. L’action est locale, momentanée, visible. Quelqu’un fait quelque chose et cette action produit un résultat. La transformation, elle, est progressive, globale et s’inscrit dans la durée. Elle ne se détache pas suffisamment du cours des choses pour attirer notre attention.</p>
<figure><img alt="François Jullien, auteur de l'essai Les transformations silencieuses" loading="lazy" width="1100" height="495" src="../assets/img/cogito-008-fig1-francois-jullien.jpg"/><figcaption>François Jullien, auteur de l'essai Les transformations silencieuses</figcaption></figure>
<p>Cette distinction s’inscrit chez lui dans un écart plus large entre deux traditions de pensée. La pensée grecque s’est construite autour d’une exigence particulièrement puissante : déterminer. Dire ce qu’est une chose, la distinguer d’une autre, identifier un sujet et lui attribuer des propriétés.</p>
<p>Cette structure se retrouve jusque dans notre langage qui est prédicatif : un sujet sert de support auquel viennent s’attribuer différentes qualités. Cette manière de penser est extrêmement efficace pour identifier ce qui est. Elle l’est moins pour saisir ce qui est en train de devenir.</p>
<h2>La force des petits écarts</h2>
<p>Le sport illustre bien cette idée. Une séance de course ne transforme presque rien. Si je vais courir aujourd’hui, je ne serai pas fondamentalement plus endurant demain. Mon corps n’aura pas changé de manière perceptible.</p>
<p>Et pourtant, si je répète cette séance plusieurs centaines de fois, il devient impossible de prétendre qu’il ne s’est rien passé. Quelle séance m’a transformé ? Aucune. Et toutes.</p>
<p>Le problème est que cette logique fonctionne aussi dans l’autre sens. Une mauvaise nuit de sommeil n’est pas très grave. Passer une heure de trop sur son téléphone non plus. Manger mal un soir n’a probablement aucune conséquence importante. Ce soir, ce n’est pas grave. Et c’est vrai.</p>
<figure><img alt="Citation de Naval Ravikant sur les intérêts composés" loading="lazy" width="1100" height="482" src="../assets/img/cogito-008-fig2-citation-naval-ravikant.jpg"/></figure>
<p>Les transformations silencieuses, bonnes ou mauvaises, sont toujours constituées de centaines de répétitions qui avec le temps ont de grandes conséquences.</p>
<h2>Le biais du mesurable</h2>
<p>Nous accordons naturellement plus d’attention à ce que nous pouvons isoler et mesurer. L’argent en est probablement l’exemple le plus évident. Un salaire possède un chiffre. Un patrimoine aussi. On peut les comparer, suivre leur évolution, constater précisément si l’on possède plus ou moins qu’un an auparavant.</p>
<p>Le bonheur n’a pas cette propriété. Une amitié non plus. Il n’existe pas de relevé mensuel qui indique que ma relation avec un ami s’est améliorée de 12 % cette année. Pourtant, personne ne prétendrait sérieusement que ces choses comptent moins.Elles sont simplement plus difficiles à saisir.</p>
<p>Le problème apparaît alors lorsque la facilité avec laquelle une chose se mesure a tendance à déterminer l’importance qu’on lui accorde. Un salaire, une note, un chrono, un poids sont faciles à suivre. La qualité d’une relation, notre confiance en nous, notre sérénité ou notre présence sont des choses qui évoluent beaucoup plus silencieusement</p>
<h2>Les relations silencieuses</h2>
<p>C’est probablement dans nos relations que cette idée me frappe le plus. Deux personnes qui « ne s’aiment plus » n’ont pas nécessairement connu d’instant précis où leur amour aurait disparu.</p>
<p>Il y a eu des conversations un peu moins longues. Des gestes qui ont manqué une fois, puis plusieurs fois. Des silences. Des évitements. Une irritation devenue progressivement plus fréquente. François Jullien utilise précisément cet exemple. Ce qui apparaît finalement comme une rupture est l’aboutissement visible d’une érosion beaucoup plus ancienne. La dispute n’est alors pas nécessairement la cause du problème. Elle est la facture, présentée d’un coup après des mois de crédit accumulé sans qu’on en tienne le compte.</p>
<figure><img alt="Edward Hopper, Nighthawks" loading="lazy" width="1100" height="507" src="../assets/img/cogito-008-fig3-nighthawks-hopper.jpg"/><figcaption>Edward Hopper, Nighthawks</figcaption></figure>
<p>Mais l’inverse est tout aussi vrai. On ne devient pas profondément ami avec quelqu’un à un instant précis. Une discussion, puis une autre. Une confiance accordée. Un service rendu. Des souvenirs communs. Une présence dans un moment difficile. Et un jour, sans vraiment savoir quand la transformation a eu lieu, cette personne est devenue essentielle.</p>
<h2>Le piège de la lucidité</h2>
<p>Mais il y a un danger dans ce raisonnement qu’il faut nommer. Si tout nous transforme silencieusement, faut-il commencer à tout surveiller ? Analyser chaque interaction. Mesurer son sommeil, son humeur, ses relations. Se demander après chaque décision ce qu’elle est en train de faire de nous.</p>
<p>Je ne le pense pas.</p>
<p>Ce serait même probablement une manière assez pénible de vivre. On ne peut pas vivre et se regarder vivre en permanence. Une amitié a aussi besoin de ne pas être évaluée chaque semaine. Le sport peut être pratiqué simplement parce qu’on aime courir. Certaines expériences ont besoin d’être vécues avant d’être comprises. Surtout, vouloir tout quantifier reviendrait exactement au problème évoqué précédemment : croire qu’une chose ne devient réelle ou importante qu’à partir du moment où elle peut être mesurée.</p>
<figure><img alt="Perfect Days, un film sur les transformations silencieuses du quotidien." loading="lazy" width="1100" height="455" src="../assets/img/cogito-008-fig4-perfect-days.jpg"/><figcaption>Perfect Days, un film sur les transformations silencieuses du quotidien.</figcaption></figure>
<h2>Conclusion</h2>
<p>Je ne pense pas qu’il faille essayer de rendre visible tout ce qui ne l’est pas. Certaines choses ont besoin de temps. Certaines ont besoin d’être vécues sans être immédiatement analysées. Et certaines ne pourront probablement jamais être correctement mesurées.</p>
<p>Mais je pense qu’il y a un intérêt à apprendre à éduquer notre attention. À moins regarder uniquement les événements et davantage les trajectoires.</p>
<p>Notre vigilance devrait notamment porter sur les dispositions dans lesquelles nous vivons, sur l’environnement que nous construisons et sur les personnes que nous fréquentons. Sont-ils alignés avec la personne que nous pensons être et avec celle que nous voulons devenir ?</p>
<p>Si nous parvenons à maîtriser cet alignement, alors notre environnement et nos relations forment un écosystème sain. Et cet écosystème nous transforme silencieusement, de la bonne manière.</p>
<p>À bientôt pour de nouvelles réflexions</p>
<p>Elouan</p>"""

AUTHOR_LINKEDIN = "https://www.linkedin.com/in/elouan-noel-248283256/"
AUTHOR_BIO = "Fondateur d'Intracogito. Philosophie appliquée, chaque semaine, pour mieux comprendre ce qu'on vit."

AUTHOR_PHOTO = "assets/img/author-elouan.jpg"

def real_article_page(slug, title, chapo, description, cover_path, cover_credit, tags,
                       body_html, word_count, extra_block="", ref="", date_published="2026-10-24",
                       related=None, section="essais", extra_jsonld_blocks=""):
    if not cover_path:
        cover_abs = OG_DEFAULT_IMAGE
    else:
        cover_abs = cover_path if cover_path.startswith("http") else f"{BASE_URL}/{cover_path}"
    cover_rel = img_src(cover_path, "../")
    reading_min = max(1, round(word_count / 200))
    ref_html = f'<span class="hero-eyebrow article-ref">{ref}</span>' if ref else ""
    chapo_html = f'<p class="chapo">{chapo}</p>' if chapo else ""
    tags_html = "\n    ".join(f'<a class="article-tag" href="../{href}">{label}</a>' for (href, label) in tags)
    credit_html = f'<p class="article-credit" style="color:var(--on-dark-muted); text-align:right; padding: .4rem var(--px); position:relative; z-index:1;">{cover_credit}</p>' if cover_credit else ""
    cover_alt = cover_credit if cover_credit else f"Image de couverture, {title}"
    # « À lire aussi » : 3 recommandations justifiées (href, pourquoi), sinon ancien gabarit vide
    if related:
        related_html = "\n      ".join(article_card(ARTICLES_BY_HREF[h], prefix="../", chapo=why) for h, why in related)
    else:
        related_html = "\n      ".join(card("../essais.html", badge=False) for _ in range(3))
    section_label = RUBRIQUES.get(section, {}).get("label", section.capitalize())
    section_href = f"{section}.html"
    jsonld = f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {{"@type": "ListItem", "position": 1, "name": "Intracogito", "item": "https://intracogito.vercel.app/"}},
    {{"@type": "ListItem", "position": 2, "name": "{section_label}", "item": "https://intracogito.vercel.app/{section_href}"}},
    {{"@type": "ListItem", "position": 3, "name": "{title}", "item": "https://intracogito.vercel.app/{section}/{slug}.html"}}
  ]
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{title}",
  "description": "{description}",
  "image": "{cover_abs}",
  "datePublished": "{date_published}",
  "dateModified": "{date_published}",
  "author": {{"@type": "Person", "name": "Elouan Noël"}},
  "publisher": {{"@type": "Organization", "name": "Intracogito", "logo": {{"@type": "ImageObject", "url": "{BASE_URL}/assets/img/favicon.png"}}}}
}}
</script>{extra_jsonld_blocks}"""
    return f"""<!doctype html>
<html lang="fr">
<head>
{head_meta(f"{title}, Intracogito", description, f"{section}/{slug}.html", og_type="article", extra_jsonld=jsonld, image=cover_abs)}
</head>
<body>

{topbar(prefix="../", on_hero=True)}
<main>

<section class="article-hero">
  {f'<img class="bg-cover-img" src="{cover_rel}" alt="{cover_alt}" loading="eager"{img_wh(cover_path)} />' if cover_path else ''}
  <div class="article-hero-content">
    {ref_html}
    <h1>{title}</h1>
    {chapo_html}
  </div>
</section>
{credit_html}

<div class="wrap article-meta-wrap">
  <div class="article-sub-meta">
    <time datetime="{date_published}">{format_date_fr(date_published)}</time>
    <span>·</span>
    <span>{reading_min} min de lecture</span>
    <span>·</span>
    <span>{word_count} mots</span>
  </div>
</div>

<div class="wrap article-body">
  {body_html}
  {extra_block}
</div>

<div class="wrap article-end-meta">
  <div class="article-tags">
    {tags_html}
  </div>
  <div class="article-author-row">
    <a class="article-author-avatar" href="{AUTHOR_LINKEDIN}" target="_blank" rel="noopener" aria-label="Profil LinkedIn d'Elouan Noël"><img src="../{AUTHOR_PHOTO}" alt="Elouan Noël" loading="lazy"{img_wh(AUTHOR_PHOTO)} /></a>
    <div>
      <div class="article-author-name">Elouan Noël, fondateur d'Intracogito</div>
    </div>
  </div>
</div>

<div class="article-related">
  <div class="wrap">
    <h2 class="sec-title">À lire aussi</h2>
    <div class="card-grid">
      {related_html}
    </div>
  </div>
</div>

</main>
{footer(prefix="../")}
{TOGGLE_SCRIPT}
</body>
</html>
"""

cogito_001_html = real_article_page(
    slug="la-quete-de-notre-destinee",
    title="La quête de notre destinée",
    chapo="Entre sens et identité",
    ref="Cogito #001",
    description="Essai Cogito : une réflexion sur l'identité comme itération, entre le concept aristotélicien de puissance et une analogie mathématique du développement limité.",
    cover_path="assets/img/cogito-001-cover.jpg",
    cover_credit="Hermann David Salomon Corrodi, Evening on the banks of the Nile (1905)",
    tags=[("cogito.html", "Cogito"), ("philosophes.html", "Philosophes")],
    body_html=COGITO_001_BODY,
    word_count=1090,
    date_published="2026-03-18",
    related=[
        ('essais/le-poids-de-lidentite.html', "Approfondit la même question : à quoi choisit-on vraiment de s'identifier."),
        ('essais/la-voie-par-defaut.html', 'Prolonge la réflexion sur le sens : choisir sa vie plutôt que la subir.'),
        ('essais/la-force-de-lintuition.html', "Une autre voie pour trouver sa direction, par l'intuition plutôt que la raison."),
    ],
)


PERSON_JSONLD_MARC_AURELE = """
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "Marc Aurèle",
  "alternateName": "Marcus Aurelius",
  "description": "Empereur romain (121-180) et philosophe stoïcien, auteur des Pensées pour moi-même.",
  "birthDate": "121",
  "deathDate": "180"
}
</script>"""

MARC_AURELE_BODY = '<p>Marc Aurèle écrit ses pensées les plus intimes en grec, pas en latin, la langue de son pouvoir. Plus frappant encore : ce texte n’était destiné à aucun lecteur, il devait même être détruit à sa mort. Il n’a survécu jusqu’à nous que par deux manuscrits, dont l’un a depuis disparu et ne nous est connu qu’à travers une traduction faite avant sa perte. Dix-huit siècles plus tard, ce carnet voué à la destruction est devenu l’un des livres les plus lus de l’histoire : <em>Pensées pour moi-même</em>.</p>\n<p>Entre 170 et 180, l’empereur l’écrit le soir, sous sa tente, entre deux campagnes militaires le long du Danube. Il ne s’adresse à aucun lecteur, à aucune postérité. Il se parle, pour tenir : souviens-toi de ce qui dépend de toi et de ce qui n’en dépend pas, ne t’emporte pas, fais ce que tu as à faire.</p>\n<p>C’est peut-être ce qui rend ce texte différent des grands traités de philosophie. Marc Aurèle n’essaie de convaincre personne. Il essaie de tenir.</p>\n<h2>Un homme qui avait toutes les raisons de craquer</h2>\n<p>Si quelqu’un avait une excuse légitime pour perdre patience, c’était lui. Marc Aurèle règne de 161 à 180, en pleine peste antonine (une épidémie qui tue sans doute plusieurs millions de personnes dans l’empire), en guerre quasi permanente aux frontières, et il perd plusieurs de ses enfants en bas âge. Il est à la fois l’homme le plus puissant du monde connu et quelqu’un d’épuisé, malade, qui écrit pour ne pas sombrer.</p>\n<p>C’est cette tension qui rend ses Pensées utiles aujourd’hui. Elles ne viennent pas d’un philosophe au calme dans son jardin, mais d’un homme en stress constant, qui cherche une méthode concrète pour ne pas y céder. Ce n’est pas un hasard si, presque deux mille ans plus tard, ce texte reste un point de départ si souvent cité sur <a href="../essais/la-paix-interieure.html">la paix intérieure</a>.</p>\n<p class="image-placeholder" style="border:1px dashed var(--border); padding:1.6rem; text-align:center; font-family:var(--mono); font-size:.68rem; letter-spacing:.06em; text-transform:uppercase; color:var(--ink-muted); margin:2.2rem 0;">Image à venir : buste ou peinture évoquant Marc Aurèle (domaine public). Fichier suggéré : assets/img/philosophe-marc-aurele-fig1.jpg</p>\n<h2>La seule question qui compte vraiment</h2>\n<p>Toute une partie des Pensées tourne autour d’une seule distinction, que les stoïciens appelleront plus tard la <strong>dichotomie du contrôle</strong> : ce qui dépend de moi (mes jugements, mes réactions, mes choix), et ce qui n’en dépend pas (les événements, les autres, la maladie, la mort).</p>\n<blockquote><p>« Nos troubles ne viennent que de l’idée tout intérieure que nous nous en faisons. [...] Supprime l’idée que tu t’es faite, et, du même coup, tu supprimes aussi ta plainte. Supprime le « Je suis blessé », et, du même coup, la blessure est supprimée également. »</p><p>Marc Aurèle, <em>Pensées pour moi-même</em>, Livre IV, 3 et 7</p></blockquote>\n<p>Ce n’est pas du déni. Marc Aurèle ne dit pas que la douleur n’existe pas : il dit qu’une plainte est un étage ajouté par nous, au-dessus de l’événement brut. Un genou qui cogne une table fait mal, qu’on s’en plaigne ou non. Retirer la plainte ne retire pas le choc. Ce qui disparaît, c’est seulement ce que le jugement y ajoutait.</p>\n<div class="newsletter-insert">\n  <div class="newsletter-insert-head">\n    <img class="newsletter-insert-photo" src="../assets/img/vitruvian-man.jpg" alt="Elouan Noël" loading="lazy" width="46" height="46" />\n    <div>\n      <h3>Rejoins la newsletter</h3>\n      <p>Une édition par semaine, 4 à 5 citations commentées.</p>\n    </div>\n  </div>\n  <a href="https://elouannoel.substack.com/" target="_blank" rel="noopener" class="hero-cta newsletter-insert-cta">S\'abonner →</a>\n</div>\n<h2>Un refuge que personne ne peut te confisquer</h2>\n<p>Marc Aurèle revient souvent à une image : celle d’un refuge intérieur, disponible à tout instant, qu’aucune circonstance extérieure ne peut atteindre.</p>\n<blockquote><p>« Tu peux toujours, quand tu le veux, à ton heure, trouver un asile en toi-même. »</p><p>Marc Aurèle, <em>Pensées pour moi-même</em>, Livre IV, 3</p></blockquote>\n<p>Les stoïciens appellent cette instance l’<strong>hégémonikon</strong> : la part de l’esprit qui juge et qui décide, et qu’aucune force extérieure ne peut contraindre à consentir contre son gré. Le philosophe Pierre Hadot parlera plus tard, à propos de Marc Aurèle précisément, d’une « citadelle intérieure ». Ce n’est pas une image de bien-être : c’est une description technique de ce qui, selon les stoïciens, nous appartient en propre et qu’un empire en guerre ne peut pas nous arracher.</p>\n<p class="image-placeholder" style="border:1px dashed var(--border); padding:1.6rem; text-align:center; font-family:var(--mono); font-size:.68rem; letter-spacing:.06em; text-transform:uppercase; color:var(--ink-muted); margin:2.2rem 0;">Image à venir : paysage évoquant le camp militaire du Danube ou une citadelle intérieure (domaine public). Fichier suggéré : assets/img/philosophe-marc-aurele-fig2.jpg</p>\n<h2>Agir maintenant, pas un jour</h2>\n<p>Les Pensées reviennent aussi, sans relâche, sur l’urgence d’agir.</p>\n<blockquote><p>« À toute heure, songe sérieusement, comme Romain et comme homme, à faire tout ce que tu as en mains [...] tu t’en débarrasseras si tu accomplis chacun de tes actes comme le dernier de ta vie. [...] Ne te conduis pas comme si tu devais vivre des millions d’années. »</p><p>Marc Aurèle, <em>Pensées pour moi-même</em>, Livre II, 5 et Livre IV, 17</p></blockquote>\n<p>Ce rappel n’est pas un conseil de productivité : c’est un réflexe proprement stoïcien, hérité de Chrysippe puis d’Épictète avant lui, qui consiste à juger chaque acte en lui-même, indépendamment de ce qui suit. Rome elle-même n’est, à l’échelle du temps, qu’un épisode : Marc Aurèle le sait, et c’est précisément ce qui, selon lui, rend chaque geste présent plus sérieux, pas moins.</p>\n<h2>Un stoïcien parmi d’autres</h2>\n<p>Marc Aurèle n’a jamais voulu fonder une école : il reprend, pour lui-même, une discipline déjà posée par Zénon de Citium trois siècles plus tôt, puis par Chrysippe, puis par Épictète, dont il a lu le Manuel, et par <a href="../essais/la-sagesse.html">Sénèque</a> un siècle avant lui. Ce qui rend ses Pensées particulières dans cette lignée n’est pas la doctrine, déjà fixée avant lui : c’est qu’elles la montrent appliquée en direct, par quelqu’un qui n’écrit pour aucun public et qui a tout à perdre s’il se trompe.</p>\n<p>Le philosophe Pierre Hadot, qui a consacré un livre entier à Marc Aurèle (<em>La Citadelle intérieure</em>), montre que cette discipline stoïcienne se décline en trois gestes : juger, désirer, agir. Les trois sections précédentes de cette page en sont, presque malgré elles, une illustration : accepter ce qui ne dépend pas de nous, trouver refuge dans ce qui nous appartient en propre, continuer d’agir sans attendre. Ce n’est pas l’<strong>ataraxie</strong> des épicuriens, qui vise l’absence de trouble, ni l’<strong>apatheia</strong> au sens où on l’entend parfois, l’indifférence : c’est une discipline qui n’élimine rien, mais qui apprend à agir juste au milieu de ce qu’on ne contrôle pas.</p>\n<p class="image-placeholder" style="border:1px dashed var(--border); padding:1.6rem; text-align:center; font-family:var(--mono); font-size:.68rem; letter-spacing:.06em; text-transform:uppercase; color:var(--ink-muted); margin:2.2rem 0;">Image à venir : manuscrit ancien ou bibliothèque antique évoquant la transmission des Pensées (domaine public). Fichier suggéré : assets/img/philosophe-marc-aurele-fig3.jpg</p>\n<p>Les Pensées n’ont été publiées qu’après sa mort. Marc Aurèle écrivait pour un lecteur unique, qui n’était autre que lui-même, en train d’essayer, sans certitude d’y parvenir, de rester cet homme qu’il décrit page après page. Dix-huit siècles plus tard, ce carnet privé se lit encore, non parce qu’il a réussi, mais parce qu’il a continué à écrire alors même qu’il n’en était pas sûr.</p>\n<h2>En bref 💡</h2>\n<p>📌 <strong>Marc Aurèle (121-180) était un empereur romain et philosophe stoïcien</strong> qui écrivait les <em>Pensées pour moi-même</em> en grec, pour lui seul, entre deux campagnes militaires sur le Danube.</p>\n<p>📌 <strong>Son concept central est la dichotomie du contrôle</strong> : agir sur ce qui dépend de nous, accepter le reste.</p>\n<p>📌 <strong>Il prolonge une lignée stoïcienne</strong> qui va de Zénon de Citium à Chrysippe, Épictète et Sénèque.</p>'

philosophe_marc_aurele_html = real_article_page(
    slug="marc-aurele",
    title="Marc Aurèle : les pensées d\'un empereur",
    chapo="Un empereur qui écrivait, seul le soir, pour apprendre à se gouverner avant de gouverner Rome.",
    ref="Philosophe",
    description="Marc Aurèle, empereur romain et philosophe stoïcien : qui il était, et ce que ses Pensées pour moi-même enseignent encore sur le contrôle de soi et le calme intérieur.",
    cover_path=None,
    cover_credit=None,
    tags=[("philosophes.html", "Philosophes")],
    body_html=MARC_AURELE_BODY,
    word_count=1020,
    date_published="2026-10-29",
    section="philosophes",
    extra_jsonld_blocks=PERSON_JSONLD_MARC_AURELE,
    related=[
        ("essais/la-paix-interieure.html", "Approfondit la paix intérieure, l\'objectif concret derrière la dichotomie du contrôle de Marc Aurèle."),
        ("essais/la-sagesse.html", "Sénèque, autre grande voix du stoïcisme, sur ce que la sagesse exige vraiment."),
        ("essais/la-peur.html", "La même discipline intérieure appliquée à une émotion différente : la peur."),
    ],
)


def _intracogito_description(e):
    noms = []
    for n in e["authors"]:
        if n != "Intracogito" and n not in noms:
            noms.append(n)
    k = len(e["authors"])
    cites = (", ".join(noms[:-1]) + f" et {noms[-1]}") if len(noms) > 1 else (noms[0] if noms else "Intracogito")
    return f"Intracogito #{e['num']:03d}, {e['title']} : {k} citations commentées, de {cites}, avec une lecture « Entre les lignes » pour chacune."

INTRACOGITO_PAGES = {}
for _e in INTRACOGITO_EDITIONS:
    INTRACOGITO_PAGES[_e["href"]] = real_article_page(
        slug=_e["slug"],
        title=_e["title"],
        chapo="",
        ref=_e["badge"],
        description=_e.get("description") or _intracogito_description(_e),
        cover_path=_e["cover"],
        cover_credit=_e.get("credit", ""),
        tags=[("intracogito.html", "Intracogito")],
        body_html=_e["body"],
        word_count=_e["words"],
        date_published=_e["date"],
        related=_e.get("related"),
    )

cogito_002_html = real_article_page(
    slug="la-matiere-premiere-du-heros",
    title="La matière première du héros",
    chapo="Choisir sa souffrance",
    ref="Cogito #002",
    description="Essai Cogito : une réflexion sur la souffrance choisie comme matière du sens, entre Viktor Frankl, Camus et le mécanisme neurobiologique de la récompense.",
    cover_path="assets/img/cogito-002-cover.jpg",
    cover_credit="Edvard Munch, Le Cri (1893)",
    tags=[("cogito.html", "Cogito"), ("philosophes.html", "Philosophes")],
    body_html=COGITO_002_BODY,
    word_count=1816,
    date_published="2026-04-01",
    related=[
        ('essais/la-verite-du-chemin.html', 'Même matière : ce que la souffrance et les épreuves construisent en nous.'),
        ('essais/le-poids-de-lidentite.html', "Le piège symétrique : s'identifier à sa souffrance plutôt que la choisir."),
        ('essais/les-transformations-silencieuses.html', "Comment l'épreuve nous transforme, souvent sans qu'on le voie venir."),
    ],
)

cogito_003_html = real_article_page(
    slug="la-force-de-lintuition",
    title="La force de l'intuition",
    chapo="Entre le cœur et la raison",
    ref="Cogito #003",
    description="Essai Cogito : une réflexion sur l'intuition comme vérité première, à partir de Pascal, du Petit Prince et de L'Alchimiste de Paulo Coelho.",
    cover_path="assets/img/cogito-003-cover.jpg",
    cover_credit="Albert Bierstadt, Yosemite Valley (1868)",
    tags=[("cogito.html", "Cogito"), ("philosophes.html", "Philosophes")],
    body_html=COGITO_003_BODY,
    word_count=1093,
    date_published="2026-04-22",
    related=[
        ('essais/la-quete-de-notre-destinee.html', "L'intuition comme boussole pour trouver sa propre voie."),
        ('essais/la-voie-par-defaut.html', 'Le contraste : penser par soi-même contre suivre le troupeau.'),
        ('essais/lunite-du-corps-et-de-lesprit.html', 'Une autre forme de savoir non rationnel : celui du corps.'),
    ],
)

cogito_004_html = real_article_page(
    slug="la-verite-du-chemin",
    title="La vérité du chemin",
    chapo="Ce que le bouddhisme enseigne du chemin",
    ref="Cogito #004",
    description="Essai Cogito : une réflexion sur la quatrième noble vérité du bouddhisme, le chemin comme expérience vécue, entre Siddhartha de Hermann Hesse et Frédéric Lenoir.",
    cover_path="assets/img/cogito-004-cover.jpg",
    cover_credit="Nicholas Roerich, Tibet. Himalayas (1933)",
    tags=[("cogito.html", "Cogito"), ("philosophes.html", "Philosophes")],
    body_html=COGITO_004_BODY,
    word_count=1487,
    date_published="2026-05-13",
    related=[
        ('essais/le-poids-de-lidentite.html', "Même terrain philosophique : l'impermanence et le détachement bouddhistes."),
        ('essais/la-matiere-premiere-du-heros.html', "Le sens que l'on donne à ce qui nous fait souffrir."),
        ('essais/la-quete-de-notre-destinee.html', 'Chemin vécu contre destinée choisie : deux lectures du sens.'),
    ],
)

cogito_005_html = real_article_page(
    slug="lunite-du-corps-et-de-lesprit",
    title="L'unité du corps et de l'esprit",
    chapo="Ce que le corps dit de la pensée",
    ref="Cogito #005",
    description="Essai Cogito : une réflexion sur le lien entre corps et esprit, à travers les biographies de Platon, Schopenhauer et Nietzsche.",
    cover_path="assets/img/cogito-005-cover.jpg",
    cover_credit="Auguste Rodin, Le Penseur",
    tags=[("cogito.html", "Cogito"), ("philosophes.html", "Philosophes")],
    body_html=COGITO_005_BODY,
    word_count=1736,
    date_published="2026-06-10",
    related=[
        ('essais/les-transformations-silencieuses.html', 'Le corps comme lieu des transformations les plus silencieuses.'),
        ('essais/le-poids-de-lidentite.html', 'Le corps façonne-t-il qui nous sommes autant que nos idées ?'),
        ('essais/la-force-de-lintuition.html', "Le corps comme une autre forme d'intuition, incarnée."),
    ],
)

cogito_006_html = real_article_page(
    slug="le-poids-de-lidentite",
    title="Le poids de l'identité",
    chapo="À quoi choisit-on de s'identifier ?",
    ref="Cogito #006",
    description="Essai Cogito : une réflexion sur l'identité comme construction narrative, entre l'impermanence bouddhiste, Montaigne et le piège de s'identifier à sa souffrance ou à ses convictions.",
    cover_path="assets/img/cogito-006-cover.jpg",
    cover_credit="John Ross Key, Mt. Diablo, San Joaquin Valley",
    tags=[("cogito.html", "Cogito"), ("philosophes.html", "Philosophes")],
    body_html=COGITO_006_BODY,
    word_count=1132,
    date_published="2026-07-15",
    related=[
        ('essais/la-quete-de-notre-destinee.html', "Même fil : l'identité comme construction plutôt que donnée fixe."),
        ('essais/la-matiere-premiere-du-heros.html', "Le piège précis qu'il nomme : s'identifier à sa propre souffrance."),
        ('essais/la-voie-par-defaut.html', 'Choisir lucidement ses convictions plutôt que les hériter par défaut.'),
    ],
)

cogito_007_html = real_article_page(
    slug="la-voie-par-defaut",
    title="La voie par défaut",
    chapo="Sur le courage de penser par soi-même",
    ref="Cogito #007",
    description="Essai Cogito : une réflexion sur le conformisme et la voie par défaut, entre l'expérience de Solomon Asch, la banalité du mal selon Hannah Arendt et le piège symétrique de l'anticonformisme.",
    cover_path="assets/img/cogito-007-cover.jpg",
    cover_credit="Johann Ludwig Bleuler, Wimmis an der Kander bey Thun",
    tags=[("cogito.html", "Cogito"), ("philosophes.html", "Philosophes")],
    body_html=COGITO_007_BODY,
    word_count=1437,
    date_published="2026-09-09",
    related=[
        ('essais/le-poids-de-lidentite.html', "Vivre selon des choix qu'on a vraiment examinés, pas hérités."),
        ('essais/la-force-de-lintuition.html', 'Écouter sa propre voix plutôt que suivre le groupe.'),
        ('essais/les-transformations-silencieuses.html', "Comment le conformisme s'installe, lui aussi, en silence."),
    ],
)

cogito_008_html = real_article_page(
    slug="les-transformations-silencieuses",
    title="Les transformations silencieuses",
    chapo="Ce qui change sans qu'on le voie",
    ref="Cogito #008",
    description="Essai Cogito : une réflexion sur les transformations silencieuses, à partir de François Jullien, sur ce qui façonne une vie sans jamais se laisser isoler en un instant précis.",
    cover_path="assets/img/cogito-008-cover.jpg",
    cover_credit="Richard Wilson, Italian Landscape (1765)",
    tags=[("cogito.html", "Cogito"), ("philosophes.html", "Philosophes")],
    body_html=COGITO_008_BODY,
    word_count=1104,
    date_published="2026-10-07",
    related=[
        ('essais/lunite-du-corps-et-de-lesprit.html', 'Même logique : ce qui nous change par répétition plutôt que par choc.'),
        ('essais/la-matiere-premiere-du-heros.html', "Ce qui nous façonne vraiment en profondeur, au-delà de l'instant."),
        ('essais/la-voie-par-defaut.html', 'Les petites répétitions qui, cumulées, mènent à une vie par défaut.'),
    ],
)

# ---------------------------------------------------------------------------
# PAGE: 404.html (erreur, hors sitemap, noindex)
# ---------------------------------------------------------------------------
VITRUVE_IMG = f'<img class="page-404-icon" src="assets/img/vitruvian-man.jpg" alt="L\'homme de Vitruve, Léonard de Vinci" loading="eager"{img_wh("assets/img/vitruvian-man.jpg")} />'

page_404_html = f"""<!doctype html>
<html lang="fr">
<head>
{head_meta(
    "Page introuvable, Intracogito",
    "Cette page n'existe pas ou plus sur Intracogito.",
    "404.html",
    robots="noindex, follow"
)}
</head>
<body>

<div class="page-404">
  <a href="index.html" class="page-404-logo">Intracogito</a>
  {VITRUVE_IMG}
  <p class="page-404-code">404</p>
  <h1>Cette page a quitté le cadre.</h1>
  <p>Elle n'existe pas, plus, ou pas encore à cette adresse. Le reste du site, lui, tient toujours debout.</p>
  <a href="index.html" class="hero-cta">Retourner à l'accueil →</a>
</div>

</body>
</html>
"""

# ---------------------------------------------------------------------------
# PAGE: mentions-legales.html
# ---------------------------------------------------------------------------
mentions_legales_html = f"""<!doctype html>
<html lang="fr">
<head>
{head_meta(
    "Mentions légales & confidentialité, Intracogito",
    "Mentions légales, hébergement, propriété intellectuelle et politique de confidentialité du site Intracogito.",
    "mentions-legales.html"
)}
</head>
<body>

{topbar(active="")}
<main>

<div class="wrap listing-head">
  <h1>Mentions légales &amp; confidentialité</h1>
</div>

<div class="wrap article-body">

<h2>Éditeur du site</h2>
<p>Le site Intracogito est édité par Elouan Noël, micro-entrepreneur.<br/>
Numéro SIRET : 924 088 891 00016<br/>
Contact : <a href="mailto:elouan.noel@gmail.com">elouan.noel@gmail.com</a><br/>
Directeur de la publication : Elouan Noël</p>

<h2>Hébergement</h2>
<p>Le site est hébergé par :<br/>
Vercel Inc.<br/>
440 N Barranca Avenue #4133, Covina, CA 91723, États-Unis<br/>
<a href="https://vercel.com" target="_blank" rel="noopener">vercel.com</a></p>

<h2>Propriété intellectuelle</h2>
<p>L'ensemble des contenus présents sur ce site (textes, essais, illustrations) est la propriété d'Elouan Noël, sauf mention contraire. Toute reproduction, même partielle, est interdite sans autorisation préalable.</p>

<h2>Données personnelles et cookies</h2>
<p>Ce site ne dépose aucun cookie de suivi et ne collecte aucune donnée personnelle directement via ses formulaires : le bouton d'inscription à la newsletter redirige vers Substack, qui dispose de sa propre politique de confidentialité.</p>
<p>Le site charge des polices via Google Fonts (Google LLC), ce qui peut entraîner un transfert de l'adresse IP du visiteur vers les serveurs de Google lors du chargement d'une page.</p>
<p>Le site peut utiliser un outil de mesure d'audience respectueux de la vie privée (Plausible), qui ne dépose pas de cookies et ne collecte aucune donnée permettant d'identifier individuellement un visiteur.</p>

<h2>Contact</h2>
<p>Pour toute question relative à ce site ou à ses contenus : <a href="mailto:elouan.noel@gmail.com">elouan.noel@gmail.com</a></p>

</div>

</main>
{footer()}
{TOGGLE_SCRIPT}
</body>
</html>
"""

# ---------------------------------------------------------------------------
# PAGE: a-propos.html
# ---------------------------------------------------------------------------
a_propos_html = f"""<!doctype html>
<html lang="fr">
<head>
{head_meta(
    "À propos, Intracogito",
    "Qui écrit Intracogito et Cogito : une philosophie incarnée, pratique, livrée chaque dimanche à 13h.",
    "a-propos.html"
)}
</head>
<body>

{topbar(active="")}
<main>

<div class="wrap listing-head">
  <h1>À propos</h1>
  <p>Qui écrit, et pourquoi.</p>
</div>

<div class="wrap article-body">

<p>Je m'appelle Elouan. Et si tu es arrivé jusqu'ici, c'est sans doute que la philosophie te parle, à toi aussi.</p>

<blockquote>
  <p>« N'explique pas ta philosophie, incarne-la. »</p>
  <p>Épictète</p>
</blockquote>

<p>C'est de cette phrase qu'est né Intracogito. Ma conviction est simple : la philosophie devient réellement intéressante lorsqu'elle redevient pratique, quand elle nous aide à mieux penser, et surtout à agir plus clairement.</p>

<h2>Intracogito, une édition chaque dimanche</h2>
<p>Chaque dimanche à 13h, je partage une édition composée de 4 ou 5 citations réunies autour d'un même thème, accompagnées d'une interprétation personnelle, une lecture « entre les lignes ». L'idée n'est pas d'avoir raison, mais d'ouvrir des pistes : nourrir la réflexion, offrir des perspectives, et donner des prises concrètes pour penser et agir.</p>
<p><a href="intracogito.html" class="hero-cta">Découvrir les éditions d'Intracogito →</a></p>

<h2>Cogito, pour aller plus loin</h2>
<p>À côté des éditions hebdomadaires, j'écris aussi des essais plus longs, Cogito, où je prends le temps de creuser une question jusqu'au bout : l'identité, le sens, la souffrance, le courage de penser par soi-même, et bien d'autres.</p>
<p><a href="cogito.html" class="hero-cta">Lire les essais Cogito →</a></p>

<h2>Et maintenant ?</h2>
<p>N'hésite pas à me partager les thèmes qui te sont chers, ou les questions que tu aimerais voir abordées : je lis tous les retours.</p>
<p>Encore bienvenue, et bonne lecture !</p>

<div class="article-author-row" style="margin-top:2.4rem;">
  <a class="article-author-avatar" href="{AUTHOR_LINKEDIN}" target="_blank" rel="noopener" aria-label="Profil LinkedIn d'Elouan Noël"><img src="{AUTHOR_PHOTO}" alt="Elouan Noël" loading="lazy"{img_wh(AUTHOR_PHOTO)} /></a>
  <div>
    <div class="article-author-name">Elouan Noël, auteur d'Intracogito</div>
  </div>
</div>

</div>

</main>
{footer()}
{TOGGLE_SCRIPT}
</body>
</html>
"""

# ---------------------------------------------------------------------------
# ÉCRITURE DES FICHIERS
# ---------------------------------------------------------------------------
os.makedirs(os.path.join(ROOT, "essais"), exist_ok=True)
os.makedirs(os.path.join(ROOT, "philosophes"), exist_ok=True)

files = {
    "index.html": index_html,
    "essais.html": essais_html,
    "essais/la-quete-de-notre-destinee.html": cogito_001_html,
    "essais/la-matiere-premiere-du-heros.html": cogito_002_html,
    "essais/la-force-de-lintuition.html": cogito_003_html,
    "essais/la-verite-du-chemin.html": cogito_004_html,
    "essais/lunite-du-corps-et-de-lesprit.html": cogito_005_html,
    "essais/le-poids-de-lidentite.html": cogito_006_html,
    "essais/la-voie-par-defaut.html": cogito_007_html,
    "essais/les-transformations-silencieuses.html": cogito_008_html,
    "mentions-legales.html": mentions_legales_html,
    "a-propos.html": a_propos_html,
}
files.update(INTRACOGITO_PAGES)
files["philosophes/marc-aurele.html"] = philosophe_marc_aurele_html
for slug, data in RUBRIQUES.items():
    files[f"{slug}.html"] = rubrique_page(slug, data)

# ---------------------------------------------------------------------------
# SITEMAP.XML + ROBOTS.TXT, générés à partir des pages réellement produites
# ---------------------------------------------------------------------------
LASTMOD = "2026-10-26"
sitemap_urls = []
for path in sorted(files.keys()):
    url_path = "" if path == "index.html" else path
    sitemap_urls.append(f"{BASE_URL}/{url_path}")
sitemap_entries = "\n".join(
    f"  <url>\n    <loc>{url}</loc>\n    <lastmod>{LASTMOD}</lastmod>\n  </url>"
    for url in sitemap_urls
)
files["sitemap.xml"] = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{sitemap_entries}
</urlset>
"""
files["404.html"] = page_404_html  # hors sitemap (page d'erreur, noindex)

files["robots.txt"] = f"""User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: CCBot
Allow: /

Sitemap: {BASE_URL}/sitemap.xml
"""

# ---------------------------------------------------------------------------
# INDEX DE RECHERCHE (assets/search-index.json) : un bouton "Rechercher"
# fonctionnel dans la topbar, qui cherche dans le TEXTE réel des articles
# publiés (pas seulement les titres). On réutilise le HTML déjà généré pour
# chaque article (ALL_ARTICLES, 72 pages Cogito + Intracogito) : on extrait
# le contenu de la zone .article-body et on retire les balises HTML.
# ---------------------------------------------------------------------------
_ARTICLE_BODY_RE = re.compile(r'<div class="wrap article-body">(.*?)<div class="wrap article-end-meta">', re.S)
_HTML_ENTITIES = {
    "&nbsp;": " ", "&amp;": "&", "&eacute;": "é", "&egrave;": "è", "&agrave;": "à",
    "&ecirc;": "ê", "&ocirc;": "ô", "&ccedil;": "ç", "&icirc;": "î", "&ucirc;": "û",
    "&apos;": "'", "&quot;": '"', "&#39;": "'",
}

def _plain_text_from_html(html_src):
    t = re.sub(r"<[^>]+>", " ", html_src)
    for ent, rep in _HTML_ENTITIES.items():
        t = t.replace(ent, rep)
    t = re.sub(r"\s+", " ", t).strip()
    return t

# Pages piliers (Philosophes/Concepts/Comparatifs) : indexées à part, car elles
# ne font pas partie d'ALL_ARTICLES (qui alimente essais.html et les reco Cogito/Intracogito).
PILIER_PAGES_FOR_SEARCH = [
    {"href": "philosophes/marc-aurele.html", "meta": "Philosophes", "chapo": "Philosophes", "title": "Marc Aurèle", "img": "assets/img/og-default.jpg"},
]

search_index = []
for _a in ALL_ARTICLES + PILIER_PAGES_FOR_SEARCH:
    _html_src = files.get(_a["href"], "")
    _m = _ARTICLE_BODY_RE.search(_html_src)
    _text = _plain_text_from_html(_m.group(1)) if _m else ""
    search_index.append({
        "href": "/" + _a["href"],
        "meta": _a["meta"],
        "badge": _a["chapo"],
        "title": _a["title"],
        "img": "/" + _a["img"],
        "text": _text,
    })
search_index_json = json.dumps(search_index, ensure_ascii=False)

for path, content in files.items():
    full = os.path.join(ROOT, path)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"wrote {path} ({len(content)} chars)")

with open(os.path.join(ROOT, "assets", "search-index.json"), "w", encoding="utf-8") as f:
    f.write(search_index_json)
print(f"wrote assets/search-index.json ({len(search_index_json)} chars) [index de recherche, hors sitemap]")

# Écrit à part : jamais dans `files` (donc jamais dans le sitemap/robots.txt),
# c'est un fichier d'outillage pour la publication Artifact de cette session,
# pas une page du vrai site.
with open(os.path.join(ROOT, "_artifact_index.html"), "w", encoding="utf-8") as f:
    f.write(index_artifact_body)
print(f"wrote _artifact_index.html ({len(index_artifact_body)} chars) [outil Artifact, hors sitemap]")

print("\\nDone.")

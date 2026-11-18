#!/usr/bin/env python3
"""Build ce.html (the Windows CE / Pocket PC edition) from index.html.

Usage:  python3 tools/build_ce.py
The content is read from index.html so both editions stay in step; only the
presentation differs. Run it again whenever index.html changes.
"""
import re, html, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'index.html')
OUT = os.path.join(ROOT, 'ce.html')
s = open(SRC, encoding='utf-8').read()
I = 'assets/icons/win98/'

def ws(t): return re.sub(r'\s+', ' ', t).strip()
def text(t): return html.unescape(ws(re.sub(r'<[^>]+>', ' ', t))).replace(' ,', ',').replace(' .', '.')
def esc(t): return html.escape(t, quote=False)
def keep(t):                      # inline markup worth keeping
    t = re.sub(r'<(?!/?(?:b|em|i|u)\b)[^>]+>', '', t)
    return ws(t)

def section(id_):
    m = re.search(r'<section class="(?:sec|footer)" id="%s"' % id_, s)
    a = m.start(); b = s.index('</section>', a)
    return s[a:b]

def head(id_):
    t = section(id_)
    h = re.search(r'wiz-title">(.*?)</h2><div class="wiz-sub">(.*?)</div>', t)
    return (text(h.group(1)), text(h.group(2))) if h else ('', '')

# ---------------------------------------------------------------- content
def about():
    t = section('about')
    paras = ''.join('<p>%s</p>' % keep(p) for p in re.findall(r'<p class="about-p">(.*?)</p>', t, re.S))
    tabs = re.findall(r'data-p="\d+"[^>]*>([A-Za-z ]+)</button>', t)
    out = paras
    pages = re.findall(r'<div class="ad-page" data-p="(\d)".*?(?=<div class="ad-page"|<div class="ad-btns")', t, re.S)
    blocks = re.findall(r'<div class="ad-page" data-p="\d"[^>]*>(.*?)(?=<div class="ad-page"|<div class="ad-btns")', t, re.S)
    out += '<h4 class="grp">Properties</h4><dl class="props">'
    for name, blk in zip(tabs, blocks):
        out += '<dt class="tab">%s</dt>' % esc(name)
        rows = re.findall(r'<td class="l"[^>]*>(.*?)</td><td>(.*?)</td></tr>', blk, re.S)
        for k, v in rows:
            out += '<dd><span class="k">%s</span> <span class="v">%s</span></dd>' % (esc(text(k)), keep(v))
        for li in re.findall(r'<td> (.*?)</td>', blk):
            out += '<dd><span class="v">%s</span></dd>' % esc(text(li))
    out += '</dl>'
    return out

def career():
    t = section('experience')
    out = ''
    hops = re.split(r'<table class="hop(?: current)?"[^>]*>', t)[1:]
    for h in hops:
        n = text(re.search(r'hop-n">(.*?)</span>', h).group(1))
        host = text(re.sub(r'<span class="hop-n">.*?</span>', '', re.search(r'class="hop-host">(.*?)</td>', h).group(1)))
        tm = text(re.search(r'class="hop-time"[^>]*>(.*?)</td>', h).group(1))
        role = text(re.sub(r'<span class="tri">.*?</span>', '', re.search(r'class="hop-role">(.*?)</div>', h).group(1)))
        lis = re.findall(r'<li>(.*?)</li>', h, re.S)
        body = '<ul>%s</ul>' % ''.join('<li>%s</li>' % keep(l) for l in lis) if lis else \
               '<p>%s</p>' % keep(re.search(r'class="hop-desc">(.*?)</div>', h, re.S).group(1))
        out += ('<div class="rec"><div class="rec-h"><b>%s</b> %s<span class="tm">%s</span></div>'
                '<div class="role">%s</div>%s</div>') % (esc(n), esc(host), esc(tm), esc(role), body)
    return out

def arrays():
    import json
    res = []
    for m in re.finditer(r'const CHAPTERS = \[', s):
        i = m.end(); depth = 1
        while depth:
            c = s[i]
            if c == '[': depth += 1
            elif c == ']': depth -= 1
            i += 1
        body = s[m.end():i-1]
        items = re.findall(r"\{tab:'((?:[^'\\]|\\.)*)',\s*title:'((?:[^'\\]|\\.)*)',\s*(?:phase:(\d),\s*)?spot:(null|\[[^\]]*\]),\s*flows:(null|\[[^\]]*\]),\s*text:'((?:[^'\\]|\\.)*)'\}", body, re.S)
        res.append([{'tab': a.replace("\\'", "'"), 'title': b.replace("\\'", "'"), 'phase': int(ph) if ph else 0,
                     'spot': json.loads(sp), 'flows': json.loads(fl), 'text': keep(c.replace("\\'", "'"))} for a, b, ph, sp, fl, c in items])
    return res

SVGS = {
    'homelab': re.search(r'<svg class="topo-svg homelab-svg".*?</svg>', s, re.S).group(0),
    'openclaw': re.search(r'<svg class="topo-svg openclaw-svg".*?</svg>', s, re.S).group(0),
    'devops': re.search(r'<svg class="topo-svg devops-svg".*?</svg>', s, re.S).group(0),
    'timelapse': re.search(r'<svg class="topo-svg timelapse-svg".*?</svg>', s, re.S).group(0),
}

def viewer(title, items, key, n):
    import json
    return ('<h4 class="grp">%s</h4><div class="dg" id="dg%d" data-k="%s"><div class="dg-tabs" role="tablist"></div>'
            '<div class="dg-pan">%s</div>'
            '<div class="dg-bar"><button type="button" data-z="-">&minus;</button><button type="button" data-z="+">+</button><button type="button" data-z="f">Fit</button>'
            '<span class="sp"></span><button type="button" data-c="-">&lt;</button><button type="button" data-c="+">&gt;</button></div>'
            '<div class="dg-cap" aria-live="polite"></div><div class="dg-flows" aria-label="Traffic patterns"></div>'
            '<script type="application/json" class="dg-data">%s</script></div>') % (
            esc(title), n, key, SVGS[key], json.dumps(items).replace('</', '<\\/'))

def buildout():
    t = section('growth')
    out = '<h4 class="grp">Impact.xls</h4><table class="xl">'
    for r in re.findall(r'<tr><th class="rh">\d+</th>(.*?)</tr>', t, re.S):
        cells = re.findall(r'<td[^>]*>(.*?)</td>', r, re.S)
        if not any(text(c) for c in cells): continue
        out += '<tr>%s</tr>' % ''.join('<td>%s</td>' % esc(text(c)) for c in cells)
    out += '</table>'
    # platform chapters, as the PowerPoint slides
    out += '<h4 class="grp">Platform.ppt</h4>'
    for tag, h3, sub, lis in re.findall(r'<div class="s-tag">(.*?)</div><h3>(.*?)</h3><div class="s-sub">(.*?)</div><ul>(.*?)</ul>', t, re.S):
        out += '<div class="slide"><div class="slide-t">%s</div><h5>%s</h5><div class="sub">%s</div><ul>%s</ul></div>' % (
            esc(text(tag)), esc(text(h3)), esc(text(sub)), ''.join('<li>%s</li>' % keep(l) for l in re.findall(r'<li>(.*?)</li>', lis, re.S)))
    # featured projects
    out += '<h4 class="grp">Featured projects</h4>'
    for blk in re.findall(r'<div class="errd" role="group" aria-label="(.*?)">(.*?)</div></div>\s*</div>', t, re.S):
        pass
    for name, rest in re.findall(r'<div class="errd" role="group" aria-label="(.*?)">(.*?)(?=<div class="errd" role="group"|</div>\s*</div>\s*</div>\s*<div class="topo-wrap"|$)', t, re.S):
        sub = re.search(r'errd-name">.*?</p><p>(.*?)</p>', rest, re.S)
        det = re.search(r'<div class="errd-det"[^>]*>(.*?)</div></div>\s*$', rest.strip(), re.S) or re.search(r'<div class="errd-det"[^>]*>(.*)', rest, re.S)
        body = det.group(1) if det else ''
        body = re.sub(r'<div class="errd-mod">(.*?)</div>', lambda m: '<p class="mods">%s</p>' % esc(text(m.group(1))), body)
        body = re.sub(r'<div class="errd-li">(.*?)</div>', r'<li>\1</li>', body)
        if '<li>' in body:
            body = re.sub(r'((?:<li>.*?</li>)+)', r'<ul>\1</ul>', body, count=1)
        else:
            body = re.sub(r'^<div>(.*?)</div>', r'<p>\1</p>', body, count=1)
        cut = max(body.rfind('</p>'), body.rfind('</ul>'))
        body = body[:cut + (4 if body[cut:cut+4] == '</p>' else 5)] if cut >= 0 else body
        out += '<div class="proj"><div class="proj-h">%s</div><div class="sub">%s</div>%s</div>' % (
            esc(html.unescape(name)), esc(text(sub.group(1))) if sub else '', body)
    # skills
    out += '<h4 class="grp">Skill depth</h4><div class="skills">'
    for tech, tags, lv in re.findall(r"\{tech:'(.*?)', tags:'(.*?)', levels:\[(\d),(\d),(\d)\]\}".replace('(\\d),(\\d),(\\d)', '([\\d,]+)') if False else r"\{tech:'(.*?)',\s*tags:'(.*?)',\s*levels:\[([\d,\s]+)\]\}", s):
        l = [int(x) for x in lv.split(',')]
        out += ('<div class="sk"><div class="sk-n">%s <span>%d/5</span></div><div class="bar">%s%s%s%s</div><div class="sk-t">%s</div></div>') % (
            esc(html.unescape(tech)), l[2],
            '<i class="i"></i>' * l[0], '<i class="e"></i>' * (l[1]-l[0]), '<i class="l"></i>' * (l[2]-l[1]), '<i class="z"></i>' * (5-l[2]),
            esc(html.unescape(tags)))
    out += '</div><p class="legend"><i class="i"></i> Intern <i class="e"></i> Executive <i class="l"></i> Lead</p>'
    return out, arrays()

def sidebuilds():
    t = section('sideprojects')
    out = ''
    for h3, sub, p, tags in re.findall(r'<article class="hlp-topic"[^>]*>.*?<h3>(.*?)</h3><div class="hlp-sub">(.*?)</div><p>(.*?)</p>.*?<ul>(.*?)</ul>', t, re.S):
        out += '<div class="proj"><div class="proj-h">%s</div><div class="sub">%s</div><p>%s</p><p class="mods">%s</p></div>' % (
            esc(text(h3)), esc(text(sub)), keep(p), esc(', '.join(text(x) for x in re.findall(r'<li>(.*?)</li>', tags))))
    return out

def education():
    t = section('education'); out = ''
    for tag, h3, sub, p, meta in re.findall(r'<div class="card-tag">(.*?)</div>\s*<h3>(.*?)</h3>\s*<div class="sub">(.*?)</div>\s*<p>(.*?)</p>\s*<div class="meta">(.*?)</div>', t, re.S):
        out += '<div class="proj"><div class="proj-h">%s</div><div class="sub">%s &middot; %s</div><p>%s</p><p class="mods">%s</p></div>' % (
            esc(text(h3)), esc(text(tag)), esc(text(sub)), keep(p), esc(text(meta)))
    return out

def certs():
    t = section('certifications'); out = '<table class="xl">'
    out += '<tr><th>Name</th><th>Issuer</th></tr>'
    for n, i in re.findall(r'<td class="ic">.*?</td><td>(.*?)</td><td>(.*?)</td></tr>', t, re.S):
        out += '<tr><td>%s</td><td>%s</td></tr>' % (esc(text(n)), esc(text(i)))
    return out + '</table>'

def pubs():
    t = section('publications'); out = ''
    for ti, me in re.findall(r'<div class="pub-title"[^>]*>(.*?)</div>\s*(?:<div class="pub-meta">(.*?)</div>)?', t, re.S):
        out += '<div class="pub"><b>%s</b>%s</div>' % (esc(text(ti)), '<div class="sub">%s</div>' % esc(text(me)) if me else '')
    out += '<p class="mods">%s</p>' % esc(' · '.join(text(x) for x in re.findall(r'class="honor-chip">(.*?)</span>', t)))
    return out

def contact():
    t = section('contact')
    mail = re.search(r'href="mailto:([^"]+)"', t).group(1)
    sub = re.search(r'Subject:</td><td><span class="win-field">(.*?)</span>', t).group(1)
    body = re.search(r'<p class="footer-sub">(.*?)</p>', t).group(1)
    li = re.search(r'<a href="(https://linkedin[^"]+)"[^>]*>(.*?)</a>', t)
    return ('<p>%s</p><dl class="props"><dd><span class="k">To:</span> <span class="v"><a href="mailto:%s">%s</a></span></dd>'
            '<dd><span class="k">Subject:</span> <span class="v">%s</span></dd>'
            '<dd><span class="k">LinkedIn:</span> <span class="v"><a href="%s" rel="noopener">%s</a></span></dd></dl>') % (
            keep(body), mail, esc(mail), esc(text(sub)), li.group(1), esc(text(li.group(2))))

# ---------------------------------------------------------------- assemble
build, arr = buildout()
tours = viewer('Homelab tour', arr[0], 'homelab', 1) + viewer('AIOps agent team', arr[1], 'openclaw', 2) + viewer('GitOps pipeline', arr[2], 'devops', 3)
platform = viewer('Platform time-lapse', arr[3], 'timelapse', 0)
SECS = [
    ('about',          'briefcase_0.png' if False else 'address_book_user.png', about()),
    ('experience',     'briefcase_0.png',        career()),
    ('growth',         'server_window.png',      build + platform),
    ('sideprojects',   'tools_gear_0.png',       sidebuilds() + tours),
    ('education',      'help_book_big_0.png',    education()),
    ('certifications', 'certificate_0.png',      certs()),
    ('publications',   'newspaper.png',          pubs()),
    ('contact',        'envelope_closed_0.png',  contact()),
]
LABEL = {'about': 'About', 'experience': 'Career', 'growth': 'Buildout', 'sideprojects': 'Side Builds',
         'education': 'Education', 'certifications': 'Certifications', 'publications': 'Publications', 'contact': 'Contact'}
ROWS = ''.join(
    '<section class="tv" id="%s"><button type="button" class="tv-h" aria-expanded="%s" aria-controls="%s-b"><span class="box"></span>'
    '<img src="%s%s" alt="" width="32" height="32"><span class="tt"><b>%s</b><small>%s</small></span></button>'
    '<div class="tv-b" id="%s-b"%s>%s</div></section>' % (
        id_, 'true' if n == 0 else 'false', id_, I, icon, esc(head(id_)[0] or LABEL[id_]), esc(head(id_)[1]), id_,
        '' if n == 0 else ' hidden', body)
    for n, (id_, icon, body) in enumerate(SECS))
MENU = ''.join('<li><a href="#%s"><img src="%s%s" alt="" width="32" height="32"><span>%s</span></a></li>' % (i, I, ic, LABEL[i]) for i, ic, _ in SECS)

hero = re.search(r'hero-role">(.*?)</div>', s, re.S)
TAGLINE = keep(hero.group(1)) if hero else ''
updated = re.search(r'class="updated">(.*?)</div>', s).group(1)
ai_note = re.search(r'footer-ai">(.*?)</div>', s).group(1)

def fn_block(src, start):
    i = src.index('{', src.index(')', start)); depth = 0
    for j in range(i, len(src)):
        if src[j] == '{': depth += 1
        elif src[j] == '}':
            depth -= 1
            if depth == 0: return src[start:j + 1]
TRAFFIC_FN = fn_block(s, s.index('function trafficDiagram('))
def setup(var):
    a = s.index("const %s = document.querySelector" % var); a = s.index('{', s.index('if (%s)' % var, a)) + 1
    b = s.index('const traffic = trafficDiagram(', a)
    call = s[b:s.index('\n', b)]
    opts = re.search(r'(\{max:[^}]*\})\);', call).group(1)
    return 'function (%s, list) {\n%s\n    return trafficDiagram(%s, N, E, PATTERNS, list, %s);\n  }' % (var, s[a:b], var, opts)
TRAFFIC_JS = ('(function () {\n' + TRAFFIC_FN + '\n  window.ceTraffic = {\n    homelab: ' + setup('homelabSvg') + ',\n    openclaw: ' + setup('ocSvg') +
              ',\n    devops: ' + setup('dvSvg') + ',\n    timelapse: ' + setup('tlSvg') + '\n  };\n})();')
tpl = open(os.path.join(ROOT, 'tools', 'ce_template.html'), encoding='utf-8').read()
css0 = s.index('.topo-wrap{'); css1 = s.index('.wdeco image{'); css1 = s.index('}', css1) + 1
TOPOCSS = s[css0:css1].replace('.topo-wrap{margin-top:8px;', '.dg{')
w0 = s.index('/* Win9x desktop look for the architecture diagrams'); w0 = s.rindex('<script>', 0, w0) + len('<script>'); w1 = s.index('</script>', w0)
WINDOWIZE = s[w0:w1]
out = (tpl.replace('{{TOPOCSS}}', TOPOCSS).replace('{{WINDOWIZE}}', WINDOWIZE).replace('{{TRAFFIC}}', TRAFFIC_JS).replace('{{ROWS}}', ROWS).replace('{{MENU}}', MENU).replace('{{TAGLINE}}', TAGLINE)
          .replace('{{UPDATED}}', esc(text(updated))).replace('{{AINOTE}}', esc(text(ai_note))))
open(OUT, 'w', encoding='utf-8').write(out)
print('wrote', OUT, len(out), 'bytes')

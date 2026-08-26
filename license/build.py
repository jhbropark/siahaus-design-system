#!/usr/bin/env python3
"""
data/site.json → index.html · llms.txt · sitemap.xml 생성.

내용을 정적 HTML 로 인라인해 내보냅니다. JS 로 렌더링하면 봇이 받는 원본
HTML 이 비어 GEO 가 무너지므로, 이 스크립트가 빌드 시점에 전부 펼칩니다.

사용:
    python3 build.py            # 생성
    python3 build.py --check    # 쓰지 않고 검증만
"""
import html
import json
import re
import sys
from datetime import date, timezone, datetime
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data" / "site.json"
TBD = "확정 예정"

placeholders: list[str] = []


def val(v, path: str, unit: str = "") -> str:
    """None 이면 '확정 예정' 으로 렌더링하고 미확정 목록에 기록한다."""
    if v in (None, "", []):
        placeholders.append(path)
        return TBD
    return f"{v}{unit}"


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def build_html(d: dict, today: str) -> str:
    site, meta = d["site"], d["meta"]
    hero, how, cat, plans, faq, contact = (
        d["hero"], d["how"], d["catalog"], d["plans"], d["faq"], d["contact"]
    )

    # ── JSON-LD ────────────────────────────────────────────────────────────
    graph = [
        {
            "@type": "WebSite",
            "@id": f"{site['url']}#website",
            "url": site["url"],
            "name": site["name"],
            "inLanguage": "ko",
            "publisher": {"@id": site["parent_org_id"]},
        },
        {
            "@type": "Service",
            "@id": f"{site['url']}#service",
            "name": site["name"],
            "serviceType": "미디어아트 구독 라이선싱",
            "description": hero["definition"],
            "provider": {"@id": site["parent_org_id"]},
            "areaServed": {"@type": "Country", "name": "KR"},
            "hasOfferCatalog": {
                "@type": "OfferCatalog",
                "name": plans["title"],
                "itemListElement": [
                    {
                        "@type": "Offer",
                        "name": p["name"],
                        "description": p["tagline"],
                        **(
                            {
                                "priceSpecification": {
                                    "@type": "UnitPriceSpecification",
                                    "price": str(p["price_monthly"]),
                                    "priceCurrency": "KRW",
                                    "unitCode": "MON",
                                }
                            }
                            if p.get("price_monthly")
                            else {}
                        ),
                    }
                    for p in plans["items"]
                ],
            },
        },
        {
            "@type": "ItemList",
            "@id": f"{site['url']}#catalog",
            "name": cat["title"],
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "item": {
                        "@type": "CreativeWork",
                        "name": w["title"],
                        "genre": w["kind"],
                        "abstract": w["summary"],
                        "creator": {"@id": site["parent_org_id"]},
                        **({"dateCreated": w["year"]} if w.get("year") else {}),
                    },
                }
                for i, w in enumerate(cat["works"])
            ],
        },
        {
            "@type": "FAQPage",
            "@id": f"{site['url']}#faq",
            "isPartOf": {"@id": f"{site['url']}#website"},
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": q["q"],
                    "acceptedAnswer": {"@type": "Answer", "text": q["a"]},
                }
                for q in faq["items"]
            ],
        },
    ]
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph},
                    ensure_ascii=False, indent=2)

    # ── 카탈로그 카드 ───────────────────────────────────────────────────────
    cards = "\n".join(
        f'''        <article class="work" id="work-{esc(w['id'])}">
          <div class="work-visual tone-{esc(w['tone'])}" role="img"
               aria-label="{esc(w['title'])} — 작품 이미지 자리표시자"></div>
          <div class="work-body">
            <span class="work-kind">{esc(w['kind'])}{' · ' + esc(w['year']) if w.get('year') else ''}</span>
            <h3 class="work-title">{esc(w['title'])}</h3>
            <p class="work-sum">{esc(w['summary'])}</p>
            <dl class="spec">
              <div><dt>러닝타임</dt><dd>{esc(val(w['runtime'], f"works.{w['id']}.runtime"))}</dd></div>
              <div><dt>해상도</dt><dd>{esc(val(w['resolution'], f"works.{w['id']}.resolution"))}</dd></div>
              <div><dt>비율</dt><dd>{esc(val(w['ratio'], f"works.{w['id']}.ratio"))}</dd></div>
            </dl>
          </div>
        </article>'''
        for w in cat["works"]
    )

    # ── 플랜 카드 ──────────────────────────────────────────────────────────
    def plan_card(p: dict) -> str:
        price = p.get("price_monthly")
        if price:
            price_html = f'<span class="num">₩{int(price):,}</span><span class="per">/ 월</span>'
        else:
            placeholders.append(f"plans.{p['id']}.price_monthly")
            price_html = f'<span class="tbd">{TBD}</span>'
        feats = "\n".join(f"              <li>{esc(f)}</li>" for f in p["features"])
        return f'''        <article class="plan{' feat' if p.get('featured') else ''}">
          {'<span class="plan-badge">권장</span>' if p.get('featured') else ''}
          <h3 class="plan-name">{esc(p['name'])}</h3>
          <p class="plan-tag">{esc(p['tagline'])}</p>
          <p class="plan-price">{price_html}</p>
          <p class="plan-term">계약 기간 {esc(val(p.get('term'), f"plans.{p['id']}.term"))}</p>
          <ul class="plan-feats">
{feats}
          </ul>
          <a class="btn btn-{'accent' if p.get('featured') else 'outline'}" href="#contact">문의하기</a>
        </article>'''

    plan_cards = "\n".join(plan_card(p) for p in plans["items"])

    steps_html = "\n".join(
        '          <div class="step">\n'
        f'            <span class="step-n">{esc(s["n"])}</span>\n'
        f'            <h3 class="step-t">{esc(s["t"])}</h3>\n'
        f'            <p class="step-d">{esc(s["d"])}</p>\n'
        '          </div>'
        for s in how["steps"]
    )

    faq_items = "\n".join(
        f'''        <details class="qa">
          <summary>{esc(q['q'])}</summary>
          <p>{esc(q['a'])}</p>
        </details>'''
        for q in faq["items"]
    )

    # ── 문의 ───────────────────────────────────────────────────────────────
    if contact.get("formspree_id"):
        form = f'''      <form class="cform" action="https://formspree.io/f/{esc(contact['formspree_id'])}" method="POST">
        <label>회사 / 기관 <input type="text" name="company" required></label>
        <label>담당자 <input type="text" name="name" required></label>
        <label>연락처 <input type="text" name="phone" required></label>
        <label>이메일 <input type="email" name="email" required></label>
        <label>공간 조건 <textarea name="space" rows="4" placeholder="설치 위치, 화면 규격, 운영 기간" required></textarea></label>
        <button class="btn btn-accent btn-lg" type="submit">문의 보내기</button>
      </form>'''
    else:
        placeholders.append("contact.formspree_id")
        subject = "[SIA.HAUS 라이선스] 구독 문의"
        body = "회사 / 기관:%0D%0A담당자:%0D%0A연락처:%0D%0A%0D%0A설치 위치:%0D%0A화면 규격:%0D%0A운영 기간:%0D%0A"
        form = f'''      <div class="cform cform-mail">
        <p class="cform-note">폼 연동 전입니다. 아래 버튼을 누르면 항목이 채워진 메일이 열립니다.</p>
        <a class="btn btn-accent btn-lg" href="mailto:{esc(site['email'])}?subject={subject}&amp;body={body}">메일로 문의하기</a>
        <p class="cform-alt">또는 직접 보내기 · <a href="mailto:{esc(site['email'])}">{esc(site['email'])}</a></p>
      </div>'''

    headline = esc(hero["headline"]).replace("\n", "<br />")
    _first, _sep, _rest = hero["definition"].partition(".")
    definition_html = f"<b>{esc(_first)}{esc(_sep)}</b>{esc(_rest)}"

    return f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{esc(meta['title'])}</title>
<meta name="description" content="{esc(meta['description'])}" />
<link rel="canonical" href="{esc(site['url'])}" />
<meta property="og:type" content="website" />
<meta property="og:site_name" content="{esc(site['name'])}" />
<meta property="og:title" content="{esc(meta['title'])}" />
<meta property="og:description" content="{esc(meta['description'])}" />
<meta property="og:url" content="{esc(site['url'])}" />
<meta name="twitter:card" content="summary_large_image" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.css" />
<script type="application/ld+json">
{ld}
</script>
<style>
:root{{
  --ink-900:#08090A; --ink-850:#0C0D0F; --ink-800:#121316; --ink-700:#181A1E;
  --ink-600:#202329; --ink-500:#2A2E35;
  --paper-000:#FAFAF7; --paper-100:#F2F2EE; --paper-200:#D8D8D2; --paper-300:#A7A8A3; --paper-400:#6E7075;
  --champagne-300:#E2CFA0; --champagne-400:#C9A86A; --champagne-600:#8A6F3A;
  --spectral-amber:#D6A75C; --spectral-slate:#6E8FB8; --spectral-violet:#9A8FB5;
  --spectral-sage:#7FA88E; --spectral-rose:#C58F8A;
  --stage:var(--ink-900); --bg:var(--ink-850); --surface:var(--ink-700); --surface-raised:var(--ink-600);
  --surface-section:var(--ink-800);
  --text-strong:var(--paper-000); --text:var(--paper-100); --text-muted:var(--paper-200);
  --text-subtle:var(--paper-300); --text-faint:var(--paper-400);
  --accent:var(--champagne-400); --accent-soft:var(--champagne-300); --accent-deep:var(--champagne-600);
  --on-accent:var(--ink-900);
  --line:var(--ink-500); --line-faint:rgba(242,242,238,0.08);
  --font-display:"Pretendard Variable","Pretendard",system-ui,sans-serif;
  --font-mono:"IBM Plex Mono","SFMono-Regular",ui-monospace,monospace;
  --ease-out:cubic-bezier(0.16,1,0.3,1); --dur:280ms;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth;scroll-padding-top:72px}}
body{{background:var(--bg);color:var(--text);font-family:var(--font-display);
  line-height:1.65;letter-spacing:-0.005em;-webkit-font-smoothing:antialiased}}
a{{color:inherit;text-decoration:none}}
.wrap{{max-width:1120px;margin:0 auto;padding:0 clamp(20px,4vw,40px)}}
section{{padding:clamp(56px,9vw,104px) 0}}
.eyebrow{{font-family:var(--font-mono);font-size:12px;letter-spacing:0.28em;
  text-transform:uppercase;color:var(--accent);font-weight:700}}
h2{{font-size:clamp(26px,4vw,44px);font-weight:200;letter-spacing:-0.02em;
  line-height:1.12;margin:14px 0 0;color:var(--text-strong);text-wrap:balance}}
.lead{{margin-top:16px;color:var(--text-muted);font-size:clamp(15px,1.8vw,18px);max-width:64ch}}
.btn{{display:inline-flex;align-items:center;gap:8px;font-weight:600;border-radius:4px;
  padding:12px 22px;font-size:14px;border:1px solid transparent;font-family:inherit;
  cursor:pointer;transition:filter var(--dur) var(--ease-out),border-color var(--dur) var(--ease-out)}}
.btn-accent{{background:var(--accent);color:var(--on-accent)}}
.btn-accent:hover{{filter:brightness(1.07)}}
.btn-outline{{border-color:var(--line);color:var(--text)}}
.btn-outline:hover{{border-color:var(--accent-deep);background:var(--surface)}}
.btn-lg{{padding:15px 28px;font-size:15px}}

header.top{{position:sticky;top:0;z-index:50;background:rgba(12,13,15,0.86);
  backdrop-filter:blur(12px);border-bottom:1px solid var(--line-faint)}}
.top-in{{max-width:1120px;margin:0 auto;padding:14px clamp(20px,4vw,40px);
  display:flex;align-items:center;gap:24px}}
.logo{{font-weight:300;letter-spacing:-0.02em;font-size:17px;color:var(--text-strong)}}
.logo b{{font-weight:600;color:var(--accent)}}
.top nav{{display:flex;gap:20px;margin-left:auto;font-size:13.5px;color:var(--text-subtle)}}
.top nav a:hover{{color:var(--text)}}
@media(max-width:640px){{.top nav{{display:none}}}}

.hero{{padding:clamp(72px,13vw,140px) 0 clamp(48px,7vw,80px);
  background:linear-gradient(180deg,var(--stage),var(--bg))}}
.hero h1{{font-size:clamp(38px,7.5vw,84px);font-weight:100;letter-spacing:-0.03em;
  line-height:1.04;margin:20px 0 0;color:var(--text-strong)}}
.hero .definition{{margin-top:28px;font-size:clamp(15px,1.9vw,19px);line-height:1.72;
  color:var(--text-muted);max-width:60ch}}
.hero .definition b{{color:var(--text-strong);font-weight:600}}
.hero-cta{{display:flex;gap:12px;flex-wrap:wrap;margin-top:34px}}

.band{{background:var(--surface-section);border-top:1px solid var(--line-faint);
  border-bottom:1px solid var(--line-faint)}}
.steps{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:40px}}
@media(max-width:800px){{.steps{{grid-template-columns:1fr}}}}
.step{{border-top:1px solid var(--accent-deep);padding-top:20px}}
.step-n{{font-family:var(--font-mono);font-size:12px;letter-spacing:0.1em;color:var(--accent)}}
.step-t{{font-size:19px;font-weight:600;margin:8px 0 8px;color:var(--text-strong)}}
.step-d{{color:var(--text-subtle);font-size:14.5px;line-height:1.7}}

.works{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:40px}}
@media(max-width:980px){{.works{{grid-template-columns:repeat(2,1fr)}}}}
@media(max-width:620px){{.works{{grid-template-columns:1fr}}}}
.work{{background:var(--surface);border:1px solid var(--line);border-radius:4px;overflow:hidden;
  display:flex;flex-direction:column;transition:border-color var(--dur) var(--ease-out)}}
.work:hover{{border-color:var(--accent-deep)}}
.work-visual{{aspect-ratio:16/10;background:linear-gradient(135deg,var(--tone,#2A2E35),var(--ink-800) 70%);
  filter:saturate(0.9)}}
.tone-slate{{--tone:#6E8FB8}} .tone-violet{{--tone:#9A8FB5}} .tone-amber{{--tone:#D6A75C}}
.tone-sage{{--tone:#7FA88E}} .tone-rose{{--tone:#C58F8A}}
.work-body{{padding:20px;display:flex;flex-direction:column;flex:1}}
.work-kind{{font-family:var(--font-mono);font-size:11px;letter-spacing:0.1em;
  text-transform:uppercase;color:var(--accent)}}
.work-title{{font-size:18px;font-weight:600;margin:8px 0 8px;color:var(--text-strong);letter-spacing:-0.01em}}
.work-sum{{color:var(--text-subtle);font-size:14px;line-height:1.65;flex:1}}
.spec{{display:flex;flex-wrap:wrap;gap:6px 18px;margin-top:16px;padding-top:14px;
  border-top:1px solid var(--line-faint);font-size:12px}}
.spec div{{display:flex;gap:6px}}
.spec dt{{color:var(--text-faint);font-family:var(--font-mono)}}
.spec dd{{color:var(--text-muted)}}
.note{{margin-top:20px;font-size:12.5px;color:var(--text-faint);font-family:var(--font-mono)}}

.plans-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:40px}}
@media(max-width:900px){{.plans-grid{{grid-template-columns:1fr}}}}
.plan{{position:relative;background:var(--surface);border:1px solid var(--line);border-radius:4px;
  padding:26px 24px;display:flex;flex-direction:column}}
.plan.feat{{border-color:var(--accent-deep);background:var(--surface-raised)}}
.plan-badge{{position:absolute;top:-1px;right:20px;background:var(--accent);color:var(--on-accent);
  font-size:11px;font-weight:700;padding:4px 10px;border-radius:0 0 4px 4px;font-family:var(--font-mono)}}
.plan-name{{font-size:21px;font-weight:600;color:var(--text-strong);letter-spacing:-0.01em}}
.plan-tag{{color:var(--text-subtle);font-size:13.5px;margin-top:6px}}
.plan-price{{margin:22px 0 4px;display:flex;align-items:baseline;gap:7px}}
.plan-price .num{{font-size:34px;font-weight:200;color:var(--text-strong);letter-spacing:-0.02em}}
.plan-price .per{{font-size:13px;color:var(--text-faint)}}
.plan-price .tbd{{font-size:19px;color:var(--accent-soft);font-family:var(--font-mono);
  border-bottom:1px dashed var(--accent-deep);padding-bottom:2px}}
.plan-term{{font-size:12.5px;color:var(--text-faint);font-family:var(--font-mono)}}
.plan-feats{{list-style:none;margin:22px 0 26px;display:flex;flex-direction:column;gap:9px;flex:1}}
.plan-feats li{{font-size:14px;color:var(--text-muted);padding-left:18px;position:relative;line-height:1.6}}
.plan-feats li::before{{content:"—";position:absolute;left:0;color:var(--accent-deep)}}

.qa{{border-bottom:1px solid var(--line-faint)}}
.qa summary{{cursor:pointer;padding:20px 0;font-weight:600;font-size:16px;list-style:none;
  display:flex;justify-content:space-between;gap:16px;color:var(--text-strong)}}
.qa summary::-webkit-details-marker{{display:none}}
.qa summary::after{{content:"+";color:var(--accent);font-weight:300;font-size:22px;flex:none;line-height:1}}
.qa[open] summary::after{{content:"–"}}
.qa p{{padding:0 0 22px;color:var(--text-subtle);font-size:14.5px;line-height:1.75;max-width:72ch}}

.cform{{margin-top:36px;max-width:560px}}
.cform label{{display:block;margin-bottom:16px;font-size:13px;color:var(--text-subtle);
  font-family:var(--font-mono);letter-spacing:0.06em}}
.cform input,.cform textarea{{width:100%;margin-top:7px;background:var(--surface);
  border:1px solid var(--line);border-radius:4px;padding:12px 14px;color:var(--text);
  font-family:var(--font-display);font-size:15px;letter-spacing:-0.005em}}
.cform input:focus,.cform textarea:focus{{outline:none;border-color:var(--accent-deep)}}
.cform-note{{color:var(--text-faint);font-size:13px;margin-bottom:18px;font-family:var(--font-mono)}}
.cform-alt{{margin-top:16px;font-size:13.5px;color:var(--text-subtle)}}
.cform-alt a{{color:var(--accent);border-bottom:1px solid var(--accent-deep)}}

footer{{border-top:1px solid var(--line-faint);padding:36px 0;background:var(--stage)}}
.foot{{display:flex;flex-wrap:wrap;gap:10px 28px;font-size:12.5px;color:var(--text-faint)}}
.foot a{{color:var(--text-subtle)}}
.foot a:hover{{color:var(--accent)}}
@media(prefers-reduced-motion:reduce){{*{{transition:none!important;scroll-behavior:auto}}}}
</style>
</head>
<body>
  <header class="top">
    <div class="top-in">
      <a class="logo" href="#top">sia<b>.</b>haus <span style="color:var(--text-faint)">라이선스</span></a>
      <nav>
        <a href="#how">작동 방식</a>
        <a href="#catalog">작품</a>
        <a href="#plans">플랜</a>
        <a href="#faq">FAQ</a>
      </nav>
    </div>
  </header>

  <main id="top">
    <section class="hero">
      <div class="wrap">
        <span class="eyebrow">{esc(hero['eyebrow'])}</span>
        <h1>{headline}</h1>
        <p class="definition">{definition_html}</p>
        <div class="hero-cta">
          <a class="btn btn-accent btn-lg" href="#catalog">작품 보기</a>
          <a class="btn btn-outline btn-lg" href="#contact">문의하기</a>
        </div>
      </div>
    </section>

    <section class="band" id="how">
      <div class="wrap">
        <span class="eyebrow">{esc(how['eyebrow'])}</span>
        <h2>{esc(how['title'])}</h2>
        <p class="lead">{esc(how['lead'])}</p>
        <div class="steps">
{steps_html}
        </div>
      </div>
    </section>

    <section id="catalog">
      <div class="wrap">
        <span class="eyebrow">{esc(cat['eyebrow'])}</span>
        <h2>{esc(cat['title'])}</h2>
        <p class="lead">{esc(cat['lead'])}</p>
        <div class="works">
{cards}
        </div>
        <p class="note">// {esc(cat['note'])}</p>
      </div>
    </section>

    <section class="band" id="plans">
      <div class="wrap">
        <span class="eyebrow">{esc(plans['eyebrow'])}</span>
        <h2>{esc(plans['title'])}</h2>
        <p class="lead">{esc(plans['lead'])}</p>
        <div class="plans-grid">
{plan_cards}
        </div>
      </div>
    </section>

    <section id="faq">
      <div class="wrap">
        <span class="eyebrow">{esc(faq['eyebrow'])}</span>
        <h2>{esc(faq['title'])}</h2>
        <div style="margin-top:36px">
{faq_items}
        </div>
      </div>
    </section>

    <section class="band" id="contact">
      <div class="wrap">
        <span class="eyebrow">{esc(contact['eyebrow'])}</span>
        <h2>{esc(contact['title'])}</h2>
        <p class="lead">{esc(contact['lead'])}</p>
{form}
      </div>
    </section>
  </main>

  <footer>
    <div class="wrap foot">
      <span>SIA.HAUS</span>
      <span>{esc(site['address']['locality'])} {esc(site['address']['street'])}, {esc(site['address']['postal'])}</span>
      <a href="mailto:{esc(site['email'])}">{esc(site['email'])}</a>
      <a href="https://www.sia.haus/">스튜디오</a>
      <a href="https://varis.kr/">VARIS 아카데미</a>
    </div>
  </footer>
</body>
</html>
'''


def build_llms(d: dict) -> str:
    site, hero, cat, plans = d["site"], d["hero"], d["catalog"], d["plans"]
    works = "\n".join(
        f"- **{w['title']}**{' (' + w['year'] + ')' if w.get('year') else ''} — {w['kind']}. {w['summary']}"
        for w in cat["works"]
    )
    plan_lines = "\n".join(
        f"- **{p['name']}** — {p['tagline']}. "
        + (f"월 {int(p['price_monthly']):,}원." if p.get("price_monthly") else "가격 문의.")
        for p in plans["items"]
    )
    return f"""# {site['name']}

> {hero['definition']}

## 작동 방식

{d['how']['lead']}

{chr(10).join(f"{s['n']}. **{s['t']}** — {s['d']}" for s in d['how']['steps'])}

## 구독 가능한 작품

{works}

## 플랜

{plan_lines}

계약 기간과 상영 조건은 공간 조건에 따라 조율합니다.

## 링크

- [{site['name']}]({site['url']}) — 카탈로그, 플랜, 문의
- [SIA.HAUS](https://www.sia.haus/) — 미디어아트 스튜디오 본체
- [VARIS](https://varis.kr/) — SIA.HAUS가 운영하는 미디어아트 교육 브랜드

## 연락

- 이메일: {site['email']}
- 주소: {site['address']['locality']} {site['address']['street']}, {site['address']['postal']}
"""


def build_sitemap(d: dict, today: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{d['site']['url']}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
"""


def main() -> int:
    check_only = "--check" in sys.argv
    d = json.loads(DATA.read_text(encoding="utf-8"))
    today = date.today().isoformat()

    out = {
        "index.html": build_html(d, today),
        "llms.txt": build_llms(d),
        "sitemap.xml": build_sitemap(d, today),
    }

    # 생성한 JSON-LD 가 파싱되는지 자체 검증
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>',
                         out["index.html"], re.S):
        json.loads(m.group(1))

    if not check_only:
        for name, text in out.items():
            (ROOT / name).write_text(text, encoding="utf-8")

    verb = "검사만" if check_only else "생성"
    print(f"  {verb}: " + " · ".join(f"{n} {len(t):,}B" for n, t in out.items()))
    print(f"  작품 {len(d['catalog']['works'])} · 플랜 {len(d['plans']['items'])} · FAQ {len(d['faq']['items'])}")
    if placeholders:
        print(f"\n  ⚠️  확정 필요 값 {len(placeholders)}개 — data/site.json 에서 채우세요")
        for p in placeholders:
            print(f"       · {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

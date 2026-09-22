#!/usr/bin/env python3
"""www.sia.haus 정적 사이트를 data/ 에서 생성합니다.

    python build.py            # 생성
    python build.py --check    # 파일을 쓰지 않고 검증만

설계 원칙은 license/ 와 같습니다.

- **빌드 시점에 정적 HTML 로 펼칩니다.** JSON 을 클라이언트에서 fetch 해 렌더링하면
  봇이 받는 원본 HTML 이 껍데기만 남습니다. 이 사이트의 목적이 생성형 엔진에
  인용되는 것이므로 그 방식은 쓸 수 없습니다. 출력물의 <script> 는 JSON-LD 뿐입니다.
- **읽는 사람에게 보이는 문자열은 전부 data/ 에 있습니다.** 이 파일에는 문구가 없습니다.
- **JSON-LD 는 화면에 있는 내용만 옮겨 적습니다.** 화면에 없는 내용을 스키마로만
  선언하면 구조화 데이터 위반이 되고, 생성형 엔진도 근거 없는 주장으로 취급합니다.
  FAQPage 를 넣을 수 있는 것은 같은 문답이 본문에도 렌더링되기 때문입니다.
"""
from __future__ import annotations

import html
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
# 파일 하나가 로케일 하나입니다. site.json 이 기준이고 나머지는 있으면 함께 빌드합니다.
DATA_FILES = [ROOT / "data" / "site.json"] + sorted(
    p for p in (ROOT / "data").glob("site.*.json") if p.name != "site.json"
)

warnings: list[str] = []


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def licensing_launched(d: dict) -> bool:
    """구독 라이선싱을 운영 중으로 서술해도 되는지.

    확정 전(null)이면 **안전한 쪽**, 즉 출시 전 문안을 씁니다. 없는 서비스를
    정의문에 넣으면 첫 문의부터 어긋나기 때문에, 모를 때 더 크게 주장하지 않습니다.
    """
    v = d.get("licensing", {}).get("launched")
    if v is None:
        warnings.append(
            "licensing.launched 가 확정되지 않아 '출시 전' 문안으로 생성했습니다 "
            "(IP 로 축적하고 있습니다 / 라이선싱 FAQ 제외). "
            "실제로 운영 중이면 data/site*.json 에서 true 로 바꾸세요."
        )
        return False
    return bool(v)


def faq_items(d: dict, launched: bool) -> list[dict]:
    """라이선싱 문답은 서비스가 실제로 있을 때만 싣습니다."""
    return [i for i in d["faq"]["items"] if not (i.get("requires_licensing") and not launched)]


def definition(d: dict, launched: bool) -> str:
    return d["hero"]["definition_launched" if launched else "definition_prelaunch"]


# ─────────────────────────── JSON-LD ───────────────────────────

def build_jsonld(d: dict, launched: bool) -> str:
    """Organization · WebSite · FAQPage.

    Organization 의 @id 는 varis.kr 의 parentOrganization 이 가리키는 값과
    **글자까지 같아야** 두 노드가 하나의 엔티티로 합쳐집니다
    (academy-varis/build_jsonld.py 의 PARENT_ORG_ID). 대표 도메인을 바꾸면 양쪽을
    함께 고칠 것 — 한쪽만 고치면 관계가 조용히 끊깁니다.
    """
    s = d["site"]
    org = {
        "@type": "Organization",
        "@id": s["org_id"],
        "name": s["name"],
        "alternateName": ["시아하우스", "sia.haus"],
        "url": s["url"],
        "description": definition(d, launched),
        "email": s["email"],
        "foundingLocation": {"@type": "Place", "name": s["founding_location"]},
        "address": {
            "@type": "PostalAddress",
            "streetAddress": s["address"]["street"],
            "addressLocality": s["address"]["locality"],
            "postalCode": s["address"]["postal_code"],
            "addressCountry": {"@type": "Country", "name": s["address"]["country"]},
        },
        "areaServed": {"@type": "Country", "name": s["area_served"]},
        "knowsAbout": [f["name"] for f in d["fields"]["items"]],
        "sameAs": s["same_as"],
        # varis.kr 이 parentOrganization 으로 이쪽을 가리키고, 여기서 되받아
        # 관계가 양방향이 됩니다. @id 만 적지 않고 이름·URL 을 함께 싣는 이유는
        # 크롤러와 LLM 이 페이지 하나만 읽고 다른 도메인의 @id 를 따라가지 않기 때문입니다.
        "subOrganization": {
            "@type": ["EducationalOrganization", "Organization"],
            "@id": s["sub_org_id"],
            "name": "VARIS",
            "url": "https://varis.kr/",
        },
    }

    website = {
        "@type": "WebSite",
        "@id": s["url"] + "#website",
        "url": s["url"],
        "name": s["name"],
        "inLanguage": s["lang"],
        "publisher": {"@id": s["org_id"]},
    }

    graph = [org, website]

    items = faq_items(d, launched)
    if items:
        graph.append({
            "@type": "FAQPage",
            "@id": s["url"] + "#faq",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": i["q"],
                    # 화면 표기는 기호 그대로 두고, 스키마에는 음성 답변에서
                    # 잘못 읽히는 기호(819㎡ · 1:1)를 풀어 쓴 판을 싣습니다.
                    "acceptedAnswer": {"@type": "Answer", "text": i.get("a_spoken", i["a"])},
                }
                for i in items
            ],
        })

    return json.dumps({"@context": "https://schema.org", "@graph": graph},
                      ensure_ascii=False, indent=2)


# ─────────────────────────── CSS ───────────────────────────
# media.work 영감 흑백 미니멀 디자인 시스템. 악센트 없음, 색은 미디어에 위임.
# Inter (weight 300) 로 Neue Haas Unica Pro 를 대체.
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
:root{
  --white:#FFFFFF; --off-white:#F5F5F5; --light-gray:#E0E0E0;
  --mid-gray:#999999; --dark-gray:#666666; --charcoal:#333333;
  --near-black:#020202; --black:#000000; --footer-bg:#222222;
  --footer-text:#F7F7F7; --footer-muted:#CCCCCC;

  --bg:var(--white); --surface:var(--off-white);
  --text-strong:var(--black); --text:var(--near-black); --text-muted:var(--charcoal);
  --text-subtle:var(--dark-gray); --text-faint:var(--mid-gray);
  --line:var(--light-gray); --line-faint:rgba(0,0,0,0.06);

  --font-display:'Inter',system-ui,-apple-system,BlinkMacSystemFont,
                 'Segoe UI','Apple SD Gothic Neo',sans-serif;
  --font-mono:ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace;
  --wrap:1440px;
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--text);font-family:var(--font-display);
  font-weight:300;line-height:1.6;letter-spacing:-0.01em;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
.wrap{max-width:var(--wrap);margin:0 auto;padding:0 clamp(20px,4vw,48px)}

.skip{position:absolute;left:-9999px}
.skip:focus{left:16px;top:16px;z-index:100;background:var(--black);
  color:var(--white);padding:10px 16px}

.eyebrow{font-family:var(--font-mono);font-size:11px;letter-spacing:0.2em;
  text-transform:uppercase;color:var(--text-faint);font-weight:500}

/* nav — media.work style: 60px fixed, white bg, featured client in logo */
header.site{position:fixed;top:0;left:0;right:0;z-index:20;
  background:rgba(255,255,255,0.92);backdrop-filter:blur(10px);
  border-bottom:1px solid var(--line-faint)}
.hdr{display:flex;align-items:center;gap:24px;height:60px}
.logo{font-weight:500;font-size:15px;letter-spacing:0.01em;color:var(--text-strong)}
.logo .featured{color:var(--text-faint);font-weight:300}
nav.main{margin-left:auto;display:flex;gap:28px;font-size:14px;
  font-weight:400;color:var(--text-faint)}
nav.main a:hover{color:var(--text-strong)}
nav.main a.mailto{color:var(--text-subtle)}
.lang{font-family:var(--font-mono);font-size:11px;letter-spacing:0.08em;
  color:var(--text-faint);border:1px solid var(--line);padding:4px 10px}
.lang:hover{color:var(--text-strong);border-color:var(--charcoal)}
@media(max-width:820px){nav.main{display:none}}

section{padding:clamp(48px,7vw,100px) 0}
section:first-of-type{padding-top:0}

/* hero — media.work: fullscreen text only, 3-column distributed copy */
.hero{min-height:100vh;display:flex;align-items:center;padding-top:60px}
.hero-inner{display:grid;grid-template-columns:1fr 1fr 1fr;gap:clamp(24px,4vw,60px);
  width:100%;align-items:end}
.hero-col{display:flex;flex-direction:column;justify-content:flex-end}
.hero-col p{font-size:clamp(14px,1.4vw,17px);font-weight:300;line-height:1.65;
  color:var(--text-muted)}
.hero-col .hero-label{font-family:var(--font-mono);font-size:11px;
  letter-spacing:0.15em;text-transform:uppercase;color:var(--text-faint);
  margin-top:8px;font-weight:500}
@media(max-width:820px){
  .hero-inner{grid-template-columns:1fr;gap:32px}
  .hero{min-height:auto;padding:clamp(120px,20vw,200px) 0 clamp(60px,10vw,100px)}
}

/* intro — media.work: 57px light weight large text */
.intro{padding:clamp(60px,9vw,140px) 0;max-width:68%}
.intro h1{font-size:clamp(28px,4.2vw,57px);font-weight:300;letter-spacing:-0.5px;
  line-height:1.07;color:var(--black)}
@media(max-width:820px){.intro{max-width:100%}}

/* section heads */
.sec-head{margin-bottom:clamp(32px,5vw,56px)}
h2{font-size:clamp(22px,3vw,38px);font-weight:400;letter-spacing:-0.03em;
  line-height:1.15;color:var(--text-strong);margin:12px 0 0}
.lead{margin-top:14px;font-size:clamp(14px,1.3vw,16px);font-weight:300;
  color:var(--text-muted);max-width:60ch}

/* pipeline */
.steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1px;
  background:var(--line)}
.step{padding:clamp(24px,3vw,36px);background:var(--bg)}
.step-n{font-family:var(--font-mono);font-size:11px;letter-spacing:0.1em;
  color:var(--text-faint);font-weight:500}
.step-name{margin-top:14px;font-size:17px;font-weight:500;color:var(--text-strong)}
.step-en{margin-top:4px;font-family:var(--font-mono);font-size:11px;
  letter-spacing:0.06em;color:var(--text-faint);font-weight:400}

/* fields */
.fields{border-top:1px solid var(--line)}
.field-row{display:grid;grid-template-columns:minmax(0,1fr) auto;
  column-gap:clamp(16px,3vw,40px);align-items:baseline;
  padding:clamp(20px,2.8vw,32px) 0;border-bottom:1px solid var(--line)}
.field-name{grid-column:1;grid-row:1;
  font-size:clamp(18px,2.4vw,28px);font-weight:400;letter-spacing:-0.02em;
  line-height:1.2;color:var(--text-strong)}
.field-en{grid-column:2;grid-row:1;justify-self:end;
  font-family:var(--font-mono);font-size:11px;letter-spacing:0.06em;
  color:var(--text-faint);font-weight:400}
.field-desc{grid-column:1;grid-row:2;margin-top:8px;
  font-size:clamp(13px,1.3vw,15px);font-weight:300;color:var(--text-subtle);max-width:60ch}
@media(max-width:640px){
  .field-row{grid-template-columns:1fr}
  .field-name,.field-en,.field-desc{grid-column:1;grid-row:auto;justify-self:start}
  .field-en{margin-top:4px}
}

/* work — media.work: 3-column masonry grid with hover overlay cards */
.work-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.work-card{position:relative;overflow:hidden;background:var(--surface)}
.work-card-media{width:100%;display:block;aspect-ratio:auto}
/* placeholder when no video asset */
.work-card-placeholder{width:100%;aspect-ratio:4/5;background:
  linear-gradient(135deg,#e8e8e8 0%,#d0d0d0 50%,#e8e8e8 100%)}
.work-card:nth-child(3n+2) .work-card-placeholder{aspect-ratio:16/9}
.work-card:nth-child(3n+3) .work-card-placeholder{aspect-ratio:1/1}
/* hover overlay — media.work: fade, top-left meta */
.work-card-overlay{position:absolute;inset:0;display:flex;flex-direction:column;
  justify-content:flex-start;padding:clamp(16px,2vw,24px);
  background:rgba(0,0,0,0.45);opacity:0;transition:opacity 0.3s ease}
.work-card:hover .work-card-overlay{opacity:1}
.work-card-title{font-size:clamp(15px,1.4vw,18px);font-weight:500;
  color:var(--white);line-height:1.35}
.work-card-type{font-family:var(--font-mono);font-size:11px;letter-spacing:0.08em;
  color:rgba(255,255,255,0.7);margin-top:6px;font-weight:400}
.work-note{margin-top:16px;font-size:12px;color:var(--text-faint);font-weight:400}
@media(max-width:820px){.work-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:520px){.work-grid{grid-template-columns:1fr}}

/* faq */
.faq-list{border-top:1px solid var(--line)}
.faq-item{padding:clamp(22px,3vw,32px) 0;border-bottom:1px solid var(--line)}
.faq-item h3{font-size:clamp(15px,1.6vw,18px);font-weight:500;
  color:var(--text-strong);letter-spacing:-0.01em}
.faq-item p{margin-top:12px;font-size:15px;font-weight:300;
  color:var(--text-subtle);max-width:70ch}

/* contact */
.contact-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
  gap:clamp(20px,3vw,40px);margin-top:8px}
.c-block dt{font-family:var(--font-mono);font-size:11px;letter-spacing:0.15em;
  text-transform:uppercase;color:var(--text-faint);font-weight:500}
.c-block dd{margin-top:10px;font-size:15px;font-weight:300;
  color:var(--text-muted);line-height:1.6}
.c-block a:hover{color:var(--text-strong)}
.c-mail{font-size:clamp(20px,3vw,36px);font-weight:300;color:var(--black);
  letter-spacing:-0.03em;line-height:1.2}
.link-row{display:block;padding:12px 0;border-bottom:1px solid var(--line)}
.link-row b{color:var(--text-strong);font-weight:500}
.link-row span{display:block;margin-top:2px;font-size:13px;
  color:var(--text-faint);font-weight:300}

/* footer — media.work: #222 dark, 7-col dense layout */
footer.site{background:var(--footer-bg);padding:clamp(36px,5vw,56px) 0;
  font-size:12px;color:var(--footer-muted);font-weight:300}
.foot-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:16px}
.foot-grid dt{font-size:11px;font-weight:500;color:var(--footer-text);
  margin-bottom:10px;letter-spacing:0.04em}
.foot-grid dd{line-height:1.8}
.foot-grid a{color:var(--footer-muted)}
.foot-grid a:hover{color:var(--footer-text)}
.foot-copy{margin-top:clamp(24px,3vw,40px);padding-top:16px;
  border-top:1px solid rgba(255,255,255,0.08);font-size:11px;
  color:rgba(255,255,255,0.4)}
@media(max-width:960px){.foot-grid{grid-template-columns:repeat(3,1fr)}}
@media(max-width:520px){.foot-grid{grid-template-columns:repeat(2,1fr)}}

@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
"""


# ─────────────────────────── HTML ───────────────────────────

def build_html(d: dict, locales: list, launched: bool) -> str:
    s = d["site"]
    t = d["strings"]
    items = faq_items(d, launched)

    # media.work nav: Projects / Studies / About / mailto
    nav = "".join(
        f'<a href="#{i}">{esc(t[k])}</a>'
        for i, k in [("work", "nav_work"), ("fields", "nav_fields"),
                     ("faq", "nav_faq"), ("contact", "nav_contact")]
    )
    nav += f'<a class="mailto" href="mailto:{esc(s["email"])}">{esc(s["email"])}</a>'

    lang_link = "".join(
        f'<a class="lang" href="/{o["path"]}" hreflang="{o["lang"]}">{esc(o["lang_label"])}</a>'
        for o in locales if o["locale"] != s["locale"]
    )

    alternates = "".join(
        f'\n<link rel="alternate" hreflang="{o["lang"]}" href="{esc(o["url"])}" />'
        for o in locales
    )
    if len(locales) > 1:
        default = next(o for o in locales if o["locale"] == "ko")
        alternates += f'\n<link rel="alternate" hreflang="x-default" href="{esc(default["url"])}" />'

    # Featured client for logo (first work item)
    featured = d["work"]["items"][0]["client"] if d["work"]["items"] else ""

    steps = "".join(
        f'<div class="step"><div class="step-n">{esc(x["n"])}</div>'
        f'<div class="step-name">{esc(x["name"])}</div>'
        f'<div class="step-en">{esc(x["en"])}</div></div>'
        for x in d["pipeline"]["steps"]
    )

    fields = "".join(
        f'<div class="field-row"><h3 class="field-name">{esc(f["name"])}</h3>'
        f'<span class="field-en">{esc(f["en"])}</span>'
        f'<p class="field-desc">{esc(f["desc"])}</p></div>'
        for f in d["fields"]["items"]
    )

    # media.work: masonry grid cards instead of row list
    def work_card(w: dict) -> str:
        url = (w.get("url") or "").strip()
        video_url = (w.get("video_url") or "").strip()
        if video_url:
            media = f'<video class="work-card-media" src="{esc(video_url)}" muted loop playsinline></video>'
        else:
            media = '<div class="work-card-placeholder"></div>'
        overlay = (f'<div class="work-card-overlay">'
                   f'<span class="work-card-title">{esc(w["client"])} — {esc(w["name"])}</span>'
                   f'<span class="work-card-type">Project</span>'
                   f'</div>')
        inner = f'{media}{overlay}'
        if url:
            return f'<a class="work-card" href="{esc(url)}" aria-label="{esc(w["client"] + " — " + w["name"] + " 프로젝트 상세 보기")}">{inner}</a>'
        return f'<div class="work-card">{inner}</div>'

    works = "".join(work_card(w) for w in d["work"]["items"])

    faqs = "".join(
        f'<div class="faq-item" id="faq-{esc(i["id"])}"><h3>{esc(i["q"])}</h3>'
        f'<p>{esc(i["a"])}</p></div>'
        for i in items
    )

    links = "".join(
        f'<a class="link-row" href="{esc(l["url"])}" target="_blank" rel="noopener">'
        f'<b>{esc(l["label"])} \u2197</b><span>{esc(l["desc"])}</span></a>'
        for l in d["links"]
    )

    addr = s["address"]
    mailto = f'mailto:{s["email"]}?subject={esc(t["mail_subject"])}'

    # Hero: 3-column distributed copy (media.work style)
    hero_texts = d["hero"].get("hero_columns", [
        {"text": definition(d, launched)[:80], "label": ""},
        {"text": d["work"]["items"][0]["name"] if d["work"]["items"] else "", "label": d["work"]["items"][0]["client"] if d["work"]["items"] else ""},
        {"text": d["work"]["items"][1]["name"] if len(d["work"]["items"]) > 1 else "", "label": d["work"]["items"][1]["client"] if len(d["work"]["items"]) > 1 else ""},
    ])

    hero_cols = ""
    for col in hero_texts:
        label = f'<span class="hero-label">{esc(col.get("label", ""))}</span>' if col.get("label") else ""
        hero_cols += f'<div class="hero-col"><p>{esc(col["text"])}</p>{label}</div>'

    # Footer: media.work 7-column dense layout
    social_links = "".join(f'<dd><a href="{esc(u)}" target="_blank" rel="noopener">{esc(u.split("/")[-2] if u.endswith("/") else u.split("/")[-1])}</a></dd>' for u in s.get("same_as", []))

    return f"""<!DOCTYPE html>
<html lang="{s["lang"]}">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<link rel="icon" href="/favicon.svg" type="image/svg+xml" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<title>{esc(d["meta"]["title"])}</title>
<meta name="description" content="{esc(d["meta"]["description"])}" />
<link rel="canonical" href="{esc(s["url"])}" />{alternates}
<meta property="og:type" content="website" />
<meta property="og:site_name" content="{esc(s["name"])}" />
<meta property="og:url" content="{esc(s["url"])}" />
<meta property="og:title" content="{esc(d["meta"]["title"])}" />
<meta property="og:description" content="{esc(d["meta"]["description"])}" />
<meta property="og:locale" content="{esc(s["locale"])}" />
<meta property="og:image" content="{esc(s["url"] + "og-default.svg")}" />
<meta property="og:image:alt" content="{esc(d["meta"]["title"])}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:image" content="{esc(s["url"] + "og-default.svg")}" />
<style>{CSS}</style>
<script type="application/ld+json">
{build_jsonld(d, launched)}
</script>
</head>
<body>
<a class="skip" href="#main">{esc(t["skip"])}</a>

<header class="site">
  <div class="wrap hdr">
    <a class="logo" href="/">SIA.HAUS <span class="featured">&gt; {esc(featured)}</span></a>
    <nav class="main">{nav}</nav>
    {lang_link}
  </div>
</header>

<main id="main">
  <section class="hero">
    <div class="wrap">
      <div class="hero-inner">
        {hero_cols}
      </div>
    </div>
  </section>

  <section class="intro">
    <div class="wrap">
      <h1>{esc(definition(d, launched))}</h1>
    </div>
  </section>

  <section id="structure">
    <div class="wrap">
      <div class="sec-head">
        <p class="eyebrow">{esc(d["pipeline"]["eyebrow"])}</p>
        <h2>{esc(d["pipeline"]["title"])}</h2>
        <p class="lead">{esc(d["pipeline"]["lead"])}</p>
      </div>
      <div class="steps">{steps}</div>
    </div>
  </section>

  <section id="fields">
    <div class="wrap">
      <div class="sec-head">
        <p class="eyebrow">{esc(d["fields"]["eyebrow"])}</p>
        <h2>{esc(d["fields"]["title"])}</h2>
      </div>
      <div class="fields">{fields}</div>
    </div>
  </section>

  <section id="work">
    <div class="wrap">
      <div class="sec-head">
        <p class="eyebrow">{esc(d["work"]["eyebrow"])}</p>
        <h2>{esc(d["work"]["title"])}</h2>
        <p class="lead">{esc(d["work"]["lead"])}</p>
      </div>
      <div class="work-grid">{works}</div>
      <p class="work-note">{esc(d["work"]["note"])}</p>
    </div>
  </section>

  <section id="faq">
    <div class="wrap">
      <div class="sec-head">
        <p class="eyebrow">{esc(d["faq"]["eyebrow"])}</p>
        <h2>{esc(d["faq"]["title"])}</h2>
      </div>
      <div class="faq-list">{faqs}</div>
    </div>
  </section>

  <section id="contact">
    <div class="wrap">
      <div class="sec-head">
        <p class="eyebrow">{esc(d["contact"]["eyebrow"])}</p>
        <h2>{esc(d["contact"]["title"])}</h2>
        <p class="lead">{esc(d["contact"]["lead"])}</p>
      </div>
      <dl class="contact-grid">
        <div class="c-block">
          <dt>{esc(t["email"])}</dt>
          <dd><a class="c-mail" href="{mailto}">{esc(s["email"])}</a></dd>
        </div>
        <div class="c-block">
          <dt>{esc(t["address"])}</dt>
          <dd>{esc(addr["locality"])} {esc(addr["street"])}<br />{esc(addr["postal_code"])}</dd>
        </div>
        <div class="c-block">
          <dt>{esc(t["links"])}</dt>
          <dd>{links}</dd>
        </div>
      </dl>
    </div>
  </section>
</main>

<footer class="site">
  <div class="wrap">
    <dl class="foot-grid">
      <div>
        <dt>{esc(addr["locality"])}</dt>
        <dd>{esc(addr["street"])}<br />{esc(addr["postal_code"])}</dd>
      </div>
      <div>
        <dt>Information</dt>
        <dd><a href="/llms.txt">llms.txt</a></dd>
      </div>
      <div>
        <dt>Studio</dt>
        <dd><a href="#structure">{esc(t["nav_structure"])}</a></dd>
        <dd><a href="#fields">{esc(t["nav_fields"])}</a></dd>
      </div>
      <div>
        <dt>Social</dt>
        {social_links}
      </div>
      <div>
        <dt>Contact</dt>
        <dd><a href="{mailto}">{esc(s["email"])}</a></dd>
      </div>
      <div>
        <dt>Copyright</dt>
        <dd>All rights reserved<br />\u00a9 {date.today().year} {esc(s["name"])}</dd>
      </div>
    </dl>
    <div class="foot-copy">{esc(t["footer_note"])}</div>
  </div>
</footer>
</body>
</html>
"""



# ─────────────────────── project detail pages ───────────────────────

def build_project_jsonld(d: dict, w: dict) -> str:
    """프로젝트 상세 페이지의 CreativeWork + BreadcrumbList.

    creator 가 Organization 의 @id 를 가리켜 기존 엔티티 그래프에 붙습니다.
    **화면에 있는 값만 옮겨 적습니다** — description 은 본문이 실제로 렌더링될
    때만 넣습니다. 화면에 없는 내용을 스키마로만 선언하면 구조화 데이터 위반이고,
    생성형 엔진도 근거 없는 주장으로 취급해 인용하지 않습니다.
    """
    s = d["site"]
    url = f'{s["url"]}projects/{w["slug"]}'
    work = {
        "@type": "CreativeWork",
        "@id": url + "#work",
        "url": url,
        "name": f'{w["client"]} \u2014 {w["name"]}',
        "headline": w["name"],
        "inLanguage": s["lang"],
        "creator": {"@id": s["org_id"]},
        "isPartOf": {"@id": s["url"] + "#website"},
    }
    if w.get("description"):
        work["description"] = w["description"]
    if w.get("year"):
        work["dateCreated"] = w["year"]
    if w.get("context"):
        work["about"] = w["context"]

    crumbs = {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": s["name"], "item": s["url"]},
            {"@type": "ListItem", "position": 2, "name": w["client"], "item": url},
        ],
    }
    return json.dumps({"@context": "https://schema.org", "@graph": [work, crumbs]},
                      ensure_ascii=False, indent=2)


def build_project_html(d: dict, w: dict, locales: list, launched: bool) -> str:
    """프로젝트 상세 페이지 — media.work 톤."""
    s = d["site"]
    t = d["strings"]
    slug = w["slug"]
    url = f'{s["url"]}projects/{slug}'
    title = f'{w["client"]} \u2014 {w["name"]} | {s["name"]}'
    if w.get("description"):
        desc = w["description"].split(". ")[0].strip().rstrip(".") + "."
        if len(desc) > 300:
            desc = desc[:297].rstrip() + "\u2026"
    else:
        desc = f'{w["client"]} \u00b7 {w["name"]}'
    if w["context"]:
        desc += f' \u00b7 {w["context"]}'

    featured = w["client"]
    nav = "".join(
        f'<a href="/#{i}">{esc(t[k])}</a>'
        for i, k in [("work", "nav_work"), ("fields", "nav_fields"),
                     ("faq", "nav_faq"), ("contact", "nav_contact")]
    )
    nav += f'<a class="mailto" href="mailto:{esc(s["email"])}">{esc(s["email"])}</a>'

    lang_link = "".join(
        f'<a class="lang" href="/{o["path"]}" hreflang="{o["lang"]}">{esc(o["lang_label"])}</a>'
        for o in locales if o["locale"] != s["locale"]
    )

    year_html = f'<span class="proj-year">{esc(w["year"])}</span>' if w["year"] else ""
    ctx_html = f'<span class="proj-ctx">{esc(w["context"])}</span>' if w["context"] else ""
    desc_html = f'<p class="proj-desc">{esc(w["description"])}</p>' if w.get("description") else ""

    items = [x for x in d["work"]["items"] if x.get("slug")]
    idx = next((i for i, x in enumerate(items) if x["slug"] == slug), 0)
    prev_item = items[idx - 1] if idx > 0 else None
    next_item = items[idx + 1] if idx < len(items) - 1 else None
    prev_link = (
        f'<a class="proj-nav-link" href="/projects/{prev_item["slug"]}/">'
        f'\u2190 {esc(prev_item["client"])}</a>'
    ) if prev_item else '<span></span>'
    next_link = (
        f'<a class="proj-nav-link" href="/projects/{next_item["slug"]}/">'
        f'{esc(next_item["client"])} \u2192</a>'
    ) if next_item else '<span></span>'

    return f"""<!DOCTYPE html>
<html lang="{s["lang"]}">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<link rel="icon" href="/favicon.svg" type="image/svg+xml" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}" />
<link rel="canonical" href="{esc(url)}" />
<meta property="og:type" content="article" />
<meta property="og:site_name" content="{esc(s["name"])}" />
<meta property="og:url" content="{esc(url)}" />
<meta property="og:title" content="{esc(title)}" />
<meta property="og:description" content="{esc(desc)}" />
<meta property="og:locale" content="{esc(s["locale"])}" />
<meta property="og:image" content="{esc(s["url"] + "og-default.svg")}" />
<meta property="og:image:alt" content="{esc(title)}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:image" content="{esc(s["url"] + "og-default.svg")}" />
<script type="application/ld+json">
{build_project_jsonld(d, w)}
</script>
<style>{CSS}
.proj-hero{{padding:clamp(100px,15vw,180px) 0 clamp(48px,7vw,80px)}}
.proj-client{{font-size:clamp(32px,5.5vw,68px);font-weight:300;letter-spacing:-0.04em;
  line-height:1.1;color:var(--text-strong);margin:16px 0 0}}
.proj-name{{margin-top:12px;font-size:clamp(16px,2vw,24px);font-weight:300;
  color:var(--text-muted)}}
.proj-ctx{{font-family:var(--font-mono);font-size:12px;letter-spacing:0.06em;
  color:var(--text-faint);margin-top:8px;display:block;font-weight:400}}
.proj-year{{font-family:var(--font-mono);font-size:13px;letter-spacing:0.06em;
  color:var(--text-faint);display:block;margin-top:14px;font-weight:400}}
.proj-desc{{margin-top:clamp(28px,4vw,44px);font-size:clamp(15px,1.6vw,19px);
  line-height:1.75;font-weight:300;color:var(--text-muted);max-width:60ch}}
.proj-nav{{display:flex;justify-content:space-between;align-items:center;
  padding:clamp(28px,4vw,48px) 0;border-top:1px solid var(--line);
  margin-top:clamp(48px,6vw,80px)}}
.proj-nav-link{{font-size:14px;font-weight:400;color:var(--text-faint)}}
.proj-nav-link:hover{{color:var(--text-strong)}}
.back-link{{display:inline-block;margin-top:clamp(28px,4vw,40px);
  font-size:13px;font-weight:400;color:var(--text-faint)}}
.back-link:hover{{color:var(--text-strong)}}
</style>
</head>
<body>
<a class="skip" href="#main">{esc(t["skip"])}</a>

<header class="site">
  <div class="wrap hdr">
    <a class="logo" href="/">SIA.HAUS <span class="featured">&gt; {esc(featured)}</span></a>
    <nav class="main">{nav}</nav>
    {lang_link}
  </div>
</header>

<main id="main">
  <section class="proj-hero">
    <div class="wrap">
      <p class="eyebrow">PROJECT</p>
      <h1 class="proj-client">{esc(w["client"])}</h1>
      <p class="proj-name">{esc(w["name"])}</p>
      {ctx_html}
      {year_html}
      {desc_html}
      <a class="back-link" href="/#work">\u2190 {esc(t["nav_work"])}</a>
    </div>
  </section>

  <div class="wrap">
    <nav class="proj-nav">
      {prev_link}
      {next_link}
    </nav>
  </div>
</main>

<footer class="site">
  <div class="wrap">
    <div class="foot-copy">\u00a9 {date.today().year} {esc(s["name"])}</div>
  </div>
</footer>
</body>
</html>
"""



# ─────────────────────────── llms.txt · sitemap ───────────────────────────

def build_llms(d: dict, launched: bool) -> str:
    s = d["site"]
    lines = [f'# {s["name"]}', "", f'> {definition(d, launched)}', ""]

    lines += [f'## {d["pipeline"]["title"]}', "", d["pipeline"]["lead"], ""]

    lines += [f'## {d["fields"]["title"]}', ""]
    lines += [f'- **{f["name"]}** ({f["en"]}) — {f["desc"]}' for f in d["fields"]["items"]]
    lines.append("")

    lines += [f'## {d["work"]["title"]}', "", d["work"]["lead"], ""]
    for w in d["work"]["items"]:
        bits = [b for b in (w["name"], w["context"], w["year"]) if b]
        lines.append(f'- {w["client"]} — ' + " · ".join(bits))
    lines.append("")

    items = faq_items(d, launched)
    if items:
        lines += [f'## {d["faq"]["title"]}', ""]
        for i in items:
            lines += [f'### {i["q"]}', "", i.get("a_spoken", i["a"]), ""]

    lines += ["## 링크", ""]
    lines += [f'- [{l["label"]}]({l["url"]}) — {l["desc"]}' for l in d["links"]]
    lines.append("")

    a = s["address"]
    lines += ["## 연락", "",
              f'- 이메일: {s["email"]}',
              f'- 주소: {a["locality"]} {a["street"]}, {a["postal_code"]}', ""]
    return "\n".join(lines)


def build_sitemap(locales: list, today: str, project_urls: list[str] | None = None) -> str:
    urls = []
    for o in locales:
        alts = "".join(
            f'\n    <xhtml:link rel="alternate" hreflang="{x["lang"]}" href="{x["url"]}" />'
            for x in locales
        )
        urls.append(
            f'  <url>\n    <loc>{o["url"]}</loc>\n'
            f'    <lastmod>{today}</lastmod>{alts}\n  </url>'
        )
    for pu in (project_urls or []):
        urls.append(
            f'  <url>\n    <loc>{pu}</loc>\n'
            f'    <lastmod>{today}</lastmod>\n  </url>'
        )
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
            '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + "\n".join(urls) + "\n</urlset>\n")


# ─────────────────────────── main ───────────────────────────

def main() -> int:
    check_only = "--check" in sys.argv
    today = date.today().isoformat()

    docs = [json.loads(f.read_text(encoding="utf-8")) for f in DATA_FILES]
    locales = [d["site"] for d in docs]

    out: dict[str, str] = {}
    for d in docs:
        launched = licensing_launched(d)
        path = d["site"]["path"]
        doc = build_html(d, locales, launched)

        # 생성한 JSON-LD 가 실제로 파싱되는지 자체 검증. 여기서 죽으면 배포 전에 죽습니다.
        for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', doc, re.S):
            json.loads(m.group(1))
        # 실행 스크립트가 섞여 들어가지 않았는지 확인 — 이 사이트의 전제입니다.
        for m in re.finditer(r'<script(?![^>]*type="application/ld\+json")[^>]*>', doc):
            raise SystemExit(f"실행 스크립트가 들어갔습니다: {m.group(0)}")

        out[path + "index.html"] = doc
        out[path + "llms.txt"] = build_llms(d, launched)

        # 프로젝트 상세 페이지 생성
        for w in d["work"]["items"]:
            if not w.get("slug"):
                continue
            proj_doc = build_project_html(d, w, locales, launched)
            # JSON-LD 검증 (도입하면)
            for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', proj_doc, re.S):
                json.loads(m.group(1))
            for m in re.finditer(r'<script(?![^>]*type="application/ld\+json")[^>]*>', proj_doc):
                raise SystemExit(f"실행 스크립트가 들어갔습니다: {m.group(0)}")
            out[path + f'projects/{w["slug"]}/index.html'] = proj_doc

    # sitemap 에 프로젝트 URL 포함
    project_urls = []
    for d2 in docs:
        for w2 in d2["work"]["items"]:
            if w2.get("slug"):
                project_urls.append(d2["site"]["url"] + "projects/" + w2["slug"] )
    out["sitemap.xml"] = build_sitemap(locales, today, project_urls)

    if not check_only:
        for name, text in out.items():
            target = ROOT / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")

    print(f'  {"검사만" if check_only else "생성"}: '
          + " · ".join(f"{n} {len(t):,}B" for n, t in out.items()))
    for d, o in zip(docs, locales):
        launched = bool(d.get("licensing", {}).get("launched"))
        print(f'  [{o["locale"]}] {o["url"]} — 분야 {len(d["fields"]["items"])}'
              f' · 실적 {len(d["work"]["items"])} · FAQ {len(faq_items(d, launched))}')
    for w in dict.fromkeys(warnings):
        print(f"\n  ⚠️  {w}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

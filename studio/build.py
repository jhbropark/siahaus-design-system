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
# 디자인 시스템(project/tokens)의 ink · paper · champagne 스케일을 그대로 씁니다.
# license.sia.haus 와 같은 토큰이라 두 사이트가 한 브랜드로 읽힙니다.
CSS = """
:root{
  --ink-900:#08090A; --ink-850:#0C0D0F; --ink-800:#121316; --ink-700:#181A1E;
  --ink-600:#202329; --ink-500:#2A2E35;
  --paper-000:#FAFAF7; --paper-100:#F2F2EE; --paper-200:#D8D8D2;
  --paper-300:#A7A8A3; --paper-400:#6E7075;
  --champagne-300:#E2CFA0; --champagne-400:#C9A86A; --champagne-600:#8A6F3A;

  --bg:var(--ink-850); --surface:var(--ink-700); --surface-section:var(--ink-800);
  --text-strong:var(--paper-000); --text:var(--paper-100); --text-muted:var(--paper-200);
  --text-subtle:var(--paper-300); --text-faint:var(--paper-400);
  --accent:var(--champagne-400); --accent-soft:var(--champagne-300);
  --on-accent:var(--ink-900);
  --line:var(--ink-500); --line-faint:rgba(242,242,238,0.08);

  --font-display:'Pretendard Variable',Pretendard,-apple-system,BlinkMacSystemFont,
                 'Apple SD Gothic Neo','Malgun Gothic',system-ui,sans-serif;
  --font-mono:ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace;
  --wrap:1120px;
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--text);font-family:var(--font-display);
  line-height:1.7;letter-spacing:-0.01em;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
.wrap{max-width:var(--wrap);margin:0 auto;padding:0 clamp(20px,5vw,40px)}

.skip{position:absolute;left:-9999px}
.skip:focus{left:16px;top:16px;z-index:100;background:var(--accent);
  color:var(--on-accent);padding:10px 16px}

.eyebrow{font-family:var(--font-mono);font-size:12px;letter-spacing:0.28em;
  text-transform:uppercase;color:var(--accent);font-weight:600}

header.site{position:sticky;top:0;z-index:20;background:rgba(12,13,15,0.88);
  backdrop-filter:blur(12px);border-bottom:1px solid var(--line-faint)}
.hdr{display:flex;align-items:center;gap:28px;height:68px}
.logo{font-weight:800;font-size:17px;letter-spacing:0.02em;color:var(--text-strong)}
.logo span{color:var(--accent)}
nav.main{margin-left:auto;display:flex;gap:26px;font-size:14px;color:var(--text-subtle)}
nav.main a:hover{color:var(--text-strong)}
.lang{font-family:var(--font-mono);font-size:12px;letter-spacing:0.1em;
  color:var(--text-faint);border:1px solid var(--line);padding:5px 10px}
.lang:hover{color:var(--accent);border-color:var(--accent-deep,var(--champagne-600))}
@media(max-width:820px){nav.main{display:none}}

section{padding:clamp(64px,9vw,120px) 0;border-top:1px solid var(--line-faint)}
section:first-of-type{border-top:0}
.sec-head{max-width:760px;margin-bottom:clamp(32px,5vw,56px)}
h2{font-size:clamp(26px,3.6vw,40px);font-weight:800;letter-spacing:-0.035em;
  color:var(--text-strong);margin:14px 0 0}
.lead{margin-top:18px;font-size:clamp(15px,1.5vw,17px);color:var(--text-muted);max-width:70ch}

/* hero */
.hero{padding:clamp(80px,13vw,180px) 0 clamp(56px,8vw,96px)}
.hero h1{font-size:clamp(34px,6.4vw,76px);font-weight:800;letter-spacing:-0.045em;
  line-height:1.12;color:var(--text-strong);margin:20px 0 0;max-width:16ch}
.definition{margin-top:clamp(28px,4vw,44px);font-size:clamp(16px,1.75vw,20px);
  line-height:1.75;color:var(--text-muted);max-width:60ch;
  border-left:2px solid var(--accent);padding-left:clamp(18px,2.4vw,28px)}
.hero-cta{display:flex;flex-wrap:wrap;gap:12px;margin-top:clamp(32px,4.5vw,48px)}
.btn{display:inline-block;padding:13px 26px;font-size:14px;font-weight:700;
  border:1px solid transparent}
.btn-solid{background:var(--accent);color:var(--on-accent)}
.btn-solid:hover{background:var(--accent-soft)}
.btn-ghost{border-color:var(--line);color:var(--text-muted)}
.btn-ghost:hover{border-color:var(--accent);color:var(--accent)}

/* pipeline · fields
   칸 수가 열 수로 나눠떨어지지 않으면 마지막 줄에 빈 칸이 남습니다. 칸 사이를
   gap 으로 벌려 컨테이너 배경을 선처럼 보이게 하면 그 빈 칸이 통째로 선 색으로
   밝게 뜹니다. 그래서 gap 대신 칸에 테두리를 그려 빈 칸이 배경과 구별되지 않게 합니다. */
.steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));
  background:var(--surface-section);border:1px solid var(--line-faint)}
.step{padding:clamp(22px,3vw,32px);
  border-right:1px solid var(--line-faint);border-bottom:1px solid var(--line-faint)}
.step-n{font-family:var(--font-mono);font-size:12px;letter-spacing:0.1em;color:var(--accent)}
.step-name{margin-top:12px;font-size:18px;font-weight:700;color:var(--text-strong)}
.step-en{margin-top:4px;font-family:var(--font-mono);font-size:11px;
  letter-spacing:0.08em;color:var(--text-faint)}

.fields{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));
  background:var(--surface-section);border:1px solid var(--line-faint)}
.field{padding:clamp(24px,3vw,32px);
  border-right:1px solid var(--line-faint);border-bottom:1px solid var(--line-faint)}
.field h3{font-size:18px;font-weight:700;color:var(--text-strong);letter-spacing:-0.02em}
.field .en{margin-top:5px;font-family:var(--font-mono);font-size:11px;
  letter-spacing:0.08em;color:var(--text-faint)}
.field p{margin-top:14px;font-size:14.5px;color:var(--text-subtle);line-height:1.65}

/* work — 프로젝트 행
   Esme(Webflow 템플릿)의 행 구조를 가져왔습니다. 핵심은 세 가지입니다.

   1. 중간 크기를 두지 않습니다. 클라이언트명은 디스플레이 크기(최대 44px),
      나머지 정보는 전부 14~16px. 그 사이 단계가 없어야 한 줄이 한 작업으로 읽힙니다.
   2. 연도를 같은 베이스라인의 오른쪽 끝에 붙입니다. 가운데로 모으지 않고
      양 끝으로 밀어 그 사이 여백이 구분선 역할을 합니다.
   3. 행 전체가 링크입니다. 원본은 행마다 "View Project" 라는 같은 문구를 쓰는데,
      그러면 스크린리더에 이름이 똑같은 링크가 13개 생깁니다. 행을 통째로 감싸면
      클라이언트명과 작업명이 링크의 접근성 이름에 들어갑니다.

   원본은 전면 사진 위에 텍스트를 얹지만 이 저장소에는 작업 이미지가 없어
   타이포그래피만으로 구성했습니다. */
.work-list{border-top:1px solid var(--line-faint)}
.work-row{display:grid;grid-template-columns:1fr auto;
  column-gap:clamp(16px,3vw,40px);align-items:baseline;
  padding:clamp(22px,3vw,34px) 2px;border-bottom:1px solid var(--line-faint)}
/* h2(최대 40px)보다 작게 유지합니다. 행 하나가 섹션 제목보다 커지면 목록이
   제목을 눌러 위계가 뒤집힙니다 — 1280px 에서 44px 로 뒀다가 실제로 그랬습니다. */
.work-client{grid-column:1;grid-row:1;
  font-size:clamp(20px,2.9vw,34px);font-weight:800;letter-spacing:-0.04em;
  line-height:1.15;color:var(--text-strong)}
.work-meta{grid-column:1;grid-row:2;margin-top:clamp(8px,1vw,12px);
  font-size:clamp(14px,1.5vw,16px);color:var(--text-muted)}
.work-ctx{color:var(--text-faint)}
.work-ctx::before{content:" · "}
.work-year{grid-column:2;grid-row:1;justify-self:end;
  font-family:var(--font-mono);font-size:12.5px;letter-spacing:0.06em;color:var(--accent)}
.work-go{grid-column:2;grid-row:2;justify-self:end;margin-top:clamp(8px,1vw,12px);
  font-size:13px;color:var(--text-faint);white-space:nowrap}
.work-go::after{content:" →"}
a.work-row{transition:none}
a.work-row:hover .work-client,a.work-row:focus-visible .work-client{color:var(--accent)}
a.work-row:hover .work-go,a.work-row:focus-visible .work-go{color:var(--accent)}
a.work-row:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
.work-note{margin-top:18px;font-size:13px;color:var(--text-faint)}
@media(max-width:640px){
  .work-row{grid-template-columns:1fr}
  .work-client,.work-meta,.work-year,.work-go{
    grid-column:1;grid-row:auto;justify-self:start}
  .work-year{margin-top:8px}
}

/* faq */
.faq-list{display:grid;background:var(--surface-section);border:1px solid var(--line-faint)}
.faq-item{padding:clamp(24px,3.2vw,36px);border-bottom:1px solid var(--line-faint)}
.faq-item h3{font-size:clamp(16px,1.8vw,19px);font-weight:700;color:var(--text-strong);
  letter-spacing:-0.02em}
.faq-item p{margin-top:14px;font-size:15px;color:var(--text-subtle);max-width:75ch}

/* contact */
.contact-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));
  gap:clamp(24px,4vw,48px);margin-top:8px}
.c-block dt{font-family:var(--font-mono);font-size:11px;letter-spacing:0.18em;
  text-transform:uppercase;color:var(--text-faint)}
.c-block dd{margin-top:10px;font-size:15.5px;color:var(--text-muted);line-height:1.6}
.c-block a:hover{color:var(--accent)}
.c-mail{font-size:clamp(20px,2.8vw,30px);font-weight:700;color:var(--accent);
  letter-spacing:-0.02em}
.link-row{display:block;padding:14px 0;border-bottom:1px solid var(--line-faint)}
.link-row b{color:var(--text-strong);font-weight:600}
.link-row span{display:block;margin-top:3px;font-size:13.5px;color:var(--text-faint)}

footer.site{border-top:1px solid var(--line-faint);padding:36px 0 56px;
  font-size:13px;color:var(--text-faint)}
.foot{display:flex;flex-wrap:wrap;gap:12px 26px;align-items:center}
.foot .sep{margin-left:auto}

@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
"""


# ─────────────────────────── HTML ───────────────────────────

def build_html(d: dict, locales: list, launched: bool) -> str:
    s = d["site"]
    t = d["strings"]
    items = faq_items(d, launched)

    nav = "".join(
        f'<a href="#{i}">{esc(t[k])}</a>'
        for i, k in [("structure", "nav_structure"), ("fields", "nav_fields"),
                     ("work", "nav_work"), ("faq", "nav_faq"), ("contact", "nav_contact")]
    )

    # 다른 로케일로 가는 전환 링크. 로케일이 하나뿐이면 아무것도 넣지 않습니다.
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

    steps = "".join(
        f'<div class="step"><div class="step-n">{esc(x["n"])}</div>'
        f'<div class="step-name">{esc(x["name"])}</div>'
        f'<div class="step-en">{esc(x["en"])}</div></div>'
        for x in d["pipeline"]["steps"]
    )

    fields = "".join(
        f'<div class="field"><h3>{esc(f["name"])}</h3>'
        f'<div class="en">{esc(f["en"])}</div><p>{esc(f["desc"])}</p></div>'
        for f in d["fields"]["items"]
    )

    def work_row(w: dict) -> str:
        # url 은 선택입니다. 프로젝트 상세 페이지를 만들거나 외부 링크(Behance 등)를
        # 걸기로 정하면 그때 data/site.json 의 항목에 넣으면 됩니다. 없으면 행은
        # 링크가 아닌 그냥 행으로 렌더됩니다 — 갈 곳 없는 링크를 만들지 않습니다.
        url = (w.get("url") or "").strip()
        ctx = f'<span class="work-ctx">{esc(w["context"])}</span>' if w["context"] else ""
        year = f'<span class="work-year">{esc(w["year"])}</span>' if w["year"] else ""
        go = f'<span class="work-go">{esc(t["work_go"])}</span>' if url else ""
        inner = (f'<span class="work-client">{esc(w["client"])}</span>'
                 f'<span class="work-meta">{esc(w["name"])}{ctx}</span>'
                 f'{year}{go}')
        if url:
            return f'<a class="work-row" href="{esc(url)}">{inner}</a>'
        return f'<div class="work-row">{inner}</div>'

    works = "".join(work_row(w) for w in d["work"]["items"])

    faqs = "".join(
        f'<div class="faq-item" id="faq-{esc(i["id"])}"><h3>{esc(i["q"])}</h3>'
        f'<p>{esc(i["a"])}</p></div>'
        for i in items
    )

    links = "".join(
        f'<a class="link-row" href="{esc(l["url"])}" target="_blank" rel="noopener">'
        f'<b>{esc(l["label"])} ↗</b><span>{esc(l["desc"])}</span></a>'
        for l in d["links"]
    )

    addr = s["address"]
    mailto = f'mailto:{s["email"]}?subject={esc(t["mail_subject"])}'

    return f"""<!DOCTYPE html>
<html lang="{s["lang"]}">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{esc(d["meta"]["title"])}</title>
<meta name="description" content="{esc(d["meta"]["description"])}" />
<link rel="canonical" href="{esc(s["url"])}" />{alternates}
<meta property="og:type" content="website" />
<meta property="og:site_name" content="{esc(s["name"])}" />
<meta property="og:url" content="{esc(s["url"])}" />
<meta property="og:title" content="{esc(d["meta"]["title"])}" />
<meta property="og:description" content="{esc(d["meta"]["description"])}" />
<meta property="og:locale" content="{esc(s["locale"])}" />
<meta name="twitter:card" content="summary_large_image" />
<link rel="preconnect" href="https://cdn.jsdelivr.net" />
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.css" />
<style>{CSS}</style>
<script type="application/ld+json">
{build_jsonld(d, launched)}
</script>
</head>
<body>
<a class="skip" href="#main">{esc(t["skip"])}</a>

<header class="site">
  <div class="wrap hdr">
    <a class="logo" href="/">SIA<span>.</span>HAUS</a>
    <nav class="main">{nav}</nav>
    {lang_link}
  </div>
</header>

<main id="main">
  <section class="hero">
    <div class="wrap">
      <p class="eyebrow">{esc(d["hero"]["eyebrow"])}</p>
      <h1>{esc(d["hero"]["headline"])}</h1>
      <p class="definition">{esc(definition(d, launched))}</p>
      <div class="hero-cta">
        <a class="btn btn-solid" href="#contact">{esc(t["cta_contact"])}</a>
        <a class="btn btn-ghost" href="#work">{esc(t["cta_work"])}</a>
      </div>
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
      <div class="work-list">{works}</div>
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
  <div class="wrap foot">
    <span>© {date.today().year} {esc(t["footer_note"])}</span>
    <span class="sep"><a href="{mailto}">{esc(s["email"])}</a></span>
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


def build_sitemap(locales: list, today: str) -> str:
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
    out["sitemap.xml"] = build_sitemap(locales, today)

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

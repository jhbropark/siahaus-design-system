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
import os
import re
import struct
import sys
from datetime import date
from pathlib import Path


# Keep build validation readable on Windows machines using a legacy code page.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).parent
# Use the deployment commit when available so immutable asset URLs always change
# with a deploy, even when the build machine's timezone differs from the editor.
BUILD_VERSION = (os.getenv("VERCEL_GIT_COMMIT_SHA") or date.today().isoformat())[:12]
ANALYTICS_TAGS = ('<script defer src="/_vercel/insights/script.js"></script>\n'
                  f'<script defer src="/site-analytics.js?v={BUILD_VERSION}"></script>')
# 파일 하나가 로케일 하나입니다. site.json 이 기준이고 나머지는 있으면 함께 빌드합니다.
DATA_FILES = [ROOT / "data" / "site.json"] + sorted(
    p for p in (ROOT / "data").glob("site.*.json") if p.name != "site.json"
)

warnings: list[str] = []


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def asset_url(src: str) -> str:
    """Prefer generated WebP assets and version local URLs for immutable caching."""
    src = str(src or "")
    if src.startswith("/assets/") and "?" not in src:
        source_path = ROOT / src.lstrip("/")
        if source_path.suffix.lower() in {".jpg", ".jpeg", ".png"}:
            webp_path = source_path.with_suffix(".webp")
            if webp_path.exists():
                src = "/" + str(webp_path.relative_to(ROOT)).replace("\\", "/")
        return f"{src}?v={BUILD_VERSION}"
    return src


def absolute_asset_url(site: dict, src: str) -> str:
    src = asset_url(src)
    if src.startswith("/"):
        return site["url"].rstrip("/") + src
    return src


def video_sources_html(src: str) -> str:
    """Serve a local WebM first and retain MP4 as a browser fallback."""
    src = str(src or "")
    if src.startswith("/assets/") and src.lower().endswith(".mp4"):
        webm = src[:-4] + ".webm"
        if (ROOT / webm.lstrip("/")).exists():
            return (f'<source src="{esc(asset_url(webm))}" type="video/webm" />'
                    f'<source src="{esc(asset_url(src))}" type="video/mp4" />')
    return f'<source src="{esc(asset_url(src))}" />'


def image_dimensions(src: str) -> str:
    """Return intrinsic dimensions for local PNG/JPEG/WebP assets when available."""
    src = str(src or "")
    if not src.startswith("/assets/"):
        return ""
    source_path = ROOT / src.lstrip("/").split("?", 1)[0]
    path = source_path
    webp_path = source_path.with_suffix(".webp") if source_path.suffix.lower() in {".jpg", ".jpeg", ".png"} else source_path
    try:
        if webp_path.exists():
            path = webp_path
        with path.open("rb") as fh:
            data = fh.read()
            if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
                chunk = data[12:16]
                if chunk == b"VP8X" and len(data) >= 30:
                    width = 1 + data[24] + (data[25] << 8) + (data[26] << 16)
                    height = 1 + data[27] + (data[28] << 8) + (data[29] << 16)
                    return f' width="{width}" height="{height}"'
                if chunk == b"VP8 " :
                    marker = data.find(b"\x9d\x01\x2a")
                    if marker >= 0 and len(data) >= marker + 7:
                        width = data[marker + 3] | ((data[marker + 4] & 0x3F) << 8)
                        height = data[marker + 5] | ((data[marker + 6] & 0x3F) << 8)
                        return f' width="{width}" height="{height}"'
            if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
                width, height = struct.unpack(">II", data[16:24])
                return f' width="{width}" height="{height}"'
            if data.startswith(b"\xff\xd8"):
                i = 2
                while i + 9 < len(data):
                    if data[i] != 0xFF:
                        i += 1
                        continue
                    marker = data[i + 1]
                    i += 2
                    while marker == 0xFF and i < len(data):
                        marker = data[i]
                        i += 1
                    if marker in (0xD8, 0xD9):
                        continue
                    if i + 2 > len(data):
                        break
                    length = struct.unpack(">H", data[i:i + 2])[0]
                    if marker in list(range(0xC0, 0xC4)) + list(range(0xC5, 0xC8)) + list(range(0xC9, 0xCC)) + list(range(0xCD, 0xD0)):
                        height, width = struct.unpack(">HH", data[i + 3:i + 7])
                        return f' width="{width}" height="{height}"'
                    i += max(2, length)
    except (OSError, ValueError, struct.error):
        pass
    return ""

def project_label(w: dict) -> str:
    return w.get("display_title") or (f'{w["client"]} — {w["name"]}' if w.get("name") else w["client"])


def project_description(d: dict, w: dict, case_study: dict | None = None) -> str:
    """Use editorial copy when present, otherwise a truthful archive description."""
    explicit = str(w.get("description") or ((case_study or {}).get("summary") or "")).strip()
    if explicit:
        return explicit
    label = project_label(w)
    category = str(w.get("category") or "PROJECT").strip()
    year = str(w.get("year") or "").strip()
    year_text = f" {year}년" if year else ""
    return f"SIA.HAUS의{year_text} {category} 프로젝트 아카이브입니다. {label}의 이미지와 제작 기록을 소개합니다."


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
        "logo": absolute_asset_url(s, s.get("logo", "/favicon.svg")),
        "image": absolute_asset_url(s, s.get("image", "/og-default.svg")),
        "foundingDate": s.get("founding_date", "2018"),
        "email": s["email"],
        "contactPoint": {
            "@type": "ContactPoint",
            "contactType": "project inquiries",
            "email": s["email"],
            "areaServed": s["area_served"],
            "availableLanguage": [s["lang"]],
        },
        "foundingLocation": {"@type": "Place", "name": s["founding_location"]},
        "address": {
            "@type": "PostalAddress",
            "streetAddress": s["address"]["street"],
            "addressLocality": s["address"]["locality"],
            "postalCode": s["address"]["postal_code"],
            "addressCountry": {"@type": "Country", "name": s["address"]["country"]},
        },
        "areaServed": {"@type": "Country", "name": s["area_served"]},
        "knowsAbout": list(dict.fromkeys(
            [d.get("entity_definition", "")] +
            [f["name"] for f in d["fields"]["items"]] +
            ["AI GRAPHICS", "Generative AI", "3D", "VFX", "Motion Graphics", "Spatial Media", "Projection Mapping", "Immersive Exhibition", "Media Facade", "Sound Design"]
        )),
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

    webpage = {
        "@type": "WebPage",
        "@id": s["url"] + "#webpage",
        "url": s["url"],
        "name": d["meta"]["title"],
        "description": d["meta"]["description"],
        "inLanguage": s["lang"],
        "isPartOf": {"@id": s["url"] + "#website"},
        "about": {"@id": s["org_id"]},
        "mainEntity": {"@id": s["org_id"]},
        "primaryImageOfPage": {"@id": s["url"] + "#primary-image"},
    }

    graph = [org, website, webpage, {
        "@type": "ImageObject",
        "@id": s["url"] + "#primary-image",
        "url": absolute_asset_url(s, s.get("image", "/og-default.svg")),
        "contentUrl": absolute_asset_url(s, s.get("image", "/og-default.svg")),
        "caption": d["meta"]["title"],
    }]

    service_items = []
    for service in d.get("services", []):
        service_url = s["url"] + "services/" + service["slug"]
        service_items.append({
            "@type": "Service",
            "@id": service_url + "#service",
            "name": service["title"],
            "url": service_url,
            "description": service["description"],
            "serviceType": service["eyebrow"],
            "provider": {"@id": s["org_id"]},
            "areaServed": {"@type": "Country", "name": s["area_served"]},
            "keywords": service.get("keywords", []),
        })
    graph.extend(service_items)

    for reference in d.get("references", {}).get("items", []):
        video_url = (reference.get("video_url") or "").strip()
        if not video_url:
            continue
        video_slug = re.sub(r"[^a-z0-9]+", "-", reference.get("title", "reference").lower()).strip("-") or f"reference-{len(graph)}"
        video_node = {
            "@type": "VideoObject",
            "@id": s["url"] + "#video-" + video_slug,
            "name": reference.get("title", "SIA.HAUS reference video"),
            "description": reference.get("summary", ""),
            "contentUrl": absolute_asset_url(s, video_url),
            "publisher": {"@id": s["org_id"]},
            "inLanguage": s["lang"],
        }
        poster = (reference.get("poster") or "").strip()
        if poster:
            video_node["thumbnailUrl"] = absolute_asset_url(s, poster)
        graph.append(video_node)

    case_list = []
    for c in d.get("case_studies", {}).get("items", []):
        slug = c.get("slug")
        if not slug:
            continue
        case_url = s["url"] + "projects/" + slug
        case_list.append({
            "@type": "ListItem",
            "position": len(case_list) + 1,
            "item": {
                "@type": "CreativeWork",
                "@id": case_url + "#work",
                "url": case_url,
                "name": c.get("title", ""),
                "description": c.get("summary", ""),
                "creator": {"@id": s["org_id"]},
                "isPartOf": {"@id": s["url"] + "#website"},
            },
        })
    if case_list:
        graph.append({
            "@type": "ItemList",
            "@id": s["url"] + "#case-studies",
            "name": d.get("case_studies", {}).get("title", ""),
            "itemListOrder": "https://schema.org/ItemListOrderAscending",
            "numberOfItems": len(case_list),
            "itemListElement": case_list,
        })

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

/* services */
.service-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1px;background:var(--line);border-top:1px solid var(--line)}
.service-card{display:flex;flex-direction:column;gap:14px;min-height:260px;padding:clamp(20px,3vw,34px);background:var(--bg);color:inherit;transition:background .2s ease}
.service-card:hover{background:#e9e9e6}
.service-card-kicker{font-family:var(--font-mono);font-size:10px;letter-spacing:.14em;color:var(--text-faint)}
.service-card h3{margin:12px 0 0;font-size:clamp(20px,2.3vw,30px);line-height:1.12;font-weight:400;letter-spacing:-.035em}
.service-card p{margin:0;color:var(--text-subtle);font-size:14px;line-height:1.7;word-break:keep-all}
.service-card-link{margin-top:auto;font-size:12px;color:var(--text-muted)}
@media(max-width:900px){.service-grid{grid-template-columns:1fr}}

/* work — media.work: 3-column masonry grid with hover overlay cards */
.work-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.work-card{position:relative;overflow:hidden;background:var(--surface)}
.work-card-media{position:relative;width:100%;display:block;aspect-ratio:4/5;overflow:hidden}
.work-card-media img,.work-card-media video{width:100%;height:100%;display:block;object-fit:cover}
.work-card-video iframe{position:absolute;inset:0;width:100%;height:100%;border:0;pointer-events:none}
.work-card:nth-child(3n+2) .work-card-media{aspect-ratio:16/9}
.work-card:nth-child(3n+3) .work-card-media{aspect-ratio:1/1}
/* placeholder when no verified media asset */
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

/* case studies */
.case-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:clamp(18px,2vw,28px)}
.case-card{display:block;background:var(--surface);overflow:hidden;border:1px solid var(--line);transition:transform .25s ease,box-shadow .25s ease}
.case-card:hover{transform:translateY(-4px);box-shadow:0 16px 32px rgba(0,0,0,.08)}
.case-card-media{aspect-ratio:16/10;background:#e8e8e6;overflow:hidden}
.case-card-media img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .45s ease}
.case-card:hover .case-card-media img{transform:scale(1.03)}
.case-card-placeholder{height:100%;display:flex;align-items:flex-end;padding:22px;font-size:24px;line-height:1.1;background:#111;color:#fff}
.case-card-body{padding:clamp(20px,2.5vw,32px)}
.case-card-label,.case-detail-label{font-family:var(--font-mono);font-size:11px;letter-spacing:.12em;color:var(--text-faint);text-transform:uppercase}
.case-card h3{margin-top:12px;font-size:clamp(20px,2.2vw,30px);font-weight:400;line-height:1.12;letter-spacing:-.03em;color:var(--text-strong)}
.case-card p{margin-top:14px;font-size:14px;line-height:1.7;color:var(--text-subtle);max-width:58ch}
.case-card-link{display:inline-block;margin-top:22px;font-size:12px;color:var(--text-strong);text-decoration:underline;text-underline-offset:4px}
/* references */
.reference-grid{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(260px,.65fr);gap:clamp(22px,4vw,64px);align-items:end}
.reference-card{background:var(--surface);border:1px solid var(--line);overflow:hidden}
.reference-media{aspect-ratio:1/1;background:#111;overflow:hidden}
.reference-media video{width:100%;height:100%;display:block;object-fit:cover}
.reference-copy{padding:clamp(20px,2.5vw,32px)}
.reference-label{font-family:var(--font-mono);font-size:11px;letter-spacing:.12em;color:var(--text-faint);text-transform:uppercase}
.reference-copy h3{margin-top:12px;font-size:clamp(24px,3.2vw,44px);font-weight:400;line-height:1.05;letter-spacing:-.04em;color:var(--text-strong)}
.reference-copy p{margin-top:16px;font-size:14px;line-height:1.7;color:var(--text-subtle);max-width:42ch}
.reference-source{display:inline-block;margin-top:22px;font-size:12px;color:var(--text-strong);text-decoration:underline;text-underline-offset:4px}
@media(max-width:820px){.reference-grid{grid-template-columns:1fr}.reference-media{aspect-ratio:1/1;max-width:680px}}
/* project brief */
.brief-form{border-top:1px solid var(--line);padding-top:clamp(24px,3vw,36px)}
.brief-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px 24px}
.brief-form label{display:block;font-size:12px;color:var(--text-subtle)}
.brief-form input,.brief-form select,.brief-form textarea{width:100%;margin-top:8px;border:1px solid var(--line);background:var(--surface);border-radius:0;padding:12px 13px;font:inherit;font-size:14px;color:var(--text-strong);outline:none}
.brief-form input:focus,.brief-form select:focus,.brief-form textarea:focus{border-color:var(--text-strong);background:var(--white)}
.brief-form textarea{resize:vertical;min-height:130px}
.brief-full{display:block;margin-top:18px}
.brief-consent{display:flex;align-items:flex-start;gap:9px;margin-top:18px;font-size:12px;line-height:1.6;color:var(--text-muted)}
.brief-consent input{width:16px;height:16px;margin:2px 0 0;flex:0 0 auto}
.brief-consent a{text-decoration:underline;text-underline-offset:3px}
.brief-actions{display:flex;align-items:center;gap:18px;flex-wrap:wrap;margin-top:22px}
.brief-submit{border:0;background:var(--black);color:var(--white);padding:13px 18px;font:inherit;font-size:12px;cursor:pointer}
.brief-submit:hover{background:#333}
.brief-note{font-size:12px;color:var(--text-faint);max-width:62ch}
.brief-followup{display:flex;flex-direction:column;gap:5px;margin-top:18px;padding:16px 18px;background:#efefec;border-left:2px solid var(--black);font-size:12px;line-height:1.6;color:var(--text-subtle)}
.brief-followup strong{color:var(--text-strong);font-weight:500}
.brief-followup[hidden]{display:none}
/* project case study */
.project-case-study{padding:clamp(64px,9vw,128px) 0 0}
.project-case-study .wrap{max-width:1000px}
.project-case-study h2{max-width:18ch;margin-top:12px;font-size:clamp(30px,4.5vw,62px);line-height:1.02;letter-spacing:-.05em}
.case-detail-summary{max-width:65ch;margin-top:20px;font-size:clamp(16px,1.6vw,21px);line-height:1.7;color:var(--text-muted)}
.case-detail-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1px;background:var(--line);margin-top:48px}
.case-detail-item{background:var(--bg);padding:26px 24px;min-height:150px}
.case-detail-item p{margin-top:12px;font-size:15px;line-height:1.7;color:var(--text-subtle)}
.project-case-study .project-contact-cta{margin-top:30px}
@media(max-width:820px){.case-grid{grid-template-columns:1fr}.case-detail-grid{grid-template-columns:1fr}.brief-grid{grid-template-columns:1fr}}

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
.foot-grid>div:nth-child(5){grid-column:span 2}
.foot-grid>div:nth-child(5) a{display:inline-block;color:var(--footer-text);font-size:clamp(14px,1.2vw,18px);letter-spacing:-.02em}
.foot-copy{margin-top:clamp(24px,3vw,40px);padding-top:16px;
  border-top:1px solid rgba(255,255,255,0.08);font-size:11px;
  color:rgba(255,255,255,0.4)}
@media(max-width:960px){.foot-grid{grid-template-columns:repeat(3,1fr)}.foot-grid>div:nth-child(5){grid-column:span 1}}
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
        for i, k in [("work", "nav_work"), ("case-studies", "nav_case"),
                     ("references", "nav_reference"), ("fields", "nav_fields"),
                     ("services", "nav_services"), ("faq", "nav_faq"),
                     ("brief", "nav_brief"), ("contact", "nav_contact")]
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

    # The main logo is neutral; project clients belong in the work cards.
    featured = ""

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

    # media.work: masonry grid cards with verified image/video assets
    def work_card(w: dict) -> str:
        url = (w.get("url") or "").strip()
        video_url = (w.get("video_url") or "").strip()
        image_url = (w.get("image_url") or "").strip()
        label = w.get("display_title") or (f'{w["client"]} — {w["name"]}' if w.get("name") else w["client"])
        # Homepage cards use verified still images only.
        # This prevents iframe/video loading failures and text-bearing fallbacks.
        if image_url:
            media = (f'<div class="work-card-media">'
                     f'<img src="{esc(asset_url(image_url))}"{image_dimensions(image_url)} alt="{esc(label)} 대표 이미지" loading="lazy" decoding="async" sizes="(max-width: 520px) 100vw, (max-width: 820px) 50vw, 33vw" />'
                     f'</div>')
        else:
            media = ''
        meta = " · ".join(x for x in [w.get("category", "PROJECT"), w.get("year", "")] if x)
        overlay = (f'<div class="work-card-overlay">'
                   f'<span class="work-card-title">{esc(label)}</span>'
                   f'<span class="work-card-type">{esc(meta)}</span>'
                   f'</div>')
        inner = f'{media}{overlay}'
        if url:
            return f'<a class="work-card" href="{esc(url)}" aria-label="{esc(label + " 프로젝트 상세 보기")}">{inner}</a>'
        return f'<div class="work-card">{inner}</div>'

    selected_slugs = set(d.get("selected_work_slugs", []))
    selected_items = [w for w in d["work"]["items"] if w.get("slug") in selected_slugs]
    if not selected_items:
        selected_items = d["work"]["items"][:12]
    archive_items = [w for w in d["work"]["items"] if w not in selected_items]
    works = "".join(work_card(w) for w in selected_items)
    work_lead = f'<p class="lead">{esc(d["work"]["lead"])}</p>' if d["work"].get("lead") else ""
    fields_lead = f'<p class="lead">{esc(d["fields"]["lead"])}</p>' if d["fields"].get("lead") else ""
    service_cards = "".join(
        f'<a class="service-card" href="/services/{esc(service["slug"])}">'
        f'<span class="service-card-kicker">{esc(service["eyebrow"])}</span>'
        f'<h3>{esc(service["title"])}</h3><p>{esc(service["short"])}</p><span class="service-card-link">서비스 상세 보기 ↗</span></a>'
        for service in d.get("services", [])
    )
    archive_data = d.get("archive", {})
    archive_rows = "".join(
        f'<a class="archive-row" href="{esc(w.get("url") or ("/projects/" + w.get("slug", "")))}">'
        f'<span>{esc(w.get("display_title") or (f"{w["client"]} — {w["name"]}" if w.get("name") else w["client"]))}</span>'
        f'<span>{esc(" · ".join(x for x in [w.get("category", "PROJECT"), w.get("year", "")] if x))}</span></a>'
        for w in archive_items if w.get("slug")
    )
    archive_section = f'''<section id="archive">
    <div class="wrap">
      <div class="sec-head">
        <p class="eyebrow">{esc(archive_data.get("eyebrow", "FULL ARCHIVE"))}</p>
        <h2>{esc(archive_data.get("title", "전체 프로젝트"))}</h2>
        <p class="lead">{esc(archive_data.get("lead", ""))}</p>
      </div>
      <details class="archive-disclosure">
        <summary>{esc(archive_data.get("toggle", "전체 프로젝트 보기"))} <span>↘</span></summary>
        <div class="archive-list">{archive_rows}</div>
      </details>
    </div>
  </section>'''

    work_by_slug = {w.get("slug"): w for w in d["work"]["items"] if w.get("slug")}
    case_cards = []
    for c in d.get("case_studies", {}).get("items", []):
        if c.get("slug") in d.get("archive_only_slugs", []):
            continue
        w = work_by_slug.get(c.get("slug"), {})
        href = w.get("url") or (f'/projects/{c.get("slug")}' if c.get("slug") else "")
        image = (w.get("image_url") or "").strip()
        media = f'<img src="{esc(asset_url(image))}"{image_dimensions(image)} alt="{esc(c.get("title", ""))} 대표 이미지" loading="lazy" decoding="async" sizes="(max-width: 820px) 100vw, 50vw" />' if image else f'<div class="case-card-placeholder">{esc(c.get("title", ""))}</div>'
        case_cards.append(f'<a class="case-card" href="{esc(href)}"><div class="case-card-media">{media}</div><div class="case-card-body"><span class="case-card-label">{esc(c.get("label", "CASE STUDY"))}</span><h3>{esc(c.get("title", ""))}</h3><p>{esc(c.get("summary", ""))}</p><span class="case-card-link">상세 케이스스터디 ↗</span></div></a>')
    case_cards_html = "".join(case_cards)
    case_lead = f'<p class="lead">{esc(d["case_studies"]["lead"])}</p>' if d.get("case_studies", {}).get("lead") else ""

    references_data = d.get("references", {})
    reference_cards = []
    for r in references_data.get("items", []):
        video = (r.get("video_url") or "").strip()
        poster = (r.get("poster") or "").strip()
        source = (r.get("source") or "").strip()
        poster_attr = f' poster="{esc(asset_url(poster))}"' if poster else ""
        source_html = f'<a class="reference-source" href="{esc(source)}" target="_blank" rel="noopener noreferrer">{esc(r.get("source_label", "원문 보기 ↗"))}</a>' if source else ""
        reference_cards.append(
            f'<article class="reference-card"><div class="reference-media"><video{poster_attr} controls playsinline preload="none">{video_sources_html(video)}</video></div>'
            f'<div class="reference-copy"><span class="reference-label">{esc(r.get("label", "REFERENCE"))}</span>'
            f'<h3>{esc(r.get("title", ""))}</h3><p>{esc(r.get("summary", ""))}</p>{source_html}</div></article>'
        )
    references_html = "".join(reference_cards)

    brief_data = d.get("brief", {})
    brief_options = "".join(f'<option value="{esc(x)}">{esc(x)}</option>' for x in brief_data.get("purposes", []))
    budget_options = "".join(f'<option value="{esc(x)}">{esc(x)}</option>' for x in ["5천만원 미만", "5천만원–1억원", "1억–3억원", "3억원 이상"])
    timeline_options = "".join(f'<option value="{esc(x)}">{esc(x)}</option>' for x in ["3개월 이내", "3–6개월", "6개월 이후"])
    decision_options = "".join(f'<option value="{esc(x)}">{esc(x)}</option>' for x in ["아이디어 검토", "내부 논의 중", "예산·일정 확정", "제작사 선정 단계"])
    brief_action = "https://formspree.io/f/xaeqleva"
    brief_form = f'''<form class="brief-form" action="{brief_action}" method="POST" accept-charset="UTF-8">
        <input type="hidden" name="_subject" value="[SIA.HAUS] 프로젝트 브리프" />
        <input type="hidden" name="form_id" value="siahaus-project-brief" />
        <input type="hidden" name="source" value="website" />
        <input type="hidden" name="landing_page" />
        <input type="hidden" name="page_url" />
        <input type="hidden" name="referrer" />
        <input type="hidden" name="first_seen_at" />
        <input type="hidden" name="last_seen_at" />
        <input type="hidden" name="utm_source" />
        <input type="hidden" name="utm_medium" />
        <input type="hidden" name="utm_campaign" />
        <input type="hidden" name="utm_content" />
        <input type="hidden" name="utm_term" />
        <input type="hidden" name="service_tag" />
        <input type="hidden" name="lead_id" />
        <input type="hidden" name="relay_version" value="v2" />
        <input type="hidden" name="relay_attempted_at" />
        <input type="hidden" name="relay_client_status" />
        <input type="hidden" name="relay_status" />
        <div class="brief-grid">
          <label>회사·기관명 <input type="text" name="company" autocomplete="organization" required /></label>
          <label>담당자명 <input type="text" name="contact_name" autocomplete="name" required /></label>
          <label>이메일 <input type="email" name="email" autocomplete="email" required /></label>
          <label>프로젝트 목적 <select name="purpose" required><option value="">선택해 주세요</option>{brief_options}</select></label>
          <label>예상 예산 <select name="budget_range"><option value="">선택해 주세요</option>{budget_options}</select></label>
          <label>희망 일정 <select name="timeline"><option value="">선택해 주세요</option>{timeline_options}</select></label>
          <label>의사결정 단계 <select name="decision_stage"><option value="">선택해 주세요</option>{decision_options}</select></label>
          <label>공간 위치 <input type="text" name="space_location" placeholder="예: 서울 강남구, 해외" /></label>
        </div>
        <label class="brief-full">프로젝트 설명 <textarea name="description" rows="6" placeholder="만들고 싶은 경험, 필요한 산출물, 참고 링크를 자유롭게 적어주세요." required></textarea></label>
        <label class="brief-consent"><input type="checkbox" name="privacy_consent" value="accepted" required /> <span>{esc(d.get("privacy", {}).get("consent_label", "개인정보 처리 안내를 확인했으며, 문의 응대를 위한 정보 처리에 동의합니다."))} <a href="/privacy">전문 보기</a></span></label>
        <input type="hidden" name="privacy_policy_version" value="2026-10-29" />
        <div class="brief-actions"><button type="submit" class="brief-submit">{esc(brief_data.get("submit", "브리프 보내기"))} ↗</button><p class="brief-note" role="status">{esc(brief_data.get("note", ""))}</p></div>
        <div class="brief-followup" hidden role="status"><strong>다음 단계</strong><span>브리프를 확인한 뒤 영업일 기준 1–2일 안에 가능한 제작 방향과 다음 미팅 단계를 회신드립니다.</span></div>
      </form>'''

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

    featured_slug = d["hero"].get("featured_slug")
    featured_work = next((w for w in d["work"]["items"] if w.get("slug") == featured_slug), None)
    if featured_work is None and d["work"]["items"]:
        featured_work = d["work"]["items"][0]
    hero_media = ""
    hero_meta = ""
    if featured_work:
        fi = (featured_work.get("image_url") or "").strip()
        if fi:
            hero_media = (
                f'<img class="hero-media" src="{esc(asset_url(fi))}"{image_dimensions(fi)} '
                f'alt="{esc(featured_work["client"] + " — " + featured_work["name"])} 대표 이미지" '
                f'loading="eager" fetchpriority="high" decoding="async" sizes="100vw" />'
            )
        meta_bits = [featured_work.get("context", ""), featured_work.get("year", "")]
        meta_text = " · ".join(x for x in meta_bits if x)
        hero_meta = (
            f'<div class="hero-meta"><strong>{esc(featured_work["client"])} — '
            f'{esc(featured_work["name"])}</strong><span>{esc(meta_text)}</span></div>'
        )

    # Footer: media.work 7-column dense layout
    social_links = "".join(f'<dd><a href="{esc(u)}" target="_blank" rel="noopener">{esc(u.split("/")[-2] if u.endswith("/") else u.split("/")[-1])}</a></dd>' for u in s.get("same_as", []))
    social_image = absolute_asset_url(s, (featured_work or {}).get("image_url") or "/og-default.svg")

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
<meta name="robots" content="index,follow" />
<link rel="canonical" href="{esc(s["url"])}" />{alternates}
<meta property="og:type" content="website" />
<meta property="og:site_name" content="{esc(s["name"])}" />
<meta property="og:url" content="{esc(s["url"])}" />
<meta property="og:title" content="{esc(d["meta"]["title"])}" />
<meta property="og:description" content="{esc(d["meta"]["description"])}" />
<meta property="og:locale" content="{esc(s["locale"])}" />
<meta property="og:image" content="{esc(social_image)}" />
<meta property="og:image:alt" content="{esc(d["meta"]["title"])}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:image" content="{esc(social_image)}" />
<meta name="twitter:title" content="{esc(d["meta"]["title"])}" />
<meta name="twitter:description" content="{esc(d["meta"]["description"])}" />
<meta name="twitter:image:alt" content="{esc(d["meta"]["title"])}" />
<style>{CSS}</style>
<link rel="stylesheet" href="/theme-v2.css?v={BUILD_VERSION}" />
{ANALYTICS_TAGS}
<script type="application/ld+json">
{build_jsonld(d, launched)}
</script>
</head>
<body>
<a class="skip" href="#main">{esc(t["skip"])}</a>

<header class="site">
  <div class="wrap hdr">
    <a class="logo" href="/">SIA.HAUS</a>
    <nav class="main">{nav}</nav>
    {lang_link}
  </div>
</header>

<main id="main">
  <section class="hero">
    {hero_media}
    <div class="hero-shade" aria-hidden="true"></div>
    <div class="wrap">
      <div class="hero-v2">
        <p class="hero-kicker">{esc(d["hero"].get("role", "서울 기반 AI GRAPHICS 스튜디오"))}</p>
        <h1 class="hero-title">{esc(d["hero"].get("display_title", d["hero"]["headline"]))}</h1>
        <p class="hero-subtitle">{esc(d["hero"]["headline"])}</p>
        <p class="hero-role">{esc(d["hero"].get("service_line", ""))}</p>
        <div class="hero-actions">
          <a class="hero-action" href="#work">{esc(d["hero"].get("cta_primary", t["cta_work"]))} ↘</a>
          <a class="hero-action secondary" href="#contact">{esc(d["hero"].get("cta_secondary", t["cta_contact"]))} ↗</a>
        </div>
        {hero_meta}
      </div>
    </div>
  </section>

  <section class="intro">
    <div class="wrap">
      <p class="intro-copy">{esc(definition(d, launched))}</p>
    </div>
  </section>

  <section id="work">
    <div class="wrap">
      <div class="sec-head">
        <p class="eyebrow">{esc(d["work"]["eyebrow"])}</p>
        <h2>{esc(d["work"]["title"])}</h2>
        {work_lead}
      </div>
      <div class="work-grid">{works}</div>
      <p class="work-note">{esc(d["work"]["note"])}</p>
    </div>
  </section>

  {archive_section}

  <section id="case-studies">
    <div class="wrap">
      <div class="sec-head">
        <p class="eyebrow">{esc(d["case_studies"].get("eyebrow", "CASE STUDIES"))}</p>
        <h2>{esc(d["case_studies"].get("title", ""))}</h2>
        {case_lead}
      </div>
      <div class="case-grid">{case_cards_html}</div>
    </div>
  </section>

  <section id="references">
    <div class="wrap">
      <div class="sec-head">
        <p class="eyebrow">{esc(references_data.get("eyebrow", "REFERENCES"))}</p>
        <h2>{esc(references_data.get("title", "레퍼런스"))}</h2>
        <p class="lead">{esc(references_data.get("lead", ""))}</p>
      </div>
      <div class="reference-grid">{references_html}</div>
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
        {fields_lead}
      </div>
      <div class="fields">{fields}</div>
    </div>
  </section>

  <section id="services">
    <div class="wrap">
      <div class="sec-head">
        <p class="eyebrow">SERVICES</p>
        <h2>AI GRAPHICS를 실제 경험으로 구현합니다</h2>
        <p class="lead">생성형 AI, 3D, VFX, 모션그래픽, 공간 연출을 목적과 매체에 맞춰 연결합니다.</p>
      </div>
      <div class="service-grid">{service_cards}</div>
    </div>
  </section>

  <section id="brief">
    <div class="wrap">
      <div class="sec-head">
        <p class="eyebrow">{esc(d["brief"]["eyebrow"])}</p>
        <h2>{esc(d["brief"]["title"])}</h2>
        <p class="lead">{esc(d["brief"]["lead"])}</p>
      </div>
      {brief_form}
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
        <dd><a href="https://docs.google.com/presentation/d/171DjianF251m7syNLfqL5QrkOTJxo29TOQLVexNRJJ8/edit?usp=sharing" target="_blank" rel="noopener">brief</a></dd>
        <dd><a href="/privacy">개인정보 처리 안내</a></dd>
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



# ─────────────────────── service landing pages ───────────────────────

def build_service_jsonld(d: dict, service: dict) -> str:
    s = d["site"]
    url = s["url"] + "services/" + service["slug"]
    graph = [
        {
            "@type": "Service",
            "@id": url + "#service",
            "name": service["title"],
            "url": url,
            "description": service["description"],
            "serviceType": service["eyebrow"],
            "provider": {"@id": s["org_id"]},
            "areaServed": {"@type": "Country", "name": s["area_served"]},
            "keywords": service.get("keywords", []),
        },
        {
            "@type": "WebPage",
            "@id": url + "#webpage",
            "url": url,
            "name": service["title"],
            "description": service["description"],
            "inLanguage": s["lang"],
            "about": {"@id": url + "#service"},
            "isPartOf": {"@id": s["url"] + "#website"},
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": s["name"], "item": s["url"]},
                {"@type": "ListItem", "position": 2, "name": service["title"], "item": url},
            ],
        },
        {
            "@type": "FAQPage",
            "@id": url + "#faq",
            "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in service.get("faq", [])
            ],
        },
    ]
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)


def build_service_html(d: dict, service: dict) -> str:
    s = d["site"]
    t = d["strings"]
    url = s["url"] + "services/" + service["slug"]
    title = f'{service["title"]} | SIA.HAUS'
    related = {w.get("slug"): w for w in d["work"]["items"] if w.get("slug")}
    related_cards = []
    for slug in service.get("related_slugs", []):
        w = related.get(slug)
        if not w:
            continue
        label = w.get("display_title") or (f'{w.get("client", "")} — {w.get("name", "")}' if w.get("name") else w.get("client", ""))
        image = (w.get("image_url") or "").strip()
        media = f'<img src="{esc(asset_url(image))}"{image_dimensions(image)} alt="{esc(label)} 대표 이미지" loading="lazy" decoding="async" />' if image else ""
        related_cards.append(f'<a class="service-related-card" href="/projects/{esc(slug)}"><div class="service-related-media">{media}</div><div><span>{esc(w.get("category", "PROJECT"))} · {esc(w.get("year", ""))}</span><strong>{esc(label)}</strong></div></a>')
    faq_html = "".join(f'<div class="service-faq-item"><h3>{esc(q)}</h3><p>{esc(a)}</p></div>' for q, a in service.get("faq", []))
    keywords_html = "".join(f'<li>{esc(k)}</li>' for k in service.get("keywords", []))
    process_html = "".join(f'<li><strong>{esc(step["name"])}</strong><span>{esc(step["en"])}</span></li>' for step in d["pipeline"]["steps"])
    return f'''<!DOCTYPE html>
<html lang="{s["lang"]}">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<link rel="icon" href="/favicon.svg" type="image/svg+xml" />
<title>{esc(title)}</title>
<meta name="description" content="{esc(service["description"])}" />
<meta name="robots" content="index,follow" />
<link rel="canonical" href="{esc(url)}" />
<meta property="og:type" content="website" />
<meta property="og:site_name" content="{esc(s["name"])}" />
<meta property="og:url" content="{esc(url)}" />
<meta property="og:title" content="{esc(title)}" />
<meta property="og:description" content="{esc(service["description"])}" />
<meta property="og:image" content="{esc(absolute_asset_url(s, s.get("image", "/og-default.svg")))}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{esc(title)}" />
<meta name="twitter:description" content="{esc(service["description"])}" />
<meta name="twitter:image" content="{esc(absolute_asset_url(s, s.get("image", "/og-default.svg")))}" />
<script type="application/ld+json">{build_service_jsonld(d, service)}</script>
<style>
:root{{--service-bg:#f7f7f5;--service-line:rgba(0,0,0,.12);--service-muted:#666;--service-black:#050505}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--service-bg);color:#111;font-family:Inter,Arial,sans-serif}}a{{color:inherit;text-decoration:none}}.wrap{{max-width:1280px;margin:0 auto;padding:0 clamp(20px,4vw,56px)}}header{{height:64px;border-bottom:1px solid var(--service-line);background:rgba(255,255,255,.92);display:flex;align-items:center}}header .wrap{{width:100%;display:flex;justify-content:space-between;align-items:center}}.logo{{font-weight:600;font-size:14px}}nav{{display:flex;gap:22px;font-size:13px;color:#666}}main{{padding:clamp(72px,10vw,150px) 0 0}}.service-kicker{{font:500 11px/1.4 ui-monospace,monospace;letter-spacing:.18em;color:#666}}h1{{max-width:900px;margin:18px 0 24px;font-size:clamp(44px,7vw,96px);line-height:.95;letter-spacing:-.06em;font-weight:300}}.service-lead{{max-width:780px;font-size:clamp(18px,2vw,27px);line-height:1.55;color:#333}}.service-definition{{max-width:720px;margin-top:26px;font-size:16px;line-height:1.8;color:#555}}.service-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1px;background:var(--service-line);margin-top:80px}}.service-panel{{background:var(--service-bg);padding:26px;min-height:210px}}.service-panel h2{{font-size:21px;font-weight:400;margin:0 0 20px}}.service-panel ul{{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:12px}}.service-panel li{{display:flex;justify-content:space-between;gap:16px;border-top:1px solid var(--service-line);padding-top:11px}}.service-panel li span{{font:11px ui-monospace,monospace;color:#777}}.service-related{{padding:clamp(80px,10vw,150px) 0 0}}.section-label{{font:500 11px/1.4 ui-monospace,monospace;letter-spacing:.18em;color:#666}}.service-related h2,.service-faq h2{{font-size:clamp(32px,5vw,62px);font-weight:300;letter-spacing:-.05em;margin:14px 0 34px}}.service-related-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}}.service-related-card{{background:#fff;border:1px solid var(--service-line);display:flex;flex-direction:column;min-height:100%}}.service-related-media{{aspect-ratio:16/10;background:#e8e8e6;overflow:hidden}}.service-related-media img{{width:100%;height:100%;object-fit:cover;display:block}}.service-related-card>div:last-child{{padding:18px;display:flex;flex-direction:column;gap:9px}}.service-related-card span{{font:10px ui-monospace,monospace;color:#777}}.service-related-card strong{{font-size:20px;font-weight:400;line-height:1.15}}.service-faq{{padding:clamp(80px,10vw,150px) 0 0}}.service-faq-item{{border-top:1px solid var(--service-line);padding:22px 0;display:grid;grid-template-columns:1fr 1fr;gap:28px}}.service-faq-item h3{{margin:0;font-size:20px;font-weight:400}}.service-faq-item p{{margin:0;color:#555;line-height:1.75}}.service-cta{{margin:clamp(80px,10vw,150px) 0 0;padding:38px;background:#050505;color:#fff;display:flex;justify-content:space-between;gap:24px;align-items:center}}.service-cta h2{{margin:0;font-size:clamp(26px,4vw,50px);font-weight:300;letter-spacing:-.05em}}.service-cta a{{border:1px solid rgba(255,255,255,.55);padding:13px 18px;font-size:12px;white-space:nowrap}}footer{{margin-top:120px;padding:32px 0;border-top:1px solid var(--service-line);font-size:12px;color:#666}}@media(max-width:820px){{nav{{gap:14px;overflow-x:auto;white-space:nowrap}}.service-grid,.service-related-grid{{grid-template-columns:1fr}}.service-faq-item{{grid-template-columns:1fr;gap:10px}}.service-cta{{display:block}}.service-cta a{{display:inline-block;margin-top:24px}}}}
</style>
</head>
<body>
<header><div class="wrap"><a class="logo" href="/">SIA.HAUS</a><nav><a href="/">홈</a><a href="/#work">실적</a><a href="/#services">서비스</a><a href="/#brief">문의</a></nav></div></header>
<main><div class="wrap">
<p class="service-kicker">{esc(service["eyebrow"])}</p>
<h1>{esc(service["title"])}</h1>
<p class="service-lead">{esc(service["short"])}</p>
<p class="service-definition">{esc(service["description"])}</p>
<div class="service-grid"><section class="service-panel"><h2>핵심 키워드</h2><ul>{keywords_html}</ul></section><section class="service-panel"><h2>제작 구조</h2><ul>{process_html}</ul></section><section class="service-panel"><h2>시작점</h2><ul><li><strong>프로젝트 브리프</strong><span>공간 · 일정 · 예산</span></li><li><strong>레퍼런스 검토</strong><span>목적 · 관객 · 매체</span></li><li><strong>제작 방향 제안</strong><span>범위 · 결과물</span></li></ul></section></div>
<section class="service-related"><p class="section-label">RELATED PROJECTS</p><h2>관련 프로젝트</h2><div class="service-related-grid">{"".join(related_cards)}</div></section>
<section class="service-faq"><p class="section-label">FAQ</p><h2>자주 묻는 질문</h2>{faq_html}</section>
<section class="service-cta"><h2>프로젝트의 출발점을 보내주세요</h2><a href="/?service_tag={esc(service["slug"])}#brief">프로젝트 브리프 작성 ↗</a></section>
</div></main><footer><div class="wrap">© {date.today().year} {esc(s["name"])} · <a href="/privacy">개인정보 처리 안내</a></div></footer>
</body></html>'''


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
        "name": (w.get("display_title") or (f'{w["client"]} \u2014 {w["name"]}' if w.get("name") else w["client"])),
        "headline": (w.get("display_title") or w["name"] or w["client"]),
        "inLanguage": s["lang"],
        "creator": {"@id": s["org_id"]},
        "isPartOf": {"@id": s["url"] + "#website"},
    }
    case_study = next((c for c in d.get("case_studies", {}).get("items", []) if c.get("slug") == w.get("slug")), None)
    case_sections = case_study.get("sections", []) if case_study else []
    section_map = {
        str(x.get("label", "")).strip(): str(x.get("text", "")).strip()
        for x in case_sections
        if isinstance(x, dict) and str(x.get("label", "")).strip() and str(x.get("text", "")).strip()
    }
    work["description"] = project_description(d, w, case_study)
    image_src = (w.get("image_url") or ((w.get("gallery_images") or [""])[0] if w.get("gallery_images") else ""))
    if image_src:
        image_url = absolute_asset_url(s, image_src)
        work["image"] = [image_url]
    work["keywords"] = list(dict.fromkeys(filter(None, ["AI GRAPHICS", w.get("category", ""), w.get("client", ""), w.get("name", ""), w.get("context", "")])) )
    work["about"] = w.get("context") or w.get("category") or "AI GRAPHICS"
    work["producer"] = {"@id": s["org_id"]}
    if w.get("context"):
        work["locationCreated"] = {"@type": "Place", "name": w["context"]}
    work["additionalProperty"] = [
        {"@type": "PropertyValue", "name": "Client", "value": w.get("client", "")},
        {"@type": "PropertyValue", "name": "Category", "value": w.get("category", "PROJECT")},
    ]
    if w.get("year"):
        work["dateCreated"] = w["year"]
    if section_map.get("일정") and not section_map["일정"].startswith("공개 자료에"):
        work["temporalCoverage"] = section_map["일정"]
    if section_map.get("장소") and not section_map["장소"].startswith("공개 자료에"):
        work["locationCreated"] = {"@type": "Place", "name": section_map["장소"]}
    if w.get("context"):
        work["about"] = w["context"]
    properties = list(work.get("additionalProperty", []))
    for label in ("역할", "범위", "근거 범위"):
        if section_map.get(label):
            properties.append({"@type": "PropertyValue", "name": label, "value": section_map[label]})
    work["additionalProperty"] = properties
    if w.get("source"):
        work["citation"] = w["source"]

    crumbs = {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": s["name"], "item": s["url"]},
            {"@type": "ListItem", "position": 2, "name": (w.get("display_title") or (f'{w["client"]} — {w["name"]}' if w.get("name") else w["client"])), "item": url},
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
    display_title = w.get("display_title") or (f'{w["client"]} \u2014 {w["name"]}' if w.get("name") else w["client"])
    case_study = next((c for c in d.get("case_studies", {}).get("items", []) if c.get("slug") == slug), None)
    archive_only = slug in d.get("archive_only_slugs", [])
    is_behance = slug.startswith("behance-")
    project_type = "archive" if archive_only else ("rich-gallery" if is_behance else ("featured-case" if case_study else "archive"))
    hero_title = display_title if not w.get("name") else w["client"]
    hero_description = project_description(d, w, case_study)
    has_body = True
    explicit_description = bool(str(w.get("description") or ((case_study or {}).get("summary") or "")).strip())
    title = f'{display_title} | {s["name"]}'
    if explicit_description:
        desc = hero_description.split(". ")[0].strip().rstrip(".") + "."
    else:
        desc = hero_description
    if len(desc) > 300:
        desc = desc[:297].rstrip() + "\u2026"
    if w.get("context"):
        desc += f' \u00b7 {w["context"]}'

    featured = display_title
    nav = "".join(
        f'<a href="/#{i}">{esc(t[k])}</a>'
        for i, k in [("work", "nav_work"), ("case-studies", "nav_case"),
                     ("fields", "nav_fields"), ("services", "nav_services"), ("faq", "nav_faq"),
                     ("brief", "nav_brief"), ("contact", "nav_contact")]
    )
    nav += f'<a class="mailto" href="mailto:{esc(s["email"])}">{esc(s["email"])}</a>'

    lang_link = "".join(
        f'<a class="lang" href="/{o["path"]}" hreflang="{o["lang"]}">{esc(o["lang_label"])}</a>'
        for o in locales if o["locale"] != s["locale"]
    )

    year_html = f'<span class="proj-year">{esc(w["year"])}</span>' if w.get("year") else '<span class="proj-year is-unknown">연도 미상</span>'
    ctx_html = f'<span class="proj-ctx">{esc(w["context"])}</span>' if w.get("context") else ""
    category_html = f'<span class="proj-category">{esc(w.get("category", "PROJECT"))}</span>'
    desc_text = esc(hero_description).replace("\n", "<br>") if has_body else ""
    desc_html = f'<p class="proj-desc">{desc_text}</p>' if desc_text else ""
    fact_rows = []
    for label, value in [("클라이언트", w.get("client")), ("분류", w.get("category", "PROJECT")), ("연도", w.get("year")), ("공간·맥락", w.get("context"))]:
        if value:
            fact_rows.append(f'<div><dt>{esc(label)}</dt><dd>{esc(value)}</dd></div>')
    project_facts_html = f'<dl class="project-facts">{"".join(fact_rows)}</dl>' if fact_rows else ""
    eyebrow_labels = {
        "featured-case": t.get("project_type_featured", "FEATURED CASE STUDY"),
        "rich-gallery": t.get("project_type_gallery", "RICH GALLERY"),
        "archive": t.get("project_type_archive", "ARCHIVE PROJECT"),
    }
    project_eyebrow = eyebrow_labels[project_type]
    contact_subject = f'{display_title} 프로젝트 문의'
    contact_cta = (f'<a class="project-contact-cta" href="/#brief">'
                   f'{esc(t["cta_contact"])} ↗</a>')

    source_url = (w.get("source") or "").strip()
    source_cta = (f'<a class="project-source-link" href="{esc(source_url)}" target="_blank" '
                  f'rel="noopener noreferrer">원문 프로젝트 ↗</a>') if source_url else ""

    video_url = (w.get("video_url") or "").strip()
    video_urls = [str(x).strip() for x in (w.get("video_urls") or []) if str(x).strip()]
    image_url = (w.get("image_url") or "").strip()
    gallery_images = [str(x).strip() for x in (w.get("gallery_images") or []) if str(x).strip()]
    media_label = display_title
    media_blocks = [b for b in (w.get("media_blocks") or []) if isinstance(b, dict)]
    intro_label = t.get("media_chapter_intro", "작품 소개")
    process_label = t.get("media_chapter_process", "공간 · 과정")
    output_label = t.get("media_chapter_output", "결과 장면")

    def _poster_for(embed_url: str) -> str:
        if embed_url.startswith("/assets/") and embed_url.lower().endswith(".mp4"):
            poster_path = (ROOT / embed_url.lstrip("/")).with_suffix(".jpg")
            if poster_path.exists():
                return embed_url.rsplit(".", 1)[0] + ".jpg"
        return ""

    def _embed_stage(embed_url: str, eager: bool, role_label: str = "영상") -> str:
        loading = "eager" if eager else "lazy"
        if ("player.vimeo.com" in embed_url or "youtube.com/embed" in embed_url
                or "facebook.com/plugins/video.php" in embed_url):
            return (f'<div class="proj-media-stage is-video">'
                    f'<iframe src="{esc(embed_url)}" title="{esc(media_label)} · {esc(role_label)}" '
                    f'loading="{loading}" allow="autoplay; fullscreen" allowfullscreen></iframe></div>')
        preload = "none" if embed_url.startswith("/assets/") else "metadata"
        poster = _poster_for(embed_url)
        poster_attr = f' poster="{esc(asset_url(poster))}"' if poster else ""
        return (f'<div class="proj-media-stage is-video">'
                f'<video{poster_attr} muted loop playsinline preload="{preload}" '
                f'data-autoplay="true" aria-label="{esc(media_label)} · {esc(role_label)}">{video_sources_html(embed_url)}</video></div>')

    def _image_stage(src: str, index: int, total: int, loading: str = "lazy") -> str:
        if project_type == "rich-gallery":
            role = intro_label if index < 4 else (process_label if index < min(12, total) else output_label)
            alt = f"{media_label} · {role} 이미지 {index + 1}"
        else:
            role = "대표 이미지" if index == 0 else "프로젝트 이미지"
            alt = f"{media_label} · {role} {index + 1}"
        return (f'<div class="proj-media-stage"><img src="{esc(asset_url(src))}"{image_dimensions(src)} alt="{esc(alt)}" '
                f'loading="{loading}" decoding="async" sizes="100vw" /></div>')

    def _chapter(label: str, items: list[str]) -> str:
        if not items:
            return ""
        return (f'<section class="media-chapter"><p class="media-chapter-label">{esc(label)}</p>'
                f'<div class="media-chapter-list">{"".join(items)}</div></section>')

    def _collapse(items: list[str], label: str = "") -> str:
        if not items:
            return f'<div class="proj-media-empty">{esc(display_title)}</div>'
        if project_type == "rich-gallery":
            intro_end = min(4, len(items))
            process_end = min(12, len(items))
            intro_html = _chapter(intro_label, items[:intro_end])
            process_html = _chapter(process_label, items[intro_end:process_end])
            output_html = _chapter(output_label, items[process_end:])
            hidden_html = process_html + output_html
            more = (f'<details class="project-media-more"><summary>{esc(t.get("gallery_more", "전체 이미지 보기"))} '
                    f'<span>{len(items) - intro_end}개 미디어</span></summary><div class="project-media-more-list">{hidden_html}</div></details>'
                    if hidden_html else "")
            return intro_html + more
        visible = "".join(items[:12])
        hidden = "".join(items[12:])
        more = (f'<details class="project-media-more"><summary>{esc(t.get("gallery_more", "전체 이미지 보기"))} '
                f'<span>{len(items) - 12}개 미디어</span></summary><div class="project-media-more-list">{hidden}</div></details>'
                if hidden else "")
        return visible + more

    if media_blocks:
        stages = []
        total_blocks = len(media_blocks)
        for i, b in enumerate(media_blocks):
            kind = str(b.get("kind") or "").strip().lower()
            role = intro_label if i < 4 else (process_label if i < min(12, total_blocks) else output_label)
            if kind == "video":
                src = str(b.get("src") or "").strip()
                if src:
                    stages.append(_embed_stage(src, i == 0, role))
            elif kind == "text":
                txt = esc(str(b.get("text") or "").strip()).replace("\n", "<br>")
                if txt:
                    stages.append(f'<div class="proj-text-block">{txt}</div>')
            else:
                src = str(b.get("src") or "").strip()
                if src:
                    stages.append(_image_stage(src, i, total_blocks, "eager" if i == 0 else "lazy"))
        proj_media = _collapse(stages)
    else:
        media_parts = []
        media_index = 0
        if image_url:
            media_parts.append(_image_stage(image_url, media_index, max(1, len(gallery_images)), "eager"))
            media_index += 1
        for gallery_image in gallery_images:
            if gallery_image != image_url:
                if gallery_image.lower().endswith((".mp4", ".webm")):
                    media_parts.append(_embed_stage(gallery_image, False, "프로젝트 영상"))
                else:
                    media_parts.append(_image_stage(gallery_image, media_index, max(1, len(gallery_images)), "lazy"))
                media_index += 1
        embed_urls = video_urls or ([video_url] if video_url else [])
        for embed_url in embed_urls:
            media_parts.append(_embed_stage(embed_url, False, "프로젝트 영상"))
        proj_media = _collapse(media_parts)

    case_study_html = ""
    if case_study and not archive_only:
        case_sections = "".join(f'<div class="case-detail-item"><span class="case-detail-label">{esc(x.get("label", ""))}</span><p>{esc(x.get("text", ""))}</p></div>' for x in case_study.get("sections", []))
        case_study_html = f'''<section class="project-case-study"><div class="wrap"><p class="eyebrow">CASE STUDY</p><h2>{esc(case_study.get("title", display_title))}</h2><p class="case-detail-summary">{esc(case_study.get("summary", ""))}</p><div class="case-detail-grid">{case_sections}</div><a class="project-contact-cta" href="/#brief">프로젝트 브리프 작성 ↗</a></div></section>'''

    items = [x for x in d["work"]["items"] if x.get("slug")]
    idx = next((i for i, x in enumerate(items) if x["slug"] == slug), 0)
    prev_item = items[idx - 1] if idx > 0 else None
    next_item = items[idx + 1] if idx < len(items) - 1 else None
    def _project_label(item: dict) -> str:
        return item.get("display_title") or (f'{item["client"]} \u2014 {item["name"]}' if item.get("name") else item["client"])

    prev_label = _project_label(prev_item) if prev_item else ""
    next_label = _project_label(next_item) if next_item else ""
    prev_link = (
        f'<a class="proj-nav-link" href="/projects/{prev_item["slug"]}/">'
        f'\u2190 {esc(prev_label)}</a>'
    ) if prev_item else '<span></span>'
    next_link = (
        f'<a class="proj-nav-link" href="/projects/{next_item["slug"]}/">'
        f'{esc(next_label)} \u2192</a>'
    ) if next_item else '<span></span>'
    project_social_image = absolute_asset_url(s, image_url or (gallery_images[0] if gallery_images else "") or "/og-default.svg")
    if project_type == "archive":
        related_cards = "".join(
            f'<a class="related-project-card" href="/projects/{item["slug"]}/">'
            f'<span class="related-project-type">{esc(item.get("category", "PROJECT"))}</span>'
            f'<strong>{esc(_project_label(item))}</strong><span>상세 보기 ↗</span></a>'
            for item in (prev_item, next_item) if item
        )
        related_html = (f'<section class="project-related"><div class="wrap"><p class="eyebrow">'
                        f'{esc(t.get("related_projects", "관련 프로젝트"))}</p><div class="related-project-grid">'
                        f'{related_cards}</div></div></section>' if related_cards else "")
        project_nav_html = ""
    else:
        related_html = ""
        project_nav_html = f'<div class="wrap"><nav class="proj-nav">{prev_link}{next_link}</nav></div>'

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
<meta name="robots" content="index,follow" />
<link rel="canonical" href="{esc(url)}" />
<meta property="og:type" content="article" />
<meta property="og:site_name" content="{esc(s["name"])}" />
<meta property="og:url" content="{esc(url)}" />
<meta property="og:title" content="{esc(title)}" />
<meta property="og:description" content="{esc(desc)}" />
<meta property="og:locale" content="{esc(s["locale"])}" />
<meta property="og:image" content="{esc(project_social_image)}" />
<meta property="og:image:alt" content="{esc(title)}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:image" content="{esc(project_social_image)}" />
<meta name="twitter:title" content="{esc(title)}" />
<meta name="twitter:description" content="{esc(desc)}" />
<meta name="twitter:image:alt" content="{esc(title)}" />
<script type="application/ld+json">
{build_project_jsonld(d, w)}
</script>
<style>{CSS}
.proj-hero{{padding:clamp(68px,7vw,96px) 0 clamp(24px,3vw,40px)!important}}
.proj-hero .wrap{{display:grid;grid-template-columns:minmax(0,.85fr) minmax(320px,1.15fr);
  gap:clamp(36px,7vw,104px);align-items:end}}
.proj-hero.project-type-archive .wrap{{grid-template-columns:1fr;align-items:start}}
.proj-main{{grid-column:1;min-width:0}}
.proj-hero .eyebrow{{margin-bottom:18px}}
.proj-client{{margin:0;font-size:clamp(46px,7vw,104px)!important;line-height:.9!important;
  letter-spacing:-.06em!important;font-weight:300!important}}
.project-type-archive .proj-client{{font-size:clamp(42px,6vw,82px)!important}}
.proj-meta{{display:flex;flex-wrap:wrap;gap:8px 14px;margin-top:22px;color:#666;font-family:var(--font-mono);font-size:10px;letter-spacing:.08em}}
.proj-name,.proj-ctx,.proj-year,.proj-category{{display:inline-block}}
.proj-year.is-unknown{{color:#999}}
.proj-summary{{grid-column:2;align-self:end;min-width:0}}
.project-type-archive .proj-summary{{grid-column:1;margin-top:30px}}
.proj-desc{{margin:0!important;max-width:48ch!important;
  font-size:clamp(15px,1.45vw,19px)!important;line-height:1.75!important;word-break:keep-all}}
.project-facts{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1px;background:var(--line);margin:28px 0 0;max-width:560px}}
.project-facts>div{{background:var(--bg);padding:12px 14px;min-width:0}}
.project-facts dt{{font-family:var(--font-mono);font-size:10px;letter-spacing:.08em;color:var(--text-faint)}}
.project-facts dd{{margin:6px 0 0;font-size:13px;line-height:1.45;word-break:keep-all}}
.project-actions{{display:flex;align-items:center;gap:18px;flex-wrap:wrap;margin-top:30px}}
.back-link{{margin-top:0!important}}
.project-contact-cta{{display:inline-block;padding:10px 14px;background:#050505;color:#fff;font-size:12px;letter-spacing:.02em}}
.project-contact-cta:hover{{background:#333}}
.project-source-link{{display:inline-block;font-size:12px;color:inherit;text-decoration:underline;text-underline-offset:4px}}
.project-source-link:hover{{opacity:.65}}
.proj-media-wrap{{max-width:1720px;margin:clamp(-28px,-2vw,-12px) auto 0;padding:0 var(--v2-pad);position:relative;z-index:1;display:flex;flex-direction:column;gap:clamp(16px,2vw,28px)}}
.proj-media-stage{{position:relative;width:100%;background:#ececea;overflow:hidden}}
.proj-media-stage img{{width:100%;height:auto;object-fit:contain;display:block;background:#ececea}}
.proj-media-stage.is-video{{aspect-ratio:16/9}}
.proj-media-stage.is-video video{{width:100%;height:100%;object-fit:cover;display:block}}
.proj-media-stage iframe{{position:absolute;inset:0;width:100%;height:100%;border:0}}
.media-chapter{{display:flex;flex-direction:column;gap:14px}}
.media-chapter-label{{margin:0;font-family:var(--font-mono);font-size:10px;letter-spacing:.14em;color:#777;text-transform:uppercase}}
.media-chapter-list{{display:flex;flex-direction:column;gap:clamp(16px,2vw,28px)}}
.proj-text-block{{max-width:68ch;margin:0 auto;padding:clamp(20px,3vw,36px);background:#f4f4f2;font-size:clamp(15px,1.45vw,19px);line-height:1.8;word-break:keep-all}}
.proj-media-empty{{height:100%;display:flex;align-items:flex-end;padding:clamp(24px,4vw,56px);
  background:#111;color:#fff;font-size:clamp(30px,5vw,72px);font-weight:300;letter-spacing:-.05em}}
.project-related{{padding:clamp(64px,8vw,112px) 0 0}}
.related-project-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1px;background:var(--line)}}
.related-project-card{{display:flex;flex-direction:column;gap:12px;padding:24px;background:var(--bg);color:inherit;min-height:150px}}
.related-project-card strong{{font-size:clamp(18px,2vw,28px);font-weight:400;letter-spacing:-.035em}}
.related-project-card span:last-child{{margin-top:auto;font-size:12px;color:var(--text-muted)}}
.related-project-type{{font-family:var(--font-mono);font-size:10px;letter-spacing:.12em;color:var(--text-faint)}}
.proj-nav{{margin-top:clamp(58px,8vw,110px)!important;padding:30px 0!important}}
.proj-nav-link{{font-size:13px!important}}
@media(max-width:900px){{
  .proj-hero .wrap{{grid-template-columns:1fr;gap:0}}
  .proj-main,.proj-summary{{grid-column:1}}
  .proj-summary{{margin-top:30px}}
  .project-actions{{margin-top:26px}}
  .proj-media-wrap{{margin-top:0}}
}}</style>
<link rel="stylesheet" href="/theme-v2.css?v={BUILD_VERSION}" />
{ANALYTICS_TAGS}
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
  <section class="proj-hero project-type-{project_type}">
    <div class="wrap">
      <div class="proj-main">
        <p class="eyebrow">{esc(project_eyebrow)}</p>
        <h1 class="proj-client">{esc(hero_title)}</h1>
        <div class="proj-meta">{category_html}{f'<span class="proj-name">{esc(w["name"])}</span>' if w.get("name") else ""}{ctx_html}{year_html}</div>
        <div class="project-actions">
          <a class="back-link" href="/#work">\u2190 {esc(t["nav_work"])}</a>
          {contact_cta}
          {source_cta}
        </div>
      </div>
      <div class="proj-summary">{desc_html}{project_facts_html}</div>
    </div>
  </section>

  <div class="proj-media-wrap">
    {proj_media}
  </div>

  {case_study_html}

  {related_html}
  {project_nav_html}

</main>

<footer class="site">
  <div class="wrap">
    <div class="foot-copy">\u00a9 {date.today().year} {esc(s["name"])} · <a href="/privacy">개인정보 처리 안내</a></div>
  </div>
</footer>
</body>
</html>
"""



def build_privacy_html(d: dict, locales: list) -> str:
    s = d["site"]
    p = d.get("privacy", {})
    items = "".join(
        f'<section class="privacy-item"><h2>{esc(item.get("title", ""))}</h2><p>{esc(item.get("body", ""))}</p></section>'
        for item in p.get("items", [])
    )
    canonical = s["url"] + "privacy"
    return f"""<!DOCTYPE html>
<html lang="{s["lang"]}">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<link rel="icon" href="/favicon.svg" type="image/svg+xml" />
<title>{esc(p.get("title", "개인정보 처리 안내"))} | {esc(s["name"])}</title>
<meta name="description" content="{esc(p.get("description", ""))}" />
<link rel="canonical" href="{esc(canonical)}" />
<meta property="og:type" content="website" />
<meta property="og:site_name" content="{esc(s["name"])}" />
<meta property="og:url" content="{esc(canonical)}" />
<meta property="og:title" content="{esc(p.get("title", "개인정보 처리 안내"))} | {esc(s["name"])}" />
<meta property="og:description" content="{esc(p.get("description", ""))}" />
<meta property="og:image" content="{esc(absolute_asset_url(s, "/og-default.svg"))}" />
<link rel="stylesheet" href="/theme-v2.css?v={BUILD_VERSION}" />
{ANALYTICS_TAGS}
<style>
.privacy-page{{max-width:820px;margin:0 auto;padding:clamp(120px,14vw,200px) clamp(20px,4vw,48px) 120px}}
.privacy-page h1{{font-size:clamp(36px,5vw,64px);font-weight:300;letter-spacing:-.05em;line-height:1.05}}
.privacy-lead{{margin-top:24px;font-size:clamp(16px,1.5vw,20px);line-height:1.8;color:var(--text-muted)}}
.privacy-item{{border-top:1px solid var(--line);padding:28px 0}}
.privacy-item:first-of-type{{margin-top:64px}}
.privacy-item h2{{font-size:20px;font-weight:400}}
.privacy-item p{{margin-top:12px;max-width:70ch;font-size:15px;line-height:1.8;color:var(--text-muted)}}
.privacy-back{{display:inline-block;margin-top:42px;text-decoration:underline;text-underline-offset:4px}}
</style>
</head>
<body>
<a class="skip" href="#main">본문으로 건너뛰기</a>
<header class="site"><div class="wrap hdr"><a class="logo" href="/">{esc(s["name"])}</a></div></header>
<main id="main"><article class="privacy-page"><p class="eyebrow">INFORMATION</p><h1>{esc(p.get("title", "개인정보 처리 안내"))}</h1><p class="privacy-lead">{esc(p.get("intro", ""))}</p>{items}<a class="privacy-back" href="/">SIA.HAUS 홈으로 돌아가기 ↗</a></article></main>
<footer class="site"><div class="wrap"><div class="foot-copy">© {date.today().year} {esc(s["name"])}</div></div></footer>
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

    if d.get("services"):
        lines += ["## 서비스", ""]
        for service in d["services"]:
            lines += [f'### {service["title"]}', "", service["description"], f'- URL: {s["url"]}services/{service["slug"]}', ""]

    lines += [f'## {d["work"]["title"]}', "", d["work"]["lead"], ""]
    for w in d["work"]["items"]:
        bits = [b for b in (w["name"], w["context"], w["year"]) if b]
        lines.append(f'- {w["client"]} — ' + " · ".join(bits))
    lines.append("")

    if d.get("case_studies", {}).get("items"):
        lines += [f'## {d["case_studies"]["title"]}', "", d["case_studies"].get("lead", ""), ""]
        for c in d["case_studies"]["items"]:
            lines.append(f'### {c["title"]}')
            lines += ["", c.get("summary", "")]
            for part in c.get("sections", []):
                lines.append(f'- **{part["label"]}** — {part["text"]}')
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
        for m in re.finditer(r'<script(?![^>]*type="application/ld\+json")(?![^>]*src="/_vercel/insights/script\.js")(?![^>]*src="/site-analytics\.js(?:\?[^\"]*)?")[^>]*>', doc):
            raise SystemExit(f"실행 스크립트가 들어갔습니다: {m.group(0)}")

        out[path + "index.html"] = doc
        out[path + "llms.txt"] = build_llms(d, launched)
        out[path + "privacy/index.html"] = build_privacy_html(d, locales)

        # 서비스별 SEO 랜딩 페이지 생성
        for service in d.get("services", []):
            service_doc = build_service_html(d, service)
            for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', service_doc, re.S):
                json.loads(m.group(1))
            out[path + f'services/{service["slug"]}/index.html'] = service_doc

        # 프로젝트 상세 페이지 생성
        for w in d["work"]["items"]:
            if not w.get("slug"):
                continue
            proj_doc = build_project_html(d, w, locales, launched)
            # JSON-LD 검증 (도입하면)
            for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', proj_doc, re.S):
                json.loads(m.group(1))
            for m in re.finditer(r'<script(?![^>]*type="application/ld\+json")(?![^>]*src="/_vercel/insights/script\.js")(?![^>]*src="/site-analytics\.js(?:\?[^\"]*)?")[^>]*>', proj_doc):
                raise SystemExit(f"실행 스크립트가 들어갔습니다: {m.group(0)}")
            out[path + f'projects/{w["slug"]}/index.html'] = proj_doc

    # sitemap 에 서비스·프로젝트 URL 포함
    service_urls = []
    project_urls = []
    for d2 in docs:
        for service2 in d2.get("services", []):
            service_urls.append(d2["site"]["url"] + "services/" + service2["slug"])

        case_by_slug2 = {c.get("slug"): c for c in d2.get("case_studies", {}).get("items", [])}
        for w2 in d2["work"]["items"]:
            if w2.get("slug"):
                project_urls.append(d2["site"]["url"] + "projects/" + w2["slug"] )
    out["sitemap.xml"] = build_sitemap(locales, today, project_urls + service_urls)

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
              f' · 실적 {len(d["work"]["items"])} · 서비스 {len(d.get("services", []))}'
              f' · FAQ {len(faq_items(d, launched))}')
    for w in dict.fromkeys(warnings):
        print(f"\n  ⚠️  {w}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

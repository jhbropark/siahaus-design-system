import React from "react";
import { wordmarkWhite } from "../slides/chrome.jsx";
import "./slide.css";
import "./templates.css";

/* SIA.HAUS — 8 generic, reusable slide templates, ported from project/slides/*.html.
   These are English specimen layouts (Cover, Exec Summary, Market, Case Study,
   Timeline, Budget, Proposal, KPI) — a starting kit distinct from the Korean
   왕송호수 proposal deck. Each is a standalone 1280×720 `.tslide` canvas. */

// 01 — Cover
function Cover() {
  return (
    <div className="tslide cover stage">
      <div className="photo" data-label="Full-bleed architecture / media facade — 16:9" />
      <div className="grain" />
      <div className="scrim-b" />
      <div className="top">
        <img src={wordmarkWhite} alt="sia.haus" />
        <span className="eyebrow">base on Seoul</span>
      </div>
      <div className="cover-content">
        <span className="eyebrow"><span className="mk">//</span>Proposal — 2026</span>
        <h1 className="title" style={{ marginTop: 22 }}>Technology is a tool.<br /><b>Experience is a sensation.</b></h1>
        <p className="lead sub">몰입형 미디어 경험을 통해 공간을 감각으로 전환합니다 — 미디어 파사드부터 프로젝션 매핑까지.</p>
      </div>
      <div className="s-foot">
        <span className="s-index">SIA.HAUS — IMMERSIVE MEDIA STUDIO</span>
        <span className="s-index">sia@sia.haus</span>
      </div>
    </div>
  );
}

// 02 — Executive Summary
function ExecutiveSummary() {
  return (
    <div className="tslide exec">
      <div className="s-head">
        <span className="eyebrow"><span className="mk">//</span>Executive Summary</span>
        <span className="s-index">01 / 08</span>
      </div>
      <div className="body">
        <h1 className="title">A decade of landmark media — from <b>Seoul Light</b> to the <b>Venice Biennale</b> — engineered as one continuous sensation.</h1>
      </div>
      <div className="stats">
        <div className="stat"><div className="lab">Track Record</div><div className="num">60+</div><div className="cap">Immersive installations delivered since 2018.</div></div>
        <div className="stat"><div className="lab">Largest Canvas</div><div className="num">819㎡</div><div className="cap">Lotte Jamsil media facade, 21m × 39m.</div></div>
        <div className="stat"><div className="lab">Global Stages</div><div className="num">4</div><div className="cap">Milan, Venice, Taipei, Seoul.</div></div>
      </div>
      <div className="s-foot">
        <img src={wordmarkWhite} alt="sia.haus" />
        <span className="s-index">sia@sia.haus</span>
      </div>
    </div>
  );
}

// 03 — Market Opportunity
function MarketOpportunity() {
  const rows = [
    ["Media Facade", "+18% CAGR", "82%", "var(--spectral-amber)"],
    ["Immersive Exhibition", "+24% CAGR", "94%", "var(--spectral-slate)"],
    ["Projection Mapping", "+14% CAGR", "66%", "var(--spectral-violet)"],
    ["Brand IP Experience", "+21% CAGR", "88%", "var(--spectral-sage)"],
  ];
  return (
    <div className="tslide mkt">
      <div className="s-head">
        <span className="eyebrow"><span className="mk">//</span>Market Opportunity</span>
        <span className="s-index">02 / 08</span>
      </div>
      <div className="grid">
        <div className="big">
          <div className="lab">Global DOOH spend, 2026E</div>
          <div className="num">$38<small>.4B</small></div>
          <p>Digital out-of-home is the fastest-growing ad medium — and immersive media art is its premium tier. SIA.HAUS operates where culture, architecture and brand converge.</p>
        </div>
        <div className="rows">
          {rows.map(([rl, rv, w, color], i) => (
            <div className="row" key={i}>
              <div className="rh"><span className="rl">{rl}</span><span className="rv">{rv}</span></div>
              <div className="track"><div className="fill" style={{ width: w, background: color }} /></div>
            </div>
          ))}
        </div>
      </div>
      <div className="s-foot">
        <img src={wordmarkWhite} alt="sia.haus" />
        <span className="s-index">Source — illustrative market estimate</span>
      </div>
    </div>
  );
}

// 04 — Case Study
function CaseStudy() {
  return (
    <div className="tslide cs stage">
      <div className="photo" data-label="Project hero — KIA, Journey of Reflection · Milan 2026" />
      <div className="grain" />
      <div className="scrim-l" />
      <div className="s-head">
        <span className="eyebrow"><span className="mk">//</span>Case Study</span>
        <span className="s-index">03 / 08</span>
      </div>
      <div className="panel">
        <span className="eyebrow" style={{ color: "var(--text-subtle)" }}>Milan Design Week · 2026</span>
        <h1 className="title">Journey of <b>Reflection</b></h1>
        <p>‘Opposites United’ 브랜드 철학을 공간 경험으로 구현한 기아의 EV 비전 전시. 빛·소재·건축 구조를 활용한 몰입형 전시로 차세대 모빌리티 비전을 전달했습니다.</p>
        <div className="meta">
          <div><div className="k">Client</div><div className="v">KIA</div></div>
          <div><div className="k">Agency</div><div className="v">sonolee</div></div>
          <div><div className="k">Scope</div><div className="v">Immersive Exhibition</div></div>
        </div>
        <div className="tags"><span className="tg">Media Art</span><span className="tg">Projection</span><span className="tg">Sound Design</span></div>
      </div>
      <div className="s-foot">
        <img src={wordmarkWhite} alt="sia.haus" />
        <span className="s-index">sia@sia.haus</span>
      </div>
    </div>
  );
}

// 05 — Timeline
function Timeline() {
  const cols = [
    ["2026", false, [["Journey of Reflection", "KIA · Milan"], ["History Walk, NLC", "LG"]]],
    ["2025", false, [["Time for Trees", "Venice Biennale"], ["Heritage Lounge", "FILA Holdings"]]],
    ["2024", false, [["Entropy of Nature", "The Hyundai Seoul"], ["‘Lucky’ MV Visual", "SM · RIIZE"]]],
    ["2023", true, [["Seoul Light Gwanghwa", "Seoul City"], ["Jamsil Media Facade", "Lotte"]]],
    ["2018→", true, [["Love Alarm Zone", "Netflix"], ["LUX Soundroom", "Samsung"]]],
  ];
  return (
    <div className="tslide tl">
      <div className="s-head">
        <span className="eyebrow"><span className="mk">//</span>Selected Track Record</span>
        <span className="s-index">04 / 08</span>
      </div>
      <div className="wrap">
        <div className="track">
          <div className="line" />
          {cols.map(([yr, muted, items], i) => (
            <div className={`col${muted ? " muted" : ""}`} key={i}>
              <div className="yr">{yr}</div>
              <div className="dot" />
              <div className="items">
                {items.map(([p, c], j) => (
                  <div className="it" key={j}><div className="p">{p}</div><div className="c">{c}</div></div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className="s-foot">
        <img src={wordmarkWhite} alt="sia.haus" />
        <span className="s-index">2018 — 2026</span>
      </div>
    </div>
  );
}

// 06 — Budget
function Budget() {
  const rows = [
    ["Production & Engineering", "₩344M", "42%", "var(--spectral-amber)"],
    ["Hardware & LED", "₩254M", "31%", "var(--spectral-slate)"],
    ["Creative & Content", "₩131M", "16%", "var(--spectral-violet)"],
    ["Operations & Install", "₩90M", "11%", "var(--spectral-sage)"],
  ];
  return (
    <div className="tslide bg">
      <div className="s-head">
        <span className="eyebrow"><span className="mk">//</span>Budget — Phase 1</span>
        <span className="s-index">05 / 08</span>
      </div>
      <div className="grid">
        <div className="total">
          <div className="lab">Total Investment</div>
          <div className="num">₩<b>819</b>M</div>
          <p>Fixed-scope estimate across production, hardware, creative and operations. Excludes VAT and venue fees.</p>
        </div>
        <div className="rows">
          {rows.map(([rl, amt, pct, color], i) => (
            <div className="row" key={i}>
              <div className="rh"><span className="rl">{rl}</span><span className="rv">{amt}<small>{pct}</small></span></div>
              <div className="track"><div className="fill" style={{ width: pct, background: color }} /></div>
            </div>
          ))}
        </div>
      </div>
      <div className="s-foot">
        <img src={wordmarkWhite} alt="sia.haus" />
        <span className="s-index">Figures illustrative</span>
      </div>
    </div>
  );
}

// 07 — Proposal
function Proposal() {
  const phases = [
    ["01", "Planning", "Synopsis, conception, alignment. Defining the sensory thesis and spatial narrative.", "Weeks 1–3"],
    ["02", "Pre-Production", "Design, simulation, technical alignment. Hardware spec and content storyboards.", "Weeks 4–8"],
    ["03", "Production", "Media A/V, projection mapping, sound design and on-site integration at scale.", "Weeks 9–16"],
    ["04", "Operation", "Commissioning, CMS handover, and sustainable operation toward IP business.", "Ongoing"],
  ];
  return (
    <div className="tslide pr">
      <div className="s-head">
        <span className="eyebrow"><span className="mk">//</span>Proposed Approach</span>
        <span className="s-index">06 / 08</span>
      </div>
      <div className="intro">
        <h1 className="title">From concept to <b>continuous operation</b> — one integrated team across the full pipeline.</h1>
      </div>
      <div className="phases">
        {phases.map(([n, h, p, d], i) => (
          <div className="ph" key={i}>
            <div className="n">{n}</div><h3>{h}</h3><p>{p}</p><div className="d">{d}</div>
          </div>
        ))}
      </div>
      <div className="s-foot">
        <img src={wordmarkWhite} alt="sia.haus" />
        <span className="s-index">PLANNING · PRE · MAIN · POST</span>
      </div>
    </div>
  );
}

// 08 — KPI Dashboard
function KPIDashboard() {
  const cells = [
    ["Total Impressions", "12.4M", "up", "↑ 38%", "vs. forecast", false],
    ["Dwell Time", "4:12", "up", "↑ 1:08", "avg. per visitor", true],
    ["Social Reach", "8.9M", "up", "↑ 52%", "earned media", false],
    ["Footfall", "214K", "up", "↑ 19%", "on-site visitors", false],
    ["Cost / Impression", "₩66", "dn", "↓ 24%", "efficiency gain", false],
    ["Brand Recall", "87%", "up", "↑ 12pt", "exit survey", false],
  ];
  return (
    <div className="tslide kpi">
      <div className="s-head">
        <span className="eyebrow"><span className="mk">//</span>Performance — Campaign Window</span>
        <span className="s-index">07 / 08</span>
      </div>
      <div className="grid">
        {cells.map(([lab, num, dir, delta, cap, accent], i) => (
          <div className={`cell${accent ? " accent" : ""}`} key={i}>
            <div className="lab">{lab}</div>
            <div className="num">{num}</div>
            <div className="foot"><span className={`delta ${dir}`}>{delta}</span><span className="cap">{cap}</span></div>
          </div>
        ))}
      </div>
      <div className="s-foot">
        <img src={wordmarkWhite} alt="sia.haus" />
        <span className="s-index">Figures illustrative</span>
      </div>
    </div>
  );
}

export const TEMPLATES = [
  { id: "01-cover", name: "01 — Cover", subtitle: "Full-bleed hero. One-line statement, thin display type.", Component: Cover },
  { id: "02-exec", name: "02 — Executive Summary", subtitle: "Lead statement + three supporting metrics.", Component: ExecutiveSummary },
  { id: "03-market", name: "03 — Market Opportunity", subtitle: "Hero metric left, supporting trend + bars right.", Component: MarketOpportunity },
  { id: "04-case", name: "04 — Case Study", subtitle: "Full-bleed image, left scrim, client/agency lower-third.", Component: CaseStudy },
  { id: "05-timeline", name: "05 — Timeline", subtitle: "Horizontal track of years, projects as nodes.", Component: Timeline },
  { id: "06-budget", name: "06 — Budget", subtitle: "Total figure + line-item breakdown bars.", Component: Budget },
  { id: "07-proposal", name: "07 — Proposal", subtitle: "Phased approach — numbered scope across a process.", Component: Proposal },
  { id: "08-kpi", name: "08 — KPI Dashboard", subtitle: "Metric grid — outcomes at a glance.", Component: KPIDashboard },
];

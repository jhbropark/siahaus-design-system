import React from "react";
import { Kicker, PageNo, FootMark, wordmarkWhite } from "./chrome.jsx";

/* SIA.HAUS — 왕송호수 레일바이크 야간 미디어아트 도입 제안.
   15 premium dark slides, ported pixel-for-pixel from the design bundle.
   Korean body + English mono kickers, champagne accent, spectral data colors. */

const MONO = "var(--font-mono)";
const DISPLAY = "var(--font-display)";

// 01 — COVER
function Cover() {
  return (
    <div className="slide" style={{ background: "var(--ink-900)" }}>
      <div className="backdrop" style={{ background: "radial-gradient(135% 105% at 72% 0%, #1d222a 0%, #12151a 46%, #0a0b0d 100%)" }} />
      <div className="grain" />
      <div className="backdrop" style={{ background: "var(--scrim-bottom)" }} />
      <img src={wordmarkWhite} alt="sia.haus" style={{ position: "absolute", top: 58, left: 80, height: 20 }} />
      <div style={{ position: "absolute", top: 60, right: 80, fontFamily: MONO, fontSize: 12, fontWeight: 500, letterSpacing: ".26em", textTransform: "uppercase", color: "var(--accent)" }}>base on Seoul</div>
      <div style={{ position: "absolute", left: 80, bottom: 116, right: 80 }}>
        <div style={{ fontFamily: MONO, fontSize: 12, fontWeight: 500, letterSpacing: ".26em", textTransform: "uppercase", color: "var(--accent)" }}>
          <span style={{ opacity: 0.6, marginRight: 8 }}>//</span>Pre-Proposal · 사전 제안서
        </div>
        <h1 style={{ fontFamily: DISPLAY, fontWeight: 200, fontSize: 74, lineHeight: 1.04, letterSpacing: "-.03em", color: "var(--text-strong)", margin: "22px 0 0" }}>
          왕송호수 레일바이크<br /><b style={{ fontWeight: 600 }}>야간 미디어아트 도입 제안</b>
        </h1>
        <p style={{ fontFamily: "var(--font-body)", fontWeight: 300, fontSize: 22, lineHeight: 1.5, color: "var(--accent-soft)", margin: "24px 0 0", letterSpacing: "-.01em" }}>
          “이동하며 체험하는, 상시형 인터랙티브 야간 미디어 호수.”
        </p>
      </div>
      <div style={{ position: "absolute", bottom: 38, left: 80, fontFamily: MONO, fontSize: 11, letterSpacing: ".12em", textTransform: "uppercase", color: "var(--text-subtle)" }}>대상 — 의왕시 · 의왕도시공사</div>
      <div style={{ position: "absolute", bottom: 38, right: 80, fontFamily: MONO, fontSize: 11, letterSpacing: ".12em", color: "var(--text-subtle)" }}>협의 · 파일럿 제안용</div>
    </div>
  );
}

// 02 — EXECUTIVE SUMMARY
function Summary() {
  const rows = [
    ["문제 / Problem", <>4.3km 호수 순환·철새 습지라는 강한 자산에도, 콘텐츠가 <b style={{ fontWeight: 600, color: "var(--text-strong)" }}>주간·정적</b>에 머물러 야간 체류와 재방문 동력이 없다.</>],
    ["해법 / Solution", <>수면·철새 정체성·기존 미디어 인프라를 결합한 <b style={{ fontWeight: 600, color: "var(--text-strong)" }}>인터랙티브 야간 미디어아트 코스</b>로 전환. ‘보는 빛’이 아니라 ‘타고 들어가 반응하는’ 미디어아트.</>],
    ["차별성 / Edge", <>이동 동선(레일) + 수면 + 철새 서사 + 미디어 인프라의 조합은 국내에 <b style={{ fontWeight: 600, color: "var(--text-strong)" }}>직접 경쟁자가 사실상 없다.</b></>],
    ["요청 / Ask", <>전면 투자가 아니라 <b style={{ fontWeight: 600, color: "var(--text-strong)" }}>1구간·1시즌 파일럿</b>과, 이를 위한 데이터 공유·협의를 요청한다.</>],
  ];
  return (
    <div className="slide">
      <Kicker>Executive Summary — 한 장 요약</Kicker>
      <PageNo n={1} />
      <div style={{ position: "absolute", left: 80, right: 80, top: 150, bottom: 110, display: "flex", flexDirection: "column", justifyContent: "center" }}>
        {rows.map(([label, body], i) => (
          <div key={i} style={{ display: "grid", gridTemplateColumns: "170px 1fr", gap: 28, padding: "22px 0", borderTop: "1px solid var(--line)", ...(i === rows.length - 1 ? { borderBottom: "1px solid var(--line)" } : {}) }}>
            <div style={{ fontFamily: MONO, fontSize: 12, letterSpacing: ".14em", textTransform: "uppercase", color: "var(--accent)" }}>{label}</div>
            <div style={{ fontSize: 19, fontWeight: 300, lineHeight: 1.5, color: "var(--text)" }}>{body}</div>
          </div>
        ))}
      </div>
      <FootMark />
      <div style={{ position: "absolute", bottom: 38, right: 80, fontFamily: MONO, fontSize: 11, letterSpacing: ".1em", color: "var(--text-subtle)" }}>기대효과 — 야간 관광·체류 증대, 장소 브랜딩 강화</div>
    </div>
  );
}

// 03 — ASSETS
function Assets() {
  const items = [
    ["01", "선형 캔버스", "호수를 따라 약 4.3km, 6개 테마 존의 능동적 이동 동선 — 레일바이크."],
    ["02", "자연 배경", "수도권 최대급 인공 생태습지, 50종에 이르는 철새가 찾는 호수 수면."],
    ["03", "기존 미디어", "‘미디어 스케치북’·‘팝업뮤지엄’ 철새 조형물, 꽃터널, 다수 포토존."],
    ["04", "연계 인프라", "철도박물관·조류생태과학관·캠핑장·카페 등 체류형 클러스터."],
  ];
  return (
    <div className="slide">
      <Kicker>Background — 갖춘 자산</Kicker>
      <PageNo n={2} />
      <h1 style={{ position: "absolute", left: 80, top: 138, fontFamily: DISPLAY, fontWeight: 300, fontSize: 48, letterSpacing: "-.02em", color: "var(--text-strong)", margin: 0 }}>
        이미 갖춘 <b style={{ fontWeight: 600 }}>네 가지 자산</b>
      </h1>
      <div style={{ position: "absolute", left: 80, right: 80, bottom: 118, display: "grid", gridTemplateColumns: "repeat(4,1fr)", borderTop: "1px solid var(--line)" }}>
        {items.map(([no, title, body], i) => (
          <div key={i} style={{ padding: i === 0 ? "30px 28px 0 0" : i === 3 ? "30px 0 0 28px" : "30px 28px 0 28px", borderLeft: "1px solid var(--line)" }}>
            <div style={{ fontFamily: MONO, fontSize: 12, letterSpacing: ".16em", color: "var(--accent)" }}>{no}</div>
            <h3 style={{ fontFamily: DISPLAY, fontSize: 21, fontWeight: 600, color: "var(--text-strong)", margin: "14px 0 0", letterSpacing: "-.01em" }}>{title}</h3>
            <p style={{ fontSize: 14, lineHeight: 1.55, color: "var(--text-subtle)", margin: "12px 0 0" }}>{body}</p>
          </div>
        ))}
      </div>
      <FootMark />
    </div>
  );
}

// 04 — MARKET
function Market() {
  return (
    <div className="slide">
      <Kicker>Market — 야간경제의 부상</Kicker>
      <PageNo n={3} />
      <div style={{ position: "absolute", left: 80, right: 240, top: 0, bottom: 0, display: "flex", flexDirection: "column", justifyContent: "center" }}>
        <h1 style={{ fontFamily: DISPLAY, fontWeight: 300, fontSize: 56, lineHeight: 1.12, letterSpacing: "-.02em", color: "var(--text-strong)", margin: 0, maxWidth: 760 }}>
          야간관광은 이제 공공 관광시설의 <b style={{ fontWeight: 600 }}>새로운 표준</b>이다.
        </h1>
        <p style={{ fontSize: 20, fontWeight: 300, lineHeight: 1.6, color: "var(--text-muted)", margin: "30px 0 0", maxWidth: 660 }}>
          야간경제 수요 확대, 미디어아트 기반 체험형 관광의 대중화, 그리고 ‘반복 관람’을 전제로 한 콘텐츠 운영. 왕송호수는 이 흐름을 적용하기에 <b style={{ fontWeight: 500, color: "var(--text)" }}>입지·자산이 모두 준비된 드문 사례</b>다.
        </p>
      </div>
      <FootMark />
    </div>
  );
}

// 05 — BENCHMARKING
function Benchmarking() {
  const head = ["", "운영 방식", "미디어 수준", "핵심 시사점"];
  const rows = [
    { subject: true, cells: [<>왕송호수 <span style={{ fontFamily: MONO, fontSize: 10, color: "var(--text-subtle)", letterSpacing: ".1em" }}>대상</span></>, "상시 · 주간 중심", ["기초 인터랙티브 · 정적", "var(--spectral-rose)"], "인프라·정체성은 충분, 야간·수면·미디어가 공백"] },
    { cells: ["여수 해양레일바이크", "상시 · 주간 중심", ["패시브 LED 터널", "var(--spectral-rose)"], "‘레일+빛터널’은 정적 조명일 뿐 — 추월 여지"] },
    { cells: ["아침고요 별빛정원전", "계절 한정 야간", ["대규모 정적 라이트 · 연못 반사", null], "야간을 독립 프리미엄 상품화, 반사를 핵심 장치로"] },
    { cells: ["대구 수성못 빛예술제", "이벤트 · 무료", ["미디어아트+드론+인터랙티브", "var(--spectral-sage)"], "호수+산책로의 미디어아트화 — 가장 가까운 모델"] },
    { last: true, cells: ["한강 드론라이트쇼", "시즌제 · 무료", ["1,200~2,000대 드론 · IP", "var(--spectral-sage)"], "수면 위 군무 스케일 · IP 협업 (철새 군무 참조)"] },
  ];
  const th = { textAlign: "left", padding: "0 16px 12px", fontFamily: MONO, fontSize: 11, letterSpacing: ".12em", textTransform: "uppercase", color: "var(--text-subtle)", fontWeight: 500 };
  return (
    <div className="slide">
      <Kicker>Benchmarking — 경쟁 지형</Kicker>
      <PageNo n={4} />
      <h1 style={{ position: "absolute", left: 80, top: 132, fontFamily: DISPLAY, fontWeight: 300, fontSize: 42, letterSpacing: "-.02em", color: "var(--text-strong)", margin: 0 }}>
        네 개의 축으로 본 <b style={{ fontWeight: 600 }}>경쟁 지형</b>
      </h1>
      <table style={{ position: "absolute", left: 80, right: 80, top: 208, borderCollapse: "collapse", width: "calc(100% - 160px)", fontFamily: "var(--font-body)" }}>
        <thead>
          <tr>
            <th style={{ ...th, padding: "0 0 12px", width: "24%" }}>{head[0]}</th>
            <th style={{ ...th, width: "18%" }}>{head[1]}</th>
            <th style={{ ...th, width: "24%" }}>{head[2]}</th>
            <th style={{ ...th, padding: "0 0 12px" }}>{head[3]}</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => {
            const topBorder = r.subject ? "1px solid var(--accent-deep)" : "1px solid var(--line)";
            const cellBase = { padding: "16px", borderTop: topBorder, ...(r.last ? { borderBottom: "1px solid var(--line)" } : {}) };
            const [name, ops, [media, mediaColor], insight] = r.cells;
            return (
              <tr key={i} style={r.subject ? { background: "rgba(201,168,106,.08)" } : undefined}>
                <td style={{ ...cellBase, padding: "16px 14px", fontFamily: DISPLAY, fontSize: r.subject ? 16 : 15, fontWeight: r.subject ? 600 : 500, color: r.subject ? "var(--accent-soft)" : "var(--text-strong)" }}>{name}</td>
                <td style={{ ...cellBase, fontSize: 14, color: "var(--text-muted)" }}>{ops}</td>
                <td style={{ ...cellBase, fontSize: 14, color: mediaColor || "var(--text-muted)" }}>{media}</td>
                <td style={{ ...cellBase, padding: "16px 0 16px 14px", fontSize: 14, color: r.subject ? "var(--text)" : "var(--text-muted)" }}>{insight}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <FootMark style={{ bottom: 34 }} />
    </div>
  );
}

// 06 — INSIGHT
function Insight() {
  const cols = [
    ["수면 반사", "var(--spectral-slate)", "검증된 킬러 장치 — 상하 대칭으로 스케일을 두 배."],
    ["야간 상품화", "var(--spectral-amber)", "시간대 분리로 객단가를 끌어올린다."],
    ["철새 서사", "var(--spectral-sage)", "대체 불가능한 고유 IP의 원천."],
    ["이동 동선", "var(--spectral-violet)", "레일 위 통과 경험 — 직접 경쟁자 부재."],
  ];
  return (
    <div className="slide" style={{ background: "var(--ink-900)" }}>
      <Kicker>Insight — 도출</Kicker>
      <PageNo n={5} />
      <div style={{ position: "absolute", left: 80, right: 80, top: 172 }}>
        <h1 style={{ fontFamily: DISPLAY, fontWeight: 300, fontSize: 50, lineHeight: 1.16, letterSpacing: "-.02em", color: "var(--text-strong)", margin: 0, maxWidth: 920 }}>
          ‘빛’은 흔하지만, <b style={{ fontWeight: 600, color: "var(--accent)" }}>인터랙티브 미디어아트는 시장 공백</b>이다.
        </h1>
      </div>
      <div style={{ position: "absolute", left: 80, right: 80, bottom: 120, display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 32 }}>
        {cols.map(([label, color, body], i) => (
          <div key={i}>
            <div style={{ fontFamily: MONO, fontSize: 11, letterSpacing: ".12em", textTransform: "uppercase", color }}>{label}</div>
            <p style={{ fontSize: 15, lineHeight: 1.5, color: "var(--text-muted)", margin: "10px 0 0" }}>{body}</p>
          </div>
        ))}
      </div>
      <FootMark />
    </div>
  );
}

// 07 — SECTION DIVIDER
function ConceptDivider() {
  return (
    <div className="slide" style={{ background: "var(--ink-900)" }}>
      <div className="backdrop" style={{ background: "radial-gradient(120% 120% at 80% 100%, #1a1e24 0%, #0d0f12 50%, #08090a 100%)" }} />
      <div style={{ position: "absolute", left: 80, bottom: 120, right: 80 }}>
        <div style={{ fontFamily: MONO, fontSize: 13, fontWeight: 500, letterSpacing: ".28em", textTransform: "uppercase", color: "var(--accent)" }}>02 — Content Concept</div>
        <h1 style={{ fontFamily: DISPLAY, fontWeight: 200, fontSize: 96, lineHeight: 1, letterSpacing: "-.03em", color: "var(--text-strong)", margin: "24px 0 0" }}>
          콘텐츠 컨셉<br /><b style={{ fontWeight: 600 }}>· 포지셔닝</b>
        </h1>
      </div>
      <img src={wordmarkWhite} alt="sia.haus" style={{ position: "absolute", top: 60, left: 80, height: 18, opacity: 0.7 }} />
      <div style={{ position: "absolute", top: 62, right: 80, fontFamily: MONO, fontSize: 12, letterSpacing: ".1em", color: "var(--text-subtle)" }}>06 / 14</div>
    </div>
  );
}

// 08 — POSITIONING
function Positioning() {
  return (
    <div className="slide">
      <Kicker>Positioning</Kicker>
      <PageNo n={7} />
      <div style={{ position: "absolute", left: 80, right: 120, top: 0, bottom: 0, display: "flex", flexDirection: "column", justifyContent: "center" }}>
        <h1 style={{ fontFamily: DISPLAY, fontWeight: 300, fontSize: 58, lineHeight: 1.14, letterSpacing: "-.02em", color: "var(--text-strong)", margin: 0, maxWidth: 900 }}>
          이동하며 체험하는,<br /><b style={{ fontWeight: 600, color: "var(--accent)" }}>상시형 인터랙티브 야간 미디어 호수.</b>
        </h1>
        <p style={{ fontSize: 20, fontWeight: 300, lineHeight: 1.6, color: "var(--text-muted)", margin: "32px 0 0", maxWidth: 680 }}>
          4.3km 레일 동선 위에 호수·철새 서사를 입혀, 관람객이 <b style={{ fontWeight: 500, color: "var(--text)" }}>페달을 밟아 미디어아트 속을 통과</b>하게 한다.
        </p>
      </div>
      <FootMark />
    </div>
  );
}

// 09 — MODULES
function Modules() {
  const mods = [
    ["빛의 철새", "호수 수면 · 하늘", "var(--spectral-slate)", "철새 군무를 드론·수면 프로젝션으로 재현. 반사로 상하 대칭, 반환점에 클라이맥스."],
    ["달빛 호수", "호수 전면", "var(--spectral-sage)", "수면 캔버스 프로젝션·레이저. 계절(유채·연꽃·억새·결빙)별 콘텐츠 교체로 재방문 유도."],
    ["반응하는 레일", "터널 구간", "var(--spectral-rose)", "페달 속도에 반응하는 인터랙티브 라이트 터널+사운드. ‘이동하며 만드는’ 핵심 차별점."],
    ["사계의 습지", "조류생태존", "var(--spectral-amber)", "기존 조형물·팝업뮤지엄의 야간 미디어 버전. 갈대·연꽃·철새를 프로젝션 매핑으로."],
    ["야간 운영", "상품 구조", "var(--champagne-400)", "주간 레일+야간 미디어 이원화, 겨울 한정 빛축제, IP 타이업 회차 콘텐츠."],
  ];
  return (
    <div className="slide">
      <Kicker>Content Modules — 다섯 개의 장면</Kicker>
      <PageNo n={8} />
      <div style={{ position: "absolute", left: 80, right: 80, top: 0, bottom: 0, display: "flex", alignItems: "center" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(5,1fr)", gap: 16, width: "100%" }}>
          {mods.map(([title, zone, color, body], i) => (
            <div key={i} style={{ background: "var(--ink-700)", border: "1px solid var(--line)", borderRadius: 8, padding: "22px 18px", height: 300, display: "flex", flexDirection: "column" }}>
              <div style={{ width: 28, height: 3, background: color, borderRadius: 2 }} />
              <h3 style={{ fontFamily: DISPLAY, fontSize: 19, fontWeight: 600, color: "var(--text-strong)", margin: "18px 0 0" }}>{title}</h3>
              <div style={{ fontFamily: MONO, fontSize: 10, letterSpacing: ".1em", textTransform: "uppercase", color: "var(--text-subtle)", marginTop: 6 }}>{zone}</div>
              <p style={{ fontSize: 13, lineHeight: 1.55, color: "var(--text-subtle)", margin: "16px 0 0" }}>{body}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// 10 — REVENUE
function Revenue() {
  const bars = [
    ["보수 · 100대/일", "약 9억 원", "50%", "var(--spectral-slate)", false],
    ["중간 · 150대/일", "약 13억 원", "72%", "var(--spectral-amber)", false],
    ["적극 · 200대/일", "약 18억 원", "100%", "var(--champagne-400)", true],
  ];
  return (
    <div className="slide">
      <Kicker>Business Model — 매출 규모</Kicker>
      <PageNo n={9} />
      <div style={{ position: "absolute", left: 80, top: 170, width: 380 }}>
        <h1 style={{ fontFamily: DISPLAY, fontWeight: 300, fontSize: 40, lineHeight: 1.12, letterSpacing: "-.02em", color: "var(--text-strong)", margin: 0 }}>
          상품 이원화로<br /><b style={{ fontWeight: 600 }}>객단가를 분리</b>한다
        </h1>
        <p style={{ fontSize: 15, lineHeight: 1.6, color: "var(--text-subtle)", margin: "24px 0 0" }}>
          주간(기존 레일바이크)과 야간(미디어 코스)을 분리하고, 봄·가을 성수기와 겨울 빛축제로 비수기를 보완한다.
        </p>
      </div>
      <div style={{ position: "absolute", right: 80, top: 182, width: 600, display: "flex", flexDirection: "column", gap: 30 }}>
        {bars.map(([label, amount, w, color, hi], i) => (
          <div key={i}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 10 }}>
              <span style={{ fontFamily: MONO, fontSize: 13, letterSpacing: ".08em", textTransform: "uppercase", color: hi ? "var(--accent)" : "var(--text-muted)" }}>{label}</span>
              <span style={{ fontFamily: DISPLAY, fontSize: hi ? 26 : 22, fontWeight: hi ? 600 : 500, color: hi ? "var(--accent)" : "var(--text-strong)" }}>{amount}</span>
            </div>
            <div style={{ height: 7, background: "var(--ink-600)", borderRadius: 999, overflow: "hidden" }}>
              <div style={{ width: w, height: "100%", background: color, borderRadius: 999 }} />
            </div>
          </div>
        ))}
        <p style={{ fontFamily: MONO, fontSize: 11, lineHeight: 1.6, letterSpacing: ".02em", color: "var(--text-subtle)", margin: "4px 0 0" }}>
          가정 — 평균 객단가 3.2만원/대, 연 운영 280일. 실측은 정보공개로 확정 예정. 야간 회차·시즌 빛축제로 추가 매출 잠재.
        </p>
      </div>
      <FootMark />
    </div>
  );
}

// 11 — ROADMAP
function Roadmap() {
  const stages = [
    ["STAGE 00", "사전", "var(--text-subtle)", "var(--gray-600)", "데이터 확보(정보공개)·재개발 일정 확인·운영주체 협의."],
    ["STAGE 01", "파일럿", "var(--accent)", "var(--accent)", "1개 구간·1개 시즌 야간 미디어 시범 운영, 반응·매출 검증."],
    ["STAGE 02", "확장", "var(--accent)", "var(--accent)", "5개 모듈 단계 도입, 야간 전용 회차·계절 빛축제 정식화."],
    ["STAGE 03", "정착", "var(--accent)", "var(--accent)", "상시 운영·IP 회차 콘텐츠, (존치 시) 신규 단지 연계 랜드마크화."],
  ];
  return (
    <div className="slide">
      <Kicker>Roadmap — 단계적 추진</Kicker>
      <PageNo n={10} />
      <div style={{ position: "absolute", left: 80, right: 80, top: 0, bottom: 0, display: "flex", flexDirection: "column", justifyContent: "center" }}>
        <div style={{ position: "relative", display: "grid", gridTemplateColumns: "repeat(4,1fr)" }}>
          <div style={{ position: "absolute", left: 0, right: 0, top: 50, height: 1, background: "var(--line)" }} />
          {stages.map(([stage, name, labelColor, dotColor, body], i) => (
            <div key={i} style={{ position: "relative", paddingRight: i === 3 ? 0 : 28 }}>
              <div style={{ fontFamily: MONO, fontSize: 12, letterSpacing: ".14em", color: labelColor }}>{stage}</div>
              <div style={{ fontFamily: DISPLAY, fontSize: 30, fontWeight: 200, letterSpacing: "-.02em", color: "var(--text-strong)", marginTop: 6 }}>{name}</div>
              <div style={{ width: 11, height: 11, borderRadius: "50%", background: dotColor, margin: "26px 0 0", boxShadow: "0 0 0 5px var(--ink-850)", position: "relative", zIndex: 2 }} />
              <p style={{ fontSize: 14, lineHeight: 1.55, color: "var(--text-subtle)", margin: "26px 0 0" }}>{body}</p>
            </div>
          ))}
        </div>
      </div>
      <FootMark />
    </div>
  );
}

// 12 — RISK
function Risk() {
  const notes = [
    ["생태 저영향", "야생동물 저영향 조명·존 분리·점등 시간 제한."],
    ["야간 안전", "조도 기준, 비상 정지·구난 동선 재설계."],
    ["운영주체 협의", "시설(시·도시공사)과 운영(민간) 역할·수익 정의."],
  ];
  return (
    <div className="slide">
      <Kicker>Risk — 추진 전제</Kicker>
      <PageNo n={11} />
      <h1 style={{ position: "absolute", left: 80, top: 132, fontFamily: DISPLAY, fontWeight: 300, fontSize: 42, letterSpacing: "-.02em", color: "var(--text-strong)", margin: 0 }}>
        부지 재개발, <b style={{ fontWeight: 600 }}>정면으로 대응</b>한다
      </h1>
      <div style={{ position: "absolute", left: 80, right: 80, top: 212, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
        <div style={{ background: "var(--ink-700)", border: "1px solid var(--line)", borderRadius: 10, padding: "26px 28px" }}>
          <div style={{ fontFamily: MONO, fontSize: 11, letterSpacing: ".12em", textTransform: "uppercase", color: "var(--spectral-slate)" }}>A안 · 한시 활용</div>
          <p style={{ fontSize: 15, lineHeight: 1.6, color: "var(--text-muted)", margin: "14px 0 0" }}>잔여 운영 기간 내 저투자·시즌형 파일럿으로 빠르게 화제화. 철거 전 ‘한시 명소’로 자산화하고 운영 노하우·IP를 축적.</p>
        </div>
        <div style={{ background: "var(--ink-700)", border: "1px solid var(--line)", borderRadius: 10, padding: "26px 28px" }}>
          <div style={{ fontFamily: MONO, fontSize: 11, letterSpacing: ".12em", textTransform: "uppercase", color: "var(--spectral-rose)" }}>B안 · 신단지 연계</div>
          <p style={{ fontSize: 15, lineHeight: 1.6, color: "var(--text-muted)", margin: "14px 0 0" }}>공공주택지구 조성계획 단계에 호수 야간 미디어를 단지 정주환경·랜드마크 요소로 편입 제안 → 장기 존속 확보.</p>
        </div>
      </div>
      <div style={{ position: "absolute", left: 80, right: 80, bottom: 108, display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 28, paddingTop: 24, borderTop: "1px solid var(--line)" }}>
        {notes.map(([label, body], i) => (
          <div key={i}>
            <div style={{ fontFamily: MONO, fontSize: 11, letterSpacing: ".1em", textTransform: "uppercase", color: "var(--accent)" }}>{label}</div>
            <p style={{ fontSize: 13.5, lineHeight: 1.5, color: "var(--text-subtle)", margin: "8px 0 0" }}>{body}</p>
          </div>
        ))}
      </div>
      <FootMark style={{ bottom: 34 }} />
    </div>
  );
}

// 13 — CAPABILITY
function Capability() {
  const items = [
    ["01", "미디어아트 제작", "프로젝션 매핑·실시간 렌더링·LED 설치 제작 경험."],
    ["02", "인터랙티브 사운드", "‘반응하는 레일’의 모션 연동 사운드 설계 역량."],
    ["03", "레이저 안전 설계", "IEC 60825-1 (Class 4 RGB) 기준 안전 문서·운용 경험."],
    ["04", "IP · 콘텐츠 운영", "회차 콘텐츠를 지속 공급하는 라이선싱·운영 모델."],
  ];
  return (
    <div className="slide">
      <Kicker>Capability — 실행 역량</Kicker>
      <PageNo n={12} />
      <h1 style={{ position: "absolute", left: 80, top: 138, fontFamily: DISPLAY, fontWeight: 300, fontSize: 44, letterSpacing: "-.02em", color: "var(--text-strong)", margin: 0 }}>
        설치가 아니라 <b style={{ fontWeight: 600 }}>운영</b>까지 책임진다
      </h1>
      <div style={{ position: "absolute", left: 80, right: 80, bottom: 116, display: "grid", gridTemplateColumns: "repeat(4,1fr)", borderTop: "1px solid var(--line)" }}>
        {items.map(([no, title, body], i) => (
          <div key={i} style={{ padding: i === 0 ? "28px 26px 0 0" : i === 3 ? "28px 0 0 26px" : "28px 26px 0 26px", borderLeft: "1px solid var(--line)" }}>
            <div style={{ fontFamily: MONO, fontSize: 12, letterSpacing: ".14em", color: "var(--accent)" }}>{no}</div>
            <h3 style={{ fontSize: 18, fontWeight: 600, color: "var(--text-strong)", margin: "14px 0 0" }}>{title}</h3>
            <p style={{ fontSize: 13.5, lineHeight: 1.55, color: "var(--text-subtle)", margin: "10px 0 0" }}>{body}</p>
          </div>
        ))}
      </div>
      <FootMark />
    </div>
  );
}

// 14 — ASK
function Ask() {
  const rows = [
    ["01", "데이터 공유", "레일바이크 연·월 이용객/매출, 차량 대수, 운영 구조 (정보공개 병행 중)."],
    ["02", "의사결정 협의", "시·도시공사 소관 부서와 추진 가능성·재개발 일정 협의 미팅."],
    ["03", "파일럿 제안", "1구간·1시즌(가을~겨울) 소규모 야간 미디어 시범으로 리스크 최소화."],
    ["04", "일정(안)", "협의·데이터 확보 → 파일럿 기획·설계 → 시즌 시범 운영 → 성과 평가."],
  ];
  return (
    <div className="slide">
      <Kicker>Next Steps — 요청 사항</Kicker>
      <PageNo n={13} />
      <h1 style={{ position: "absolute", left: 80, top: 136, fontFamily: DISPLAY, fontWeight: 300, fontSize: 46, letterSpacing: "-.02em", color: "var(--text-strong)", margin: 0 }}>
        요청 드리는 <b style={{ fontWeight: 600 }}>네 가지</b>
      </h1>
      <div style={{ position: "absolute", left: 80, right: 80, bottom: 120, display: "flex", flexDirection: "column" }}>
        {rows.map(([no, title, body], i) => (
          <div key={i} style={{ display: "grid", gridTemplateColumns: "54px 220px 1fr", alignItems: "baseline", gap: 24, padding: "20px 0", borderTop: "1px solid var(--line)", ...(i === rows.length - 1 ? { borderBottom: "1px solid var(--line)" } : {}) }}>
            <span style={{ fontFamily: DISPLAY, fontSize: 28, fontWeight: 200, color: "var(--accent)" }}>{no}</span>
            <span style={{ fontSize: 18, fontWeight: 600, color: "var(--text-strong)" }}>{title}</span>
            <span style={{ fontSize: 15, lineHeight: 1.5, color: "var(--text-muted)" }}>{body}</span>
          </div>
        ))}
      </div>
      <FootMark />
    </div>
  );
}

// 15 — CLOSING
function Closing() {
  return (
    <div className="slide" style={{ background: "var(--ink-900)" }}>
      <div className="backdrop" style={{ background: "radial-gradient(120% 120% at 50% 120%, #1a1e24 0%, #0d0f12 55%, #08090a 100%)" }} />
      <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", textAlign: "center" }}>
        <img src={wordmarkWhite} alt="sia.haus" style={{ height: 30 }} />
        <p style={{ fontFamily: DISPLAY, fontWeight: 200, fontSize: 38, letterSpacing: "-.02em", color: "var(--text-strong)", margin: "34px 0 0" }}>
          기술은 도구이고, <b style={{ fontWeight: 600 }}>경험은 감각입니다.</b>
        </p>
        <p style={{ fontFamily: MONO, fontSize: 13, letterSpacing: ".16em", textTransform: "uppercase", color: "var(--accent)", margin: "30px 0 0" }}>
          sia@sia.haus · base on Seoul
        </p>
      </div>
      <div style={{ position: "absolute", bottom: 34, left: 80, right: 80, textAlign: "center", fontFamily: MONO, fontSize: 10, lineHeight: 1.7, letterSpacing: ".04em", color: "var(--text-faint)" }}>
        참고 — 여수 해양레일바이크 · 아침고요 별빛정원전 · 대구 수성못 빛예술제 · 한강 드론라이트쇼. 모든 매출 수치는 가정 기반 추정이며 확정 전 공식 채널·정보공개로 재확인 필요.
      </div>
    </div>
  );
}

export const SLIDES = [
  { label: "Cover", Component: Cover },
  { label: "Summary", Component: Summary },
  { label: "Assets", Component: Assets },
  { label: "Market", Component: Market },
  { label: "Benchmarking", Component: Benchmarking },
  { label: "Insight", Component: Insight },
  { label: "Concept", Component: ConceptDivider },
  { label: "Positioning", Component: Positioning },
  { label: "Modules", Component: Modules },
  { label: "Revenue", Component: Revenue },
  { label: "Roadmap", Component: Roadmap },
  { label: "Risk", Component: Risk },
  { label: "Capability", Component: Capability },
  { label: "Ask", Component: Ask },
  { label: "Closing", Component: Closing },
];

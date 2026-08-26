import React from "react";

/**
 * BarMeter — horizontal labelled bar for budget breakdowns and KPI progress.
 * Mono label + value on a row, hairline track, champagne (or spectral) fill.
 */
export function BarMeter({ label, value, pct, color = "var(--accent)", showPct = true }) {
  const w = Math.max(0, Math.min(100, pct));
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10, width: "100%" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: 12, letterSpacing: "0.08em", textTransform: "uppercase", color: "var(--text-muted)" }}>
          {label}
        </span>
        <span style={{ fontFamily: "var(--font-display)", fontSize: 18, fontWeight: 500, letterSpacing: "-0.01em", color: "var(--text-strong)" }}>
          {value}{showPct && <span style={{ fontFamily: "var(--font-mono)", fontSize: 12, color: "var(--text-subtle)", marginLeft: 8 }}>{w}%</span>}
        </span>
      </div>
      <div style={{ height: 6, background: "var(--ink-600)", borderRadius: "var(--r-pill)", overflow: "hidden" }}>
        <div style={{ width: `${w}%`, height: "100%", background: color, borderRadius: "var(--r-pill)", transition: "width var(--dur-cinematic) var(--ease-out)" }} />
      </div>
    </div>
  );
}

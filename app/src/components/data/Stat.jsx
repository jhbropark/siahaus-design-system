import React from "react";

/**
 * Stat — the data-driven hero metric. Huge thin number, mono label above,
 * optional delta + caption below. The backbone of KPI / Budget / Summary slides.
 */
export function Stat({
  value,
  label,
  caption,
  delta,
  deltaDir = "up",
  accent = false,
  size = "lg",
  align = "left",
}) {
  const fs = { sm: 44, md: 64, lg: 96 }[size];
  const deltaColor = deltaDir === "down" ? "var(--signal-critical)" : "var(--signal-positive)";
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10, textAlign: align, alignItems: align === "center" ? "center" : "flex-start" }}>
      {label && (
        <span style={{ fontFamily: "var(--font-mono)", fontSize: 12, fontWeight: 500, letterSpacing: "0.16em", textTransform: "uppercase", color: "var(--text-subtle)" }}>
          {label}
        </span>
      )}
      <div style={{ display: "flex", alignItems: "baseline", gap: 12, justifyContent: align === "center" ? "center" : "flex-start" }}>
        <span style={{ fontFamily: "var(--font-display)", fontSize: fs, fontWeight: 200, letterSpacing: "-0.03em", lineHeight: 0.95, color: accent ? "var(--accent)" : "var(--text-strong)" }}>
          {value}
        </span>
        {delta && (
          <span style={{ fontFamily: "var(--font-mono)", fontSize: 14, fontWeight: 600, letterSpacing: "0.02em", color: deltaColor }}>
            {deltaDir === "down" ? "↓" : "↑"} {delta}
          </span>
        )}
      </div>
      {caption && (
        <span style={{ fontFamily: "var(--font-body)", fontSize: 15, fontWeight: 400, lineHeight: 1.5, color: "var(--text-subtle)", maxWidth: 320 }}>
          {caption}
        </span>
      )}
    </div>
  );
}

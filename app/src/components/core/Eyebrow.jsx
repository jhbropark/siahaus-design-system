import React from "react";

/**
 * Eyebrow — the system's signature mono kicker. Uppercase, wide-tracked,
 * champagne by default. Optionally prefixed with an index or "//" marker.
 */
export function Eyebrow({ children, marker = false, color = "var(--accent)", ...rest }) {
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 8,
        fontFamily: "var(--font-mono)",
        fontSize: "var(--fs-eyebrow)",
        fontWeight: 500,
        letterSpacing: "var(--ls-eyebrow)",
        textTransform: "uppercase",
        color,
      }}
      {...rest}
    >
      {marker && <span style={{ opacity: 0.7 }}>//</span>}
      {children}
    </span>
  );
}

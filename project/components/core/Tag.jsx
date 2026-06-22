import React from "react";

/**
 * Tag — small mono pill / chip. Used for client names, categories, capabilities.
 * "outline" is the default; "solid" fills champagne; "ghost" is faint.
 */
export function Tag({ children, variant = "outline", ...rest }) {
  const variants = {
    outline: { background: "transparent", color: "var(--text-muted)", border: "1px solid var(--line-strong)" },
    solid: { background: "var(--accent)", color: "var(--on-accent)", border: "1px solid var(--accent)" },
    ghost: { background: "var(--ink-700)", color: "var(--text-subtle)", border: "1px solid transparent" },
  };
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        padding: "5px 12px",
        fontFamily: "var(--font-mono)",
        fontSize: 11,
        fontWeight: 500,
        letterSpacing: "0.08em",
        textTransform: "uppercase",
        borderRadius: "var(--r-pill)",
        whiteSpace: "nowrap",
        ...variants[variant],
      }}
      {...rest}
    >
      {children}
    </span>
  );
}

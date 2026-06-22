import React from "react";

/**
 * SIA.HAUS Button — restrained, near-square. Primary is champagne on ink;
 * secondary is a hairline outline; ghost is text-only with a mono feel.
 */
export function Button({
  children,
  variant = "primary",
  size = "md",
  full = false,
  disabled = false,
  iconLeft = null,
  iconRight = null,
  ...rest
}) {
  const pad = {
    sm: "10px 16px",
    md: "14px 24px",
    lg: "18px 34px",
  }[size];
  const fs = { sm: 12, md: 14, lg: 16 }[size];

  const base = {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 10,
    padding: pad,
    width: full ? "100%" : "auto",
    fontFamily: "var(--font-mono)",
    fontSize: fs,
    fontWeight: 500,
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    borderRadius: "var(--r-sm)",
    border: "1px solid transparent",
    cursor: disabled ? "not-allowed" : "pointer",
    opacity: disabled ? 0.4 : 1,
    transition: "background var(--dur-base) var(--ease-out), border-color var(--dur-base) var(--ease-out), color var(--dur-base) var(--ease-out), transform var(--dur-fast) var(--ease-out)",
    whiteSpace: "nowrap",
  };

  const variants = {
    primary: { background: "var(--accent)", color: "var(--on-accent)" },
    secondary: { background: "transparent", color: "var(--text)", borderColor: "var(--line-strong)" },
    ghost: { background: "transparent", color: "var(--text-muted)" },
  };

  return (
    <button
      style={{ ...base, ...variants[variant] }}
      disabled={disabled}
      onMouseDown={(e) => !disabled && (e.currentTarget.style.transform = "scale(0.98)")}
      onMouseUp={(e) => (e.currentTarget.style.transform = "scale(1)")}
      onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
      {...rest}
    >
      {iconLeft}
      {children}
      {iconRight}
    </button>
  );
}

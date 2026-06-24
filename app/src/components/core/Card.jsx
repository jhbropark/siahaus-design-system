import React from "react";

/**
 * Card — base surface container. Hairline border on a raised ink surface.
 * Optional hover lift. Keep corners near-square (md radius).
 */
export function Card({ children, hover = false, padded = true, style = {}, ...rest }) {
  const [h, setH] = React.useState(false);
  return (
    <div
      onMouseEnter={() => hover && setH(true)}
      onMouseLeave={() => hover && setH(false)}
      style={{
        background: "var(--surface)",
        border: "1px solid var(--line)",
        borderRadius: "var(--r-md)",
        padding: padded ? "var(--space-6)" : 0,
        transition: "border-color var(--dur-base) var(--ease-out), transform var(--dur-base) var(--ease-out), background var(--dur-base) var(--ease-out)",
        ...(h ? { borderColor: "var(--line-strong)", background: "var(--surface-raised)", transform: "translateY(-2px)" } : {}),
        ...style,
      }}
      {...rest}
    >
      {children}
    </div>
  );
}

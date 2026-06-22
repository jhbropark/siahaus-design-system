/* @ds-bundle: {"format":3,"namespace":"SIAHAUSDesignSystem_61fe1c","components":[{"name":"Button","sourcePath":"components/core/Button.jsx"},{"name":"Card","sourcePath":"components/core/Card.jsx"},{"name":"Eyebrow","sourcePath":"components/core/Eyebrow.jsx"},{"name":"Tag","sourcePath":"components/core/Tag.jsx"},{"name":"BarMeter","sourcePath":"components/data/BarMeter.jsx"},{"name":"Stat","sourcePath":"components/data/Stat.jsx"}],"sourceHashes":{"components/core/Button.jsx":"972e6433d0fd","components/core/Card.jsx":"10623bdd20e4","components/core/Eyebrow.jsx":"f6d6a8ad1b47","components/core/Tag.jsx":"38cc6939bb8e","components/data/BarMeter.jsx":"44ab02f3b1d1","components/data/Stat.jsx":"69e5b05c4d79"},"inlinedExternals":[],"unexposedExports":[]} */

(() => {

const __ds_ns = (window.SIAHAUSDesignSystem_61fe1c = window.SIAHAUSDesignSystem_61fe1c || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// components/core/Button.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * SIA.HAUS Button — restrained, near-square. Primary is champagne on ink;
 * secondary is a hairline outline; ghost is text-only with a mono feel.
 */
function Button({
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
    lg: "18px 34px"
  }[size];
  const fs = {
    sm: 12,
    md: 14,
    lg: 16
  }[size];
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
    whiteSpace: "nowrap"
  };
  const variants = {
    primary: {
      background: "var(--accent)",
      color: "var(--on-accent)"
    },
    secondary: {
      background: "transparent",
      color: "var(--text)",
      borderColor: "var(--line-strong)"
    },
    ghost: {
      background: "transparent",
      color: "var(--text-muted)"
    }
  };
  return /*#__PURE__*/React.createElement("button", _extends({
    style: {
      ...base,
      ...variants[variant]
    },
    disabled: disabled,
    onMouseDown: e => !disabled && (e.currentTarget.style.transform = "scale(0.98)"),
    onMouseUp: e => e.currentTarget.style.transform = "scale(1)",
    onMouseLeave: e => e.currentTarget.style.transform = "scale(1)"
  }, rest), iconLeft, children, iconRight);
}
Object.assign(__ds_scope, { Button });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Button.jsx", error: String((e && e.message) || e) }); }

// components/core/Card.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Card — base surface container. Hairline border on a raised ink surface.
 * Optional hover lift. Keep corners near-square (md radius).
 */
function Card({
  children,
  hover = false,
  padded = true,
  style = {},
  ...rest
}) {
  const [h, setH] = React.useState(false);
  return /*#__PURE__*/React.createElement("div", _extends({
    onMouseEnter: () => hover && setH(true),
    onMouseLeave: () => hover && setH(false),
    style: {
      background: "var(--surface)",
      border: "1px solid var(--line)",
      borderRadius: "var(--r-md)",
      padding: padded ? "var(--space-6)" : 0,
      transition: "border-color var(--dur-base) var(--ease-out), transform var(--dur-base) var(--ease-out), background var(--dur-base) var(--ease-out)",
      ...(h ? {
        borderColor: "var(--line-strong)",
        background: "var(--surface-raised)",
        transform: "translateY(-2px)"
      } : {}),
      ...style
    }
  }, rest), children);
}
Object.assign(__ds_scope, { Card });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Card.jsx", error: String((e && e.message) || e) }); }

// components/core/Eyebrow.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Eyebrow — the system's signature mono kicker. Uppercase, wide-tracked,
 * champagne by default. Optionally prefixed with an index or "//" marker.
 */
function Eyebrow({
  children,
  marker = false,
  color = "var(--accent)",
  ...rest
}) {
  return /*#__PURE__*/React.createElement("span", _extends({
    style: {
      display: "inline-flex",
      alignItems: "center",
      gap: 8,
      fontFamily: "var(--font-mono)",
      fontSize: "var(--fs-eyebrow)",
      fontWeight: 500,
      letterSpacing: "var(--ls-eyebrow)",
      textTransform: "uppercase",
      color
    }
  }, rest), marker && /*#__PURE__*/React.createElement("span", {
    style: {
      opacity: 0.7
    }
  }, "//"), children);
}
Object.assign(__ds_scope, { Eyebrow });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Eyebrow.jsx", error: String((e && e.message) || e) }); }

// components/core/Tag.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Tag — small mono pill / chip. Used for client names, categories, capabilities.
 * "outline" is the default; "solid" fills champagne; "ghost" is faint.
 */
function Tag({
  children,
  variant = "outline",
  ...rest
}) {
  const variants = {
    outline: {
      background: "transparent",
      color: "var(--text-muted)",
      border: "1px solid var(--line-strong)"
    },
    solid: {
      background: "var(--accent)",
      color: "var(--on-accent)",
      border: "1px solid var(--accent)"
    },
    ghost: {
      background: "var(--ink-700)",
      color: "var(--text-subtle)",
      border: "1px solid transparent"
    }
  };
  return /*#__PURE__*/React.createElement("span", _extends({
    style: {
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
      ...variants[variant]
    }
  }, rest), children);
}
Object.assign(__ds_scope, { Tag });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Tag.jsx", error: String((e && e.message) || e) }); }

// components/data/BarMeter.jsx
try { (() => {
/**
 * BarMeter — horizontal labelled bar for budget breakdowns and KPI progress.
 * Mono label + value on a row, hairline track, champagne (or spectral) fill.
 */
function BarMeter({
  label,
  value,
  pct,
  color = "var(--accent)",
  showPct = true
}) {
  const w = Math.max(0, Math.min(100, pct));
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: 10,
      width: "100%"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      justifyContent: "space-between",
      alignItems: "baseline"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-mono)",
      fontSize: 12,
      letterSpacing: "0.08em",
      textTransform: "uppercase",
      color: "var(--text-muted)"
    }
  }, label), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-display)",
      fontSize: 18,
      fontWeight: 500,
      letterSpacing: "-0.01em",
      color: "var(--text-strong)"
    }
  }, value, showPct && /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-mono)",
      fontSize: 12,
      color: "var(--text-subtle)",
      marginLeft: 8
    }
  }, w, "%"))), /*#__PURE__*/React.createElement("div", {
    style: {
      height: 6,
      background: "var(--ink-600)",
      borderRadius: "var(--r-pill)",
      overflow: "hidden"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      width: `${w}%`,
      height: "100%",
      background: color,
      borderRadius: "var(--r-pill)",
      transition: "width var(--dur-cinematic) var(--ease-out)"
    }
  })));
}
Object.assign(__ds_scope, { BarMeter });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/data/BarMeter.jsx", error: String((e && e.message) || e) }); }

// components/data/Stat.jsx
try { (() => {
/**
 * Stat — the data-driven hero metric. Huge thin number, mono label above,
 * optional delta + caption below. The backbone of KPI / Budget / Summary slides.
 */
function Stat({
  value,
  label,
  caption,
  delta,
  deltaDir = "up",
  accent = false,
  size = "lg",
  align = "left"
}) {
  const fs = {
    sm: 44,
    md: 64,
    lg: 96
  }[size];
  const deltaColor = deltaDir === "down" ? "var(--signal-critical)" : "var(--signal-positive)";
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: 10,
      textAlign: align,
      alignItems: align === "center" ? "center" : "flex-start"
    }
  }, label && /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-mono)",
      fontSize: 12,
      fontWeight: 500,
      letterSpacing: "0.16em",
      textTransform: "uppercase",
      color: "var(--text-subtle)"
    }
  }, label), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "baseline",
      gap: 12,
      justifyContent: align === "center" ? "center" : "flex-start"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-display)",
      fontSize: fs,
      fontWeight: 200,
      letterSpacing: "-0.03em",
      lineHeight: 0.95,
      color: accent ? "var(--accent)" : "var(--text-strong)"
    }
  }, value), delta && /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-mono)",
      fontSize: 14,
      fontWeight: 600,
      letterSpacing: "0.02em",
      color: deltaColor
    }
  }, deltaDir === "down" ? "↓" : "↑", " ", delta)), caption && /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-body)",
      fontSize: 15,
      fontWeight: 400,
      lineHeight: 1.5,
      color: "var(--text-subtle)",
      maxWidth: 320
    }
  }, caption));
}
Object.assign(__ds_scope, { Stat });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/data/Stat.jsx", error: String((e && e.message) || e) }); }

__ds_ns.Button = __ds_scope.Button;

__ds_ns.Card = __ds_scope.Card;

__ds_ns.Eyebrow = __ds_scope.Eyebrow;

__ds_ns.Tag = __ds_scope.Tag;

__ds_ns.BarMeter = __ds_scope.BarMeter;

__ds_ns.Stat = __ds_scope.Stat;

})();

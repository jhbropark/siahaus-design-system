import React from "react";
import wordmarkWhite from "../assets/wordmark-white.png";

export { wordmarkWhite };

// Mono kicker, top-left. Renders the signature "// LABEL" treatment.
export function Kicker({ children }) {
  return (
    <div className="kicker">
      <span className="mk">//</span>
      {children}
    </div>
  );
}

// Page number, top-right. Deck runs 14 numbered content slides (cover excluded).
export function PageNo({ n, total = 14 }) {
  return (
    <div className="pageno">
      {String(n).padStart(2, "0")} / {total}
    </div>
  );
}

// Faint wordmark watermark, bottom-left.
export function FootMark({ style }) {
  return <img className="footmark" src={wordmarkWhite} alt="sia.haus" style={style} />;
}

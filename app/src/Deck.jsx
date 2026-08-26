import React, { useState, useEffect, useCallback, useRef } from "react";
import { SLIDES } from "./slides/index.jsx";

const STAGE_W = 1280;
const STAGE_H = 720;

// Scale the fixed 1280×720 canvas to fit the viewport while preserving aspect.
function useFitScale() {
  const [scale, setScale] = useState(1);
  useEffect(() => {
    const fit = () => {
      const s = Math.min(window.innerWidth / STAGE_W, window.innerHeight / STAGE_H);
      setScale(s);
    };
    fit();
    window.addEventListener("resize", fit);
    return () => window.removeEventListener("resize", fit);
  }, []);
  return scale;
}

export function Deck() {
  const [i, setI] = useState(0);
  const scale = useFitScale();
  const rootRef = useRef(null);

  const go = useCallback((next) => {
    setI((cur) => Math.max(0, Math.min(SLIDES.length - 1, next(cur))));
  }, []);

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === "ArrowRight" || e.key === "PageDown" || e.key === " ") { e.preventDefault(); go((c) => c + 1); }
      else if (e.key === "ArrowLeft" || e.key === "PageUp") { e.preventDefault(); go((c) => c - 1); }
      else if (e.key === "Home") go(() => 0);
      else if (e.key === "End") go(() => SLIDES.length - 1);
      else if (e.key === "f" || e.key === "F") {
        if (document.fullscreenElement) document.exitFullscreen();
        else rootRef.current?.requestFullscreen?.();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [go]);

  const { Component, label } = SLIDES[i];

  return (
    <div className="deck-root" ref={rootRef}>
      <div className="deck-hint">← → navigate · F fullscreen</div>
      <a className="deck-nav-link nav-link" href="#/library">Library →</a>

      <div className="deck-scaler" style={{ transform: `scale(${scale})` }}>
        <Component key={i} />
      </div>

      <div className="deck-ui">
        <button className="deck-btn" onClick={() => go((c) => c - 1)} disabled={i === 0} aria-label="이전 슬라이드">←</button>
        <button className="deck-btn" onClick={() => go((c) => c + 1)} disabled={i === SLIDES.length - 1} aria-label="다음 슬라이드">→</button>
        <span className="deck-label">{label}</span>
        <div className="deck-progress">
          <span style={{ width: `${((i + 1) / SLIDES.length) * 100}%` }} />
        </div>
        <span className="deck-count">{String(i + 1).padStart(2, "0")} / {String(SLIDES.length).padStart(2, "0")}</span>
      </div>
    </div>
  );
}

import React, { useRef, useState, useLayoutEffect } from "react";

const W = 1280;
const H = 720;

// Renders a fixed 1280×720 child scaled to fill the available width,
// preserving the 16:9 aspect. Used for template thumbnails in the Library.
export function CanvasFrame({ children }) {
  const ref = useRef(null);
  const [scale, setScale] = useState(0.4);

  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    const ro = new ResizeObserver(() => setScale(el.clientWidth / W));
    ro.observe(el);
    setScale(el.clientWidth / W);
    return () => ro.disconnect();
  }, []);

  return (
    <div ref={ref} className="tpl-frame" style={{ width: "100%", height: H * scale, position: "relative" }}>
      <div style={{ width: W, height: H, transformOrigin: "top left", transform: `scale(${scale})`, position: "absolute", top: 0, left: 0 }}>
        {children}
      </div>
    </div>
  );
}

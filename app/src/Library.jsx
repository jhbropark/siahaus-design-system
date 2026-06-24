import React from "react";
import "./library.css";
import { wordmarkWhite } from "./slides/chrome.jsx";
import { Button, Card, Eyebrow, Tag, BarMeter, Stat } from "./components/index.js";
import { TEMPLATES } from "./templates/index.jsx";
import { CanvasFrame } from "./CanvasFrame.jsx";

function Section({ title, count, children }) {
  return (
    <section className="lib-section">
      <div className="lib-section-head">
        <h2>{title}</h2>
        <span className="count">{count}</span>
      </div>
      {children}
    </section>
  );
}

function Spec({ name, children }) {
  return (
    <div className="spec">
      <div className="spec-name">{name}</div>
      {children}
    </div>
  );
}

export function Library() {
  return (
    <div className="lib">
      <div className="lib-inner">
        <div className="lib-top">
          <div>
            <div className="lib-eyebrow">Design System · Library</div>
            <h1 className="lib-title">SIA.HAUS <b>Component & Slide Kit</b></h1>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
            <a className="nav-link" href="#/">← 왕송호수 Deck</a>
            <img src={wordmarkWhite} alt="sia.haus" />
          </div>
        </div>

        {/* ---- Core components ---- */}
        <Section title="Core Components" count="04">
          <div className="spec-grid">
            <Spec name="Button — variant × size">
              <div className="spec-row">
                <Button variant="primary">Primary</Button>
                <Button variant="secondary">Secondary</Button>
                <Button variant="ghost">Ghost</Button>
              </div>
              <div className="spec-row">
                <Button size="sm">Small</Button>
                <Button size="md">Medium</Button>
                <Button size="lg">Large</Button>
                <Button disabled>Disabled</Button>
              </div>
            </Spec>

            <Spec name="Tag — outline / solid / ghost">
              <div className="spec-row">
                <Tag>Media Art</Tag>
                <Tag variant="solid">Projection</Tag>
                <Tag variant="ghost">Sound Design</Tag>
              </div>
            </Spec>

            <Spec name="Eyebrow — signature mono kicker">
              <div className="spec-row"><Eyebrow marker>Executive Summary</Eyebrow></div>
              <div className="spec-row"><Eyebrow color="var(--text-subtle)">base on Seoul</Eyebrow></div>
            </Spec>

            <Spec name="Card — hairline surface (hover)">
              <Card hover style={{ padding: "20px 22px" }}>
                <Eyebrow marker>Card</Eyebrow>
                <p style={{ margin: "12px 0 0", fontSize: 15, lineHeight: 1.55, color: "var(--text-muted)" }}>
                  Raised ink surface with a hairline border and an optional hover lift. Near-square corners.
                </p>
              </Card>
            </Spec>
          </div>
        </Section>

        {/* ---- Data components ---- */}
        <Section title="Data Components" count="02">
          <div className="spec-grid">
            <Spec name="Stat — hero metric">
              <div className="spec-row" style={{ gap: 48 }}>
                <Stat value="60+" label="Track Record" caption="Installations since 2018." size="md" />
                <Stat value="819㎡" label="Largest Canvas" delta="38%" accent size="md" />
              </div>
            </Spec>

            <Spec name="BarMeter — labelled progress">
              <BarMeter label="Media Facade" value="+18%" pct={82} color="var(--spectral-amber)" />
              <BarMeter label="Immersive Exhibition" value="+24%" pct={94} color="var(--spectral-slate)" />
              <BarMeter label="Projection Mapping" value="+14%" pct={66} color="var(--spectral-violet)" />
            </Spec>
          </div>
        </Section>

        {/* ---- Slide templates ---- */}
        <Section title="Slide Templates" count="08">
          <div className="tpl-grid">
            {TEMPLATES.map(({ id, name, subtitle, Component }) => (
              <div className="tpl-card" key={id}>
                <CanvasFrame><Component /></CanvasFrame>
                <div className="tpl-meta">
                  <div className="n">{name}</div>
                  <div className="s">{subtitle}</div>
                </div>
              </div>
            ))}
          </div>
        </Section>
      </div>
    </div>
  );
}

import React from "react";

export interface BarMeterProps {
  /** Mono uppercase row label. */
  label: string;
  /** Display value, e.g. "₩320M". */
  value: React.ReactNode;
  /** Fill percentage 0–100. */
  pct: number;
  /** Fill color (defaults to champagne). Use spectral tokens for categories. */
  color?: string;
  /** Show the % next to the value. Default true. */
  showPct?: boolean;
}

/** Horizontal labelled bar for budget breakdowns and KPI progress. */
export function BarMeter(props: BarMeterProps): JSX.Element;

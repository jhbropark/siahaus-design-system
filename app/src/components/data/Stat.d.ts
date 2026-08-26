import React from "react";

export interface StatProps {
  /** The headline figure, e.g. "₩819M" or "98%". */
  value: React.ReactNode;
  /** Mono uppercase label above the number. */
  label?: string;
  /** Supporting sentence below. */
  caption?: string;
  /** Delta string, e.g. "+24%". */
  delta?: string;
  /** Delta direction. Default "up". */
  deltaDir?: "up" | "down";
  /** Render the number in champagne. */
  accent?: boolean;
  /** Default "lg". */
  size?: "sm" | "md" | "lg";
  /** Default "left". */
  align?: "left" | "center";
}

/**
 * Hero metric for KPI, budget, and summary layouts.
 * @startingPoint section="Data" subtitle="Big-number metric with label + delta" viewport="700x220"
 */
export function Stat(props: StatProps): JSX.Element;

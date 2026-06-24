import React from "react";

export interface EyebrowProps extends React.HTMLAttributes<HTMLSpanElement> {
  /** Prefix with a "//" marker. */
  marker?: boolean;
  /** Override color (defaults to champagne accent). */
  color?: string;
  children?: React.ReactNode;
}

/** Mono kicker / section label used above titles across all slide types. */
export function Eyebrow(props: EyebrowProps): JSX.Element;

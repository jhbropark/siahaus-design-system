import React from "react";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** Visual style. Default "primary". */
  variant?: "primary" | "secondary" | "ghost";
  /** Size. Default "md". */
  size?: "sm" | "md" | "lg";
  /** Stretch to fill container width. */
  full?: boolean;
  disabled?: boolean;
  iconLeft?: React.ReactNode;
  iconRight?: React.ReactNode;
  children?: React.ReactNode;
}

/**
 * Primary call-to-action button for SIA.HAUS surfaces.
 * @startingPoint section="Core" subtitle="Buttons — primary, secondary, ghost" viewport="700x150"
 */
export function Button(props: ButtonProps): JSX.Element;

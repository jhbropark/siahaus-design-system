import React from "react";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Lift + brighten border on hover. */
  hover?: boolean;
  /** Apply default interior padding. Default true. */
  padded?: boolean;
  children?: React.ReactNode;
}

/** Base surface container — hairline border on raised ink. */
export function Card(props: CardProps): JSX.Element;

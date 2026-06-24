import React from "react";

export interface TagProps extends React.HTMLAttributes<HTMLSpanElement> {
  /** Default "outline". */
  variant?: "outline" | "solid" | "ghost";
  children?: React.ReactNode;
}

/** Mono pill for client names, categories, capabilities. */
export function Tag(props: TagProps): JSX.Element;

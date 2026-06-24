import React, { useState, useEffect } from "react";
import { Deck } from "./Deck.jsx";
import { Library } from "./Library.jsx";

// Minimal hash router: #/library → component & template library, else the deck.
export function App() {
  const [hash, setHash] = useState(window.location.hash);
  useEffect(() => {
    const onHash = () => setHash(window.location.hash);
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  const isLibrary = hash.startsWith("#/library");

  // The deck is a fixed, non-scrolling stage; the library scrolls vertically.
  useEffect(() => {
    document.body.style.overflow = isLibrary ? "auto" : "hidden";
    document.getElementById("root").style.height = isLibrary ? "auto" : "100vh";
  }, [isLibrary]);

  return isLibrary ? <Library /> : <Deck />;
}

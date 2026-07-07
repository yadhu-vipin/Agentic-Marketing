"use client";

import { useEffect, useState } from "react";

export function MountLoader() {
  const [visible, setVisible] = useState(false);
  const [progress, setProgress] = useState(0);
  const [fadeOut, setFadeOut] = useState(false);

  useEffect(() => {
    // Only show loader once per session
    const hasLoaded = sessionStorage.getItem("app_loader_shown");
    if (hasLoaded) {
      return;
    }

    setVisible(true);

    // Increment progress
    let current = 0;
    const interval = setInterval(() => {
      // Accelerating progress feel
      const step = Math.max(1, Math.floor((100 - current) * 0.15));
      current += step;

      if (current >= 100) {
        current = 100;
        clearInterval(interval);
        setTimeout(() => {
          setFadeOut(true);
          setTimeout(() => {
            setVisible(false);
            sessionStorage.setItem("app_loader_shown", "true");
          }, 600); // match duration-600
        }, 300);
      }
      setProgress(current);
    }, 45);

    return () => clearInterval(interval);
  }, []);

  if (!visible) return null;

  return (
    <div
      className={`fixed inset-0 z-[9999] flex flex-col items-center justify-center bg-[#05080a] transition-all duration-700 ease-in-out ${
        fadeOut ? "opacity-0 scale-105 pointer-events-none" : "opacity-100 scale-100"
      }`}
    >
      {/* Immersive mesh glowing blobs in loader */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[400px] w-[400px] rounded-full bg-primary/5 blur-[120px] pointer-events-none animate-pulse" />

      <div className="relative flex flex-col items-center space-y-6">
        {/* Glowing ring animation */}
        <div className="relative h-16 w-16 flex items-center justify-center">
          <span className="absolute h-full w-full rounded-full border-2 border-primary/10" />
          <span className="absolute h-full w-full rounded-full border-2 border-t-primary border-r-transparent border-b-transparent border-l-transparent animate-spin" />
          <span className="h-3 w-3 rounded-full bg-primary shadow-[0_0_12px_#0055ff]" />
        </div>

        {/* Brand details */}
        <div className="text-center space-y-1">
          <div className="text-sm font-extrabold tracking-[0.2em] uppercase text-white bg-gradient-to-r from-white via-zinc-200 to-zinc-400 bg-clip-text text-transparent">
            Agentic Marketing
          </div>
          <div className="text-[10px] tracking-widest text-muted/60 uppercase font-semibold">
            Social Campaign Studio
          </div>
        </div>

        {/* Digital Counter */}
        <div className="font-mono text-xs font-semibold text-primary/80 tracking-wider">
          {progress.toString().padStart(3, "0")}%
        </div>
      </div>
    </div>
  );
}

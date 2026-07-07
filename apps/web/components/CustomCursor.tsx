"use client";

import { useEffect, useState } from "react";

export function CustomCursor() {
  const [position, setPosition] = useState({ x: -100, y: -100 });
  const [trail, setTrail] = useState({ x: -100, y: -100 });
  const [hovered, setHovered] = useState(false);
  const [active, setActive] = useState(false);
  const [visible, setVisible] = useState(false);
  const [magneticElement, setMagneticElement] = useState<DOMRect | null>(null);

  useEffect(() => {
    // Disable on mobile / touch devices
    const isTouch = window.matchMedia("(pointer: coarse)").matches;
    const prefersReducedMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    ).matches;

    if (isTouch || prefersReducedMotion) {
      return;
    }

    setVisible(true);

    const onMouseMove = (e: MouseEvent) => {
      setPosition({ x: e.clientX, y: e.clientY });
    };

    const onMouseDown = () => setActive(true);
    const onMouseUp = () => setActive(false);

    const onMouseOver = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (
        target.tagName === "BUTTON" ||
        target.tagName === "A" ||
        target.closest("a") ||
        target.closest("button") ||
        target.classList.contains("input") ||
        target.classList.contains("textarea") ||
        target.classList.contains("select") ||
        target.classList.contains("chip") ||
        target.classList.contains("card-interactive")
      ) {
        setHovered(true);

        // Magnetic attraction details if it's a small button/chip
        const interactiveEl = target.closest("button") || target.closest("a") || target;
        const rect = interactiveEl.getBoundingClientRect();
        if (rect.width < 250 && rect.height < 100) {
          setMagneticElement(rect);
        } else {
          setMagneticElement(null);
        }
      } else {
        setHovered(false);
        setMagneticElement(null);
      }
    };

    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mousedown", onMouseDown);
    window.addEventListener("mouseup", onMouseUp);
    window.addEventListener("mouseover", onMouseOver);

    return () => {
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mousedown", onMouseDown);
      window.removeEventListener("mouseup", onMouseUp);
      window.removeEventListener("mouseover", onMouseOver);
    };
  }, []);

  // Smooth trail spring effect loop
  useEffect(() => {
    let animFrame: number;
    
    const updateTrail = () => {
      setTrail((prev) => {
        // If magneticElement is active, snap the trailing ring to the center of the element
        if (magneticElement) {
          const targetX = magneticElement.left + magneticElement.width / 2;
          const targetY = magneticElement.top + magneticElement.height / 2;
          return {
            x: prev.x + (targetX - prev.x) * 0.22,
            y: prev.y + (targetY - prev.y) * 0.22,
          };
        }

        // Standard trailing spring physics
        return {
          x: prev.x + (position.x - prev.x) * 0.18,
          y: prev.y + (position.y - prev.y) * 0.18,
        };
      });

      animFrame = requestAnimationFrame(updateTrail);
    };

    if (visible) {
      animFrame = requestAnimationFrame(updateTrail);
    }

    return () => cancelAnimationFrame(animFrame);
  }, [position, visible, magneticElement]);

  if (!visible) return null;

  // Render cursor details
  // 1. Pointer Dot: moves immediately with mouse.
  // 2. Trailing ring: spring physics lag, snaps to button centers on hover.
  return (
    <>
      {/* Outer Ring */}
      <div
        className="fixed top-0 left-0 rounded-full pointer-events-none z-[9999] mix-blend-difference"
        style={{
          width: magneticElement ? `${magneticElement.width + 12}px` : "24px",
          height: magneticElement ? `${magneticElement.height + 12}px` : "24px",
          border: "1.5px solid rgba(0, 170, 255, 0.7)",
          transform: `translate3d(${trail.x - (magneticElement ? magneticElement.width / 2 + 6 : 12)}px, ${
            trail.y - (magneticElement ? magneticElement.height / 2 + 6 : 12)
          }px, 0)`,
          borderRadius: magneticElement ? "12px" : "50%",
          transition: "width 0.3s cubic-bezier(0.16, 1, 0.3, 1), height 0.3s cubic-bezier(0.16, 1, 0.3, 1), border-radius 0.3s cubic-bezier(0.16, 1, 0.3, 1)",
          backgroundColor: hovered ? "rgba(0, 85, 255, 0.05)" : "transparent",
          boxShadow: hovered ? "0 0 16px rgba(0, 85, 255, 0.15)" : "none",
        }}
      />

      {/* Center Dot */}
      <div
        className="fixed top-0 left-0 w-2.5 h-2.5 bg-white rounded-full pointer-events-none z-[9999] mix-blend-difference"
        style={{
          transform: `translate3d(${position.x - 5}px, ${position.y - 5}px, 0) scale(${active ? 0.7 : hovered ? 1.4 : 1})`,
          transition: "transform 0.2s cubic-bezier(0.16, 1, 0.3, 1)",
        }}
      />
    </>
  );
}

"use client";

import { useEffect, useRef } from "react";

export function InteractiveCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationFrameId: number;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const prefersReducedMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    ).matches;

    // Track scroll depth
    let scrollY = 0;
    let targetScrollY = 0;

    function handleScroll() {
      targetScrollY = window.scrollY;
    }

    // Track mouse coords
    const mouse = { x: -1000, y: -1000, tx: -1000, ty: -1000 };

    function handleMouseMove(e: MouseEvent) {
      mouse.tx = e.clientX;
      mouse.ty = e.clientY;
    }

    function handleMouseLeave() {
      mouse.tx = -1000;
      mouse.ty = -1000;
    }

    function handleResize() {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    }

    window.addEventListener("scroll", handleScroll, { passive: true });
    window.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseleave", handleMouseLeave);
    window.addEventListener("resize", handleResize);

    // Particle type for our 3D Ring structure
    class RingParticle {
      theta: number; // angle around the ring
      phi: number; // vertical angle
      radius: number;
      baseRadius: number;
      color: string;
      size: number;

      constructor(phi: number, theta: number, baseRadius: number) {
        this.phi = phi;
        this.theta = theta;
        this.baseRadius = baseRadius;
        this.radius = baseRadius;
        this.size = Math.random() * 1.2 + 0.6;
        this.color = Math.random() > 0.4 ? "rgba(0, 85, 255, 0.45)" : "rgba(0, 210, 255, 0.3)";
      }

      render3D(scrollProgress: number, rotationX: number, rotationY: number) {
        if (!ctx) return;

        // Evolve particle state based on scrollProgress
        // 1. Separate: Rings expand and separate along Z/Y axes
        // 2. Collapse: at mid scroll they reassemble
        // 3. Scale: size grows as we scroll down
        const separationOffset = scrollProgress * 150;
        const currentRadius = this.baseRadius * (1 + scrollProgress * 0.4);

        // Spherical coordinates -> 3D coordinates
        let x = currentRadius * Math.sin(this.phi) * Math.cos(this.theta);
        let y = currentRadius * Math.sin(this.phi) * Math.sin(this.theta) + (this.phi > Math.PI / 2 ? separationOffset : -separationOffset);
        let z = currentRadius * Math.cos(this.phi);

        // Apply Z/Y rotation based on mouse coordinates & auto-rotation
        // Rotate Y
        const cosY = Math.cos(rotationY);
        const sinY = Math.sin(rotationY);
        let x1 = x * cosY - z * sinY;
        let z1 = x * sinY + z * cosY;

        // Rotate X
        const cosX = Math.cos(rotationX);
        const sinX = Math.sin(rotationX);
        let y2 = y * cosX - z1 * sinX;
        let z2 = y * sinX + z1 * cosX;

        // Simple perspective projection (Camera Distance = 900)
        const cameraDistance = 900;
        const perspective = cameraDistance / (cameraDistance + z2);

        // Center projection on screen
        const screenX = width / 2 + x1 * perspective;
        const screenY = height / 2 + y2 * perspective;

        // Mouse warping / attraction
        let finalX = screenX;
        let finalY = screenY;

        if (mouse.x > -500 && !prefersReducedMotion) {
          const dx = mouse.x - screenX;
          const dy = mouse.y - screenY;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 150) {
            const force = (150 - dist) / 150;
            // Push particles slightly away from mouse cursor
            finalX -= (dx / dist) * force * 15;
            finalY -= (dy / dist) * force * 15;
          }
        }

        // Draw particle
        if (finalX > 0 && finalX < width && finalY > 0 && finalY < height) {
          const opacity = Math.max(0.05, perspective * 0.65 * (z2 > 0 ? 0.45 : 1));
          ctx.fillStyle = this.phi > Math.PI / 2 ? `rgba(0, 85, 255, ${opacity})` : `rgba(0, 210, 255, ${opacity})`;
          ctx.beginPath();
          ctx.arc(finalX, finalY, this.size * perspective, 0, Math.PI * 2);
          ctx.fill();
        }
      }
    }

    // Generate orbiting particles representing nested holographic rings
    const particles: RingParticle[] = [];
    const ringCount = 5;
    const particlesPerRing = 150;

    for (let r = 0; r < ringCount; r++) {
      const radius = 100 + r * 55;
      const phi = (r / ringCount) * Math.PI; // latitude distribution

      for (let p = 0; p < particlesPerRing; p++) {
        const theta = (p / particlesPerRing) * Math.PI * 2; // longitude
        particles.push(new RingParticle(phi, theta, radius));
      }
    }

    let angleX = 0;
    let angleY = 0;

    // Main animation loop
    function loop() {
      if (!ctx || !canvas) return;

      // Inertial scroll interpolation
      scrollY += (targetScrollY - scrollY) * 0.08;
      const maxScroll = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
      const scrollProgress = Math.min(1, Math.max(0, scrollY / maxScroll));

      // Smooth mouse interpolation
      mouse.x += (mouse.tx - mouse.x) * 0.08;
      mouse.y += (mouse.ty - mouse.y) * 0.08;

      ctx.clearRect(0, 0, width, height);

      // Radial background spotlight glow reacting to scroll progress
      const gradientRadius = Math.min(width, height) * (0.8 + scrollProgress * 0.3);
      const bgGrad = ctx.createRadialGradient(
        width / 2,
        height / 2,
        0,
        width / 2,
        height / 2,
        gradientRadius
      );
      // Fades slightly into dark navy towards edges
      bgGrad.addColorStop(0, "rgba(2, 6, 20, 1)");
      bgGrad.addColorStop(0.5, "rgba(2, 4, 8, 1)");
      bgGrad.addColorStop(1, "rgba(1, 2, 4, 1)");
      ctx.fillStyle = bgGrad;
      ctx.fillRect(0, 0, width, height);

      // Deep cyan/blue auroral spotlights drifting
      if (!prefersReducedMotion) {
        // Spotlight 1: Top-Left
        const glow1 = ctx.createRadialGradient(
          width * 0.25 + Math.sin(angleX * 0.3) * 100,
          height * 0.25 + Math.cos(angleY * 0.3) * 100,
          0,
          width * 0.25 + Math.sin(angleX * 0.3) * 100,
          height * 0.25 + Math.cos(angleY * 0.3) * 100,
          Math.min(width, height) * 0.6
        );
        glow1.addColorStop(0, "rgba(0, 85, 255, 0.045)");
        glow1.addColorStop(1, "rgba(0, 0, 0, 0)");
        ctx.fillStyle = glow1;
        ctx.fillRect(0, 0, width, height);

        // Spotlight 2: Bottom-Right
        const glow2 = ctx.createRadialGradient(
          width * 0.75 + Math.cos(angleX * 0.2) * 120,
          height * 0.75 + Math.sin(angleY * 0.2) * 120,
          0,
          width * 0.75 + Math.cos(angleX * 0.2) * 120,
          height * 0.75 + Math.sin(angleY * 0.2) * 120,
          Math.min(width, height) * 0.6
        );
        glow2.addColorStop(0, "rgba(0, 210, 255, 0.035)");
        glow2.addColorStop(1, "rgba(0, 0, 0, 0)");
        ctx.fillStyle = glow2;
        ctx.fillRect(0, 0, width, height);
      }

      // Rotate camera angles (evolves with time & scroll)
      if (!prefersReducedMotion) {
        angleX += 0.003 + scrollProgress * 0.008;
        angleY += 0.004 + scrollProgress * 0.004;
      } else {
        angleX = scrollProgress * 2;
        angleY = scrollProgress * 2;
      }

      // Render 3D particles
      particles.forEach((p) => {
        p.render3D(scrollProgress, angleX, angleY);
      });

      animationFrameId = requestAnimationFrame(loop);
    }

    loop();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener("scroll", handleScroll);
      window.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseleave", handleMouseLeave);
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 w-full h-full pointer-events-none z-0"
    />
  );
}

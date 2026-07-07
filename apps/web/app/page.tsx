import Link from "next/link";
import { isSupabaseConfigured } from "@/lib/supabase/config";

const BACKEND_API_URL = process.env.BACKEND_API_URL || "http://localhost:8000";

async function isMetaConfiguredOnBackend(): Promise<boolean> {
  try {
    const res = await fetch(
      `${BACKEND_API_URL.replace(/\/$/, "")}/publish/status`,
      { cache: "no-store" },
    );
    if (!res.ok) return false;
    const data = await res.json();
    return data.configured === true;
  } catch {
    return false;
  }
}

const steps = [
  {
    step: "01",
    title: "Upload Product Guides",
    detail: "Synthesize target niches, core features, brand aesthetics, and assets into the active workspace database.",
  },
  {
    step: "02",
    title: "Map Channels",
    detail: "Direct campaign pipelines to organic social channels or local B2B lead discovery scrapers.",
  },
  {
    step: "03",
    title: "Generate Campaign",
    detail: "Orchestrate stateless LLM agents to render platform captions, target hashtags, and custom graphic assets.",
  },
  {
    step: "04",
    title: "Broadcast Live",
    detail: "Perform manual copy edits, execute instant creative regeneration, and post to Meta feeds.",
  },
];

export default async function HomePage() {
  const supabase = isSupabaseConfigured();
  const meta = await isMetaConfiguredOnBackend();

  return (
    <div className="space-y-40 py-12 relative">
      {/* Cinematic Scene 1: The Hero */}
      <section className="min-h-[70vh] flex flex-col justify-center items-center text-center max-w-5xl mx-auto py-16 animate-fade-in-up relative z-10">
        {/* Subtitle tag */}
        <div className="inline-flex items-center gap-2.5 rounded-full border border-primary/20 bg-primary/5 px-4.5 py-1.5 text-xs font-semibold text-primary tracking-widest uppercase mb-6 shadow-[0_0_15px_rgba(0,85,255,0.08)]">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary/40 opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-primary" />
          </span>
          Autonomous Social Studio
        </div>

        {/* Cinematic Title */}
        <h1 className="text-5xl font-extrabold tracking-tight sm:text-6xl md:text-7xl lg:text-8xl text-foreground leading-[1.05] max-w-4xl mx-auto">
          Autonomous campaign <br className="hidden sm:inline" />
          <span className="bg-gradient-to-r from-blue-500 via-[#00d2ff] to-[#0055ff] bg-clip-text text-transparent">
            orchestration.
          </span>
        </h1>

        {/* Elegant Subtitle */}
        <p className="max-w-2xl mx-auto text-sm sm:text-base text-muted/75 leading-relaxed font-normal mt-8">
          A stateless, agentic marketing studio designed to synthesise product knowledge bases, draft customized platform copy, and execute instant social broadcasting.
        </p>

        {/* Call to Actions */}
        <div className="flex flex-wrap items-center justify-center gap-4 pt-10">
          <Link href="/products/new" className="btn flex items-center gap-2 px-8 py-3.5 text-sm font-semibold shadow-lg hover:shadow-primary/30">
            <span>Add Brand Profile</span>
            <svg className="h-4.5 w-4.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
            </svg>
          </Link>
          <Link href="/campaigns" className="btn-ghost flex items-center gap-2 px-8 py-3.5 text-sm font-semibold">
            <span>Open Studio</span>
            <svg className="h-4.5 w-4.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        </div>
      </section>

      {/* Cinematic Scene 2: Workflow Pipeline */}
      <section className="space-y-16 relative z-10 max-w-6xl mx-auto">
        <div className="text-center max-w-2xl mx-auto space-y-3">
          <h2 className="text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">System Pipeline</h2>
          <p className="text-sm text-muted/75 leading-relaxed">
            Stateless agent operations executing in sequential stages, from onboarding to live network deployment.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {steps.map((s, idx) => (
            <div
              key={s.title}
              className="glow-card card flex flex-col justify-between group h-full border-border/40 hover:-translate-y-1 transition-all duration-300"
              style={{ animationDelay: `${idx * 100}ms` }}
            >
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-primary/75 tracking-wider">
                    {s.step}
                  </span>
                  <div className="h-1.5 w-1.5 rounded-full bg-primary/20 group-hover:bg-primary transition-colors duration-300" />
                </div>
                <h3 className="font-bold text-base text-foreground/90 group-hover:text-primary transition-colors duration-200">
                  {s.title}
                </h3>
                <p className="text-xs text-muted/70 leading-relaxed">
                  {s.detail}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Cinematic Scene 3: Platform Integration Health */}
      <section className="glow-card card max-w-2xl mx-auto border-border/40 shadow-2xl relative overflow-hidden bg-panel/90 z-10">
        <div className="absolute top-0 left-0 h-[1px] w-full bg-gradient-to-r from-transparent via-primary/30 to-transparent" />
        
        <div className="flex items-center gap-4">
          <div className="p-2.5 rounded-lg bg-surface border border-border/80 text-primary">
            <svg className="h-5.5 w-5.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.25">
              <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div>
            <h2 className="text-lg font-bold text-foreground">Relay Integrations</h2>
            <p className="text-xs text-muted/80">Active health checks of data nodes and social publishing relays.</p>
          </div>
        </div>

        <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className={`flex items-center justify-between rounded-xl border p-4 bg-surface/50 transition-colors ${supabase ? "border-primary/25" : "border-border"}`}>
            <div className="space-y-0.5">
              <span className="text-xs font-semibold text-foreground block">Supabase Node</span>
              <span className="text-[10px] text-muted/70 block">Database campaign sync</span>
            </div>
            <span className={`badge ${supabase ? "bg-primary/10 text-primary border-primary/20" : "badge-danger"} flex items-center gap-1.5`}>
              <span className={`h-1.5 w-1.5 rounded-full ${supabase ? "bg-primary animate-pulse" : "bg-rose-400"}`} />
              {supabase ? "Connected" : "Offline"}
            </span>
          </div>

          <div className={`flex items-center justify-between rounded-xl border p-4 bg-surface/50 transition-colors ${meta ? "border-primary/25" : "border-border"}`}>
            <div className="space-y-0.5">
              <span className="text-xs font-semibold text-foreground block">Meta SDK Client</span>
              <span className="text-[10px] text-muted/70 block">Facebook / Instagram relay</span>
            </div>
            <span className={`badge ${meta ? "bg-primary/10 text-primary border-primary/20" : "badge-danger"} flex items-center gap-1.5`}>
              <span className={`h-1.5 w-1.5 rounded-full ${meta ? "bg-primary animate-pulse" : "bg-rose-400"}`} />
              {meta ? "Configured" : "Offline"}
            </span>
          </div>
        </div>
      </section>
    </div>
  );
}

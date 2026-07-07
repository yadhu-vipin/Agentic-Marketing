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
    title: "1. Add your product",
    detail: "Name, description, features, audience, industry, plus images and logo.",
  },
  {
    title: "2. Pick platforms",
    detail: "Instagram, Facebook, and LinkedIn — choose where you want to post.",
  },
  {
    title: "3. Generate campaign",
    detail: "AI writes captions, hashtags, and post copy with matching creatives.",
  },
  {
    title: "4. Review & publish",
    detail: "Edit anything, then publish or schedule directly to Meta platforms.",
  },
];

export default async function HomePage() {
  const supabase = isSupabaseConfigured();
  const meta = await isMetaConfiguredOnBackend();

  return (
    <div className="space-y-16 py-4">
      {/* Hero Section */}
      <section className="space-y-6 text-center max-w-3xl mx-auto py-8">
        <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-3.5 py-1 text-xs font-semibold text-primary shadow-sm shadow-primary/5">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary/40 opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-primary" />
          </span>
          Next-Gen Social Campaign Studio
        </div>
        <h1 className="text-4xl font-extrabold tracking-tight md:text-5xl lg:text-6xl text-foreground">
          Upload a product. <br />
          <span className="bg-gradient-to-r from-primary via-[#5ef7bc] to-cyan-400 bg-clip-text text-transparent">
            Generate a campaign.
          </span>{" "}
          <br className="hidden sm:inline" />
          Publish to social in seconds.
        </h1>
        <p className="max-w-xl mx-auto text-base text-muted/90 leading-relaxed">
          Leverage a stateless, workflow-driven AI agent pipeline to draft platform-ready social copy and high-quality creative assets. Directly publish or schedule to Facebook and Instagram.
        </p>
        <div className="flex flex-wrap items-center justify-center gap-3.5 pt-2">
          <Link href="/products/new" className="btn flex items-center gap-2 shadow-lg shadow-primary/10">
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
            </svg>
            Add a Product
          </Link>
          <Link href="/campaigns" className="btn-ghost flex items-center gap-2">
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
            </svg>
            View Campaigns
          </Link>
        </div>
      </section>

      {/* Steps Grid */}
      <section className="space-y-6">
        <div className="text-center max-w-md mx-auto">
          <h2 className="text-xl font-bold tracking-tight">How it works</h2>
          <p className="text-xs text-muted/80 mt-1">Four automated steps to go from code to published content.</p>
        </div>
        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-4">
          {steps.map((s, idx) => (
            <div key={s.title} className="card relative overflow-hidden group hover:border-primary/20">
              <div className="absolute top-0 right-0 -mt-4 -mr-4 h-16 w-16 rounded-full bg-primary/5 blur-xl group-hover:bg-primary/10 transition duration-300" />
              <div className="text-xs font-bold text-primary/80 uppercase tracking-widest mb-3">Step 0{idx + 1}</div>
              <h3 className="font-semibold text-base text-foreground/90">{s.title.substring(3)}</h3>
              <p className="mt-2.5 text-xs text-muted/80 leading-relaxed">{s.detail}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Status Section */}
      <section className="card max-w-xl mx-auto border-border/60 shadow-lg relative overflow-hidden">
        <div className="absolute top-0 left-0 h-[2px] w-full bg-gradient-to-r from-transparent via-primary/30 to-transparent" />
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-surface border border-border/80 text-primary">
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <div>
            <h2 className="text-base font-bold text-foreground">Integration Health</h2>
            <p className="text-xs text-muted">Current connection status of your external integrations.</p>
          </div>
        </div>
        <div className="mt-5 grid grid-cols-1 sm:grid-cols-2 gap-3.5">
          <div className={`flex items-center justify-between rounded-lg border p-3 bg-surface/50 ${supabase ? "border-emerald-500/20" : "border-border"}`}>
            <span className="text-xs font-medium text-muted/90">Supabase DB</span>
            <span className={`badge ${supabase ? "badge-success" : "badge-danger"}`}>
              <span className={`h-1.5 w-1.5 rounded-full ${supabase ? "bg-emerald-400 animate-pulse" : "bg-rose-400"}`} />
              {supabase ? "Connected" : "Offline"}
            </span>
          </div>
          <div className={`flex items-center justify-between rounded-lg border p-3 bg-surface/50 ${meta ? "border-emerald-500/20" : "border-border"}`}>
            <span className="text-xs font-medium text-muted/90">Meta API Endpoint</span>
            <span className={`badge ${meta ? "badge-success" : "badge-danger"}`}>
              <span className={`h-1.5 w-1.5 rounded-full ${meta ? "bg-emerald-400 animate-pulse" : "bg-rose-400"}`} />
              {meta ? "Configured" : "Not Configured"}
            </span>
          </div>
        </div>
      </section>
    </div>
  );
}

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ALL_PLATFORMS, PLATFORM_LABELS, type Platform, type WorkflowType } from "@/lib/types";

export function GenerateForm({ productId, defaultAudience }: { productId: string; defaultAudience: string }) {
  const router = useRouter();
  const [workflow, setWorkflow] = useState<WorkflowType>("organic_campaign");

  // Organic Campaign state
  const [selected, setSelected] = useState<Platform[]>([...ALL_PLATFORMS]);

  // Lead Generation state
  const [location, setLocation] = useState("");
  const [targetAudience, setTargetAudience] = useState(defaultAudience || "");
  const [scrapers] = useState<string[]>(["google_maps"]);
  const [imageMode, setImageMode] = useState<"none" | "campaign" | "per_lead">("none");
  const [instructions, setInstructions] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function toggle(platform: Platform) {
    setSelected((prev) =>
      prev.includes(platform)
        ? prev.filter((p) => p !== platform)
        : [...prev, platform],
    );
  }

  async function generate() {
    setError(null);
    setLoading(true);
    try {
      let body: any = {
        product_id: productId,
        workflow,
      };

      if (workflow === "lead_generation") {
        if (!location.trim()) {
          throw new Error("Location is required for B2B Lead Generation.");
        }
        body.config = {
          location,
          target_audience: targetAudience,
          scrapers,
          image_mode: imageMode,
          instructions,
        };
      } else {
        if (selected.length === 0) {
          throw new Error("Select at least one platform.");
        }
        body.platforms = selected;
      }

      const res = await fetch("/api/campaigns", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Generation failed");
      router.push(`/campaigns/${data.campaign.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Generation failed");
      setLoading(false);
    }
  }

  return (
    <div className="card space-y-6 relative overflow-hidden">
      {/* Workflow Selection Tabs */}
      <div className="border-b border-border pb-1 flex gap-6">
        <button
          type="button"
          onClick={() => !loading && setWorkflow("organic_campaign")}
          className={`pb-3 font-semibold text-sm transition-all relative ${
            workflow !== "lead_generation"
              ? "text-primary"
              : "text-muted hover:text-foreground"
          }`}
          disabled={loading}
        >
          Organic Social Media
          {workflow !== "lead_generation" && (
            <span className="absolute bottom-0 left-0 h-[2px] w-full bg-primary" />
          )}
        </button>
        <button
          type="button"
          onClick={() => !loading && setWorkflow("lead_generation")}
          className={`pb-3 font-semibold text-sm transition-all relative ${
            workflow === "lead_generation"
              ? "text-primary"
              : "text-muted hover:text-foreground"
          }`}
          disabled={loading}
        >
          B2B Lead Generation
          {workflow === "lead_generation" && (
            <span className="absolute bottom-0 left-0 h-[2px] w-full bg-primary" />
          )}
        </button>
      </div>

      {workflow !== "lead_generation" ? (
        /* Organic Social Media Form */
        <div className="space-y-4 animate-in fade-in duration-300">
          <div>
            <h3 className="font-semibold text-foreground/90">Select target channels</h3>
            <p className="text-xs text-muted">
              Our agent generates localized marketing copy and unique creative templates for each.
            </p>
          </div>

          <div className="flex flex-wrap gap-2.5 pt-1">
            {ALL_PLATFORMS.map((p) => {
              const on = selected.includes(p);
              return (
                <button
                  key={p}
                  type="button"
                  onClick={() => !loading && toggle(p)}
                  className={`chip cursor-pointer py-1.5 px-4 font-semibold text-xs flex items-center gap-1.5 ${
                    on ? "chip-on" : "hover:border-primary/30"
                  }`}
                  disabled={loading}
                >
                  <span className={`h-1.5 w-1.5 rounded-full transition-all duration-300 ${on ? "bg-primary scale-100" : "bg-transparent scale-0"}`} />
                  {PLATFORM_LABELS[p]}
                </button>
              );
            })}
          </div>
        </div>
      ) : (
        /* Lead Discovery Form */
        <div className="space-y-5 animate-in fade-in duration-300">
          <div>
            <h3 className="font-semibold text-foreground/90">Configure Lead Discovery</h3>
            <p className="text-xs text-muted">
              Search local B2B prospects using Google Maps API, filter by profile fit, and craft personalized outreach drafts.
            </p>
          </div>

          <div className="grid gap-5 sm:grid-cols-2">
            <div className="space-y-1.5">
              <label className="label">Target Location *</label>
              <input
                type="text"
                placeholder="e.g. Indiranagar, Bangalore"
                className="input"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                required
                disabled={loading}
              />
            </div>

            <div className="space-y-1.5">
              <label className="label">Target Audience / Niche</label>
              <input
                type="text"
                placeholder="e.g. cafes, bakeries, coffee shops"
                className="input"
                value={targetAudience}
                onChange={(e) => setTargetAudience(e.target.value)}
                disabled={loading}
              />
            </div>

            <div className="space-y-1.5 sm:col-span-2">
              <label className="label">Custom Outreach Guidelines / Instructions</label>
              <textarea
                placeholder="e.g. Focus on our wholesale pricing model and 24/7 delivery services..."
                className="textarea h-24"
                value={instructions}
                onChange={(e) => setInstructions(e.target.value)}
                disabled={loading}
              />
            </div>

            <div className="space-y-1.5 sm:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
              <div>
                <label className="label">Lead Research Providers</label>
                <div className="flex gap-2">
                  <span className="chip chip-on text-xs select-none py-1.5 px-3">
                    <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    Google Maps API Scraper
                  </span>
                </div>
              </div>

              <div>
                <label className="label">Outreach Creative Generation</label>
                <select
                  className="select"
                  value={imageMode}
                  onChange={(e) => setImageMode(e.target.value as any)}
                  disabled={loading}
                >
                  <option value="none">No images (text-only)</option>
                  <option value="per_lead">Generate personalized image per lead</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="p-3.5 rounded-lg bg-rose-500/10 border border-rose-500/20 text-xs font-medium text-rose-400">
          {error}
        </div>
      )}

      <button
        onClick={generate}
        className={`btn w-full flex items-center justify-center gap-2 ${loading ? "pulse-glow pointer-events-none" : ""}`}
        disabled={loading}
      >
        {loading ? (
          <>
            <svg className="animate-spin h-4 w-4 text-[#04130d]" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            <span>
              {workflow === "lead_generation"
                ? "Executing Lead Discovery Pipeline..."
                : "Generating Campaign..."}
            </span>
          </>
        ) : (
          <>
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <span>
              {workflow === "lead_generation" ? "Start Lead Discovery" : "Generate Campaign"}
            </span>
          </>
        )}
      </button>

      {loading && (
        <p className="text-[11px] text-muted/75 text-center leading-normal max-w-sm mx-auto">
          {workflow === "lead_generation"
            ? "Executing B2B scraper, ranking lead profile fit, and drafting tailored copies. This takes 15-45 seconds."
            : "Formulating templates, running copywriting agents, and rendering creatives. Please wait..."}
        </p>
      )}
    </div>
  );
}

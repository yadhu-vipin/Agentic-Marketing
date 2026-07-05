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
    <div className="card space-y-5">
      {/* Workflow Selection Tabs */}
      <div className="border-b border-border pb-2 flex gap-4">
        <button
          type="button"
          onClick={() => setWorkflow("organic_campaign")}
          className={`pb-2 font-semibold text-sm transition-all ${
            workflow === "organic_campaign"
              ? "border-b-2 border-accent text-accent"
              : "text-muted hover:text-foreground"
          }`}
        >
          Organic Social Media
        </button>
        <button
          type="button"
          onClick={() => setWorkflow("lead_generation")}
          className={`pb-2 font-semibold text-sm transition-all ${
            workflow === "lead_generation"
              ? "border-b-2 border-accent text-accent"
              : "text-muted hover:text-foreground"
          }`}
        >
          B2B Lead Generation
        </button>
      </div>

      {workflow === "organic_campaign" ? (
        <div className="space-y-4">
          <div>
            <h3 className="font-semibold">Select platforms</h3>
            <p className="text-sm text-muted">
              The agent writes platform-specific content and a matching creative for
              each.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            {ALL_PLATFORMS.map((p) => {
              const on = selected.includes(p);
              return (
                <button
                  key={p}
                  type="button"
                  onClick={() => toggle(p)}
                  className={`chip cursor-pointer ${on ? "chip-on" : ""}`}
                >
                  {on ? "✓ " : ""}
                  {PLATFORM_LABELS[p]}
                </button>
              );
            })}
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <div>
            <h3 className="font-semibold">Configure Lead Discovery</h3>
            <p className="text-sm text-muted">
              Discover and rank local B2B leads using Google Maps and enrich them with AI outreach copies.
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-1">
              <label className="label text-sm">Target Location *</label>
              <input
                type="text"
                placeholder="e.g. Indiranagar, Bangalore"
                className="input text-sm"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                required
              />
            </div>

            <div className="space-y-1">
              <label className="label text-sm">Target Audience / Niche</label>
              <input
                type="text"
                placeholder="e.g. cafes, bakeries, coffee shops"
                className="input text-sm"
                value={targetAudience}
                onChange={(e) => setTargetAudience(e.target.value)}
              />
            </div>

            <div className="space-y-1 sm:col-span-2">
              <label className="label text-sm">Custom Outreach Guidelines / Instructions</label>
              <textarea
                placeholder="e.g. Highlight our free shipping and wholesale discounts..."
                className="textarea text-sm h-20"
                value={instructions}
                onChange={(e) => setInstructions(e.target.value)}
              />
            </div>

            <div className="space-y-1 col-span-2 grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="label text-sm">Lead Research Providers</label>
                <div className="flex gap-2">
                  <span className="chip chip-on text-xs select-none">
                    ✓ Google Maps Scraper
                  </span>
                </div>
              </div>

              <div className="space-y-1">
                <label className="label text-sm">Outreach Creative Generation</label>
                <select
                  className="input text-sm select"
                  value={imageMode}
                  onChange={(e) => setImageMode(e.target.value as any)}
                >
                  <option value="none">No images (text-only)</option>
                  <option value="per_lead">Generate personalized image per lead</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      )}

      {error && <p className="text-sm text-danger">{error}</p>}

      <button onClick={generate} className="btn w-full" disabled={loading}>
        {loading
          ? workflow === "lead_generation"
            ? "Executing lead discovery pipeline..."
            : "Generating campaign..."
          : workflow === "lead_generation"
          ? "Start Lead Discovery"
          : "Generate campaign"}
      </button>
      
      {loading && (
        <p className="text-xs text-muted text-center">
          {workflow === "lead_generation"
            ? "This will scrape Google Maps, extract intents, score matches, and write custom copy. Please wait about 15-45 seconds."
            : "Writing copy and rendering creatives — this can take a few seconds."}
        </p>
      )}
    </div>
  );
}

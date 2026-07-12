"use client";

import { useState, useEffect } from "react";
import {
  PLATFORM_LABELS,
  type Campaign,
  type CampaignAsset,
} from "@/lib/types";

export function CampaignDashboard({
  campaign: initialCampaign,
  metaConfigured,
}: {
  campaign: Campaign;
  metaConfigured: boolean;
}) {
  const [campaign, setCampaign] = useState(initialCampaign);
  const [activeTab, setActiveTab] = useState<"research" | "content">("research");
  const [isPolling, setIsPolling] = useState(false);
  const [triggeringResearch, setTriggeringResearch] = useState(false);

  // Poll campaign status if researching
  useEffect(() => {
    if (campaign.status === "researching" || isPolling) {
      const interval = setInterval(async () => {
        try {
          const res = await fetch(`/api/campaigns/${campaign.id}`);
          if (res.ok) {
            const data = await res.json();
            if (data.campaign) {
              setCampaign(data.campaign);
              if (data.campaign.status !== "researching") {
                setIsPolling(false);
              }
            }
          }
        } catch (e) {}
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [campaign.id, campaign.status, isPolling]);
  
  // Auto scroll to top
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  const handleRunResearch = async () => {
    setTriggeringResearch(true);
    try {
      const res = await fetch(`/api/campaigns/${campaign.id}/research`, { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        setCampaign(data.campaign);
        setIsPolling(true);
      }
    } catch (e) {
       console.error("Failed to run research", e);
    }
    setTriggeringResearch(false);
  };
  
  const researchReport = (campaign.results as any)?.research_report;

  return (
    <div className="space-y-6">
      {/* Tabs */}
      <div className="flex border-b border-border/40">
        <button
          className={`py-3 px-6 font-semibold text-sm transition ${activeTab === "research" ? "text-primary border-b-2 border-primary" : "text-muted hover:text-foreground"}`}
          onClick={() => setActiveTab("research")}
        >
          Research & Strategy
        </button>
        <button
          className={`py-3 px-6 font-semibold text-sm transition ${activeTab === "content" ? "text-primary border-b-2 border-primary" : "text-muted hover:text-foreground"}`}
          onClick={() => setActiveTab("content")}
        >
          {campaign.workflow === "lead_generation" ? "Discovered Leads" : "Generated Content"}
        </button>
      </div>

      {activeTab === "research" && (
         <div className="space-y-6">
           {!researchReport && campaign.status !== "researching" && (
             <div className="card py-12 flex flex-col items-center gap-4 text-center">
                <p className="text-muted text-sm">Research has not been executed yet.</p>
                <button className="btn px-6 py-2" onClick={handleRunResearch} disabled={triggeringResearch}>
                  {triggeringResearch ? "Starting..." : "Run Research"}
                </button>
             </div>
           )}
           {campaign.status === "researching" && (
             <div className="card py-12 flex flex-col items-center gap-4 text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                <p className="text-muted text-sm animate-pulse">Running Research Agents... This may take a minute.</p>
             </div>
           )}
           {researchReport && campaign.status !== "researching" && (
             <div className="grid gap-6 md:grid-cols-2">
                <div className="card space-y-3">
                   <h3 className="font-bold text-primary">Overview</h3>
                   <p className="text-sm text-foreground/80 leading-relaxed">{researchReport.overview || "No overview available."}</p>
                </div>
                <div className="card space-y-3">
                   <h3 className="font-bold text-primary">Target Audience</h3>
                   <p className="text-sm text-foreground/80 leading-relaxed">{researchReport.target_audience || "No target audience defined."}</p>
                </div>
                <div className="card space-y-3 col-span-1 md:col-span-2">
                   <h3 className="font-bold text-primary">Competitor Analysis</h3>
                   {researchReport.competitors && researchReport.competitors.length > 0 ? (
                     <div className="grid gap-4 md:grid-cols-3">
                       {researchReport.competitors.map((c: any, i: number) => (
                         <div key={i} className="p-3 bg-surface rounded-lg border border-border/40">
                           <h4 className="font-semibold text-sm mb-1">{c.name}</h4>
                           <p className="text-xs text-muted mb-2">{c.description}</p>
                           <p className="text-[11px] text-primary/80"><span className="font-bold">Weakness:</span> {c.weakness}</p>
                         </div>
                       ))}
                     </div>
                   ) : (
                     <p className="text-sm text-foreground/80">No competitor analysis available.</p>
                   )}
                </div>
                <div className="card space-y-3 col-span-1 md:col-span-2">
                   <h3 className="font-bold text-primary">Strategic Angle</h3>
                   <p className="text-sm text-foreground/80 leading-relaxed">{researchReport.strategic_angle || "No strategy provided."}</p>
                </div>
             </div>
           )}
         </div>
      )}

      {activeTab === "content" && (
        <>
          {campaign.workflow === "lead_generation" ? (
             <LeadsDashboard leads={campaign.results && campaign.results.workflow === "lead_generation" ? campaign.results.leads : []} />
          ) : (
             <AssetsDashboard assets={campaign.assets || []} campaignId={campaign.id} metaConfigured={metaConfigured} />
          )}
        </>
      )}
    </div>
  );
}

function AssetsDashboard({ assets, campaignId, metaConfigured }: { assets: CampaignAsset[], campaignId: string, metaConfigured: boolean }) {
  if (assets.length === 0) {
    return (
      <div className="card text-center py-12 text-muted col-span-2 flex flex-col items-center justify-center gap-3 border-dashed border-2">
        <svg className="h-10 w-10 text-muted/50" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
        <span>No campaign assets generated.</span>
      </div>
    );
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {assets.map((asset) => (
        <AssetCard
          key={asset?.id}
          campaignId={campaignId}
          initial={asset}
          metaConfigured={metaConfigured}
        />
      ))}
    </div>
  );
}

function LeadsDashboard({ leads }: { leads: any[] }) {
  const safeLeads = Array.isArray(leads) ? leads : [];

  if (safeLeads.length === 0) {
    return (
      <div className="card text-center py-12 text-muted col-span-2 flex flex-col items-center justify-center gap-3">
        <svg className="h-10 w-10 text-muted/50" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <span>No leads discovered for this campaign.</span>
      </div>
    );
  }

  return (
    <div className="space-y-6 col-span-2">
      <div className="flex items-center justify-between border-b border-border/40 pb-4">
        <h2 className="text-xl font-bold text-foreground flex items-center gap-2">
          <svg className="h-5.5 w-5.5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          Discovered Leads <span className="text-sm font-normal text-muted">({safeLeads.length} matches)</span>
        </h2>
      </div>
      <div className="grid gap-6 md:grid-cols-2">
        {safeLeads.map((lead, idx) => (
          <LeadCard key={lead?.id || idx} lead={lead} />
        ))}
      </div>
    </div>
  );
}

function LeadCard({ lead }: { lead: any }) {
  const [activeTab, setActiveTab] = useState<"email" | "whatsapp">("email");

  if (!lead) return null;

  const isHighPriority = lead.priority === "high";
  const hasOutreach = lead.outreach?.email || lead.outreach?.whatsapp;

  return (
    <div className="card space-y-5 flex flex-col justify-between h-full bg-panel border border-border/60 hover:border-primary/20 transition-all duration-300">
      <div className="space-y-4">
        {/* Card Header Info */}
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3 className="font-bold text-base text-foreground tracking-tight">{lead.name || "Unnamed Lead"}</h3>
            {lead.category && (
              <span className="inline-block text-[10px] text-primary bg-primary/10 border border-primary/20 font-bold px-2 py-0.5 rounded mt-1.5 uppercase tracking-wide">
                {lead.category}
              </span>
            )}
          </div>
          <div className="flex flex-col items-end gap-1.5 shrink-0">
            {lead.priority && (
              <span className={`badge text-[10px] uppercase font-semibold ${isHighPriority ? "badge-success" : "badge-muted"}`}>
                {lead.priority} Priority
              </span>
            )}
            {lead.score !== null && lead.score !== undefined && (
              <span className="text-[11px] text-muted font-medium">
                Match Fit: <strong className={lead.score >= 80 ? "text-emerald-400 font-bold" : "text-muted-foreground"}>{lead.score}%</strong>
              </span>
            )}
          </div>
        </div>

        {/* Scoring Explanation */}
        {lead.score_reason && (
          <div className="text-[11px] text-muted/90 bg-surface/50 p-3 rounded-lg border border-border/40 leading-relaxed">
            <span className="font-bold text-foreground/80 block mb-0.5">Scoring Fit Analysis</span>
            {lead.score_reason}
          </div>
        )}

        {/* Directory Fields */}
        <div className="grid grid-cols-2 gap-2 text-xs pt-1 border-t border-border/40">
          {lead.rating !== null && lead.rating !== undefined && (
            <div className="col-span-2 flex items-center gap-1.5 text-muted">
              <span>Rating:</span>
              <strong className="text-amber-400 flex items-center gap-0.5">
                ★ {lead.rating}
              </strong>
              {lead.reviews !== null && lead.reviews !== undefined && <span className="text-[10px] text-muted/70">({lead.reviews} reviews)</span>}
            </div>
          )}
          {lead.phone && (
            <div className="col-span-2 sm:col-span-1 flex items-center gap-1 truncate text-muted">
              <svg className="h-3.5 w-3.5 text-muted/70" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.94.725l.548 2.2a1 1 0 01-.321.988l-1.305.98a10.582 10.582 0 004.872 4.872l.98-1.305a1 1 0 01.988-.321l2.2.548a1 1 0 01.725.94V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
              <a href={`tel:${lead.phone}`} className="hover:text-primary transition truncate">{lead.phone}</a>
            </div>
          )}
          {lead.website && (
            <div className="col-span-2 sm:col-span-1 flex items-center gap-1 truncate text-muted">
              <svg className="h-3.5 w-3.5 text-muted/70" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9-9c1.657 0 3 4.03 3 9s-1.343 9-3 9m0-18c-1.657 0-3 4.03-3 9s1.343 9 3 9m-9-9h18" />
              </svg>
              <a href={lead.website} target="_blank" rel="noopener noreferrer" className="hover:text-primary transition truncate">{lead.website.replace(/^https?:\/\/(www\.)?/, "")}</a>
            </div>
          )}
          {lead.email && (
            <div className="col-span-2 flex items-center gap-1 truncate text-muted">
              <svg className="h-3.5 w-3.5 text-muted/70" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <a href={`mailto:${lead.email}`} className="hover:text-primary transition truncate">{lead.email}</a>
            </div>
          )}
          {lead.address && (
            <div className="col-span-2 pt-1 flex items-start gap-1 text-muted">
              <svg className="h-3.5 w-3.5 text-muted/70 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span className="text-foreground/80 leading-normal">{lead.address}</span>
            </div>
          )}
        </div>
      </div>

      {/* Outreach Draft Section */}
      {hasOutreach && (
        <div className="space-y-3 pt-3 border-t border-border/40">
          <div className="flex gap-2">
            {lead.outreach?.email && (
              <button
                onClick={() => setActiveTab("email")}
                className={`btn-sm px-3.5 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                  activeTab === "email"
                    ? "bg-primary/10 text-primary border-primary/30"
                    : "bg-transparent text-muted border-transparent hover:text-foreground"
                }`}
              >
                Email Draft
              </button>
            )}
            {lead.outreach?.whatsapp && (
              <button
                onClick={() => setActiveTab("whatsapp")}
                className={`btn-sm px-3.5 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                  activeTab === "whatsapp"
                    ? "bg-primary/10 text-primary border-primary/30"
                    : "bg-transparent text-muted border-transparent hover:text-foreground"
                }`}
              >
                WhatsApp Draft
              </button>
            )}
          </div>

          {activeTab === "email" && lead.outreach?.email && (
            <div className="space-y-1.5 animate-in fade-in duration-200">
              <label className="label text-[10px] tracking-widest text-muted/70 uppercase">Personalized Email Draft</label>
              <textarea
                className="textarea text-xs h-32 font-mono bg-[#0c1311] border-border/30 text-foreground/90 p-3 w-full rounded-lg leading-relaxed focus:ring-0"
                readOnly
                value={lead.outreach.email}
              />
            </div>
          )}

          {activeTab === "whatsapp" && lead.outreach?.whatsapp && (
            <div className="space-y-1.5 animate-in fade-in duration-200">
              <label className="label text-[10px] tracking-widest text-muted/70 uppercase">Personalized WhatsApp Draft</label>
              <textarea
                className="textarea text-xs h-32 font-mono bg-[#0c1311] border-border/30 text-foreground/90 p-3 w-full rounded-lg leading-relaxed focus:ring-0"
                readOnly
                value={lead.outreach.whatsapp}
              />
            </div>
          )}

          {lead.outreach?.image_url && (
            <div className="mt-3 space-y-1.5">
              <label className="label text-[10px] tracking-widest text-muted/70 uppercase">Generated Outreach Creative</label>
              <div className="relative aspect-square w-full rounded-lg overflow-hidden border border-border/40 bg-surface">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={lead.outreach.image_url}
                  alt="Lead creative"
                  className="absolute inset-0 w-full h-full object-cover transition-transform duration-300 hover:scale-105"
                  loading="lazy"
                />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

const STATUS_BADGES: Record<string, string> = {
  draft: "badge-muted",
  scheduled: "badge-info",
  publishing: "badge-info animate-pulse",
  published: "badge-success",
  failed: "badge-danger",
};

function AssetCard({
  campaignId,
  initial,
  metaConfigured,
}: {
  campaignId: string;
  initial: CampaignAsset;
  metaConfigured: boolean;
}) {
  const [asset, setAsset] = useState<CampaignAsset>(initial || ({} as CampaignAsset));
  const [headline, setHeadline] = useState(initial?.headline || "");
  const [body, setBody] = useState(initial?.body || "");
  const [hashtags, setHashtags] = useState(Array.isArray(initial?.hashtags) ? initial.hashtags.join(" ") : "");
  const [cta, setCta] = useState(initial?.cta || "");
  const [scheduledTime, setScheduledTime] = useState("");
  const [busy, setBusy] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const base = `/api/campaigns/${campaignId}/assets/${asset?.id}`;
  const canPublishHere = asset?.platform === "instagram" || asset?.platform === "facebook";

  async function save() {
    setBusy("save");
    setError(null);
    setMessage(null);
    try {
      const res = await fetch(base, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ headline, body, cta, hashtags }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Save failed");
      if (data.asset) {
        setAsset(data.asset);
        setHashtags(Array.isArray(data.asset.hashtags) ? data.asset.hashtags.join(" ") : "");
      }
      setMessage("Edits saved successfully.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    } finally {
      setBusy(null);
    }
  }

  async function regenerateCreative() {
    setBusy("creative");
    setError(null);
    setMessage(null);
    try {
      const res = await fetch(`${base}/creative`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ creative_prompt: asset?.creative_prompt || "" }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Regenerate failed");
      if (data.asset) {
        setAsset(data.asset);
      }
      setMessage("Creative generated successfully.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Regenerate failed");
    } finally {
      setBusy(null);
    }
  }

  async function publish(schedule: boolean) {
    setBusy(schedule ? "schedule" : "publish");
    setError(null);
    setMessage(null);
    try {
      // Persist edits first so we publish the latest copy.
      await fetch(base, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ headline, body, cta, hashtags }),
      });
      const res = await fetch(`${base}/publish`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(
          schedule && scheduledTime ? { scheduled_time: scheduledTime } : {},
        ),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Publish failed");
      if (data.asset) {
        setAsset(data.asset);
      }
      setMessage(
        data.asset?.status === "scheduled"
          ? "Scheduled successfully."
          : "Published successfully.",
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Publish failed");
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="card space-y-5 bg-panel border border-border/60 hover:border-primary/10 transition-all duration-300">
      {/* Platform & Status Header */}
      <div className="flex items-center justify-between border-b border-border/40 pb-3">
        <h3 className="font-bold text-base text-foreground tracking-tight flex items-center gap-2">
          {asset?.platform === "instagram" ? (
            <svg className="h-5 w-5 text-pink-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.25">
              <rect x="2" y="2" width="20" height="20" rx="5" ry="5" />
              <path d="M16 11.37A4 4 0 1112.63 8 4 4 0 0116 11.37z" />
              <line x1="17.5" y1="6.5" x2="17.51" y2="6.5" />
            </svg>
          ) : asset?.platform === "facebook" ? (
            <svg className="h-5 w-5 text-blue-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.25">
              <path d="M18 2h-3a5 5 0 00-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 011-1h3z" />
            </svg>
          ) : (
            <svg className="h-5 w-5 text-sky-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.25">
              <path d="M16 8a6 6 0 016 6v7h-4v-7a2 2 0 00-2-2 2 2 0 00-2 2v7h-4v-7a6 6 0 016-6zM2 9h4v12H2z" />
              <circle cx="4" cy="4" r="2" />
            </svg>
          )}
          {asset?.platform && PLATFORM_LABELS[asset.platform] ? PLATFORM_LABELS[asset.platform] : "Social Post"}
        </h3>
        <span className={`badge ${STATUS_BADGES[asset?.status || "draft"] ?? "badge-muted"} capitalize`}>
          {asset?.status || "draft"}
        </span>
      </div>

      {/* Asset Creative Box */}
      {asset?.creative_url ? (
        <div className="relative aspect-square w-full rounded-lg overflow-hidden border border-border/50 bg-surface shadow-inner group">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={asset.creative_url}
            alt={`${asset.platform || "platform"} creative`}
            className="absolute inset-0 w-full h-full object-cover transition duration-300 group-hover:scale-102"
            loading="lazy"
          />
        </div>
      ) : (
        <div className="flex aspect-square w-full items-center justify-center rounded-lg border border-border bg-surface text-xs text-muted/70">
          No Creative Asset Generated
        </div>
      )}

      {/* Action to regenerate */}
      <button
        type="button"
        onClick={regenerateCreative}
        className="btn-ghost btn-sm w-full py-2 flex items-center justify-center gap-1.5"
        disabled={busy !== null}
      >
        {busy === "creative" ? (
          <>
            <svg className="animate-spin h-3.5 w-3.5 text-muted" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            <span>Rendering creative...</span>
          </>
        ) : (
          <>
            <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 1121.21 8H18.5" />
            </svg>
            <span>Regenerate Creative Image</span>
          </>
        )}
      </button>

      {/* Form Fields */}
      <div className="space-y-3.5 pt-2">
        <div className="space-y-1">
          <label className="label">Headline</label>
          <input
            className="input"
            value={headline}
            onChange={(e) => setHeadline(e.target.value)}
            disabled={busy !== null}
          />
        </div>

        <div className="space-y-1">
          <label className="label">Post Copy</label>
          <textarea
            className="textarea h-24"
            value={body}
            onChange={(e) => setBody(e.target.value)}
            disabled={busy !== null}
          />
        </div>

        <div className="grid gap-3.5 sm:grid-cols-2">
          <div className="space-y-1">
            <label className="label">Hashtags</label>
            <input
              className="input text-xs font-mono"
              value={hashtags}
              placeholder="e.g. #marketing #saas"
              onChange={(e) => setHashtags(e.target.value)}
              disabled={busy !== null}
            />
          </div>
          <div className="space-y-1">
            <label className="label">Call to Action (CTA)</label>
            <input
              className="input text-xs"
              value={cta}
              onChange={(e) => setCta(e.target.value)}
              disabled={busy !== null}
            />
          </div>
        </div>
      </div>

      {/* Bottom Publish Actions */}
      <div className="flex flex-col gap-3 pt-3 border-t border-border/40">
        <div className="flex flex-wrap gap-2">
          <button
            onClick={save}
            className="btn-ghost btn-sm py-2 px-4 flex-1 sm:flex-initial flex items-center justify-center gap-1"
            disabled={busy !== null}
          >
            {busy === "save" ? "Saving..." : "Save Edits"}
          </button>

          {canPublishHere ? (
            <button
              onClick={() => publish(false)}
              className="btn btn-sm py-2 px-4 flex-1 sm:flex-initial flex items-center justify-center gap-1"
              disabled={busy !== null || !metaConfigured}
              title={metaConfigured ? "Publish copy to page" : "Configure Meta in environment to publish"}
            >
              {busy === "publish" ? "Publishing..." : "Publish Now"}
            </button>
          ) : (
            <span className="chip text-[10px] font-semibold flex items-center justify-center py-1.5 px-3 bg-surface/50 select-none">
              API Publish Unavailable
            </span>
          )}
        </div>

        {canPublishHere && asset?.platform === "facebook" && (
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 p-3 rounded-lg bg-surface/50 border border-border/50">
            <div className="flex-1 space-y-1">
              <label className="label text-[10px] tracking-wider mb-0 text-muted/80">Schedule Publish Time</label>
              <input
                type="datetime-local"
                className="input py-1 px-2.5 text-xs w-full bg-surface border-border/60"
                value={scheduledTime}
                onChange={(e) => setScheduledTime(e.target.value)}
                disabled={busy !== null}
              />
            </div>
            <button
              onClick={() => publish(true)}
              className="btn-ghost btn-sm py-2.5 px-4 self-stretch sm:self-end"
              disabled={busy !== null || !metaConfigured || !scheduledTime}
            >
              {busy === "schedule" ? "Scheduling..." : "Schedule Post"}
            </button>
          </div>
        )}
      </div>

      {/* Post URL Link */}
      {asset?.external_id && (
        <div className="pt-1.5 text-xs font-semibold flex items-center">
          {String(asset.external_id).startsWith("http") ? (
            <a
              href={asset.external_id}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:text-primary-hover flex items-center gap-1"
            >
              <span>View Published Post</span>
              <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>
          ) : (
            <span className="text-muted/70 font-mono">Meta ID: {asset.external_id}</span>
          )}
        </div>
      )}

      {message && (
        <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-xs font-semibold text-emerald-400">
          {message}
        </div>
      )}
      {(error || asset?.error) && (
        <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-xs font-semibold text-rose-400 leading-normal break-words">
          {error || asset?.error}
        </div>
      )}
    </div>
  );
}

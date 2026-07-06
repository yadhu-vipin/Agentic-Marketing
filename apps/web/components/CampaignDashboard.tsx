"use client";

import { useState } from "react";
import {
  PLATFORM_LABELS,
  type Campaign,
  type CampaignAsset,
} from "@/lib/types";

export function CampaignDashboard({
  campaign,
  metaConfigured,
}: {
  campaign: Campaign;
  metaConfigured: boolean;
}) {
  if (campaign.workflow === "lead_generation") {
    const leads = campaign.results && campaign.results.workflow === "lead_generation"
      ? campaign.results.leads
      : [];
    return <LeadsDashboard leads={leads} />;
  }

  return (
    <div className="grid gap-5 lg:grid-cols-2">
      {campaign.assets.map((asset) => (
        <AssetCard
          key={asset.id}
          campaignId={campaign.id}
          initial={asset}
          metaConfigured={metaConfigured}
        />
      ))}
    </div>
  );
}

function LeadsDashboard({ leads }: { leads: any[] }) {
  if (!leads || leads.length === 0) {
    return (
      <div className="card text-center py-10 text-muted col-span-2">
        No leads discovered for this campaign.
      </div>
    );
  }

  return (
    <div className="space-y-6 col-span-2">
      <div className="flex items-center justify-between border-b border-border pb-3">
        <h2 className="text-xl font-bold">Discovered B2B Leads ({leads.length})</h2>
      </div>
      <div className="grid gap-5 md:grid-cols-2">
        {leads.map((lead, idx) => (
          <LeadCard key={lead.id || idx} lead={lead} />
        ))}
      </div>
    </div>
  );
}

function LeadCard({ lead }: { lead: any }) {
  const [activeTab, setActiveTab] = useState<"email" | "whatsapp">("email");

  const scoreColor = lead.score >= 80 ? "text-[#58c0a8] font-bold" : "text-muted";
  const priorityStyle = lead.priority === "high" ? "chip-on" : "";

  return (
    <div className="card space-y-4 flex flex-col justify-between h-full bg-[#182421] border border-border/40">
      <div className="space-y-3">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="font-semibold text-lg text-foreground">{lead.name}</h3>
            {lead.category && (
              <p className="text-xs text-accent font-medium mt-0.5">{lead.category}</p>
            )}
          </div>
          <div className="flex flex-col items-end gap-1.5">
            {lead.priority && (
              <span className={`chip text-xs ${priorityStyle} select-none`}>
                {lead.priority} priority
              </span>
            )}
            {lead.score !== null && (
              <span className="text-xs text-muted">
                Score: <span className={scoreColor}>{lead.score}</span>/100
              </span>
            )}
          </div>
        </div>

        {lead.score_reason && (
          <p className="text-xs text-muted bg-[#121c19]/70 p-2.5 rounded border border-border/30">
            <strong>Reason:</strong> {lead.score_reason}
          </p>
        )}

        <div className="grid grid-cols-2 gap-2 text-xs text-muted pt-2 border-t border-border/30">
          {lead.rating !== null && (
            <div className="col-span-2">
              <span>Rating:</span> <strong className="text-foreground">★ {lead.rating}</strong> {lead.reviews !== null && `(${lead.reviews} reviews)`}
            </div>
          )}
          {lead.phone && (
            <div className="col-span-2 sm:col-span-1">
              <span>Phone:</span> <a href={`tel:${lead.phone}`} className="text-accent hover:underline ml-1">{lead.phone}</a>
            </div>
          )}
          {lead.website && (
            <div className="col-span-2 sm:col-span-1 truncate">
              <span>Website:</span> <a href={lead.website} target="_blank" rel="noopener noreferrer" className="text-accent hover:underline ml-1">{lead.website}</a>
            </div>
          )}
          {lead.email && (
            <div className="col-span-2 truncate">
              <span>Email:</span> <a href={`mailto:${lead.email}`} className="text-accent hover:underline ml-1">{lead.email}</a>
            </div>
          )}
          {lead.address && (
            <div className="col-span-2 pt-1">
              <span>Address:</span> <span className="text-foreground/80 block mt-0.5">{lead.address}</span>
            </div>
          )}
        </div>
      </div>

      <div className="space-y-3 pt-3 border-t border-border/30">
        <div className="flex gap-2">
          {lead.outreach?.email && (
            <button
              onClick={() => setActiveTab("email")}
              className={`btn-sm px-3 py-1 rounded text-xs transition-all ${
                activeTab === "email"
                  ? "bg-[#1f3731] text-accent border border-accent/40"
                  : "bg-transparent text-muted hover:text-foreground"
              }`}
            >
              Email Draft
            </button>
          )}
          {lead.outreach?.whatsapp && (
            <button
              onClick={() => setActiveTab("whatsapp")}
              className={`btn-sm px-3 py-1 rounded text-xs transition-all ${
                activeTab === "whatsapp"
                  ? "bg-[#1f3731] text-accent border border-accent/40"
                  : "bg-transparent text-muted hover:text-foreground"
              }`}
            >
              WhatsApp Draft
            </button>
          )}
        </div>

        {activeTab === "email" && lead.outreach?.email && (
          <div className="space-y-1">
            <label className="label text-[11px] text-muted uppercase tracking-wider">Personalized Email outreach</label>
            <textarea
              className="textarea text-xs h-32 font-mono bg-[#0e1614] border-border/20 text-foreground/90 p-2 w-full rounded"
              readOnly
              value={lead.outreach.email}
            />
          </div>
        )}

        {activeTab === "whatsapp" && lead.outreach?.whatsapp && (
          <div className="space-y-1">
            <label className="label text-[11px] text-muted uppercase tracking-wider">Personalized WhatsApp outreach</label>
            <textarea
              className="textarea text-xs h-32 font-mono bg-[#0e1614] border-border/20 text-foreground/90 p-2 w-full rounded"
              readOnly
              value={lead.outreach.whatsapp}
            />
          </div>
        )}

        {lead.outreach?.image_url && (
          <div className="mt-2 space-y-1.5">
            <label className="label text-[11px] text-muted uppercase tracking-wider">Generated Outreach Creative</label>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={lead.outreach.image_url}
              alt="Lead creative"
              className="aspect-square w-full rounded border border-border/20 object-cover bg-[#0e1614]"
              loading="lazy"
            />
          </div>
        )}
      </div>
    </div>
  );
}

const STATUS_STYLE: Record<string, string> = {
  draft: "",
  scheduled: "chip-on",
  publishing: "chip-on",
  published: "chip-on",
  failed: "",
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
  const [asset, setAsset] = useState<CampaignAsset>(initial);
  const [headline, setHeadline] = useState(initial.headline);
  const [body, setBody] = useState(initial.body);
  const [hashtags, setHashtags] = useState(initial.hashtags.join(" "));
  const [cta, setCta] = useState(initial.cta);
  const [scheduledTime, setScheduledTime] = useState("");
  const [busy, setBusy] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const base = `/api/campaigns/${campaignId}/assets/${asset.id}`;
  const canPublishHere = asset.platform === "instagram" || asset.platform === "facebook";

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
      setAsset(data.asset);
      setHashtags(data.asset.hashtags.join(" "));
      setMessage("Saved.");
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
        body: JSON.stringify({ creative_prompt: asset.creative_prompt }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Regenerate failed");
      setAsset(data.asset);
      setMessage("New creative generated.");
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
      setAsset(data.asset);
      setMessage(
        data.asset.status === "scheduled"
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
    <div className="card space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">{PLATFORM_LABELS[asset.platform]}</h3>
        <span className={`chip ${STATUS_STYLE[asset.status] ?? ""}`}>
          {asset.status}
        </span>
      </div>

      {asset.creative_url ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={asset.creative_url}
          alt={`${asset.platform} creative`}
          className="aspect-square w-full rounded-lg border border-border object-cover"
          loading="lazy"
        />
      ) : (
        <div className="flex aspect-square w-full items-center justify-center rounded-lg border border-border bg-surface text-sm text-muted">
          No creative yet
        </div>
      )}

      <button
        type="button"
        onClick={regenerateCreative}
        className="btn-ghost btn-sm w-full"
        disabled={busy !== null}
      >
        {busy === "creative" ? "Generating…" : "Regenerate creative"}
      </button>

      <div>
        <label className="label">Headline</label>
        <input
          className="input"
          value={headline}
          onChange={(e) => setHeadline(e.target.value)}
        />
      </div>

      <div>
        <label className="label">Post copy</label>
        <textarea
          className="textarea"
          value={body}
          onChange={(e) => setBody(e.target.value)}
        />
      </div>

      <div>
        <label className="label">Hashtags (space separated)</label>
        <input
          className="input"
          value={hashtags}
          onChange={(e) => setHashtags(e.target.value)}
        />
      </div>

      <div>
        <label className="label">Call to action</label>
        <input className="input" value={cta} onChange={(e) => setCta(e.target.value)} />
      </div>

      <div className="flex flex-wrap gap-2">
        <button onClick={save} className="btn-ghost btn-sm" disabled={busy !== null}>
          {busy === "save" ? "Saving…" : "Save edits"}
        </button>

        {canPublishHere ? (
          <>
            <button
              onClick={() => publish(false)}
              className="btn btn-sm"
              disabled={busy !== null || !metaConfigured}
              title={metaConfigured ? "" : "Configure Meta to publish"}
            >
              {busy === "publish" ? "Publishing…" : "Publish now"}
            </button>
            {asset.platform === "facebook" && (
              <div className="flex items-center gap-2">
                <input
                  type="datetime-local"
                  className="input btn-sm w-auto"
                  value={scheduledTime}
                  onChange={(e) => setScheduledTime(e.target.value)}
                />
                <button
                  onClick={() => publish(true)}
                  className="btn-ghost btn-sm"
                  disabled={busy !== null || !metaConfigured || !scheduledTime}
                >
                  {busy === "schedule" ? "Scheduling…" : "Schedule"}
                </button>
              </div>
            )}
          </>
        ) : (
          <span className="chip">Generate-only (no API publish)</span>
        )}
      </div>

      {asset.external_id && (
        <p className="text-xs text-muted">
          {asset.external_id.startsWith("http") ? (
            <a
              href={asset.external_id}
              target="_blank"
              rel="noopener noreferrer"
              className="text-accent hover:underline inline-flex items-center gap-1"
            >
              View on {asset.platform === "instagram" ? "Instagram" : "Facebook"} ↗
            </a>
          ) : (
            `Meta ID: ${asset.external_id}`
          )}
        </p>
      )}
      {message && <p className="text-sm text-primary">{message}</p>}
      {(error || asset.error) && (
        <p className="text-sm text-danger">{error || asset.error}</p>
      )}
    </div>
  );
}

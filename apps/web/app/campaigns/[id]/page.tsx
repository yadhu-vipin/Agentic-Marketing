import Link from "next/link";
import { notFound } from "next/navigation";
import { getCurrentUser } from "@/lib/auth";
import { getRepo } from "@/lib/db/repo";
import { CampaignDashboard } from "@/components/CampaignDashboard";

export const dynamic = "force-dynamic";

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

export default async function CampaignPage({
  params,
}: {
  params: { id: string };
}) {
  const user = await getCurrentUser();
  const campaign = await getRepo().getCampaign(user.id, params.id);
  if (!campaign) notFound();

  const metaConfigured = await isMetaConfiguredOnBackend();

  return (
    <div className="space-y-6">
      {/* Back and Title */}
      <div>
        <Link href="/campaigns" className="text-xs font-semibold text-primary/95 hover:text-primary flex items-center gap-1 transition">
          <svg className="h-4.5 w-4.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          <span>Back to Campaigns</span>
        </Link>
        <h1 className="mt-3 text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
          {campaign.product_name}
        </h1>
        <p className="text-xs text-muted mt-0.5">
          {campaign.workflow === "lead_generation"
            ? "Review scraped Google Maps profiles, matching intent criteria, and outreach drafts."
            : "Review platform-specific copy versions, custom AI graphics, and direct publishing status."}
        </p>
      </div>

      {campaign.workflow !== "lead_generation" && !metaConfigured && (
        <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4 text-xs text-amber-400 flex items-start gap-3 shadow-md">
          <div className="mt-0.5 text-amber-400">
            <svg className="h-4.5 w-4.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <div className="space-y-1">
            <span className="font-semibold block text-[13px]">Meta API integration is not configured on the backend</span>
            <p className="text-muted/90 leading-normal">
              To publish posts directly to Facebook/Instagram pages from the dashboard, you need to provide your <code>META_ACCESS_TOKEN</code>, <code>META_PAGE_ID</code>, and <code>META_IG_USER_ID</code> as environment variables on Railway. You can still generate and edit all copies here in the meantime.
            </p>
          </div>
        </div>
      )}

      <CampaignDashboard campaign={campaign} metaConfigured={metaConfigured} />
    </div>
  );
}

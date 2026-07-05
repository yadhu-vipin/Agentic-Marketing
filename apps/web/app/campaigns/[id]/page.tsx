import Link from "next/link";
import { notFound } from "next/navigation";
import { getCurrentUser } from "@/lib/auth";
import { getRepo } from "@/lib/db/repo";
import { isMetaConfigured } from "@/lib/meta/config";
import { CampaignDashboard } from "@/components/CampaignDashboard";

export const dynamic = "force-dynamic";

export default async function CampaignPage({
  params,
}: {
  params: { id: string };
}) {
  const user = await getCurrentUser();
  const campaign = await getRepo().getCampaign(user.id, params.id);
  if (!campaign) notFound();

  return (
    <div className="space-y-6">
      <div>
        <Link href="/campaigns" className="text-sm text-accent">
          ← Campaigns
        </Link>
        <h1 className="mt-2 text-2xl font-bold">{campaign.product_name}</h1>
        <p className="text-muted">
          {campaign.workflow === "lead_generation"
            ? "Review discovered leads and outreach drafts."
            : "Review, edit, then publish or schedule each post."}
        </p>
      </div>

      {campaign.workflow !== "lead_generation" && !isMetaConfigured() && (
        <div className="card border-accent/30 text-sm text-muted">
          Meta publishing is not configured. Add <code>META_ACCESS_TOKEN</code>,{" "}
          <code>META_PAGE_ID</code>, and <code>META_IG_USER_ID</code> to publish to
          Facebook and Instagram. You can still review and edit content now.
        </div>
      )}

      <CampaignDashboard campaign={campaign} metaConfigured={isMetaConfigured()} />
    </div>
  );
}

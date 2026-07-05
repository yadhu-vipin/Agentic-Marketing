import Link from "next/link";
import { getCurrentUser } from "@/lib/auth";
import { getRepo } from "@/lib/db/repo";
import { PLATFORM_LABELS } from "@/lib/types";

export const dynamic = "force-dynamic";

export default async function CampaignsPage() {
  const user = await getCurrentUser();
  const campaigns = await getRepo().listCampaigns(user.id);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Campaigns</h1>
          <p className="text-muted">Generated content bundles.</p>
        </div>
        <Link href="/products" className="btn-ghost">
          From a product
        </Link>
      </div>

      {campaigns.length === 0 ? (
        <div className="card text-center text-muted">
          No campaigns yet. Pick a product and generate one.
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {campaigns.map((c) => (
            <Link key={c.id} href={`/campaigns/${c.id}`} className="card block">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold">{c.product_name}</h3>
                <span className="chip">{c.status}</span>
              </div>
              <p className="mt-1 text-xs text-muted">
                {new Date(c.created_at).toLocaleString()}
              </p>
              <div className="mt-3 flex flex-wrap gap-1">
                {c.workflow === "lead_generation" ? (
                  <span className="chip chip-on">Lead Generation</span>
                ) : c.platforms.length > 0 ? (
                  c.platforms.map((p) => (
                    <span key={p} className="chip chip-on">
                      {PLATFORM_LABELS[p]}
                    </span>
                  ))
                ) : (
                  <span className="chip">Campaign</span>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

import Link from "next/link";
import { getCurrentUser } from "@/lib/auth";
import { getRepo } from "@/lib/db/repo";
import { PLATFORM_LABELS } from "@/lib/types";

export const dynamic = "force-dynamic";

const STATUS_BADGES: Record<string, string> = {
  draft: "badge-muted",
  active: "badge-info",
  completed: "badge-success",
  failed: "badge-danger",
};

export default async function CampaignsPage() {
  const user = await getCurrentUser();
  const campaigns = await getRepo().listCampaigns(user.id);

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-border/60 pb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <svg className="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Campaigns
          </h1>
          <p className="text-sm text-muted">Review, publish, and track your active campaign assets.</p>
        </div>
        <Link href="/products" className="btn-ghost flex items-center gap-1.5 self-start sm:self-auto py-2 px-4">
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          Select Product
        </Link>
      </div>

      {campaigns.length === 0 ? (
        /* Empty State */
        <div className="card text-center max-w-lg mx-auto py-12 px-6 flex flex-col items-center gap-4 border-dashed border-2">
          <div className="rounded-full bg-surface border border-border/80 p-4 text-muted/60">
            <svg className="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </div>
          <div>
            <h3 className="font-semibold text-lg text-foreground">No campaigns generated yet</h3>
            <p className="text-sm text-muted mt-1 max-w-xs mx-auto">
              Choose a product and run an organic or B2B outreach campaign generator.
            </p>
          </div>
          <Link href="/products" className="btn btn-sm mt-2 flex items-center gap-1.5">
            <span>Select a Product</span>
            <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        </div>
      ) : (
        /* Campaigns Grid */
        <div className="grid gap-6 md:grid-cols-2">
          {campaigns.map((c) => (
            <Link key={c.id} href={`/campaigns/${c.id}`} className="card-interactive block group">
              <div className="flex items-start justify-between gap-4">
                <div className="space-y-1 truncate">
                  <h3 className="font-semibold text-base text-foreground group-hover:text-primary transition duration-200 truncate">
                    {c.product_name}
                  </h3>
                  <p className="text-[10px] text-muted/75 flex items-center gap-1.5">
                    <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {new Date(c.created_at).toLocaleString(undefined, {
                      month: "short",
                      day: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </p>
                </div>
                <span className={`badge ${STATUS_BADGES[c.status] || "badge-muted"} capitalize`}>
                  {c.status}
                </span>
              </div>

              <div className="mt-5 pt-4 border-t border-border/40 flex items-center justify-between gap-3">
                <div className="flex flex-wrap gap-1.5">
                  {c.workflow === "lead_generation" ? (
                    <span className="chip chip-on text-[10px] font-semibold flex items-center gap-1 py-0.5 px-2.5">
                      <span className="relative flex h-1.5 w-1.5">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary/40 opacity-75" />
                        <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-primary" />
                      </span>
                      B2B Lead Discovery
                    </span>
                  ) : c.platforms && c.platforms.length > 0 ? (
                    c.platforms.map((p) => (
                      <span key={p} className="chip chip-on text-[10px] font-semibold py-0.5 px-2.5">
                        {PLATFORM_LABELS[p]}
                      </span>
                    ))
                  ) : (
                    <span className="chip text-[10px] font-semibold py-0.5 px-2.5">Social Post</span>
                  )}
                </div>

                <span className="text-xs font-semibold text-primary/80 group-hover:text-primary flex items-center gap-1 transition duration-200">
                  <span>View Details</span>
                  <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                  </svg>
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

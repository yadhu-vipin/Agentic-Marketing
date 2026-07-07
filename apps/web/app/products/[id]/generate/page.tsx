import Link from "next/link";
import { notFound } from "next/navigation";
import { getCurrentUser } from "@/lib/auth";
import { getRepo } from "@/lib/db/repo";
import { GenerateForm } from "@/components/GenerateForm";

export const dynamic = "force-dynamic";

export default async function GenerateCampaignPage({
  params,
}: {
  params: { id: string };
}) {
  const user = await getCurrentUser();
  const product = await getRepo().getProduct(user.id, params.id);
  if (!product) notFound();

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      {/* Navigation and Title */}
      <div>
        <Link href="/products" className="text-xs font-semibold text-primary/95 hover:text-primary flex items-center gap-1 transition">
          <svg className="h-4.5 w-4.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          <span>Back to Products</span>
        </Link>
        <h1 className="mt-3 text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
          <span>Generate Campaign</span>
        </h1>
        <p className="text-xs text-muted mt-0.5">
          Configure a campaign workflow for <span className="font-semibold text-foreground">{product.name}</span>.
        </p>
      </div>

      {/* Product Summary Card */}
      <div className="card space-y-3.5 border-border/80 bg-surface/30">
        <div className="flex items-center justify-between border-b border-border/40 pb-2">
          <h2 className="font-semibold text-sm text-foreground/90 uppercase tracking-wider">Product Scope</h2>
          {product.industry && (
            <span className="badge badge-muted text-[10px] uppercase font-semibold">
              {product.industry}
            </span>
          )}
        </div>
        <p className="text-xs text-muted/90 leading-relaxed">{product.description || "No description provided."}</p>
        
        {product.features && product.features.length > 0 && (
          <div className="flex flex-wrap gap-1.5 pt-1.5">
            {product.features.map((f) => (
              <span key={f} className="chip bg-surface text-[10px] py-0.5 px-2 font-medium">
                {f}
              </span>
            ))}
          </div>
        )}

        {product.target_audience && (
          <div className="pt-2 border-t border-border/30 text-[10px] text-muted/70 flex items-center gap-1.5">
            <svg className="h-3.5 w-3.5 text-primary/70" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <span>Target Audience: <strong className="text-foreground/80">{product.target_audience}</strong></span>
          </div>
        )}
      </div>

      <GenerateForm productId={product.id} defaultAudience={product.target_audience || ""} />
    </div>
  );
}

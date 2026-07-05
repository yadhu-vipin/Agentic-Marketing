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
      <div>
        <Link href="/products" className="text-sm text-accent">
          ← Products
        </Link>
        <h1 className="mt-2 text-2xl font-bold">Generate campaign</h1>
        <p className="text-muted">
          For <span className="font-semibold text-[#e6f1ee]">{product.name}</span>
        </p>
      </div>

      <div className="card space-y-2">
        <h2 className="font-semibold">Product summary</h2>
        <p className="text-sm text-muted">{product.description || "No description"}</p>
        <div className="flex flex-wrap gap-1 pt-1">
          {product.features.map((f) => (
            <span key={f} className="chip">
              {f}
            </span>
          ))}
        </div>
        <p className="pt-1 text-xs text-muted">
          Audience: {product.target_audience || "—"} · Industry:{" "}
          {product.industry || "—"}
        </p>
      </div>

      <GenerateForm productId={product.id} defaultAudience={product.target_audience || ""} />
    </div>
  );
}

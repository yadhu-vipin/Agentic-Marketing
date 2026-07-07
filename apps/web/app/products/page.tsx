import Link from "next/link";
import { getCurrentUser } from "@/lib/auth";
import { getRepo } from "@/lib/db/repo";

export const dynamic = "force-dynamic";

export default async function ProductsPage() {
  const user = await getCurrentUser();
  const products = await getRepo().listProducts(user.id);

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-border/60 pb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <svg className="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
            Products
          </h1>
          <p className="text-sm text-muted">Your active product knowledge base for AI campaign execution.</p>
        </div>
        <Link href="/products/new" className="btn flex items-center gap-1.5 self-start sm:self-auto">
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          New Product
        </Link>
      </div>

      {products.length === 0 ? (
        /* Empty State */
        <div className="card text-center max-w-lg mx-auto py-12 px-6 flex flex-col items-center gap-4 border-dashed border-2">
          <div className="rounded-full bg-surface border border-border/80 p-4 text-muted/60">
            <svg className="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
            </svg>
          </div>
          <div>
            <h3 className="font-semibold text-lg text-foreground">No products added yet</h3>
            <p className="text-sm text-muted mt-1 max-w-xs mx-auto">
              Add your first product to train the AI agent and generate tailored social media assets.
            </p>
          </div>
          <Link href="/products/new" className="btn btn-sm mt-2 flex items-center gap-1.5">
            <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
            </svg>
            Add Product Now
          </Link>
        </div>
      ) : (
        /* Products Grid */
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {products.map((p) => (
            <div key={p.id} className="card-interactive flex flex-col justify-between group">
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  {p.logo_url ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={p.logo_url}
                      alt={p.name}
                      className="h-11 w-11 rounded-lg object-cover border border-border bg-surface shadow-sm"
                    />
                  ) : (
                    <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-gradient-to-br from-primary/10 to-primary/30 border border-primary/20 text-sm font-bold text-primary shadow-sm shadow-primary/5">
                      {p.name.slice(0, 1).toUpperCase()}
                    </div>
                  )}
                  <div className="truncate">
                    <h3 className="font-semibold text-foreground group-hover:text-primary transition duration-200 truncate">{p.name}</h3>
                    <p className="text-xs text-muted/80 font-medium truncate">
                      {p.industry ? p.industry : "General"}
                    </p>
                  </div>
                </div>
                
                <p className="line-clamp-3 text-xs text-muted/90 leading-relaxed min-h-[54px]">{p.description}</p>
                
                {p.features && p.features.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {p.features.slice(0, 3).map((f) => (
                      <span key={f} className="chip bg-surface/80 text-[10px] py-0.5 px-2 font-semibold">
                        {f}
                      </span>
                    ))}
                    {p.features.length > 3 && (
                      <span className="chip bg-surface/80 text-[10px] py-0.5 px-2 font-semibold">
                        +{p.features.length - 3} more
                      </span>
                    )}
                  </div>
                )}
              </div>

              <div className="mt-6 flex items-center justify-between gap-3 pt-4 border-t border-border/40">
                <span className="text-[10px] text-muted/65 flex items-center gap-1">
                  <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  {p.created_at ? new Date(p.created_at).toLocaleDateString(undefined, {month: 'short', day: 'numeric'}) : "Just now"}
                </span>
                
                <Link
                  href={`/products/${p.id}/generate`}
                  className="btn btn-sm flex items-center gap-1 px-4 py-1.5"
                >
                  <span>Launch Campaign</span>
                  <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                  </svg>
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

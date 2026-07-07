"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function NewProductPage() {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const formData = new FormData(e.currentTarget);
      const res = await fetch("/api/products", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to create product");
      router.push(`/products/${data.product.id}/generate`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      {/* Title */}
      <div>
        <Link href="/products" className="text-xs font-semibold text-primary/95 hover:text-primary flex items-center gap-1 transition">
          <svg className="h-4.5 w-4.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          <span>Back to Products</span>
        </Link>
        <h1 className="mt-3 text-2xl font-bold tracking-tight text-foreground">Add a product</h1>
        <p className="text-xs text-muted mt-0.5">
          Train the AI agents by building your product information base.
        </p>
      </div>

      <form onSubmit={onSubmit} className="card space-y-5 relative">
        <div className="space-y-4">
          <div>
            <label className="label">Product Name *</label>
            <input name="name" className="input" placeholder="e.g. Acme Analytics Platform" required disabled={submitting} />
          </div>

          <div>
            <label className="label">Product Description</label>
            <textarea
              name="description"
              className="textarea h-24"
              placeholder="Detail what the product does, its core value proposition, and the main problems it solves."
              disabled={submitting}
            />
          </div>

          <div>
            <label className="label">Key Features (One per line)</label>
            <textarea
              name="features"
              className="textarea h-28 font-mono text-xs"
              placeholder={"e.g.\nRealtime event tracking\nCustom multi-touch attribution\nAutomated cohort reporting"}
              disabled={submitting}
            />
            <p className="text-[10px] text-muted/70 mt-1">Provide up to 5 main highlights to drive copy generation.</p>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="label">Target Audience</label>
              <input
                name="target_audience"
                className="input"
                placeholder="e.g. growth marketers, developers"
                disabled={submitting}
              />
            </div>
            <div>
              <label className="label">Industry / Niche</label>
              <input name="industry" className="input" placeholder="e.g. Analytics / SaaS" disabled={submitting} />
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-2 pt-2 border-t border-border/40">
            <div>
              <label className="label">Brand Logo</label>
              <div className="relative">
                <input
                  name="logo"
                  type="file"
                  accept="image/*"
                  className="w-full text-xs text-muted file:mr-4 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-surface file:text-foreground hover:file:bg-border/60 transition"
                  disabled={submitting}
                />
              </div>
            </div>
            <div>
              <label className="label">Product Assets / Screenshots</label>
              <div className="relative">
                <input
                  name="images"
                  type="file"
                  accept="image/*"
                  multiple
                  className="w-full text-xs text-muted file:mr-4 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-surface file:text-foreground hover:file:bg-border/60 transition"
                  disabled={submitting}
                />
              </div>
            </div>
          </div>
        </div>

        {error && (
          <div className="p-3 rounded bg-rose-500/10 border border-rose-500/20 text-xs font-medium text-rose-400">
            {error}
          </div>
        )}

        <div className="flex items-center gap-3 pt-4 border-t border-border/40">
          <button type="submit" className="btn flex items-center gap-1.5 px-6" disabled={submitting}>
            {submitting ? (
              <>
                <svg className="animate-spin h-3.5 w-3.5 text-[#04130d]" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                <span>Saving Product...</span>
              </>
            ) : (
              <>
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
                <span>Save & Continue</span>
              </>
            )}
          </button>
          
          <Link href="/products" className={`btn-ghost btn-sm py-2.5 px-4 ${submitting ? 'pointer-events-none opacity-50' : ''}`}>
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}

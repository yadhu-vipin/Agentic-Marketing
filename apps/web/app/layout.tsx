import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
import { getCurrentUser } from "@/lib/auth";
import HeaderAuth from "@/components/HeaderAuth";

export const metadata: Metadata = {
  title: "Agentic Marketing — Social Campaign Generator",
  description:
    "Upload a product, generate ready-to-post campaigns, and publish to Instagram & Facebook.",
};

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  let email: string | null = null;
  try {
    const user = await getCurrentUser();
    email = user.email;
  } catch {
    // Not logged in
  }

  return (
    <html lang="en">
      <body className="antialiased grid-bg">
        <header className="sticky top-0 z-50 border-b border-border/80 bg-bg/75 backdrop-blur-md">
          <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3.5">
            <Link href="/" className="flex items-center gap-2.5 font-bold tracking-tight text-foreground transition hover:opacity-90">
              <div className="relative flex h-3.5 w-3.5 items-center justify-center">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary/30 opacity-75" />
                <span className="relative h-2.5 w-2.5 rounded-full bg-primary shadow-[0_0_12px_rgba(16,185,129,0.7)]" />
              </div>
              <span className="bg-gradient-to-r from-white to-zinc-300 bg-clip-text text-transparent font-extrabold text-base">
                Agentic Marketing
              </span>
              <span className="hidden sm:inline text-xs font-medium text-muted/70">
                · studio
              </span>
            </Link>
            {email && (
              <nav className="flex items-center gap-3.5 text-sm">
                <Link href="/products" className="chip hover:chip-on flex items-center gap-1.5 py-1 px-3">
                  <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                  </svg>
                  Products
                </Link>
                <Link href="/campaigns" className="chip hover:chip-on flex items-center gap-1.5 py-1 px-3">
                  <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  Campaigns
                </Link>
                <Link href="/products/new" className="btn btn-sm flex items-center gap-1">
                  <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                  </svg>
                  New Product
                </Link>
                <div className="h-4 w-[1px] bg-border/60" />
                <HeaderAuth initialEmail={email} />
              </nav>
            )}
          </div>
        </header>
        <main className="mx-auto max-w-6xl px-6 py-10 min-h-[calc(100vh-65px)]">{children}</main>
      </body>
    </html>
  );
}


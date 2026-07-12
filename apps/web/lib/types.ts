export type Platform = "instagram" | "facebook" | "linkedin";

export const ALL_PLATFORMS: Platform[] = ["instagram", "facebook", "linkedin"];

export const PLATFORM_LABELS: Record<Platform, string> = {
  instagram: "Instagram",
  facebook: "Facebook",
  linkedin: "LinkedIn",
};

export interface Product {
  id: string;
  user_id: string;
  name: string;
  description: string;
  features: string[];
  target_audience: string;
  industry: string;
  logo_url: string | null;
  image_urls: string[];
  created_at: string;
}

export interface ProductInput {
  name: string;
  description: string;
  features: string[];
  target_audience: string;
  industry: string;
  logo_url?: string | null;
  image_urls?: string[];
}

export type CampaignStatus = "draft" | "researching" | "ready" | "partially_published" | "published" | "running" | "failed";

export type AssetStatus =
  | "draft"
  | "scheduled"
  | "publishing"
  | "published"
  | "failed";

export interface CampaignAsset {
  id: string;
  campaign_id: string;
  platform: Platform;
  /** Headline or hook (used for LinkedIn banner / IG title). */
  headline: string;
  /** Main caption or post body. */
  body: string;
  hashtags: string[];
  cta: string;
  creative_prompt: string;
  creative_url: string | null;
  status: AssetStatus;
  scheduled_time: string | null;
  external_id: string | null;
  error: string | null;
}

// ── Polymorphic B2B Lead Gen Types ───────────────────────────────────────────
export interface Lead {
  id: string;
  name: string;
  category: string | null;
  address: string | null;
  phone: string | null;
  email: string | null;
  website: string | null;
  rating: number | null;
  reviews: number | null;
  source: string;
  score: number | null;
  score_reason: string | null;
  priority: "high" | "medium" | "low" | null;
  outreach: {
    email?: string;
    whatsapp?: string;
    image_url?: string | null;
    image_prompt?: string;
    image_mode?: string;
  };
  status?: string;
  error?: string | null;
}

export type WorkflowType = "organic_campaign" | "lead_generation" | "content_only";

export type CampaignConfig =
  | { workflow: "organic_campaign" | "content_only"; data: { platforms: Platform[]; instructions?: string; image_mode?: string } }
  | { workflow: "lead_generation"; data: { location: string; target_audience?: string; scrapers?: string[]; instructions?: string } };

export type CampaignResults =
  | { workflow: "organic_campaign" | "content_only"; assets: CampaignAsset[] }
  | { workflow: "lead_generation"; leads: Lead[]; research_report?: any };

export interface Campaign {
  id: string;
  user_id: string;
  product_id: string;
  product_name: string;
  platforms: Platform[];
  status: CampaignStatus;
  created_at: string;
  
  // Polymorphic Workflow fields
  workflow: WorkflowType;
  config: CampaignConfig;
  results: CampaignResults;

  // Legacy / Organic compatibility
  assets: CampaignAsset[];

  // Phase 2 Demo Fields
  research_report?: any;
}

export interface CurrentUser {
  id: string;
  email: string | null;
  user_metadata: Record<string, any>;
}


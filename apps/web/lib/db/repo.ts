import type {
  Campaign,
  CampaignAsset,
  CampaignStatus,
  Platform,
  Product,
  ProductInput,
  WorkflowType,
  CampaignConfig,
  CampaignResults,
} from "@/lib/types";
import { SupabaseRepo } from "./supabase-repo";

export interface NewCampaignInput {
  product: Product;
  platforms: Platform[];
  workflow: WorkflowType;
  config: CampaignConfig;
  results: CampaignResults;
  assets?: Omit<CampaignAsset, "id" | "campaign_id">[];
}

export interface Repo {
  createProduct(userId: string, input: ProductInput): Promise<Product>;
  listProducts(userId: string): Promise<Product[]>;
  getProduct(userId: string, id: string): Promise<Product | null>;

  createCampaign(userId: string, input: NewCampaignInput): Promise<Campaign>;
  listCampaigns(userId: string): Promise<Campaign[]>;
  getCampaign(userId: string, id: string): Promise<Campaign | null>;
  updateCampaignStatus(
    campaignId: string,
    status: CampaignStatus,
  ): Promise<void>;

  updateCampaignResults(
    campaignId: string,
    results: CampaignResults,
    status?: CampaignStatus,
  ): Promise<Campaign>;

  updateAsset(
    campaignId: string,
    assetId: string,
    patch: Partial<CampaignAsset>,
  ): Promise<CampaignAsset | null>;
}

let cached: Repo | null = null;

export function getRepo(): Repo {
  if (cached) return cached;
  cached = new SupabaseRepo();
  return cached;
}


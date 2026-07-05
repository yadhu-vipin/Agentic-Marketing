import type {
  Campaign,
  CampaignAsset,
  CampaignStatus,
  Product,
  ProductInput,
  CampaignResults,
} from "@/lib/types";
import type { NewCampaignInput, Repo } from "./repo";

/**
 * In-memory store for demo mode. Persists for the lifetime of the server
 * process. Uses a global to survive Next.js dev hot-reloads.
 */
interface Store {
  products: Product[];
  campaigns: Campaign[];
}

const globalForStore = globalThis as unknown as { __mvpStore?: Store };

function store(): Store {
  if (!globalForStore.__mvpStore) {
    globalForStore.__mvpStore = { products: [], campaigns: [] };
  }
  return globalForStore.__mvpStore;
}

function uid(): string {
  return globalThis.crypto?.randomUUID?.() ?? Math.random().toString(36).slice(2);
}

export class MemoryRepo implements Repo {
  async createProduct(userId: string, input: ProductInput): Promise<Product> {
    const product: Product = {
      id: uid(),
      user_id: userId,
      name: input.name,
      description: input.description,
      features: input.features,
      target_audience: input.target_audience,
      industry: input.industry,
      logo_url: input.logo_url ?? null,
      image_urls: input.image_urls ?? [],
      created_at: new Date().toISOString(),
    };
    store().products.unshift(product);
    return product;
  }

  async listProducts(userId: string): Promise<Product[]> {
    return store().products.filter((p) => p.user_id === userId);
  }

  async getProduct(userId: string, id: string): Promise<Product | null> {
    return (
      store().products.find((p) => p.id === id && p.user_id === userId) ?? null
    );
  }

  async createCampaign(
    userId: string,
    input: NewCampaignInput,
  ): Promise<Campaign> {
    const campaignId = uid();
    const assets: CampaignAsset[] = (input.assets ?? []).map((a) => ({
      ...a,
      id: uid(),
      campaign_id: campaignId,
    }));
    const campaign: Campaign = {
      id: campaignId,
      user_id: userId,
      product_id: input.product.id,
      product_name: input.product.name,
      platforms: input.platforms,
      status: "ready",
      created_at: new Date().toISOString(),
      workflow: input.workflow,
      config: input.config,
      results: input.results,
      assets,
    };
    store().campaigns.unshift(campaign);
    return campaign;
  }

  async listCampaigns(userId: string): Promise<Campaign[]> {
    return store().campaigns.filter((c) => c.user_id === userId);
  }

  async getCampaign(userId: string, id: string): Promise<Campaign | null> {
    return (
      store().campaigns.find((c) => c.id === id && c.user_id === userId) ?? null
    );
  }

  async updateCampaignStatus(
    campaignId: string,
    status: CampaignStatus,
  ): Promise<void> {
    const campaign = store().campaigns.find((c) => c.id === campaignId);
    if (campaign) campaign.status = status;
  }

  async updateCampaignResults(
    campaignId: string,
    results: CampaignResults,
    status?: CampaignStatus,
  ): Promise<Campaign> {
    const campaign = store().campaigns.find((c) => c.id === campaignId);
    if (!campaign) throw new Error("Campaign not found");
    campaign.results = results;
    if (status) campaign.status = status;
    return campaign;
  }

  async updateAsset(
    campaignId: string,
    assetId: string,
    patch: Partial<CampaignAsset>,
  ): Promise<CampaignAsset | null> {
    const campaign = store().campaigns.find((c) => c.id === campaignId);
    if (!campaign) return null;
    const asset = campaign.assets.find((a) => a.id === assetId);
    if (!asset) return null;
    Object.assign(asset, patch);
    return asset;
  }
}

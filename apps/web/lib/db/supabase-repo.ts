import type { SupabaseClient } from "@supabase/supabase-js";
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
import { createSupabaseServerClient } from "@/lib/supabase/server";
import type { NewCampaignInput, Repo } from "./repo";

function client(): SupabaseClient {
  const supabase = createSupabaseServerClient();
  if (!supabase) {
    throw new Error("Supabase is not configured.");
  }
  return supabase;
}

type DbRow = Record<string, unknown>;

function asString(value: unknown, fallback = ""): string {
  return typeof value === "string" ? value : fallback;
}

function asStringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.map(String) : [];
}

function mapProduct(row: DbRow): Product {
  return {
    id: String(row.id),
    user_id: String(row.user_id),
    name: asString(row.name),
    description: asString(row.description),
    features: asStringArray(row.features),
    target_audience: asString(row.target_audience),
    industry: asString(row.industry),
    logo_url: typeof row.logo_url === "string" ? row.logo_url : null,
    image_urls: asStringArray(row.image_urls),
    created_at: asString(row.created_at),
  };
}

function mapAsset(row: DbRow): CampaignAsset {
  return {
    id: String(row.id),
    campaign_id: String(row.campaign_id),
    platform: asString(row.platform) as Platform,
    headline: asString(row.headline),
    body: asString(row.body),
    hashtags: asStringArray(row.hashtags),
    cta: asString(row.cta),
    creative_prompt: asString(row.creative_prompt),
    creative_url: typeof row.creative_url === "string" ? row.creative_url : null,
    status: (asString(row.status, "draft") || "draft") as CampaignAsset["status"],
    scheduled_time: typeof row.scheduled_time === "string" ? row.scheduled_time : null,
    external_id: typeof row.external_id === "string" ? row.external_id : null,
    error: typeof row.error === "string" ? row.error : null,
  };
}

function mapCampaign(row: DbRow): Campaign {
  const assets = Array.isArray(row.campaign_assets)
    ? row.campaign_assets.map((a) => mapAsset(a as DbRow))
    : [];
  const workflow = (asString(row.workflow) || "organic_campaign") as WorkflowType;
  
  // Parse JSONB columns or fallback to valid default structures
  const config = (row.config && typeof row.config === "object"
    ? row.config
    : { workflow, data: { platforms: [] } }) as CampaignConfig;
    
  const results = (row.results && typeof row.results === "object"
    ? row.results
    : { workflow, assets: [] }) as CampaignResults;

  return {
    id: String(row.id),
    user_id: String(row.user_id),
    product_id: String(row.product_id),
    product_name: asString(row.product_name),
    platforms: asStringArray(row.platforms) as Platform[],
    status: (asString(row.status, "draft") || "draft") as CampaignStatus,
    created_at: asString(row.created_at),
    workflow,
    config,
    results,
    assets,
  };
}

function isUuid(str: string): boolean {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(str);
}

export class SupabaseRepo implements Repo {
  async createProduct(userId: string, input: ProductInput): Promise<Product> {
    if (!isUuid(userId)) {
      throw new Error("Authentication required. Please sign in to create products.");
    }
    const { data, error } = await client()
      .from("products")
      .insert({
        user_id: userId,
        name: input.name,
        description: input.description,
        features: input.features,
        target_audience: input.target_audience,
        industry: input.industry,
        logo_url: input.logo_url ?? null,
        image_urls: input.image_urls ?? [],
      })
      .select("*")
      .single();
    if (error) throw new Error(error.message);
    return mapProduct(data);
  }

  async listProducts(userId: string): Promise<Product[]> {
    if (!isUuid(userId)) return [];
    const { data, error } = await client()
      .from("products")
      .select("*")
      .eq("user_id", userId)
      .order("created_at", { ascending: false });
    if (error) throw new Error(error.message);
    return (data ?? []).map(mapProduct);
  }

  async getProduct(userId: string, id: string): Promise<Product | null> {
    if (!isUuid(userId) || !isUuid(id)) return null;
    const { data, error } = await client()
      .from("products")
      .select("*")
      .eq("user_id", userId)
      .eq("id", id)
      .maybeSingle();
    if (error) throw new Error(error.message);
    return data ? mapProduct(data) : null;
  }

  async createCampaign(
    userId: string,
    input: NewCampaignInput,
  ): Promise<Campaign> {
    if (!isUuid(userId)) {
      throw new Error("Authentication required. Please sign in to create campaigns.");
    }
    const supabase = client();
    const { data: campaignRow, error: campaignError } = await supabase
      .from("campaigns")
      .insert({
        user_id: userId,
        product_id: input.product.id,
        product_name: input.product.name,
        platforms: input.platforms,
        status: "ready",
        workflow: input.workflow,
        config: input.config,
        results: input.results,
      })
      .select("*")
      .single();
    if (campaignError) throw new Error(campaignError.message);

    let assets: any[] = [];
    if (input.assets && input.assets.length > 0) {
      const assetRows = input.assets.map((a) => ({
        campaign_id: campaignRow.id,
        platform: a.platform,
        headline: a.headline,
        body: a.body,
        hashtags: a.hashtags,
        cta: a.cta,
        creative_prompt: a.creative_prompt,
        creative_url: a.creative_url,
        status: a.status,
        scheduled_time: a.scheduled_time,
        external_id: a.external_id,
        error: a.error,
      }));

      const { data: insertedAssets, error: assetError } = await supabase
        .from("campaign_assets")
        .insert(assetRows)
        .select("*");
      if (assetError) throw new Error(assetError.message);
      assets = insertedAssets ?? [];
    }

    return mapCampaign({ ...campaignRow, campaign_assets: assets });
  }

  async listCampaigns(userId: string): Promise<Campaign[]> {
    if (!isUuid(userId)) return [];
    const { data, error } = await client()
      .from("campaigns")
      .select("*, campaign_assets(*)")
      .eq("user_id", userId)
      .order("created_at", { ascending: false });
    if (error) throw new Error(error.message);
    return (data ?? []).map(mapCampaign);
  }

  async getCampaign(userId: string, id: string): Promise<Campaign | null> {
    if (!isUuid(userId) || !isUuid(id)) return null;
    const { data, error } = await client()
      .from("campaigns")
      .select("*, campaign_assets(*)")
      .eq("user_id", userId)
      .eq("id", id)
      .maybeSingle();
    if (error) throw new Error(error.message);
    return data ? mapCampaign(data) : null;
  }


  async updateCampaignStatus(
    campaignId: string,
    status: CampaignStatus,
  ): Promise<void> {
    const { error } = await client()
      .from("campaigns")
      .update({ status })
      .eq("id", campaignId);
    if (error) throw new Error(error.message);
  }

  async updateCampaignResults(
    campaignId: string,
    results: CampaignResults,
    status?: CampaignStatus,
  ): Promise<Campaign> {
    const supabase = client();
    const updateData: any = { results };
    if (status) updateData.status = status;

    const { data: campaignRow, error: campaignError } = await supabase
      .from("campaigns")
      .update(updateData)
      .eq("id", campaignId)
      .select("*, campaign_assets(*)")
      .maybeSingle();
    if (campaignError) throw new Error(campaignError.message);
    if (!campaignRow) throw new Error("Campaign not found");
    return mapCampaign(campaignRow);
  }

  async updateAsset(
    campaignId: string,
    assetId: string,
    patch: Partial<CampaignAsset>,
  ): Promise<CampaignAsset | null> {
    const { data, error } = await client()
      .from("campaign_assets")
      .update(patch)
      .eq("id", assetId)
      .eq("campaign_id", campaignId)
      .select("*")
      .maybeSingle();
    if (error) throw new Error(error.message);
    return data ? mapAsset(data) : null;
  }
}

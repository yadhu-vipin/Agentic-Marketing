import { NextResponse } from "next/server";
import { getCurrentUser } from "@/lib/auth";
import { getRepo } from "@/lib/db/repo";
import { generateCampaignContent } from "@/lib/ai/campaign";
import { generateCreative } from "@/lib/creative/generate";
import { ALL_PLATFORMS, type CampaignAsset, type Platform, type WorkflowType } from "@/lib/types";
import { backendClient } from "@/lib/backend";

export async function GET() {
  const user = await getCurrentUser();
  const campaigns = await getRepo().listCampaigns(user.id);
  return NextResponse.json({ campaigns });
}

export async function POST(request: Request) {
  try {
    const user = await getCurrentUser();
    const body = await request.json();
    const productId = String(body.product_id ?? "");
    const workflow = (body.workflow || "organic_campaign") as WorkflowType;

    if (!productId) {
      return NextResponse.json({ error: "product_id is required." }, { status: 400 });
    }

    const repo = getRepo();
    const product = await repo.getProduct(user.id, productId);
    if (!product) {
      return NextResponse.json({ error: "Product not found." }, { status: 404 });
    }

    if (workflow === "lead_generation") {
      const configData = body.config || {};
      const location = String(configData.location ?? "");
      if (!location) {
        return NextResponse.json({ error: "location is required for lead generation." }, { status: 400 });
      }

      const scrapers = Array.isArray(configData.scrapers) ? configData.scrapers : ["google_maps"];
      const targetAudience = configData.target_audience || product.target_audience;
      const instructions = configData.instructions || "";
      const imageMode = configData.image_mode || "none";

      const campaignConfig = {
        workflow: "lead_generation" as const,
        data: {
          location,
          target_audience: targetAudience,
          scrapers,
          instructions,
        }
      };

      const initialResults = {
        workflow: "lead_generation" as const,
        leads: []
      };

      // 1. Create campaign locally in Next.js DB
      const campaign = await repo.createCampaign(user.id, {
        product,
        platforms: [],
        workflow: "lead_generation",
        config: campaignConfig,
        results: initialResults,
        assets: [],
      });

      try {
        // Update status to running
        await repo.updateCampaignStatus(campaign.id, "running" as any);

        // 2. Initialize in the backend
        await backendClient.createCampaign(campaign.id, campaign.product_name, "lead_generation", {
          product_name: product.name,
          product_description: product.description,
          location,
          target_audience: targetAudience,
          scrapers,
          image_mode: imageMode,
          instructions,
        });

        // 3. Run execution
        const finalState = await backendClient.runCampaign(campaign.id);

        // 4. Persist results
        const updatedCampaign = await repo.updateCampaignResults(
          campaign.id,
          { workflow: "lead_generation", leads: finalState.leads || [] },
          "ready"
        );

        return NextResponse.json({ campaign: updatedCampaign, usedAi: true });
      } catch (backendError) {
        console.error("[campaign] backend execution failed:", backendError);
        await repo.updateCampaignStatus(campaign.id, "failed" as any);
        return NextResponse.json(
          { error: backendError instanceof Error ? backendError.message : "Lead generation failed." },
          { status: 502 }
        );
      }

    } else {
      // Legacy Organic Campaign flow
      const platforms: Platform[] = Array.isArray(body.platforms)
        ? body.platforms.filter((p: Platform) => ALL_PLATFORMS.includes(p))
        : [];

      if (platforms.length === 0) {
        return NextResponse.json(
          { error: "Select at least one platform." },
          { status: 400 },
        );
      }

      const { content, usedAi } = await generateCampaignContent(product, platforms);

      const assets: Omit<CampaignAsset, "id" | "campaign_id">[] = [];
      for (const platform of platforms) {
        const c = content[platform];
        let creativeUrl: string | null = null;
        try {
          creativeUrl = await generateCreative(c.creative_prompt, platform);
        } catch (err) {
          console.error("[campaign] creative failed:", err);
        }
        assets.push({
          platform,
          headline: c.headline,
          body: c.body,
          hashtags: c.hashtags,
          cta: c.cta,
          creative_prompt: c.creative_prompt,
          creative_url: creativeUrl,
          status: "draft",
          scheduled_time: null,
          external_id: null,
          error: null,
        });
      }

      const campaign = await repo.createCampaign(user.id, {
        product,
        platforms,
        workflow: "organic_campaign",
        config: { workflow: "organic_campaign", data: { platforms } },
        results: { workflow: "organic_campaign", assets: assets as CampaignAsset[] },
        assets,
      });

      return NextResponse.json({ campaign, usedAi });
    }
  } catch (err) {
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Failed to generate campaign." },
      { status: 500 },
    );
  }
}

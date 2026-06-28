import type { CampaignAsset } from "@/lib/types";
import {
  isMetaConfigured,
  metaAccessToken,
  metaGraphUrl,
  metaIgUserId,
  metaPageId,
  metaGraphVersion,
  instagramAccessToken,
} from "./config";

export interface PublishResult {
  externalId: string;
  scheduled: boolean;
}

export function captionFor(asset: CampaignAsset): string {
  const tags = asset.hashtags.map((h) => `#${h.replace(/^#/, "")}`).join(" ");
  return [asset.body, asset.cta, tags].filter(Boolean).join("\n\n");
}

async function graphPost(
  path: string,
  params: Record<string, string>,
  token: string = metaAccessToken,
): Promise<Record<string, unknown>> {
  const body = new URLSearchParams({ ...params, access_token: token });
  const res = await fetch(metaGraphUrl(path), { method: "POST", body });
  const data = (await res.json()) as Record<string, unknown>;
  if (!res.ok) {
    const err = data?.error as { message?: string } | undefined;
    throw new Error(err?.message || `Meta Graph HTTP ${res.status}`);
  }
  return data;
}

/** Facebook Page photo post, with optional native scheduling. */
async function publishFacebook(
  asset: CampaignAsset,
  scheduledTime: string | null,
): Promise<PublishResult> {
  if (!metaPageId) throw new Error("META_PAGE_ID not configured.");
  if (!asset.creative_url) throw new Error("No creative image to publish.");

  const params: Record<string, string> = {
    url: asset.creative_url,
    caption: captionFor(asset),
  };

  let scheduled = false;
  if (scheduledTime) {
    const ts = Math.floor(new Date(scheduledTime).getTime() / 1000);
    params.published = "false";
    params.scheduled_publish_time = String(ts);
    scheduled = true;
  }

  const data = await graphPost(`${metaPageId}/photos`, params);
  const id = (data.post_id || data.id) as string;
  return { externalId: id, scheduled };
}

/** Instagram Business publish: create container then publish.
 *  Verified sequence (graph.instagram.com, INSTAGRAM_ACCESS_TOKEN):
 *    GET  /me                      → discover igUserId (skipped if META_IG_USER_ID set)
 *    POST /{igUserId}/media        → create media container
 *    POST /{igUserId}/media_publish → publish container
 */
async function publishInstagram(asset: CampaignAsset): Promise<PublishResult> {
  const token = instagramAccessToken || metaAccessToken;
  if (!token) throw new Error("No Instagram access token. Set INSTAGRAM_ACCESS_TOKEN in .env.");
  if (!asset.creative_url) throw new Error("No creative image to publish.");

  const igBase = `https://graph.instagram.com/${metaGraphVersion}`;

  // ── Step 1: GET /me — discover igUserId if not configured ───────────────────
  let igUserId = metaIgUserId;
  if (!igUserId) {
    const meRes = await fetch(`${igBase}/me?access_token=${token}`);
    const meData = (await meRes.json()) as Record<string, unknown>;
    if (!meRes.ok || !meData?.id) {
      throw new Error(
        `Instagram /me failed (HTTP ${meRes.status}): ${JSON.stringify(meData)}. ` +
        "Set META_IG_USER_ID in .env to skip discovery."
      );
    }
    igUserId = String(meData.id);
  }

  // ── Step 2: POST /{igUserId}/media — create media container ─────────────────
  const containerRes = await fetch(`${igBase}/${igUserId}/media`, {
    method: "POST",
    body: new URLSearchParams({
      image_url: asset.creative_url,
      caption: captionFor(asset),
      access_token: token,
    }),
  });
  const containerData = (await containerRes.json()) as Record<string, unknown>;
  if (!containerRes.ok) {
    const err = containerData?.error as { message?: string } | undefined;
    throw new Error(`Instagram /media failed (HTTP ${containerRes.status}): ${err?.message ?? JSON.stringify(containerData)}`);
  }
  const creationId = containerData.id as string;
  if (!creationId) throw new Error("Instagram /media succeeded but returned no container id.");

  // ── Step 3: POST /{igUserId}/media_publish — publish container ───────────────
  const publishRes = await fetch(`${igBase}/${igUserId}/media_publish`, {
    method: "POST",
    body: new URLSearchParams({ creation_id: creationId, access_token: token }),
  });
  const publishData = (await publishRes.json()) as Record<string, unknown>;
  if (!publishRes.ok) {
    const err = publishData?.error as { message?: string } | undefined;
    throw new Error(`Instagram /media_publish failed (HTTP ${publishRes.status}): ${err?.message ?? JSON.stringify(publishData)}`);
  }

  return { externalId: publishData.id as string, scheduled: false };
}

/**
 * Publish (or schedule) a single asset to its platform via the Meta Graph API.
 * Instagram has no native scheduling endpoint, so scheduled IG posts are left
 * for a scheduler/worker and reported back to the caller.
 */
export async function publishAsset(
  asset: CampaignAsset,
  scheduledTime: string | null = null,
): Promise<PublishResult> {
  if (!isMetaConfigured()) {
    throw new Error(
      "Meta publishing is not configured. Set META_ACCESS_TOKEN and page/IG IDs.",
    );
  }

  if (asset.platform === "facebook") {
    return publishFacebook(asset, scheduledTime);
  }
  if (asset.platform === "instagram") {
    if (scheduledTime) {
      throw new Error(
        "Instagram has no native API scheduling. Use a scheduled job to publish at the target time.",
      );
    }
    return publishInstagram(asset);
  }
  throw new Error(
    `Publishing for ${asset.platform} is not supported in this MVP (generate-only).`,
  );
}

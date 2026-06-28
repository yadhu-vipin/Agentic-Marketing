export const metaGraphVersion = process.env.META_GRAPH_VERSION ?? "v21.0";
export const metaAccessToken = process.env.META_ACCESS_TOKEN ?? "";
export const metaPageId = process.env.META_PAGE_ID ?? "";
export const metaIgUserId = process.env.META_IG_USER_ID ?? "";
export const instagramAccessToken = process.env.INSTAGRAM_ACCESS_TOKEN ?? "";

export function isMetaConfigured(): boolean {
  const hasFb = Boolean(metaAccessToken && metaPageId);
  const hasIg = Boolean((instagramAccessToken || metaAccessToken) && metaIgUserId);
  return hasFb || hasIg;
}

export function metaGraphUrl(path: string): string {
  const clean = path.startsWith("/") ? path.slice(1) : path;
  return `https://graph.facebook.com/${metaGraphVersion}/${clean}`;
}

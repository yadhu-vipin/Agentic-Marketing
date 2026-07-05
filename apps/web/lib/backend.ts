import type { WorkflowType } from "./types";

const BACKEND_API_URL = process.env.BACKEND_API_URL || "http://localhost:8000";
const REQUEST_TIMEOUT_MS = 300_000; // 5 minutes — Google Maps scraping + LLM can take a while

export interface BackendCampaignState {
  campaign_id: string;
  workflow_name: string;
  created_at: string;
  product_name: string;
  product_description: string;
  target_audience?: string;
  industry?: string;
  location?: string;
  platforms: string[];
  scrapers: string[];
  image_mode: string;
  instructions: string;
  leads: any[];
  assets: any[];
  research_summary?: string;
  status: string;
  errors: string[];
  log: string[];
}

export class BackendClientError extends Error {
  constructor(
    message: string,
    public status?: number,
    public body?: any,
  ) {
    super(message);
    this.name = "BackendClientError";
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${BACKEND_API_URL.replace(/\/$/, "")}${path}`;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    let responseData: any;
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.includes("application/json")) {
      responseData = await response.json();
    } else {
      responseData = await response.text();
    }

    if (!response.ok) {
      throw new BackendClientError(
        typeof responseData === "object" && responseData.detail
          ? String(responseData.detail)
          : `API request failed with status ${response.status}`,
        response.status,
        responseData,
      );
    }

    return responseData as T;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof BackendClientError) {
      throw error;
    }
    if (error instanceof Error && error.name === "AbortError") {
      throw new BackendClientError(`Request to backend timed out after ${REQUEST_TIMEOUT_MS}ms`);
    }
    throw new BackendClientError(
      error instanceof Error ? error.message : "An unexpected error occurred communicating with the backend"
    );
  }
}

export const backendClient = {
  /**
   * Health check / ping.
   */
  async health(): Promise<{ status: string }> {
    return request<{ status: string }>("/health");
  },

  /**
   * Get list of available workflows.
   */
  async workflows(): Promise<string[]> {
    return request<string[]>("/workflows");
  },

  /**
   * Create a campaign resource in the backend.
   */
  async createCampaign(
    id: string,
    name: string,
    workflow: WorkflowType,
    config: Record<string, any>
  ): Promise<BackendCampaignState> {
    return request<BackendCampaignState>("/campaigns", {
      method: "POST",
      body: JSON.stringify({
        id,
        name,
        workflow,
        config,
      }),
    });
  },

  /**
   * Get a campaign resource from the backend.
   */
  async getCampaign(id: string): Promise<BackendCampaignState> {
    return request<BackendCampaignState>(`/campaigns/${id}`);
  },

  /**
   * Update campaign config/metadata in the backend.
   */
  async updateCampaign(
    id: string,
    patch: {
      name?: string;
      workflow?: WorkflowType;
      config?: Record<string, any>;
    }
  ): Promise<BackendCampaignState> {
    return request<BackendCampaignState>(`/campaigns/${id}`, {
      method: "PATCH",
      body: JSON.stringify(patch),
    });
  },

  /**
   * Trigger execution of the campaign's workflow.
   */
  async runCampaign(id: string): Promise<BackendCampaignState> {
    return request<BackendCampaignState>(`/campaigns/${id}/run`, {
      method: "POST",
    });
  },
};

import type {
  ProviderListResponse,
  ProviderRecord,
  ProviderSummary,
  RiskLevel,
  User
} from "../types";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

type RequestOptions = {
  method?: string;
  body?: BodyInit | null;
  token?: string | null;
  headers?: Record<string, string>;
};

async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body = null, token = null, headers = {} } = options;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    body,
    headers: {
      ...headers,
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    }
  });

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`;
    try {
      const payload = (await response.json()) as { detail?: string };
      if (payload.detail) {
        detail = payload.detail;
      }
    } catch {
      // Keep fallback error text when payload is not JSON.
    }
    throw new Error(detail);
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export async function login(email: string, password: string): Promise<string> {
  const formData = new URLSearchParams();
  formData.append("username", email);
  formData.append("password", password);

  const data = await apiRequest<{ access_token: string }>("/auth/login", {
    method: "POST",
    body: formData,
    headers: { "Content-Type": "application/x-www-form-urlencoded" }
  });
  return data.access_token;
}

export function register(email: string, password: string): Promise<User> {
  return apiRequest<User>("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password }),
    headers: { "Content-Type": "application/json" }
  });
}

export function fetchMe(token: string): Promise<User> {
  return apiRequest<User>("/auth/me", { token });
}

export function fetchProviderSummary(token: string): Promise<ProviderSummary> {
  return apiRequest<ProviderSummary>("/providers/summary", { token });
}

type ProviderQuery = {
  page: number;
  pageSize: number;
  search: string;
  riskLevel: RiskLevel | "All";
};

export function fetchProviders(token: string, query: ProviderQuery): Promise<ProviderListResponse> {
  const params = new URLSearchParams({
    page: String(query.page),
    page_size: String(query.pageSize)
  });
  if (query.search.trim()) {
    params.set("search", query.search.trim());
  }
  if (query.riskLevel !== "All") {
    params.set("risk_level", query.riskLevel);
  }
  return apiRequest<ProviderListResponse>(`/providers?${params.toString()}`, { token });
}

export function importProviders(token: string, file: File): Promise<{ imported: number; source_file: string }> {
  const formData = new FormData();
  formData.append("file", file);
  return apiRequest<{ imported: number; source_file: string }>("/providers/import-csv", {
    method: "POST",
    token,
    body: formData
  });
}

export function validateProvider(token: string, providerId: string): Promise<ProviderRecord> {
  return apiRequest<ProviderRecord>(`/providers/${providerId}/validate`, {
    method: "POST",
    token
  });
}

export function validateAllProviders(token: string): Promise<{ processed: number }> {
  return apiRequest<{ processed: number }>("/providers/validate-all", {
    method: "POST",
    token
  });
}

export async function downloadProvidersCsv(token: string): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/providers/export/csv`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  if (!response.ok) {
    throw new Error(`Export failed with status ${response.status}`);
  }
  return response.blob();
}

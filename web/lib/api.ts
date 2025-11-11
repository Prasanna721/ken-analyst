const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
const API_SECRET = process.env.NEXT_PUBLIC_HASHED_API_SECRET;

interface APIResponse<T = any> {
  status: number;
  response: T;
}

async function apiRequest<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<APIResponse<T>> {
  const url = `${API_URL}${endpoint}`;

  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  if (API_SECRET && !endpoint.startsWith("/create_workspace")) {
    headers["Authorization"] = `Bearer ${API_SECRET}`;
  }

  if (options.body && typeof options.body === "object" && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }

  return response.json();
}

export async function searchCompanies(query: string, signal?: AbortSignal) {
  return apiRequest(`/search_listed?query=${encodeURIComponent(query)}`, { signal });
}

export async function getWorkspaces() {
  return apiRequest("/data/workspace");
}

export async function getWorkspaceById(workspaceId: string) {
  return apiRequest(`/data/workspace/${workspaceId}`);
}

export async function createWorkspace(
  workspaceId: string,
  ticker?: string,
  file?: File
) {
  const formData = new FormData();
  formData.append("workspace_id", workspaceId);
  if (ticker) {
    formData.append("ticker", ticker);
  }
  if (file) {
    formData.append("file", file);
  }

  return apiRequest("/create_workspace", {
    method: "POST",
    body: formData,
  });
}

export async function getDocuments(workspaceId: string) {
  return apiRequest(`/documents?workspace_id=${encodeURIComponent(workspaceId)}`);
}

export async function downloadDocument(documentId: string): Promise<Blob> {
  const url = `${API_URL}/documents/${documentId}/download`;

  const headers: Record<string, string> = {};
  if (API_SECRET) {
    headers["Authorization"] = `Bearer ${API_SECRET}`;
  }

  const response = await fetch(url, { headers });

  if (!response.ok) {
    throw new Error(`Failed to download document: ${response.statusText}`);
  }

  return response.blob();
}

export async function getActivities(workspaceId: string) {
  return apiRequest(`/data/activity?workspace_id=${encodeURIComponent(workspaceId)}`);
}

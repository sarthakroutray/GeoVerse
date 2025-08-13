// Centralized API client for GeoVerse frontend
// Handles environment-based base URL resolution for local dev (localhost:8000), Render, and Vercel
// Minimal type shims to avoid needing full @types/node in edge runtimes
// (The project already has @types/node, but we guard anyway.)
declare const process: any;

export function getApiBaseUrl(): string {
  if (process.env.NEXT_PUBLIC_API_BASE_URL) {
    return process.env.NEXT_PUBLIC_API_BASE_URL.replace(/\/$/, "");
  }
  if (process.env.NEXT_PUBLIC_RENDER_BACKEND_URL) {
    return process.env.NEXT_PUBLIC_RENDER_BACKEND_URL.replace(/\/$/, "");
  }
  return 'http://localhost:8000';
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail: any = undefined;
    try { detail = await res.json(); } catch {}
    throw new Error(detail?.detail || `Request failed (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export interface ChatSourceDocument {
  title: string; url: string; content_snippet: string; score: number; relevance_score?: number; snippet?: string;
}
export interface ChatResponse {
  query: string; response: string; sources: ChatSourceDocument[]; retrieved_docs_count: number; timestamp: string; model?: string; status: string; error?: string;
}
export interface ChatRequestBody { message: string; top_k?: number; session_id?: string; }

export async function chatRequest(body: ChatRequestBody, signal?: AbortSignal): Promise<ChatResponse> {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/chat/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ top_k: 8, ...body }),
    signal,
  });
  return handleResponse<ChatResponse>(res);
}

export interface SearchResult { chunk_id: string; content: string; title: string; url: string; score: number; source_type: string; metadata?: Record<string, any>; }
export interface SearchResponse { results: SearchResult[]; total_results: number; query: string; processing_time: number; }

export async function searchRequest(query: string, opts: { top_k?: number; source_type?: string; min_score?: number } = {}): Promise<SearchResponse> {
  const init: RequestInit & { next?: { revalidate?: number } } = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, top_k: opts.top_k ?? 12, source_type: opts.source_type ?? 'webpage', min_score: opts.min_score ?? 0.5 })
  };
  // If running in Next.js (node runtime), it's safe to attach the next property
  try { (init as any).next = { revalidate: 0 }; } catch {}
  const res = await fetch(`${getApiBaseUrl()}/api/v1/search/`, init);
  return handleResponse<SearchResponse>(res);
}

export async function fetchSuggestions(partial: string): Promise<string[]> {
  const url = new URL(`${getApiBaseUrl()}/api/v1/chat/suggestions`);
  if (partial) url.searchParams.set('partial_query', partial);
  const res = await fetch(url.toString());
  const json = await handleResponse<{ suggestions: string[] }>(res);
  return json.suggestions;
}

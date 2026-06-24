import { ApiResult, apiRequest, get } from '@/lib/api/client';

import type { Job } from '@/lib/api/jobs';

export type SearchResult = {
  job: Job;
  rank: number;
  score: number;
  explanation: string;
};

export type Search = {
  id: string;
  prompt: string;
  created_at: string;
};

export type SearchDetail = Search & {
  results: SearchResult[];
};

export type TriggerSearchRequest = {
  cv_id: string;
  prompt: string;
  location?: string;
  include_remote?: boolean;
};

export type IngestAccepted = {
  status: string;
  job_id: string;
  message: string;
};

export type TriggerSearchResult =
  | { kind: 'search'; data: SearchDetail }
  | { kind: 'ingesting'; data: IngestAccepted };

export type ListSearchesParams = {
  limit?: number;
  offset?: number;
};

function buildQuery(params: Record<string, string | number | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined) {
      search.set(key, String(value));
    }
  }
  const query = search.toString();
  return query ? `?${query}` : '';
}

export async function triggerSearch(
  body: TriggerSearchRequest,
): Promise<ApiResult<TriggerSearchResult>> {
  const result = await apiRequest<SearchDetail | IngestAccepted>('/searches', {
    method: 'POST',
    body: JSON.stringify(body),
  });

  if (!result.ok) {
    return result;
  }

  if ('results' in result.data) {
    return { ok: true, data: { kind: 'search', data: result.data } };
  }

  return { ok: true, data: { kind: 'ingesting', data: result.data } };
}

export function getSearch(searchId: string): Promise<ApiResult<SearchDetail>> {
  return get<SearchDetail>(`/searches/${searchId}`);
}

export function listSearches(
  params: ListSearchesParams = {},
): Promise<ApiResult<Search[]>> {
  const query = buildQuery({
    limit: params.limit,
    offset: params.offset,
  });
  return get<Search[]>(`/searches${query}`);
}

export function findJobMatch(
  search: SearchDetail | null,
  jobId: string,
): SearchResult | undefined {
  return search?.results.find((result) => result.job.id === jobId);
}

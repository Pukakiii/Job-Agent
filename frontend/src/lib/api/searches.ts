import { ApiResult, get, post } from '@/lib/api/client';

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
};

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

export function triggerSearch(
  body: TriggerSearchRequest,
): Promise<ApiResult<SearchDetail>> {
  return post<SearchDetail>('/searches', body);
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

export function getSearchResults(
  searchId: string,
): Promise<ApiResult<SearchResult[]>> {
  return get<SearchResult[]>(`/searches/${searchId}/results`);
}

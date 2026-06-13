import { ApiResult, get } from '@/lib/api/client';

export type Job = {
  id: string;
  title: string;
  company: string | null;
  location: string | null;
  url: string;
};

export type JobScore = {
  job_id: string;
  rank: number;
  score: number;
  explanation: string;
};

export type PaginatedJobs = {
  items: Job[];
  total: number;
  limit: number;
  offset: number;
};

export type ListJobsParams = {
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

export function listJobs(
  params: ListJobsParams = {},
): Promise<ApiResult<PaginatedJobs>> {
  const query = buildQuery({
    limit: params.limit,
    offset: params.offset,
  });
  return get<PaginatedJobs>(`/jobs${query}`);
}

export function getJob(jobId: string): Promise<ApiResult<Job>> {
  return get<Job>(`/jobs/${jobId}`);
}

export function getJobScore(
  searchId: string,
  jobId: string,
): Promise<ApiResult<JobScore>> {
  return get<JobScore>(`/searches/${searchId}/jobs/${jobId}`);
}

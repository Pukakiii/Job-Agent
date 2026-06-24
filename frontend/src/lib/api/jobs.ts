import { ApiResult, get } from '@/lib/api/client';

export type Job = {
  id: string;
  title: string;
  company: string | null;
  location: string | null;
  url: string;
};

export type JobDetail = Job & {
  description: string;
  source: string;
  posted_at: string | null;
  ingested_at: string;
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
): Promise<ApiResult<Job[]>> {
  const query = buildQuery({
    limit: params.limit,
    offset: params.offset,
  });
  return get<Job[]>(`/jobs${query}`);
}

export function getJob(jobId: string): Promise<ApiResult<JobDetail>> {
  return get<JobDetail>(`/jobs/${jobId}`);
}

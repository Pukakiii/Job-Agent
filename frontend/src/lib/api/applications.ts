import { ApiResult, del, get, post, put } from '@/lib/api/client';

import type { Job } from '@/lib/api/jobs';

export type ApplicationStatus =
  | 'saved'
  | 'applied'
  | 'interview'
  | 'offer'
  | 'rejected';

export type Application = {
  id: string;
  job_id: string;
  cv_id: string | null;
  status: ApplicationStatus;
  notes: string | null;
  applied_at: string | null;
  created_at: string;
  updated_at: string;
  job?: Job;
};

export type CreateApplicationRequest = {
  job_id: string;
  status?: ApplicationStatus;
  notes?: string;
};

export type UpdateApplicationStatusRequest = {
  status: ApplicationStatus;
  notes?: string;
};

export type ListApplicationsParams = {
  status?: ApplicationStatus;
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

export function listApplications(
  params: ListApplicationsParams = {},
): Promise<ApiResult<Application[]>> {
  const query = buildQuery({
    status: params.status,
    limit: params.limit,
    offset: params.offset,
  });
  return get<Application[]>(`/applications${query}`);
}

export function createApplication(
  body: CreateApplicationRequest,
): Promise<ApiResult<Application>> {
  return post<Application>('/applications', body);
}

export function updateApplicationStatus(
  applicationId: string,
  body: UpdateApplicationStatusRequest,
): Promise<ApiResult<Application>> {
  return put<Application>(`/applications/${applicationId}`, body);
}

export function deleteApplication(
  applicationId: string,
): Promise<ApiResult<void>> {
  return del<void>(`/applications/${applicationId}`);
}

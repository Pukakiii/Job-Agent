import { ApiResult, get, post } from '@/lib/api/client';

export type OutreachEmail = {
  id: string;
  job_id: string | null;
  application_id: string | null;
  to_address: string;
  subject: string;
  body: string;
  status: 'draft' | 'sent' | 'failed';
  sent_at: string | null;
  created_at: string;
};

export type SendOutreachRequest = {
  to_address: string;
  subject: string;
  body: string;
  job_id?: string;
};

export type GenerateOutreachRequest = {
  to_address: string;
  job_id?: string;
  context?: string;
};

export function listOutreach(
  params: { limit?: number; offset?: number } = {},
): Promise<ApiResult<OutreachEmail[]>> {
  const search = new URLSearchParams();
  if (params.limit !== undefined) search.set('limit', String(params.limit));
  if (params.offset !== undefined) search.set('offset', String(params.offset));
  const query = search.toString();
  return get<OutreachEmail[]>(`/outreach${query ? `?${query}` : ''}`);
}

export function generateOutreachDraft(
  body: GenerateOutreachRequest,
): Promise<ApiResult<OutreachEmail>> {
  return post<OutreachEmail>('/outreach/generate', body);
}

export function sendOutreach(
  body: SendOutreachRequest,
): Promise<ApiResult<OutreachEmail>> {
  return post<OutreachEmail>('/outreach/send', body);
}

export function getOutreach(emailId: string): Promise<ApiResult<OutreachEmail>> {
  return get<OutreachEmail>(`/outreach/${emailId}`);
}

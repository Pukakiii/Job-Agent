import { ApiResult, apiRequest, del, get } from '@/lib/api/client';

export type CV = {
  id: string;
  original_filename: string;
  content_type: string;
  created_at: string;
};

export type UploadCVResponse = {
  id: string;
  original_filename: string;
  created_at: string;
};

export type ListCVsParams = {
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

export function listCVs(
  params: ListCVsParams = {},
): Promise<ApiResult<CV[]>> {
  const query = buildQuery({
    limit: params.limit,
    offset: params.offset,
  });
  return get<CV[]>(`/cvs${query}`);
}

export async function uploadCV(
  file: File,
): Promise<ApiResult<UploadCVResponse>> {
  const formData = new FormData();
  formData.append('file', file);

  return apiRequest<UploadCVResponse>('/cvs', {
    method: 'POST',
    headers: {
      Accept: 'application/json',
    },
    body: formData,
  });
}

export function setActiveCV(cvId: string): Promise<ApiResult<CV>> {
  return apiRequest<CV>(`/cvs/${cvId}/active`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
  });
}

export function deleteCV(cvId: string): Promise<ApiResult<void>> {
  return del<void>(`/cvs/${cvId}`);
}

import { ApiResult, del, get, post } from '@/lib/api/client';

export type DocumentType = 'resume' | 'cover_letter';

export type GeneratedDocument = {
  id: string;
  job_id: string;
  cv_id: string | null;
  doc_type: DocumentType;
  content: string;
  created_at: string;
};

export type GenerateDocumentRequest = {
  job_id: string;
  doc_type: DocumentType;
  cv_id?: string;
};

export function listDocuments(
  params: { doc_type?: DocumentType; limit?: number; offset?: number } = {},
): Promise<ApiResult<GeneratedDocument[]>> {
  const search = new URLSearchParams();
  if (params.doc_type) search.set('doc_type', params.doc_type);
  if (params.limit !== undefined) search.set('limit', String(params.limit));
  if (params.offset !== undefined) search.set('offset', String(params.offset));
  const query = search.toString();
  return get<GeneratedDocument[]>(`/documents${query ? `?${query}` : ''}`);
}

export function generateDocument(
  body: GenerateDocumentRequest,
): Promise<ApiResult<GeneratedDocument>> {
  return post<GeneratedDocument>('/documents/generate', body);
}

export function getDocument(docId: string): Promise<ApiResult<GeneratedDocument>> {
  return get<GeneratedDocument>(`/documents/${docId}`);
}

export function deleteDocument(docId: string): Promise<ApiResult<void>> {
  return del<void>(`/documents/${docId}`);
}

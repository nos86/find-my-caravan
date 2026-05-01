import { apiClient } from './client'
import type { ImportPreviewResult, ImportResult } from '../types/import'

export async function previewImport(
  file: File,
  format: 'csv' | 'json',
): Promise<ImportPreviewResult> {
  const formData = new FormData()
  formData.append('file', file)
  const response = await apiClient.post<ImportPreviewResult>(
    `/imports/preview?format=${format}`,
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } },
  )
  return response.data
}

export async function confirmImport(
  file: File,
  format: 'csv' | 'json',
  columnMapping: Record<string, string>,
): Promise<ImportResult> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('column_mapping', JSON.stringify(columnMapping))
  const response = await apiClient.post<ImportResult>(
    `/imports/confirm?format=${format}`,
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } },
  )
  return response.data
}

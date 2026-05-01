import { apiClient } from './client'
import type { Source, SourceCreate } from '../types/source'

export async function fetchSources(): Promise<Source[]> {
  const response = await apiClient.get<Source[]>('/sources')
  return response.data
}

export async function fetchSource(id: number): Promise<Source> {
  const response = await apiClient.get<Source>(`/sources/${id}`)
  return response.data
}

export async function createSource(data: SourceCreate): Promise<Source> {
  const response = await apiClient.post<Source>('/sources', data)
  return response.data
}

export async function updateSource(id: number, data: Partial<SourceCreate>): Promise<Source> {
  const response = await apiClient.patch<Source>(`/sources/${id}`, data)
  return response.data
}

export async function deleteSource(id: number): Promise<void> {
  await apiClient.delete(`/sources/${id}`)
}

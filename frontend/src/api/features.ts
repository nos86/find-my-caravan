import { apiClient } from './client'
import type { Feature } from '../types/feature'

export async function fetchFeatures(): Promise<Feature[]> {
  const response = await apiClient.get<Feature[]>('/features')
  return response.data
}

export async function fetchFeature(key: string): Promise<Feature> {
  const response = await apiClient.get<Feature>(`/features/${key}`)
  return response.data
}

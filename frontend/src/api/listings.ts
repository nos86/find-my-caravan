import { apiClient } from './client'
import type { Listing, ListingFilters, ListingSearchResult } from '../types/listing'

export interface MapListing {
  id: number
  title: string
  price: number | null
  year: number | null
  latitude: number
  longitude: number
  seller_type: string | null
  source_name: string | null
}

export async function fetchListings(filters: ListingFilters): Promise<ListingSearchResult> {
  const params: Record<string, unknown> = { ...filters }
  if (filters.features?.length) params.features = filters.features.join(',')
  if (filters.exclude_features?.length) params.exclude_features = filters.exclude_features.join(',')
  const response = await apiClient.get<ListingSearchResult>('/listings', { params })
  return response.data
}

export async function fetchListing(id: number): Promise<Listing> {
  const response = await apiClient.get<Listing>(`/listings/${id}`)
  return response.data
}

export async function markSold(id: number): Promise<void> {
  await apiClient.post(`/listings/${id}/mark-sold`)
}

export async function updateListing(id: number, data: Partial<Listing>): Promise<Listing> {
  const response = await apiClient.patch<Listing>(`/listings/${id}`, data)
  return response.data
}

export async function deleteListing(id: number): Promise<void> {
  await apiClient.delete(`/listings/${id}`)
}

export async function fetchMapListings(filters?: object): Promise<MapListing[]> {
  const response = await apiClient.get<MapListing[]>('/listings/map', { params: filters })
  return response.data
}

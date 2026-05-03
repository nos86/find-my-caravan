import { apiClient } from './client'
import type {
  PriceYearPoint,
  PriceDistributionBin,
  PriceByBrand,
  PriceByRegion,
} from '../types/analytics'

export async function fetchPriceYear(filters?: object): Promise<PriceYearPoint[]> {
  const response = await apiClient.get<PriceYearPoint[]>('/analytics/price-year', {
    params: filters,
  })
  return response.data
}

export async function fetchPriceDistribution(): Promise<PriceDistributionBin[]> {
  const response = await apiClient.get<PriceDistributionBin[]>('/analytics/price-distribution')
  return response.data
}

export async function fetchPriceByBrand(): Promise<PriceByBrand[]> {
  const response = await apiClient.get<PriceByBrand[]>('/analytics/price-by-brand')
  return response.data
}

export async function fetchPriceByRegion(): Promise<PriceByRegion[]> {
  const response = await apiClient.get<PriceByRegion[]>('/analytics/price-by-region')
  return response.data
}

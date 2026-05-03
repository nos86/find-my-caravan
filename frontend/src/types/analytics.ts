export interface PriceYearPoint {
  id: number
  title: string
  year: number
  price: number
  brand: string | null
  city: string | null
  source_name: string | null
  mileage_km: number | null
}

export interface PriceDistributionBin {
  bin: string
  count: number
}

export interface PriceByBrand {
  brand: string
  avg_price: number
  count: number
}

export interface PriceByRegion {
  region: string
  avg_price: number
  count: number
}

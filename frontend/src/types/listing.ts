export interface ListingFeature {
  feature_key: string
  value: string | null
  confidence: number | null
}

export interface Listing {
  id: number
  source_name: string | null
  source_type: string | null
  source_url: string | null
  title: string
  brand: string | null
  model: string | null
  version: string | null
  year: number | null
  price: number | null
  mileage_km: number | null
  fuel_type: string | null
  transmission: string | null
  engine_power_kw: number | null
  engine_displacement_cc: number | null
  emission_class: string | null
  length_mm: number | null
  width_mm: number | null
  height_mm: number | null
  mass_kg: number | null
  driving_license_category: string | null
  seats_travel: number | null
  seats_sleeping: number | null
  layout_type: string | null
  bed_types: string[] | null
  has_rear_garage: boolean | null
  garage_size_category: string | null
  has_bunk_beds: boolean | null
  has_double_floor: boolean | null
  bathroom_type: string | null
  heating_type: string | null
  air_conditioning: boolean | null
  solar_panel: boolean | null
  tow_bar: boolean | null
  seller_name: string | null
  seller_type: string | null
  address_raw: string | null
  city: string | null
  province: string | null
  region: string | null
  latitude: number | null
  longitude: number | null
  description_raw: string | null
  images: string[] | null
  first_seen_at: string
  last_seen_at: string
  status: string
  extraction_confidence: number | null
  enrichment_confidence: number | null
  features: ListingFeature[]
}

export interface ListingSearchResult {
  items: Listing[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface ListingFilters {
  q?: string
  source_type?: string
  region?: string
  province?: string
  city?: string
  price_min?: number
  price_max?: number
  year_min?: number
  year_max?: number
  mileage_min?: number
  mileage_max?: number
  brand?: string
  model?: string
  vehicle_type?: string
  seller_type?: string
  features?: string[]
  exclude_features?: string[]
  length_max_mm?: number
  sleeping_min?: number
  travel_seats_min?: number
  has_rear_garage?: boolean
  garage_size?: string
  license_category?: string
  only_with_coords?: boolean
  only_active?: boolean
  sort_by?: string
  page?: number
  page_size?: number
}

export interface Source {
  id: number
  name: string
  source_type: string
  base_url: string | null
  is_active: boolean
  scrape_interval_hours: number | null
  last_scraped_at: string | null
  created_at: string
  listing_count?: number
}

export interface SourceCreate {
  name: string
  source_type: string
  base_url?: string
  is_active?: boolean
  scrape_interval_hours?: number
}

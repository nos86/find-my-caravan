export interface ImportPreviewResult {
  detected_columns: string[]
  column_mapping: Record<string, string>
  preview_rows: Record<string, unknown>[]
  warnings: string[]
  total_rows: number
}

export interface ImportResult {
  total: number
  imported: number
  skipped: number
  errors: number
  error_messages: string[]
}

export interface ColumnMappingEntry {
  source_column: string
  target_field: string
}

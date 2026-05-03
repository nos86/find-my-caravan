from __future__ import annotations

import csv
import io
from pathlib import Path

from app.connectors.base import ParsedListing, RawListing, SourceConnector
from app.services.import_service import _map_columns, _process_row


class CSVConnector(SourceConnector):
    """Connector that reads listings from a local CSV file."""

    source_name = "csv_file"
    source_type = "csv"
    allowed = True

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)

    async def fetch_listing_urls(self, criteria: dict) -> list[str]:
        # CSV files don't have URLs per se; return row indices as pseudo-URLs.
        text = self.file_path.read_text(encoding="utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        return [f"csv://{self.file_path}#row{i}" for i, _ in enumerate(reader, 1)]

    async def fetch_listing_detail(self, url: str) -> RawListing:
        # For CSV we return the whole file as raw_data; real use would index by row.
        text = self.file_path.read_text(encoding="utf-8-sig")
        return RawListing(
            url=url,
            raw_data={"file": str(self.file_path), "content": text},
            source_name=self.source_name,
            source_type=self.source_type,
        )

    async def parse_listing(self, raw: RawListing) -> ParsedListing:
        # Extract row index from pseudo-URL and re-parse that row.
        row_num = int(raw.url.split("#row")[-1]) if raw.url and "#row" in raw.url else 0
        content = raw.raw_data.get("content", "")
        reader = csv.DictReader(io.StringIO(content))
        for i, row in enumerate(reader, 1):
            if i == row_num:
                cleaned, _ = _process_row(dict(row), i)
                if cleaned:
                    return ParsedListing(**{k: v for k, v in cleaned.items() if hasattr(ParsedListing, k)})
        return ParsedListing()

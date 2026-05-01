from __future__ import annotations

import json
from pathlib import Path

from app.connectors.base import ParsedListing, RawListing, SourceConnector
from app.services.import_service import _process_row


class JSONConnector(SourceConnector):
    """Connector that reads listings from a local JSON file."""

    source_name = "json_file"
    source_type = "json"
    allowed = True

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)

    def _load_rows(self) -> list[dict]:
        data = json.loads(self.file_path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            for key in ("listings", "items", "data", "results"):
                if key in data and isinstance(data[key], list):
                    return data[key]
            return [data]
        return data if isinstance(data, list) else []

    async def fetch_listing_urls(self, criteria: dict) -> list[str]:
        rows = self._load_rows()
        return [
            row.get("source_url") or row.get("url") or f"json://{self.file_path}#row{i}"
            for i, row in enumerate(rows, 1)
        ]

    async def fetch_listing_detail(self, url: str) -> RawListing:
        row_num = int(url.split("#row")[-1]) if "#row" in url else 1
        rows = self._load_rows()
        raw = rows[row_num - 1] if row_num <= len(rows) else {}
        return RawListing(
            url=url,
            raw_data=raw,
            source_name=self.source_name,
            source_type=self.source_type,
        )

    async def parse_listing(self, raw: RawListing) -> ParsedListing:
        row_num = int(raw.url.split("#row")[-1]) if raw.url and "#row" in raw.url else 1
        cleaned, _ = _process_row(raw.raw_data, row_num)
        if cleaned:
            pl = ParsedListing()
            for k, v in cleaned.items():
                if hasattr(pl, k):
                    setattr(pl, k, v)
            return pl
        return ParsedListing()

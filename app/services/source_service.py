import json
from typing import List
from app.schemas.source import SourceSchema

class SourceService:
    def get_sources(self) -> List[SourceSchema]:
        try:
            with open("app/config/sources.json", "r") as f:
                data = json.load(f)
                return [SourceSchema(**item) for item in data]
        except FileNotFoundError:
            return []

def get_source_service() -> SourceService:
    return SourceService()

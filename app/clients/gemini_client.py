import httpx
from typing import List, Optional
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class GeminiClient:
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not set. GeminiClient will fail if used.")

    async def embed_content(self, text: str, model: str = "models/gemini-embedding-001") -> List[float]:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required")

        url = f"{self.BASE_URL}/{model}:embedContent"
        
        # Construct payload adhering to Gemini API specs
        payload = {
            "model": model,
            "content": {
                "parts": [{
                    "text": text
                }]
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                params={"key": self.api_key},
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                logger.error(f"Gemini API Error: {response.status_code} - {response.text}")
                response.raise_for_status()
            
            data = response.json()
            # Response format: { "embedding": { "values": [ ... ] } }
            return data["embedding"]["values"]

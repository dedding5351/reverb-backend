from typing import List
from app.clients.gemini_client import GeminiClient

class GeminiService:
    def __init__(self, client: GeminiClient):
        self.client = client

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generates an embedding for the given text using Gemini.
        """
        # We can add caching or other logic here later
        return await self.client.embed_content(text)

def get_gemini_service() -> GeminiService:
    client = GeminiClient()
    return GeminiService(client)

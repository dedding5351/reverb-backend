from abc import ABC, abstractmethod
from typing import Iterator, List
from app.engine.models import PostMetadata
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class BaseScraper(ABC):
    def __init__(self, client: httpx.Client = None):
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Upgrade-Insecure-Requests": "1"
        }
        self.client = client or httpx.Client(timeout=10.0, follow_redirects=True, headers=headers)

    @abstractmethod
    def crawl(self, url: str) -> Iterator[PostMetadata]:
        """
        Main entry point. Crawls the given URL (e.g. blog home or feed)
        and yields PostMetadata for each discovered post.
        """
        pass

    @retry(
        retry=retry_if_exception_type(httpx.HTTPStatusError),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        stop=stop_after_attempt(5),
        reraise=True
    )
    def fetch(self, url: str) -> str:
        """Helper to fetch page content."""
        response = self.client.get(url)
        
        # Explicit check for 429 to trigger retry, others raise immediately
        if response.status_code == 429:
             raise httpx.HTTPStatusError(
                message="Rate Limited", 
                request=response.request, 
                response=response
            )
            
        response.raise_for_status()
        return response.text

from abc import abstractmethod
from typing import Iterator, List, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from app.engine.base import BaseScraper
from app.engine.models import PostMetadata
import time
import logging

logger = logging.getLogger(__name__)

class BlogScraper(BaseScraper):
    """
    Base class for specific blog scraping strategies.
    Implements a standard deep-crawling loop with pagination.
    Subclasses must define how to find links and extract data.
    """

    def crawl(self, url: str) -> Iterator[PostMetadata]:
        current_url = url
        visited_urls = set()
        
        # Safety limit
        page_limit = 10
        page_count = 0

        while current_url and page_count < page_limit:
            logger.info(f"Crawling Page: {current_url}")
            try:
                html = self.fetch(current_url)
                soup = BeautifulSoup(html, "html.parser")
                
                # 1. Get List of Post URLs
                post_links = self._get_post_links(soup, current_url)
                
                # 2. Visit Each Post
                for link in post_links:
                    if link in visited_urls:
                        continue
                    visited_urls.add(link)
                    
                    try:
                        # Re-fetch is inside process which calls fetch->extract
                        # Actually we need to fetch the post page here
                        post_html = self.fetch(link)
                        post_soup = BeautifulSoup(post_html, "html.parser")
                        
                        meta = self._extract_post_metadata(post_soup, link)
                        if meta:
                            yield meta
                        
                        time.sleep(0.5) # Polite delay
                    except Exception as e:
                        logger.error(f"Failed to process post {link}: {e}")

                # 3. Find Next Page
                next_link = self._get_next_page(soup, current_url)
                if next_link and next_link != current_url:
                    current_url = next_link
                    page_count += 1
                    time.sleep(1)
                else:
                    logger.info("No more pages found.")
                    break
            except Exception as e:
                logger.error(f"Error crawling page {current_url}: {e}")
                break

    @abstractmethod
    def _get_post_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Return a list of full URLs to blog posts found on the index page."""
        pass

    @abstractmethod
    def _get_next_page(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Return the URL of the next page, or None if last page."""
        pass

    @abstractmethod
    def _extract_post_metadata(self, soup: BeautifulSoup, post_url: str) -> Optional[PostMetadata]:
        """Extract metadata from a single post page."""
        pass

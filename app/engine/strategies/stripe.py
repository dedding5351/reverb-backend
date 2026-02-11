from typing import List, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from app.engine.blog_scraper import BlogScraper
from app.engine.models import PostMetadata
import dateutil.parser
import re

class StripeScraper(BlogScraper):
    def _get_post_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        links = []
        # Stripe specific: Articles are linked via generic anchors but with specific class pattern usually
        # Based on research: a.BlogIndexPost__titleLink
        
        for a in soup.find_all("a", class_="BlogIndexPost__titleLink"):
            href = a.get('href')
            if not href:
                continue
                
            full_url = urljoin(base_url, href)
            
            # Domain check
            if urlparse(full_url).netloc != urlparse(base_url).netloc:
                continue
            
            if full_url not in links and full_url != base_url:
                links.append(full_url)
                     
        return links

    def _get_next_page(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        # Based on research: a.BlogCategoryPagination__directionLink
        # It usually contains text "Next"
        
        # Look for the link with the specific class
        next_links = soup.find_all("a", class_="BlogCategoryPagination__directionLink")
        for link in next_links:
            if "Next" in link.get_text():
                return urljoin(base_url, link["href"])
                
        return None

    def _extract_post_metadata(self, soup: BeautifulSoup, post_url: str) -> Optional[PostMetadata]:
        # 1. Title
        title = None
        og_title = soup.find("meta", property="og:title")
        if og_title:
            title = og_title["content"]
        else:
            title_tag = soup.find("h1")
            if title_tag:
                title = title_tag.get_text().strip()
            else:
                title = soup.title.string if soup.title else "No Title"

        # 2. Description
        description = None
        og_desc = soup.find("meta", property="og:description")
        if og_desc:
            description = og_desc["content"]

        # 3. Authors
        authors = []
        # Meta author often works
        meta_auth = soup.find("meta", attrs={"name": "author"})
        if meta_auth:
             authors.append(meta_auth["content"])
        else:
            # Fallback to DOM
            author_link = soup.find("a", class_="BlogAuthor__link")
            if author_link:
                authors.append(author_link.get_text().strip())

        # 4. Date
        published_date = None
        pub_meta = soup.find("meta", property="article:published_time")
        if pub_meta:
            try:
                published_date = dateutil.parser.parse(pub_meta["content"])
            except:
                pass
        
        if not published_date:
            # Fallback to generic date extraction if needed, or specific class
            date_link = soup.find("a", class_="BlogPostDate__link")
            if date_link:
                try:
                    published_date = dateutil.parser.parse(date_link.get_text().strip())
                except:
                    pass

        # 5. Image
        image_url = None
        og_image = soup.find("meta", property="og:image")
        if og_image:
            candidate = og_image["content"]
            # Filter out invalid or query-only images like "?q=80"
            if candidate and not candidate.startswith("?"):
                # Handle relative URLs
                image_url = urljoin(post_url, candidate)
                
                # Double check it looks like a url
                if not image_url.startswith("http"):
                    image_url = None


        # 6. Content
        content = None
        body = soup.select_one(".BlogPost__body")
        if body:
             content = body.get_text(separator="\n\n", strip=True)

        return PostMetadata(
            title=title,
            url=post_url,
            description=description,
            authors=authors,
            published_date=published_date,
            site_name="Stripe Engineering",
            image_url=image_url,
            content=content
        )
